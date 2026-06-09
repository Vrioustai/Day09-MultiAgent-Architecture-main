"""
VinShop Multi-Agent Shopping Assistant — Gradio UI
Chạy: PYTHONPATH=src python ui.py
"""
import sys
import json
import os

sys.path.insert(0, "src")

import gradio as gr
from app.graph import ShoppingAssistant

# ── Khởi tạo assistant một lần duy nhất ──────────────────────────────────────
print("Loading assistant (first run may take a moment)...")
assistant = ShoppingAssistant()
print("Assistant ready!")

# ── Câu hỏi mẫu ──────────────────────────────────────────────────────────────
SAMPLE_QUESTIONS = [
    "Chính sách hoàn trả hàng ra sao?",
    "Giao hàng tiêu chuẩn thường mất bao lâu?",
    "Voucher có được hoàn lại khi hủy đơn không?",
    "Đơn hàng 1971 bao giờ được giao?",
    "Đơn hàng 1971 có được hoàn trả không?",
    "Đơn hàng 2058 còn trong thời gian trả hàng không?",
    "Khách hàng C001 thuộc hạng gì và còn quota voucher bao nhiêu?",
    "Voucher của khách hàng C001 còn những mã nào dùng được?",
    "Voucher của tôi còn dùng được không?",
    "Kiểm tra đơn hàng 9999 giúp tôi",
]


# ── Hàm xử lý ─────────────────────────────────────────────────────────────────
def process_question(question: str):
    if not question.strip():
        return "", "", "", ""

    try:
        result = assistant.ask(question.strip())
    except Exception as e:
        return f"❌ Lỗi: {e}", "", "", ""

    # Final answer
    answer = result.get("final_answer", "")

    # Route info
    route = result.get("route", {})
    route_parts = []
    if route.get("needs_policy"):
        route_parts.append("📋 Policy")
    if route.get("needs_data"):
        route_parts.append("🗃️ Data")
    status = route.get("status", "ok")
    route_badge = " + ".join(route_parts) if route_parts else "—"
    route_info = f"**Status:** `{status}`  |  **Workers:** {route_badge}"

    # Trace
    trace = result.get("trace", [])
    trace_md = ""
    for entry in trace:
        agent = entry.get("agent", "?")
        action = entry.get("action", "?")
        st = entry.get("status", "ok")
        ts = entry.get("timestamp", "")[:19]
        icon = "✅" if st == "ok" else "⚠️"
        trace_md += f"{icon} `{ts}` **{agent}** → `{action}`\n"
        if agent == "supervisor":
            d = entry.get("decision", {})
            trace_md += f"   - needs_policy: `{d.get('needs_policy')}`, needs_data: `{d.get('needs_data')}`\n"
        elif agent == "worker_1_policy":
            cits = entry.get("citations", [])
            if cits:
                trace_md += f"   - Citations: {', '.join(cits[:2])}\n"
        elif agent == "worker_2_data":
            trace_md += f"   - Facts found: `{entry.get('facts_count', 0)}`\n"
        elif agent == "worker_3_response":
            trace_md += f"   - Answer length: `{entry.get('answer_length', 0)}` chars\n"

    # Raw JSON
    raw = json.dumps(result, ensure_ascii=False, indent=2)

    return answer, route_info, trace_md, raw


def use_sample(sample: str):
    return sample


# ── Giao diện ─────────────────────────────────────────────────────────────────
with gr.Blocks(title="VinShop Multi-Agent Assistant") as demo:

    # Header
    gr.HTML("""
        <div class="header-text">
            <h1>🛒 VinShop Multi-Agent Shopping Assistant</h1>
            <p style="color: #666;">Powered by LangGraph · RAG · Tool Calling</p>
        </div>
    """)

    with gr.Row():
        # Left: Input
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="💬 Câu hỏi của bạn",
                placeholder="Ví dụ: Đơn hàng 1971 có được hoàn trả không?",
                lines=3,
            )

            with gr.Row():
                submit_btn = gr.Button("🚀 Gửi câu hỏi", variant="primary", scale=3)
                clear_btn = gr.Button("🗑️ Xóa", scale=1)

            gr.Markdown("**📌 Câu hỏi mẫu:**")
            sample_btns = []
            for i in range(0, len(SAMPLE_QUESTIONS), 2):
                with gr.Row():
                    for j in [i, i + 1]:
                        if j < len(SAMPLE_QUESTIONS):
                            btn = gr.Button(
                                SAMPLE_QUESTIONS[j],
                                size="sm",
                                variant="secondary",
                            )
                            sample_btns.append((btn, SAMPLE_QUESTIONS[j]))

        # Right: Output
        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="✅ Câu trả lời",
                lines=8,
                interactive=False,
                elem_classes=["answer-box"],
            )
            route_output = gr.Markdown(label="🔀 Route")

    with gr.Accordion("🔍 Trace (luồng xử lý)", open=False):
        trace_output = gr.Markdown()

    with gr.Accordion("📄 Raw JSON output", open=False):
        raw_output = gr.Code(language="json", lines=20)

    # ── Event handlers ───────────────────────────────────────────────────────
    submit_btn.click(
        fn=process_question,
        inputs=[question_input],
        outputs=[answer_output, route_output, trace_output, raw_output],
    )

    question_input.submit(
        fn=process_question,
        inputs=[question_input],
        outputs=[answer_output, route_output, trace_output, raw_output],
    )

    clear_btn.click(
        fn=lambda: ("", "", "", "", ""),
        outputs=[question_input, answer_output, route_output, trace_output, raw_output],
    )

    # Sample buttons
    for btn, q in sample_btns:
        btn.click(fn=lambda x=q: x, outputs=[question_input])


# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        theme=gr.themes.Soft(),
    )
