from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

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


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

class ShoppingAssistant:
    """Multi-agent shopping assistant dùng LangGraph."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.load()

        # 1. Load LLM
        self._llm = get_chat_model(self.settings)

        # 2. Load dataset order/customer
        self._data_store = ShoppingDataStore(self.settings.orders_path)

        # 3. Load embedding model + vector store
        self._embedding_model = SentenceTransformerEmbeddings(
            self.settings.embedding_model_name
        )
        self._policy_store = ChromaPolicyStore(
            persist_directory=self.settings.chroma_dir,
            embedding_model=self._embedding_model,
        )
        self._policy_store.ensure_index(self.settings.policy_path)

        # 4. Build tools
        self._data_tools = build_data_tools(self._data_store)
        self._policy_tool = self._build_policy_tool()

        # 5. Compile LangGraph
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
            """Tìm kiếm thông tin chính sách VinShop Demo liên quan đến query.
            Trả về các đoạn policy có liên quan với citation và nội dung.
            Dùng khi cần tra cứu chính sách giao hàng, đổi trả, hoàn tiền, voucher.
            """
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
                        "status": "ok",
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
            "ok": sum(1 for r in results if r["status"] == "ok"),
            "error": sum(1 for r in results if r["status"] == "error"),
            "results": results,
        }
        summary_path = output_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return summary


# ---------------------------------------------------------------------------
# LangGraph definition
# ---------------------------------------------------------------------------

def build_graph(
    llm: Any,
    policy_store: ChromaPolicyStore,
    data_tools: list,
    policy_tool: Any,
    top_k: int = 4,
) -> Any:
    """Định nghĩa StateGraph với 3 workers + supervisor."""

    # LLM bind tools cho từng worker
    llm_with_policy_tool = llm.bind_tools([policy_tool])
    llm_with_data_tools = llm.bind_tools(data_tools)

    # Node functions (closure để capture llm, tools)
    def _supervisor(state: ShoppingState) -> ShoppingState:
        return supervisor_node(state, llm)

    def _worker1(state: ShoppingState) -> ShoppingState:
        return worker_1_policy_node(state, llm_with_policy_tool, policy_tool)

    def _worker2(state: ShoppingState) -> ShoppingState:
        return worker_2_data_node(state, llm_with_data_tools, data_tools)

    def _worker3(state: ShoppingState) -> ShoppingState:
        return worker_3_response_node(state, llm)

    # Build graph
    graph = StateGraph(ShoppingState)
    graph.add_node("supervisor", _supervisor)
    graph.add_node("worker_1_policy", _worker1)
    graph.add_node("worker_2_data", _worker2)
    graph.add_node("worker_3_response", _worker3)

    # Entry point
    graph.set_entry_point("supervisor")

    # Conditional routing từ supervisor
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

    # Sau policy worker → kiểm tra xem có cần data không
    graph.add_conditional_edges(
        "worker_1_policy",
        _route_after_policy,
        {
            "data": "worker_2_data",
            "response": "worker_3_response",
        },
    )

    # Sau data worker → luôn đến response
    graph.add_edge("worker_2_data", "worker_3_response")

    # Response worker → END
    graph.add_edge("worker_3_response", END)

    return graph.compile()


def _route_after_supervisor(state: ShoppingState) -> str:
    route = state.get("route", {})

    # Nếu clarification_needed → thẳng đến response để trả câu hỏi lại
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
    # Fallback
    return "response"


def _route_after_policy(state: ShoppingState) -> str:
    route = state.get("route", {})
    if route.get("needs_data", False):
        return "data"
    return "response"


# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def supervisor_node(state: ShoppingState, llm: Any) -> ShoppingState:
    question = state.get("question", "")
    prompt = SUPERVISOR_PROMPT.format(question=question)

    t_start = timestamp_utc()
    response = llm.invoke([HumanMessage(content=prompt)])
    route = extract_json_payload(str(response.content))

    # Fallback nếu LLM không trả JSON đúng
    if not route:
        route = {
            "status": "ok",
            "needs_policy": True,
            "needs_data": False,
            "clarification_question": None,
        }

    trace_entry = {
        "timestamp": t_start,
        "agent": "supervisor",
        "action": "route",
        "decision": {
            "needs_policy": route.get("needs_policy"),
            "needs_data": route.get("needs_data"),
            "status": route.get("status"),
        },
        "status": "ok",
    }

    return {
        **state,
        "route": route,
        "trace": [trace_entry],
    }


def worker_1_policy_node(
    state: ShoppingState, llm_with_tools: Any, policy_tool: Any
) -> ShoppingState:
    question = state.get("question", "")
    prompt = POLICY_WORKER_PROMPT.format(question=question)

    t_start = timestamp_utc()

    # Agentic loop: gọi LLM → nếu có tool call → thực thi → gọi lại LLM
    from langchain_core.messages import AIMessage, ToolMessage

    messages = [HumanMessage(content=prompt)]
    policy_result = {}

    for _ in range(3):  # tối đa 3 vòng
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            # LLM đã trả lời cuối
            policy_result = extract_json_payload(str(response.content))
            break

        # Thực thi tool calls
        for tc in response.tool_calls:
            tool_output = policy_tool.invoke(tc["args"])
            messages.append(
                ToolMessage(
                    content=str(tool_output),
                    tool_call_id=tc["id"],
                    name=tc["name"],
                )
            )

    if not policy_result:
        policy_result = {
            "status": "not_found",
            "summary": "Không tìm thấy thông tin chính sách liên quan.",
            "facts": [],
            "citations": [],
        }

    trace_entry = {
        "timestamp": t_start,
        "agent": "worker_1_policy",
        "action": "rag_search",
        "status": policy_result.get("status", "ok"),
        "citations": policy_result.get("citations", []),
    }

    return {
        **state,
        "policy_result": policy_result,
        "trace": [trace_entry],
    }


def worker_2_data_node(
    state: ShoppingState, llm_with_tools: Any, data_tools: list
) -> ShoppingState:
    question = state.get("question", "")
    prompt = DATA_WORKER_PROMPT.format(question=question)

    t_start = timestamp_utc()

    from langchain_core.messages import AIMessage, ToolMessage

    # Build tool map để dispatch
    tool_map = {t.name: t for t in data_tools}

    messages = [HumanMessage(content=prompt)]
    data_result = {}

    for _ in range(5):  # tối đa 5 vòng (có thể gọi nhiều tools)
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            data_result = extract_json_payload(str(response.content))
            break

        # Thực thi tất cả tool calls trong response
        for tc in response.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                tool_output = tool_fn.invoke(tc["args"])
            else:
                tool_output = json.dumps({"error": f"Tool '{tc['name']}' not found"})

            messages.append(
                ToolMessage(
                    content=str(tool_output),
                    tool_call_id=tc["id"],
                    name=tc["name"],
                )
            )

    if not data_result:
        data_result = {
            "status": "not_found",
            "summary": "Không tìm thấy dữ liệu liên quan.",
            "facts": [],
            "missing_fields": [],
            "not_found_entities": [],
        }

    trace_entry = {
        "timestamp": t_start,
        "agent": "worker_2_data",
        "action": "data_lookup",
        "status": data_result.get("status", "ok"),
        "facts_count": len(data_result.get("facts", [])),
    }

    return {
        **state,
        "data_result": data_result,
        "trace": [trace_entry],
    }


def worker_3_response_node(state: ShoppingState, llm: Any) -> ShoppingState:
    question = state.get("question", "")
    route = state.get("route", {})
    policy_result = state.get("policy_result", {})
    data_result = state.get("data_result", {})

    t_start = timestamp_utc()

    prompt = RESPONSE_WORKER_PROMPT.format(
        question=question,
        route=json.dumps(route, ensure_ascii=False),
        policy_result=json.dumps(policy_result, ensure_ascii=False),
        data_result=json.dumps(data_result, ensure_ascii=False),
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    final_answer = str(response.content).strip()

    trace_entry = {
        "timestamp": t_start,
        "agent": "worker_3_response",
        "action": "synthesize",
        "status": "ok",
        "answer_length": len(final_answer),
    }

    return {
        **state,
        "final_answer": final_answer,
        "trace": [trace_entry],
    }
