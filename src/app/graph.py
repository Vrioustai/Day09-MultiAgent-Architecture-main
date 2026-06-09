from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph

from app.config import Settings
from app.data_access import ShoppingDataStore, build_data_tools
from app.prompts import (
    DATA_WORKER_PROMPT,
    POLICY_WORKER_PROMPT,
    RESPONSE_WORKER_PROMPT,
    SUPERVISOR_PROMPT,
)
from app.state import ShoppingState
from app.utils import extract_json_payload, timestamp_utc
from provider import get_chat_model
from rag.embeddings import SentenceTransformerEmbeddings
from rag.vector_store import ChromaPolicyStore


class ShoppingAssistant:
    """End-to-end multi-agent shopping assistant."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.load()
        self._llm = get_chat_model(self.settings)

        self._data_store = ShoppingDataStore(self.settings.orders_path)
        self._embedding_model = SentenceTransformerEmbeddings(
            self.settings.embedding_model_name
        )
        self._policy_store = ChromaPolicyStore(
            persist_directory=self.settings.chroma_dir,
            embedding_model=self._embedding_model,
        )
        self._policy_store.ensure_index(self.settings.policy_path)

        self._data_tools = build_data_tools(self._data_store)
        self._policy_tool = self._build_policy_tool()

        self.graph = build_graph(
            llm=self._llm,
            policy_store=self._policy_store,
            data_tools=self._data_tools,
            policy_tool=self._policy_tool,
            top_k=self.settings.top_k,
        )

    def _build_policy_tool(self):
        store = self._policy_store
        top_k = self.settings.top_k

        @tool
        def search_policy(query: str) -> str:
            """Search VinShop Demo policy with citations."""
            hits = store.search(query, top_k=top_k)
            return json.dumps(hits, ensure_ascii=False)

        return search_policy

    def ask(
        self,
        question: str,
        trace_file: Path | None = None,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        if rebuild_index:
            self._policy_store.rebuild(self.settings.policy_path)

        initial_state: ShoppingState = {
            "question": question,
            "route": {},
            "policy_result": {},
            "data_result": {},
            "final_answer": "",
            "trace": [],
        }

        final_state = self.graph.invoke(initial_state)
        payload = {
            "question": question,
            "route": final_state.get("route", {}),
            "policy_result": final_state.get("policy_result", {}),
            "data_result": final_state.get("data_result", {}),
            "final_answer": final_state.get("final_answer", ""),
            "trace": final_state.get("trace", []),
        }

        if trace_file is not None:
            trace_file = Path(trace_file)
            trace_file.parent.mkdir(parents=True, exist_ok=True)
            trace_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        return payload

    def run_batch(
        self,
        test_file: Path,
        output_dir: Path,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        test_file = Path(test_file)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        test_data = json.loads(test_file.read_text(encoding="utf-8"))
        cases = test_data if isinstance(test_data, list) else test_data.get("cases", [])

        results = []
        for i, case in enumerate(cases):
            question = case.get("question", "")
            case_id = case.get("id", f"case_{i:03d}")
            trace_path = output_dir / f"{case_id}_trace.json"
            try:
                result = self.ask(
                    question,
                    trace_file=trace_path,
                    rebuild_index=(rebuild_index and i == 0),
                )
                results.append(
                    {
                        "id": case_id,
                        "question": question,
                        "final_answer": result["final_answer"],
                        "route": result["route"],
                        "status": _answer_status(result["final_answer"]),
                        "trace_file": str(trace_path),
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "id": case_id,
                        "question": question,
                        "final_answer": "",
                        "route": {},
                        "status": "error",
                        "error": str(exc),
                    }
                )

        summary = {
            "total": len(results),
            "ok": sum(1 for r in results if r["status"] != "error"),
            "error": sum(1 for r in results if r["status"] == "error"),
            "results": results,
        }
        summary_path = output_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return summary


def build_graph(
    llm: Any,
    policy_store: ChromaPolicyStore,
    data_tools: list,
    policy_tool: Any,
    top_k: int = 4,
) -> Any:
    del policy_store, top_k

    llm_with_policy_tool = llm.bind_tools([policy_tool])
    llm_with_data_tools = llm.bind_tools(data_tools)

    graph = StateGraph(ShoppingState)
    graph.add_node("supervisor", lambda state: supervisor_node(state, llm))
    graph.add_node(
        "worker_1_policy",
        lambda state: worker_1_policy_node(state, llm_with_policy_tool, policy_tool),
    )
    graph.add_node(
        "worker_2_data",
        lambda state: worker_2_data_node(state, llm_with_data_tools, data_tools),
    )
    graph.add_node("worker_3_response", lambda state: worker_3_response_node(state, llm))

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {
            "policy_only": "worker_1_policy",
            "data_only": "worker_2_data",
            "both_policy_first": "worker_1_policy",
            "response": "worker_3_response",
        },
    )
    graph.add_conditional_edges(
        "worker_1_policy",
        _route_after_policy,
        {"data": "worker_2_data", "response": "worker_3_response"},
    )
    graph.add_edge("worker_2_data", "worker_3_response")
    graph.add_edge("worker_3_response", END)

    return graph.compile()


def _route_after_supervisor(state: ShoppingState) -> str:
    route = state.get("route", {})
    if route.get("status") == "clarification_needed":
        return "response"

    needs_policy = route.get("needs_policy", False)
    needs_data = route.get("needs_data", False)

    if needs_policy and needs_data:
        return "both_policy_first"
    if needs_policy:
        return "policy_only"
    if needs_data:
        return "data_only"
    return "response"


def _route_after_policy(state: ShoppingState) -> str:
    if state.get("route", {}).get("needs_data", False):
        return "data"
    return "response"


def supervisor_node(state: ShoppingState, llm: Any) -> ShoppingState:
    question = state.get("question", "")
    heuristic_route = _heuristic_route(question)
    route: dict[str, Any] = {}
    try:
        prompt = SUPERVISOR_PROMPT.format(question=question)
        response = llm.invoke([HumanMessage(content=prompt)])
        route = extract_json_payload(str(response.content))
    except Exception:
        route = {}

    if (
        not route
        or heuristic_route.get("status") == "clarification_needed"
        or heuristic_route.get("needs_data")
    ):
        route = heuristic_route

    trace_entry = {
        "timestamp": timestamp_utc(),
        "agent": "supervisor",
        "action": "route",
        "decision": {
            "needs_policy": route.get("needs_policy"),
            "needs_data": route.get("needs_data"),
            "status": route.get("status"),
        },
        "status": "ok",
    }
    return {**state, "route": route, "trace": [trace_entry]}


def worker_1_policy_node(
    state: ShoppingState, llm_with_tools: Any, policy_tool: Any
) -> ShoppingState:
    question = state.get("question", "")
    policy_result: dict[str, Any] = {}
    tool_calls: list[dict[str, Any]] = []

    try:
        from langchain_core.messages import ToolMessage

        messages = [HumanMessage(content=POLICY_WORKER_PROMPT.format(question=question))]
        for _ in range(3):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            if not response.tool_calls:
                policy_result = extract_json_payload(str(response.content))
                break

            for tc in response.tool_calls:
                output = policy_tool.invoke(tc["args"])
                tool_calls.append({"name": tc["name"], "args": tc["args"]})
                messages.append(
                    ToolMessage(content=str(output), tool_call_id=tc["id"], name=tc["name"])
                )
    except Exception:
        policy_result = {}

    if not policy_result:
        policy_result = _policy_fallback(question, policy_tool)
        tool_calls.append({"name": "search_policy", "args": {"query": question}})

    trace_entry = {
        "timestamp": timestamp_utc(),
        "agent": "worker_1_policy",
        "action": "rag_search",
        "status": policy_result.get("status", "ok"),
        "citations": policy_result.get("citations", []),
        "tool_calls": tool_calls,
    }
    return {**state, "policy_result": policy_result, "trace": [trace_entry]}


def worker_2_data_node(
    state: ShoppingState, llm_with_tools: Any, data_tools: list
) -> ShoppingState:
    question = state.get("question", "")
    tool_map = {t.name: t for t in data_tools}
    data_result: dict[str, Any] = {}
    tool_calls: list[dict[str, Any]] = []

    try:
        from langchain_core.messages import ToolMessage

        messages = [HumanMessage(content=DATA_WORKER_PROMPT.format(question=question))]
        for _ in range(5):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            if not response.tool_calls:
                data_result = extract_json_payload(str(response.content))
                break

            for tc in response.tool_calls:
                tool_fn = tool_map.get(tc["name"])
                if tool_fn:
                    output = tool_fn.invoke(tc["args"])
                    tool_calls.append({"name": tc["name"], "args": tc["args"]})
                else:
                    output = json.dumps({"error": f"Tool '{tc['name']}' not found"})
                messages.append(
                    ToolMessage(content=str(output), tool_call_id=tc["id"], name=tc["name"])
                )
    except Exception:
        data_result = {}

    if state.get("route", {}).get("needs_data"):
        data_result = _data_fallback(question, tool_map)
        tool_calls.extend(data_result.pop("_tool_calls", []))
    elif not data_result:
        data_result = _data_fallback(question, tool_map)
        tool_calls.extend(data_result.pop("_tool_calls", []))

    trace_entry = {
        "timestamp": timestamp_utc(),
        "agent": "worker_2_data",
        "action": "data_lookup",
        "status": data_result.get("status", "ok"),
        "facts_count": len(data_result.get("facts", [])),
        "tool_calls": tool_calls,
    }
    return {**state, "data_result": data_result, "trace": [trace_entry]}


def _trim_for_prompt(result: dict) -> dict:
    """Chỉ giữ fields cần thiết, bỏ raw_results để LLM không in JSON thô."""
    return {
        "status": result.get("status"),
        "summary": result.get("summary", ""),
        "facts": result.get("facts", [])[:6],
        "citations": result.get("citations", [])[:4],
        "missing_fields": result.get("missing_fields", []),
        "not_found_entities": result.get("not_found_entities", []),
    }


def worker_3_response_node(state: ShoppingState, llm: Any) -> ShoppingState:
    question = state.get("question", "")
    route = state.get("route", {})
    policy_result = state.get("policy_result", {})
    data_result = state.get("data_result", {})

    final_answer = ""
    if route.get("status") == "clarification_needed" or data_result.get("status") in {
        "clarification_needed",
        "not_found",
    }:
        final_answer = _response_fallback(question, route, policy_result, data_result)
    else:
        try:
            prompt = RESPONSE_WORKER_PROMPT.format(
                question=question,
                route=json.dumps(
                    {"status": route.get("status"), "needs_policy": route.get("needs_policy"), "needs_data": route.get("needs_data")},
                    ensure_ascii=False,
                ),
                policy_result=json.dumps(_trim_for_prompt(policy_result), ensure_ascii=False),
                data_result=json.dumps(_trim_for_prompt(data_result), ensure_ascii=False),
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            final_answer = str(response.content).strip()
        except Exception:
            final_answer = ""

    if not final_answer:
        final_answer = _response_fallback(question, route, policy_result, data_result)

    trace_entry = {
        "timestamp": timestamp_utc(),
        "agent": "worker_3_response",
        "action": "synthesize",
        "status": _answer_status(final_answer),
        "answer_length": len(final_answer),
    }
    return {**state, "final_answer": final_answer, "trace": [trace_entry]}


def _normalize(text: str) -> str:
    return text.lower()


def _extract_order_id(question: str) -> str | None:
    match = re.search(r"\b(\d{4,})\b", question)
    return match.group(1) if match else None


def _extract_customer_id(question: str) -> str | None:
    match = re.search(r"\b(C\d{3,})\b", question, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def _heuristic_route(question: str) -> dict[str, Any]:
    q = _normalize(question)
    order_id = _extract_order_id(question)
    customer_id = _extract_customer_id(question)

    mentions_order = any(k in q for k in ["đơn", "order", "giao", "trạng thái"])
    mentions_customer = any(k in q for k in ["khách", "customer", "quota", "hạng"])
    mentions_voucher = "voucher" in q or "mã" in q
    mentions_policy = any(
        k in q
        for k in [
            "chính sách",
            "policy",
            "hoàn",
            "trả hàng",
            "đổi ý",
            "từ chối nhận",
            "bao lâu",
            "thời hạn",
            "kiểm hàng",
            "tiêu chuẩn",
            "giao nhanh",
            "15 ngày",
            "không hỗ trợ",
        ]
    )

    if (mentions_order and not order_id and "của tôi" in q) or (
        mentions_voucher and not customer_id and "của tôi" in q
    ):
        missing = "order_id" if mentions_order else "customer_id"
        return {
            "status": "clarification_needed",
            "needs_policy": False,
            "needs_data": False,
            "clarification_question": f"Bạn vui lòng cung cấp {missing} để mình tra cứu chính xác.",
        }

    if mentions_order and not order_id and not customer_id and "tôi" in q:
        return {
            "status": "clarification_needed",
            "needs_policy": False,
            "needs_data": False,
            "clarification_question": "Bạn vui lòng cung cấp order_id hoặc customer_id để mình tra cứu đơn hàng.",
        }

    needs_data = bool(
        order_id
        or customer_id
        or mentions_customer
        or (mentions_voucher and "của tôi" in q)
    )
    needs_policy = mentions_policy
    if order_id and any(k in q for k in ["hoàn", "trả", "đổi ý", "15 ngày", "từ chối nhận"]):
        needs_policy = True
        needs_data = True

    if not needs_policy and not needs_data:
        needs_policy = True

    return {
        "status": "ok",
        "needs_policy": needs_policy,
        "needs_data": needs_data,
        "clarification_question": None,
    }


def _policy_fallback(question: str, policy_tool: Any) -> dict[str, Any]:
    try:
        raw = policy_tool.invoke({"query": question})
        hits = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        hits = []

    if not hits:
        return {
            "status": "not_found",
            "summary": "Không tìm thấy thông tin chính sách liên quan.",
            "facts": [],
            "citations": [],
        }

    citations = [h.get("citation", "") for h in hits if h.get("citation")]
    facts = []
    for hit in hits[:3]:
        content = str(hit.get("content", "")).replace("\n", " ").strip()
        if content:
            facts.append(content[:350])

    return {
        "status": "ok",
        "summary": "Đã tìm thấy các mục chính sách liên quan trong knowledge base.",
        "facts": facts,
        "citations": citations,
    }


def _invoke_json_tool(tool_map: dict[str, Any], name: str, args: dict[str, Any]) -> dict[str, Any]:
    raw = tool_map[name].invoke(args)
    return json.loads(raw) if isinstance(raw, str) else raw


def _data_fallback(question: str, tool_map: dict[str, Any]) -> dict[str, Any]:
    order_id = _extract_order_id(question)
    customer_id = _extract_customer_id(question)
    q = _normalize(question)
    results: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    facts: list[str] = []
    not_found: list[str] = []

    if not order_id and not customer_id:
        missing = "customer_id" if "voucher" in q else "order_id/customer_id"
        return {
            "status": "clarification_needed",
            "summary": "Thiếu định danh để tra cứu dữ liệu.",
            "facts": [],
            "missing_fields": [missing],
            "not_found_entities": [],
            "_tool_calls": [],
        }

    if order_id:
        args = {"order_id": order_id}
        result = _invoke_json_tool(tool_map, "get_order_detail_by_order_id", args)
        calls.append({"name": "get_order_detail_by_order_id", "args": args})
        results.append(result)
        if result.get("status") == "ok":
            order = result["order"]
            facts.extend(
                [
                    f"Order {order.get('order_id')} status: {order.get('order_status')}",
                    f"Estimated delivery: {order.get('estimated_delivery')}",
                    f"Delivered at: {order.get('delivered_at')}",
                    f"Eligible for return until: {order.get('eligible_for_return_until')}",
                    f"Can return now: {order.get('can_return_now')}",
                    f"Shipping method: {order.get('shipping_method')}",
                ]
            )
        else:
            not_found.append(f"order_id={order_id}")

    if customer_id:
        if any(k in q for k in ["hạng", "quota", "tối đa", "khách", "customer"]):
            args = {"customer_id": customer_id}
            result = _invoke_json_tool(tool_map, "get_customer_by_id", args)
            calls.append({"name": "get_customer_by_id", "args": args})
            results.append(result)
            if result.get("status") == "ok":
                customer = result["customer"]
                facts.extend(
                    [
                        f"Customer {customer.get('customer_id')} tier: {customer.get('tier')}",
                        f"Max voucher per month: {customer.get('max_voucher_per_month')}",
                        f"Remaining voucher quota this month: {customer.get('remaining_voucher_quota_this_month')}",
                        f"Latest order id: {customer.get('latest_order_id')}",
                    ]
                )
            else:
                not_found.append(f"customer_id={customer_id}")

        if any(k in q for k in ["đơn", "order", "gần đây", "danh sách"]):
            args = {"customer_id": customer_id}
            result = _invoke_json_tool(tool_map, "get_orders_by_customer_id", args)
            calls.append({"name": "get_orders_by_customer_id", "args": args})
            results.append(result)
            if result.get("status") == "ok":
                orders = result.get("orders", [])
                facts.append(
                    f"Customer {customer_id} has {result.get('total')} orders; recent order ids: "
                    + ", ".join(str(o.get("order_id")) for o in orders[:5])
                )
            else:
                not_found.append(f"orders_by_customer_id={customer_id}")

        if "voucher" in q or "mã" in q:
            args = {
                "customer_id": customer_id,
                "only_active": "còn" in q or "dùng được" in q,
            }
            result = _invoke_json_tool(tool_map, "get_vouchers_by_customer_id", args)
            calls.append({"name": "get_vouchers_by_customer_id", "args": args})
            results.append(result)
            if result.get("status") == "ok":
                vouchers = result.get("vouchers", [])
                codes = [v.get("voucher_code") for v in vouchers if v.get("voucher_code")]
                facts.append(f"Customer {customer_id} vouchers: " + ", ".join(codes[:10]))
            else:
                not_found.append(f"vouchers_by_customer_id={customer_id}")

    status = "ok" if facts else "not_found"
    return {
        "status": status,
        "summary": "Đã tra cứu dữ liệu đơn hàng/khách hàng/voucher." if facts else "Không tìm thấy dữ liệu liên quan.",
        "facts": facts,
        "missing_fields": [],
        "not_found_entities": not_found,
        "raw_results": results,
        "_tool_calls": calls,
    }


def _response_fallback(
    question: str,
    route: dict[str, Any],
    policy_result: dict[str, Any],
    data_result: dict[str, Any],
) -> str:
    del question
    if route.get("status") == "clarification_needed" or data_result.get("status") == "clarification_needed":
        clarification = route.get("clarification_question") or "Bạn vui lòng cung cấp thêm mã đơn hàng hoặc mã khách hàng."
        return f"Status: clarification_needed\nQuestion: {clarification}"

    if data_result.get("status") == "not_found":
        entities = ", ".join(data_result.get("not_found_entities", [])) or "dữ liệu được yêu cầu"
        return f"Status: not_found\nMessage: Không tìm thấy {entities}."

    if policy_result.get("status") == "not_found" and not data_result.get("facts"):
        return "Status: not_found\nMessage: Không tìm thấy thông tin phù hợp trong policy hoặc dữ liệu nội bộ."

    policy_facts = policy_result.get("facts", [])
    data_facts = data_result.get("facts", [])
    citations = policy_result.get("citations", [])

    answer_parts = []
    if data_facts:
        answer_parts.append("; ".join(data_facts[:4]))
    if policy_facts:
        answer_parts.append(policy_result.get("summary", "Có policy liên quan."))
    if not answer_parts:
        answer_parts.append("Đã xử lý câu hỏi dựa trên thông tin hiện có.")

    return (
        "Answer: "
        + " ".join(answer_parts)
        + "\nEvidence:\n- Policy: "
        + ("; ".join(citations[:3]) if citations else "Không dùng policy.")
        + "\n- Data: "
        + ("; ".join(data_facts[:6]) if data_facts else "Không dùng dữ liệu đơn hàng/khách hàng.")
    )


def _answer_status(answer: str) -> str:
    if answer.startswith("Status: clarification_needed"):
        return "clarification_needed"
    if answer.startswith("Status: not_found"):
        return "not_found"
    return "ok"
