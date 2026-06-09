from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import Settings
from app.state import ShoppingState


class ShoppingAssistant:
    """Student scaffold.

    Mục tiêu:
    - Dùng `Settings` để load config.
    - Dùng provider trong `src/provider/`.
    - Dùng embedding loader thật trong `src/rag/embeddings.py`.
    - Tự hoàn thiện phần còn lại: graph, routing, tool calling, RAG search, response synthesis.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.load()

        # TODO 1:
        # - load chat model từ provider tương ứng
        # - load dataset order/customer
        # - load vector store cho policy
        # - build worker tools
        # - compile LangGraph

        self.graph = None

    def ask(
        self,
        question: str,
        trace_file: Path | None = None,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        # TODO 2:
        # - nếu rebuild_index=True thì rebuild Chroma collection
        # - invoke graph với state ban đầu
        # - lưu trace ra JSON nếu trace_file được cung cấp
        # - trả về payload gồm route, policy_result, data_result, final_answer, trace
        raise NotImplementedError("Student TODO: implement ask()")

    def run_batch(
        self,
        test_file: Path,
        output_dir: Path,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        # TODO 3:
        # - đọc data/test.json hoặc file test được truyền từ CLI
        # - chạy từng câu qua ask()
        # - lưu trace riêng cho từng case
        # - sinh summary.json
        raise NotImplementedError("Student TODO: implement run_batch()")


def build_graph() -> Any:
    # TODO 4:
    # - định nghĩa StateGraph(ShoppingState)
    # - add các node: supervisor, worker_1_policy, worker_2_data, worker_3_response
    # - add conditional edges cho routing
    raise NotImplementedError("Student TODO: compile the LangGraph workflow")


def supervisor_node(state: ShoppingState) -> ShoppingState:
    # TODO 5:
    # - gọi LLM để route câu hỏi
    # - output nên có:
    #   {
    #     "status": "ok | clarification_needed",
    #     "needs_policy": bool,
    #     "needs_data": bool,
    #     "clarification_question": str | None
    #   }
    raise NotImplementedError("Student TODO: implement supervisor routing")


def worker_1_policy_node(state: ShoppingState) -> ShoppingState:
    # TODO 6:
    # - build subgraph hoặc agent cho policy worker
    # - worker này phải dùng RAG thật qua tool `search_policy`
    # - output nên có summary + facts + citations
    raise NotImplementedError("Student TODO: implement the policy worker")


def worker_2_data_node(state: ShoppingState) -> ShoppingState:
    # TODO 7:
    # - build subgraph hoặc agent cho data worker
    # - worker này phải dùng các tools như:
    #   get_customer_by_id
    #   get_orders_by_customer_id
    #   get_order_detail_by_order_id
    #   get_vouchers_by_customer_id
    raise NotImplementedError("Student TODO: implement the data worker")


def worker_3_response_node(state: ShoppingState) -> ShoppingState:
    # TODO 8:
    # - tổng hợp output từ supervisor + workers
    # - tuân thủ format lab:
    #   Answer / Evidence
    #   hoặc clarification_needed
    #   hoặc not_found
    raise NotImplementedError("Student TODO: implement the response worker")
