# Rubric

Thang điểm: `0-100`

## 0-60: Core Lab Completion

- `15` điểm: Có `Supervisor Agent` và route đúng nhóm câu hỏi
- `15` điểm: Có `Worker 1` dùng RAG thật trên policy markdown
- `15` điểm: Có `Worker 2` dùng ít nhất 4 tools nhỏ, rõ nhiệm vụ
- `15` điểm: Có `Worker 3` tổng hợp được final answer

## 60-90: Engineering Quality

- `10` điểm: Chunking policy đúng cấu trúc `H2 + H3 + content`
- `10` điểm: Dùng `Chroma` + `sentence-transformers/all-MiniLM-L6-v2` thật
- `5` điểm: Có xử lý `clarification_needed`
- `5` điểm: Có xử lý `not_found`
- `10` điểm: Có batch test từ `data/test.json`

## 90-100: Bonus

- `3` điểm: Có citation rõ ràng cho policy chunks
- `3` điểm: Có trace JSON để debug từng bước graph
- `2` điểm: Provider abstraction sạch, đổi được `gemini/openai/openrouter/ollama/custom`
- `2` điểm: Prompt tách riêng cho từng agent, dễ đọc và dễ thay

## Trừ điểm

- `-10` đến `-20`: Gom toàn bộ lookup vào 1 tool chung chung
- `-10`: Không có routing thật, hard-code toàn bộ flow
- `-10`: Không có evidence hoặc không phân biệt policy/data
- `-10`: Không chạy được với dữ liệu hiện có trong repo
