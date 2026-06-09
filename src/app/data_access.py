from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


class ShoppingDataStore:
    """Mock-data lookup với các index đã được build sẵn khi khởi tạo."""

    def __init__(self, json_path: Path) -> None:
        data = json.loads(json_path.read_text(encoding="utf-8"))

        self.metadata: dict = data.get("metadata", {})

        # Index customers
        customers: list[dict] = data.get("customers", [])
        self._customer_by_id: dict[str, dict] = {
            c["customer_id"]: c for c in customers
        }

        # Index orders
        orders: list[dict] = data.get("orders", [])
        self._order_by_id: dict[str, dict] = {
            str(o["order_id"]): o for o in orders
        }
        self._orders_by_customer_id: dict[str, list[dict]] = {}
        for o in orders:
            cid = str(o.get("customer_id", ""))
            self._orders_by_customer_id.setdefault(cid, []).append(o)

        # Index vouchers
        vouchers: list[dict] = data.get("vouchers", [])
        self._vouchers_by_customer_id: dict[str, list[dict]] = {}
        for v in vouchers:
            cid = str(v.get("customer_id", ""))
            self._vouchers_by_customer_id.setdefault(cid, []).append(v)

    # ------------------------------------------------------------------
    # Lookup methods
    # ------------------------------------------------------------------

    def get_customer_by_id(self, customer_id: str) -> dict[str, Any]:
        customer = self._customer_by_id.get(str(customer_id))
        if customer is None:
            return {
                "status": "not_found",
                "message": f"Không tìm thấy khách hàng với ID '{customer_id}'.",
            }
        return {"status": "ok", "customer": customer}

    def get_orders_by_customer_id(
        self, customer_id: str, limit: int = 10
    ) -> dict[str, Any]:
        orders = self._orders_by_customer_id.get(str(customer_id), [])
        if not orders:
            return {
                "status": "not_found",
                "message": f"Không tìm thấy đơn hàng nào cho khách hàng '{customer_id}'.",
            }
        # Sắp xếp mới nhất trước
        sorted_orders = sorted(
            orders, key=lambda o: o.get("created_at", ""), reverse=True
        )
        return {
            "status": "ok",
            "customer_id": customer_id,
            "total": len(sorted_orders),
            "orders": sorted_orders[:limit],
        }

    def get_order_detail_by_order_id(self, order_id: str) -> dict[str, Any]:
        order = self._order_by_id.get(str(order_id))
        if order is None:
            return {
                "status": "not_found",
                "message": f"Không tìm thấy đơn hàng với ID '{order_id}'.",
            }
        return {"status": "ok", "order": order}

    def get_vouchers_by_customer_id(
        self,
        customer_id: str,
        only_active: bool = False,
    ) -> dict[str, Any]:
        vouchers = self._vouchers_by_customer_id.get(str(customer_id), [])
        if not vouchers:
            return {
                "status": "not_found",
                "message": f"Không tìm thấy voucher nào cho khách hàng '{customer_id}'.",
            }
        if only_active:
            vouchers = [
                v for v in vouchers
                if v.get("status") == "active" and v.get("remaining_uses", 0) > 0
            ]
        return {
            "status": "ok",
            "customer_id": customer_id,
            "total": len(vouchers),
            "vouchers": vouchers,
        }


# ------------------------------------------------------------------
# LangChain tools builder
# ------------------------------------------------------------------

def build_data_tools(store: ShoppingDataStore) -> list:
    """Wrap 4 lookup methods thành LangChain tools để LLM có thể gọi."""

    @tool
    def get_customer_by_id(customer_id: str) -> str:
        """Tra cứu thông tin khách hàng theo customer_id.
        Trả về thông tin hạng thành viên, hạn mức voucher, tổng đơn hàng.
        Dùng khi cần biết thông tin profile hoặc hạn mức voucher của khách.
        """
        result = store.get_customer_by_id(customer_id)
        return json.dumps(result, ensure_ascii=False)

    @tool
    def get_orders_by_customer_id(customer_id: str) -> str:
        """Tra cứu danh sách đơn hàng gần nhất của khách hàng theo customer_id.
        Trả về tối đa 10 đơn hàng mới nhất với trạng thái và thông tin cơ bản.
        Dùng khi cần xem lịch sử mua hàng hoặc tìm order_id của khách.
        """
        result = store.get_orders_by_customer_id(customer_id)
        return json.dumps(result, ensure_ascii=False)

    @tool
    def get_order_detail_by_order_id(order_id: str) -> str:
        """Tra cứu chi tiết một đơn hàng theo order_id.
        Trả về trạng thái giao hàng, phương thức thanh toán, ngày giao dự kiến,
        ngày giao thực tế, hạn trả hàng (eligible_for_return_until), can_return_now.
        Dùng khi cần kiểm tra trạng thái đơn hoặc quyền trả hàng.
        """
        result = store.get_order_detail_by_order_id(order_id)
        return json.dumps(result, ensure_ascii=False)

    @tool
    def get_vouchers_by_customer_id(customer_id: str, only_active: bool = False) -> str:
        """Tra cứu danh sách voucher của khách hàng theo customer_id.
        Nếu only_active=True thì chỉ trả về voucher còn hiệu lực và còn lượt dùng.
        Trả về loại voucher, giá trị giảm, điều kiện áp dụng, trạng thái.
        Dùng khi cần kiểm tra voucher hiện có hoặc hạn mức voucher.
        """
        result = store.get_vouchers_by_customer_id(customer_id, only_active=only_active)
        return json.dumps(result, ensure_ascii=False)

    return [
        get_customer_by_id,
        get_orders_by_customer_id,
        get_order_detail_by_order_id,
        get_vouchers_by_customer_id,
    ]
