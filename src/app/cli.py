from __future__ import annotations

import argparse

from app.graph import ShoppingAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Student scaffold CLI.")
    parser.add_argument("--question", help="Run one question through the graph.")
    parser.add_argument("--test-file", default="data/test.json")
    parser.add_argument("--trace-file", default=None)
    parser.add_argument("--batch", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    assistant = ShoppingAssistant()

    # TODO:
    # - nếu `--batch` thì đọc `data/test.json` và chạy batch
    # - nếu có `--question` thì chạy một câu
    # - lưu trace nếu user truyền `--trace-file`
    # - in final answer hoặc summary ra terminal
    raise NotImplementedError("Student TODO: finish the CLI entry point")


if __name__ == "__main__":
    main()
