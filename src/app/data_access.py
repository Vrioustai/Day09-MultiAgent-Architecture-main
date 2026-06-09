from __future__ import annotations

from pathlib import Path
from typing import Any


class ShoppingDataStore:
    """Student scaffold for mock-data lookup."""

    def __init__(self, json_path: Path) -> None:
        # TODO 1:
        # - đọc JSON
        # - lưu `metadata`, `customers`, `orders`, `vouchers`
        # - build các index để lookup nhanh
        raise NotImplementedError("Student TODO: load mock data and build indexes")

    def get_customer_by_id(self, customer_id: str) -> dict[str, Any]:
        # TODO 2:
        # - trả {"status":"ok","customer":...} hoặc {"status":"not_found", ...}
        raise NotImplementedError

    def get_orders_by_customer_id(self, customer_id: str, limit: int = 10) -> dict[str, Any]:
        # TODO 3:
        # - trả danh sách order gần nhất cho customer
        raise NotImplementedError

    def get_order_detail_by_order_id(self, order_id: str) -> dict[str, Any]:
        # TODO 4:
        # - trả chi tiết một order
        raise NotImplementedError

    def get_vouchers_by_customer_id(
        self,
        customer_id: str,
        only_active: bool = False,
    ) -> dict[str, Any]:
        # TODO 5:
        # - lọc voucher theo customer
        # - nếu `only_active=True` thì chỉ giữ voucher còn dùng được
        raise NotImplementedError


def build_data_tools(store: ShoppingDataStore) -> list:
    # TODO 6:
    # - dùng decorator @tool của LangChain
    # - wrap 4 methods lookup thành 4 tools nhỏ
    # - mô tả tool rõ ràng để LLM chọn đúng
    raise NotImplementedError("Student TODO: build lookup tools")
