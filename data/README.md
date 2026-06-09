# Data Dictionary

## Files

- `policy_mock_vi.md`: knowledge base tiếng Việt cho `Policy / RAG Agent`
- `order_customer_mock_data.json`: mock data lớn cho `Order / Customer Lookup Agent`

## JSON structure

Top-level keys:

- `metadata`
- `customers`
- `orders`
- `vouchers`

## `metadata`

Thông tin tóm tắt dataset:

- `counts.customers`
- `counts.orders`
- `counts.vouchers`
- `featured_examples`
- `suggested_tools`

Các ID mẫu quan trọng:

- `C001`: khách hàng dùng cho case voucher
- `1971`: đơn đang giao, phù hợp cho câu hỏi ETA và quyền trả hàng khi chưa giao xong
- `2058`: đơn đã giao và còn trong hạn trả hàng
- `9999`: ví dụ cho case không tìm thấy dữ liệu

## `customers`

Một phần các field chính:

- `customer_id`
- `customer_name`
- `tier`
- `max_voucher_per_month`
- `vouchers_used_this_month`
- `remaining_voucher_quota_this_month`
- `total_orders`
- `total_spent`
- `latest_order_id`

Phù hợp cho các tools:

- `get_customer_by_id(customer_id)`
- `get_customer_voucher_info(customer_id)`

## `orders`

Một phần các field chính:

- `order_id`
- `customer_id`
- `order_status`
- `payment_method`
- `shipping_method`
- `carrier`
- `tracking_number`
- `created_at`
- `estimated_delivery`
- `delivered_at`
- `eligible_for_return_until`
- `can_return_now`
- `voucher_code`
- `items`

Phù hợp cho các tools:

- `get_order_detail_by_order_id(order_id)`
- `get_orders_by_customer_id(customer_id)`

## `vouchers`

Một phần các field chính:

- `voucher_code`
- `customer_id`
- `voucher_type`
- `discount_type`
- `discount_value`
- `min_order_value`
- `max_discount`
- `status`
- `remaining_uses`
- `assigned_order_id`
- `restored_after_cancellation`

Phù hợp cho tools:

- `get_vouchers_by_customer_id(customer_id)`

## Gợi ý implement nhanh

Sinh viên có thể đọc toàn bộ JSON một lần, sau đó build các index đơn giản:

- `customer_by_id`
- `orders_by_customer_id`
- `order_by_id`
- `vouchers_by_customer_id`

Như vậy mỗi tool chỉ cần lookup trên index tương ứng, không cần query phức tạp.
