from __future__ import annotations


def parse_policy_markdown(markdown_text: str) -> list[dict]:
    # TODO:
    # - parse markdown theo cấu trúc:
    #   ## 4. Chính sách giao hàng
    #   ### 4.3. Thời gian giao hàng dự kiến
    #   content...
    # - mỗi chunk cần giữ:
    #   - section_h2
    #   - section_h3
    #   - citation
    #   - rendered_text = H2 + H3 + content
    raise NotImplementedError("Student TODO: chunk policy markdown for RAG")
