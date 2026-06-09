# Guide

Tài liệu này là hướng dẫn đầy đủ để bạn hoàn thiện lab multi-agent từ các file đã có trong repo.

## 1. Bài toán bạn cần giải

Bạn cần xây dựng một assistant hỗ trợ khách hàng mua sắm online. Assistant phải biết:

- trả lời câu hỏi về policy
- tra cứu dữ liệu đơn hàng, khách hàng, voucher
- kết hợp cả policy và dữ liệu thật để trả lời các câu hỏi phức hợp

Ví dụ:

- `Chính sách hoàn trả hàng ra sao?`
- `Đơn hàng 1971 bao giờ được giao?`
- `Đơn hàng 1971 có được hoàn trả không?`
- `Voucher của tôi còn dùng được không?`

## 2. Kiến trúc bắt buộc

Hệ thống của bạn phải có 4 phần:

1. `Supervisor Agent`
2. `Worker 1: Policy / RAG Agent`
3. `Worker 2: Order / Customer Lookup Agent`
4. `Worker 3: Response Agent`

Luồng xử lý:

1. User gửi câu hỏi
2. Supervisor phân tích câu hỏi
3. Supervisor quyết định gọi worker nào
4. Worker trả kết quả về state
5. Response worker tổng hợp câu trả lời cuối

## 3. Những gì repo đã cung cấp

Data:

- [data/policy_mock_vi.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/policy_mock_vi.md)
- [data/order_customer_mock_data.json](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/order_customer_mock_data.json)
- [data/README.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/README.md)

Starter code:

- [src/app/graph.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/graph.py)
- [src/app/data_access.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/data_access.py)
- [src/app/prompts.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/prompts.py)
- [src/rag/parser.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/parser.py)
- [src/rag/vector_store.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/vector_store.py)

Testing:

- [data/test.json](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/test.json)
- [Rubric.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/Rubric.md)

## 4. Việc cần làm trước tiên

Tạo `.env` trước khi chạy lab.

### Option A: Gemini

```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
GOOGLE_API_KEY=your_key_here
```

### Option B: OpenAI

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your_key_here
```

### Option C: OpenRouter

```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4.1-mini
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Option D: Ollama

```bash
LLM_PROVIDER=ollama
LLM_MODEL=qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434
```

### Option E: Anthropic

```bash
LLM_PROVIDER=custom
LLM_MODEL=claude-sonnet-4-0
CUSTOM_LLM_MODEL=claude-sonnet-4-0
CUSTOM_LLM_BASE_URL=your_anthropic_compatible_endpoint
CUSTOM_LLM_API_KEY=your_key_here
```

### Option F: Custom Provider

```bash
LLM_PROVIDER=custom
LLM_MODEL=your-model-name
CUSTOM_LLM_MODEL=your-model-name
CUSTOM_LLM_BASE_URL=your_base_url
CUSTOM_LLM_API_KEY=your_key_here
```

### Ghi chú về provider

- Scaffold hiện đã có provider modules cho:
  - `gemini`
  - `openai`
  - `openrouter`
  - `ollama`
  - `custom`
- Nếu bạn muốn dùng `anthropic` theo đúng package/provider riêng, bạn có thể:
  - tự thêm một module mới trong `src/provider/`
  - hoặc tạm đi qua `custom` nếu bạn có endpoint tương thích
- Không cần hỗ trợ tất cả provider để pass lab.
- Chỉ cần chọn `1` provider để hoàn thành bài.

Tạo môi trường và cài thư viện:

```bash
python3 -m venv .venv
.venv/bin/pip install -r src/requirements.txt
```

Sau đó chạy:

```bash
python -m py_compile src/app/*.py src/provider/*.py src/rag/*.py
```

Mục tiêu là kiểm tra code scaffold hiện tại chưa có lỗi syntax trước khi bạn sửa.

## 5. Hiểu dữ liệu order/customer

Trước khi viết agent, bạn phải hiểu schema JSON.

Đọc [data/README.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/README.md) và nắm các field quan trọng:

- `customer_id`
- `order_id`
- `order_status`
- `estimated_delivery`
- `eligible_for_return_until`
- `can_return_now`
- `max_voucher_per_month`
- `remaining_voucher_quota_this_month`

Các ID mẫu quan trọng:

- `C001`
- `1971`
- `2058`
- `9999`

## 6. Hoàn thiện Worker 2 trước

Lý do: worker dữ liệu dễ làm hơn RAG và sẽ giúp bạn debug flow multi-agent nhanh hơn.

Bạn cần sửa [src/app/data_access.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/data_access.py):

1. Load JSON một lần
2. Build các index:
   - `customer_by_id`
   - `order_by_id`
   - `orders_by_customer_id`
   - `vouchers_by_customer_id`
3. Viết ít nhất 4 tools nhỏ:
   - `get_customer_by_id(customer_id)`
   - `get_orders_by_customer_id(customer_id)`
   - `get_order_detail_by_order_id(order_id)`
   - `get_vouchers_by_customer_id(customer_id)`

Mỗi tool nên trả về object có `status`.

Ví dụ:

```json
{
  "status": "ok",
  "order": { "...": "..." }
}
```

hoặc:

```json
{
  "status": "not_found",
  "order_id": "9999"
}
```

## 7. Hoàn thiện Policy RAG

Bạn cần sửa:

