# Day 09 Multi Agents Architecture

Mục tiêu của bạn là xây dựng một `shopping assistant` theo mô hình multi-agent bằng `LangGraph`, dùng LLM thật, RAG thật, và mock data local.

Bạn sẽ làm việc trong [src](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src). Repo đã cung cấp:

- knowledge base ở [data/policy_mock_vi.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/policy_mock_vi.md)
- mock data ở [data/order_customer_mock_data.json](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/order_customer_mock_data.json)
- câu hỏi test ở [data/test.json](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/data/test.json)
- rubric chấm điểm ở [Rubric.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/Rubric.md)
- hướng dẫn chi tiết ở [Guide.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/Guide.md)

## Your Mission

Bạn cần hoàn thiện một hệ thống gồm:

- `Supervisor Agent`
- `Worker 1: Policy / RAG Agent`
- `Worker 2: Order / Customer Lookup Agent`
- `Worker 3: Response Agent`

Luồng mong muốn:

User  
→ Supervisor  
→ Policy worker và/hoặc Data worker  
→ Response worker  
→ Final answer

## Technical Requirements

- Dùng `LangGraph` để tổ chức flow multi-agent
- Dùng `sentence-transformers/all-MiniLM-L6-v2` để tạo embeddings
- Dùng `Chroma` làm vector store
- Chunk policy theo đúng cấu trúc:
  - `heading 2`
  - `heading 3`
  - `content của heading 3`
- Có ít nhất 4 tools:
  - `1` tool RAG search policy
  - `3` tools lookup order/customer/voucher
- Hỗ trợ đủ 3 nhóm câu hỏi:
  - policy
  - order/customer/voucher data
  - câu hỏi kết hợp policy + data
- Có xử lý:
  - `clarification_needed`
  - `not_found`

## Student Starter Files

Bắt đầu từ các file này:

- [src/app/graph.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/graph.py)
- [src/app/data_access.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/data_access.py)
- [src/app/prompts.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/app/prompts.py)
- [src/rag/parser.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/parser.py)
- [src/rag/vector_store.py](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/rag/vector_store.py)

Provider abstraction và embedding loader đã có sẵn. Bạn cần hoàn thiện phần graph orchestration, tools, RAG indexing, retrieval, và batch testing.

## Suggested Workflow

1. Tạo `.env` với tối thiểu `LLM_MODEL` và `GOOGLE_API_KEY`.
2. Cài dependencies từ [src/requirements.txt](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-9-MultiAgent/src/requirements.txt).
3. Hoàn thiện lookup tools trước.
4. Hoàn thiện policy chunking và Chroma index.
5. Hoàn thiện supervisor routing.
6. Hoàn thiện response worker.
7. Chạy test bằng `data/test.json`.
8. Lưu trace JSON để debug flow.

Ví dụ `.env`:

```bash
LLM_MODEL=gemini-3.1-flash-lite
GOOGLE_API_KEY=your_key_here
```

## Run After You Finish The TODOs

Ví dụ chạy 1 câu:

```bash
PYTHONPATH=src python -m app.cli --question "Đơn hàng 1971 có được hoàn trả không?"
```

Ví dụ chạy batch:

```bash
PYTHONPATH=src python -m app.cli --batch --test-file data/test.json
```
