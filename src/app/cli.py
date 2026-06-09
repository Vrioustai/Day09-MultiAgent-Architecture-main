from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.graph import ShoppingAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VinShop Multi-Agent Shopping Assistant CLI")
    parser.add_argument("--question", help="Chạy một câu hỏi qua graph.")
    parser.add_argument(
        "--test-file",
        default="data/test.json",
        help="File test JSON cho batch mode (default: data/test.json)",
    )
    parser.add_argument(
        "--output-dir",
        default="src/artifacts/traces",
        help="Thư mục lưu trace output (default: src/artifacts/traces)",
    )
    parser.add_argument(
        "--trace-file",
        default=None,
        help="Lưu trace của câu hỏi đơn vào file JSON.",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Chạy batch test từ --test-file.",
    )
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Rebuild Chroma index trước khi chạy.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    assistant = ShoppingAssistant()

    if args.batch:
        # Batch mode
        test_file = Path(args.test_file)
        output_dir = Path(args.output_dir)
        print(f"[Batch] Đọc test từ: {test_file}")
        summary = assistant.run_batch(
            test_file=test_file,
            output_dir=output_dir,
            rebuild_index=args.rebuild_index,
        )
        print(f"\n[Batch] Kết quả: {summary['ok']}/{summary['total']} thành công")
        print(f"[Batch] Summary lưu tại: {output_dir}/summary.json")

        for r in summary["results"]:
            status_icon = "✓" if r["status"] == "ok" else "✗"
            print(f"\n{status_icon} [{r['id']}] {r['question']}")
            if r["status"] == "ok":
                # In 3 dòng đầu của answer
                lines = r["final_answer"].splitlines()
                for line in lines[:3]:
                    print(f"   {line}")
                if len(lines) > 3:
                    print(f"   ...")
            else:
                print(f"   ERROR: {r.get('error', '')}")

    elif args.question:
        # Single question mode
        trace_file = Path(args.trace_file) if args.trace_file else None

        print(f"[Question] {args.question}")
        print("[Processing...]\n")

        result = assistant.ask(
            question=args.question,
            trace_file=trace_file,
            rebuild_index=args.rebuild_index,
        )

        print("=" * 60)
        print(result["final_answer"])
        print("=" * 60)

        # In route info
        route = result.get("route", {})
        print(f"\n[Route] needs_policy={route.get('needs_policy')} | "
              f"needs_data={route.get('needs_data')} | "
              f"status={route.get('status')}")

        # In trace summary
        trace = result.get("trace", [])
        if trace:
            print(f"[Trace] {len(trace)} bước:")
            for entry in trace:
                print(f"  - {entry.get('agent', '?')} → {entry.get('action', '?')} "
                      f"[{entry.get('status', '?')}]")

        if trace_file:
            print(f"\n[Trace saved] {trace_file}")

    else:
        print("Vui lòng cung cấp --question hoặc --batch")
        print("Ví dụ:")
        print('  PYTHONPATH=src python -m app.cli --question "Đơn hàng 1971 có được hoàn trả không?"')
        print("  PYTHONPATH=src python -m app.cli --batch --test-file data/test.json")


if __name__ == "__main__":
    main()