- [src/rag/parser.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/parser.py)
- [src/rag/vector_store.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/vector_store.py)

### Bước 1: parse markdown

Chunk phải theo đúng logic:

- lấy `## heading 2`
- lấy từng `### heading 3`
- gom toàn bộ content của heading 3

Mỗi chunk nên có:

- `section_h2`
- `section_h3`
- `citation`
- `rendered_text`

Ví dụ một chunk:

- `5. Chính sách đổi trả và hoàn tiền`
- `5.1. Điều kiện chung để gửi yêu cầu`
- nội dung của mục `5.1`

### Bước 2: tạo Chroma index

Bạn cần:

1. Load embedding model `sentence-transformers/all-MiniLM-L6-v2`
2. Embed toàn bộ chunks
3. Add vào Chroma collection
4. Viết hàm search trả về top-k hits

Output của search nên có:

- `citation`
- `content`
- `distance`

## 8. Hoàn thiện prompts

File [src/app/prompts.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/prompts.py) hiện chỉ là pseudo code.

Bạn cần tự viết prompt thật cho:

- supervisor
- policy worker
- data worker
- response worker

Lưu ý:

- supervisor nên trả JSON nhỏ, dễ parse
- policy worker nên luôn gọi tool RAG trước
- data worker nên dùng tool nhỏ thay vì một tool lớn
- response worker phải giữ output format ổn định

## 9. Hoàn thiện Supervisor Agent

Bạn cần sửa [src/app/graph.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/graph.py).

Supervisor cần làm được:

- câu hỏi policy chung → route sang policy worker
- câu hỏi order/customer/voucher cụ thể → route sang data worker
- câu hỏi kiểu `đơn hàng 1971 có được hoàn trả không` → route sang cả hai
- câu hỏi thiếu `order_id` hoặc `customer_id` → `clarification_needed`

Ví dụ:

- `Voucher của tôi còn dùng được không?`
  - cần clarification vì thiếu định danh
- `Đơn hàng 1971 có được hoàn trả không?`
  - cần policy + data

## 10. Hoàn thiện các worker nodes

Trong [src/app/graph.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/graph.py), bạn cần hoàn thiện:

- `worker_1_policy_node`
- `worker_2_data_node`
- `worker_3_response_node`

### Worker 1

- gọi `search_policy`
- nhận các chunks liên quan
- tóm tắt policy
- trích citations

### Worker 2

- gọi các tools lookup
- trả facts đủ để response worker tổng hợp
- phản ánh `not_found` hoặc `clarification_needed` nếu có

### Worker 3

Phải trả final answer theo một trong ba format:

1. Success

```text
Answer: ...
Evidence:
- Policy: ...
- Order data: ...
```

2. Clarification

```text
Status: clarification_needed
Question: ...
```

3. Not found

```text
Status: not_found
Message: ...
```

## 11. Hoàn thiện LangGraph workflow

Bạn cần compile graph với:

- state chung
- node cho supervisor
- node cho worker 1
- node cho worker 2
- node cho worker 3
- conditional edges cho routing

State tối thiểu nên có:

- `question`
- `route`
- `policy_result`
- `data_result`
- `final_answer`
- `trace`

## 12. Thêm trace để debug

Mỗi lần chạy, bạn nên lưu trace ra JSON.

Trace nên ghi:

- output của supervisor
- tool calls của worker 1
- tool calls của worker 2
- policy chunks retrieve được
- final answer

Trace rất quan trọng vì nếu route sai hoặc tool chọn sai, bạn sẽ thấy lỗi ngay.

## 13. Chạy test từng bước

Đừng chờ đến cuối mới test.

Thứ tự tốt:

1. test data lookup
2. test RAG search
3. test supervisor route
4. test một câu policy
5. test một câu data
6. test một câu mixed
7. test clarification
8. test not_found

Ví dụ:

```bash
PYTHONPATH=src python -m app.cli --question "Chính sách hoàn trả hàng ra sao?"
PYTHONPATH=src python -m app.cli --question "Đơn hàng 1971 bao giờ được giao?"
PYTHONPATH=src python -m app.cli --question "Đơn hàng 1971 có được hoàn trả không?"
```

## 14. Chạy batch test với data/test.json

Sau khi hệ thống cơ bản chạy ổn, dùng [data/test.json](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/test.json).

Bạn nên hỗ trợ:

- đọc toàn bộ file test
- chạy từng câu
- lưu trace riêng từng case
- ghi `summary.json`

Các tiêu chí nên check:

- route có đúng không
- status có đúng không
- answer có đủ evidence không

## 15. Checklist trước khi nộp

Bạn nên tự kiểm tra:

- graph chạy được end-to-end
- RAG dùng `Chroma` thật
- embeddings dùng `all-MiniLM-L6-v2` thật
- có ít nhất 4 tools nhỏ
- có xử lý `clarification_needed`
- có xử lý `not_found`
- có trace JSON
- chạy được với `data/test.json`

## 16. Nếu muốn làm tốt hơn mức pass

Bạn có thể thêm:

- prompt rõ hơn cho từng worker
- citation đẹp hơn
- summary file cho batch test
- evaluator đơn giản để check route/status
- đổi provider mà không phải sửa graph

Cuối cùng, đối chiếu lại với [Rubric.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/Rubric.md) để biết mình đang ở mức điểm nào.
