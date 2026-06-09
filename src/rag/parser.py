from __future__ import annotations

import re


def parse_policy_markdown(markdown_text: str) -> list[dict]:
    """Parse policy markdown thành các chunk theo cấu trúc H2 / H3.

    Mỗi chunk trả về:
    {
        "section_h2": str,       # tiêu đề ## cấp 2
        "section_h3": str,       # tiêu đề ### cấp 3 (rỗng nếu không có)
        "citation": str,         # "policy_mock_vi.md > H2 > H3" hoặc "policy_mock_vi.md > H2"
        "rendered_text": str,    # H2 + H3 + content đầy đủ để embed
    }
    """
    chunks: list[dict] = []

    current_h2 = ""
    current_h3 = ""
    content_lines: list[str] = []

    def flush_chunk() -> None:
        """Lưu chunk hiện tại nếu có nội dung."""
        nonlocal content_lines
        text = "\n".join(content_lines).strip()
        if not text and not current_h3:
            content_lines = []
            return

        if current_h3:
            citation = f"policy_mock_vi.md > {current_h2} > {current_h3}"
            rendered = f"{current_h2}\n{current_h3}\n{text}".strip()
        else:
            citation = f"policy_mock_vi.md > {current_h2}"
            rendered = f"{current_h2}\n{text}".strip()

        chunks.append(
            {
                "section_h2": current_h2,
                "section_h3": current_h3,
                "citation": citation,
                "rendered_text": rendered,
            }
        )
        content_lines = []

    for line in markdown_text.splitlines():
        # Bỏ qua dòng H1 và blockquote đầu file
        if re.match(r"^# ", line) or re.match(r"^> ", line):
            continue

        if re.match(r"^## ", line):
            # Gặp H2 mới → flush chunk cũ, reset cả H2 lẫn H3
            flush_chunk()
            current_h2 = line.lstrip("# ").strip()
            current_h3 = ""
            content_lines = []

        elif re.match(r"^### ", line):
            # Gặp H3 mới → flush chunk cũ (giữ nguyên H2)
            flush_chunk()
            current_h3 = line.lstrip("# ").strip()
            content_lines = []

        else:
            # Dòng nội dung thường
            if current_h2:  # chỉ thu thập nếu đã vào section H2
                content_lines.append(line)

    # Flush chunk cuối cùng
    flush_chunk()

    return chunks
