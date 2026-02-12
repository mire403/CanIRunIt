"""
Command line interface for the `readmejudge` tool.

Example:
    readmejudge https://github.com/xxx/yyy
"""

from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from .repo_loader import RepoLoaderError, fetch_repo_info
from .metrics import compute_all_metrics
from .llm_review import generate_review


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="readmejudge",
        description="给 GitHub 仓库的 README 做一次“能不能跑起来”体检。",
    )
    parser.add_argument(
        "repo",
        help="GitHub 仓库地址，例如: https://github.com/owner/repo",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 形式输出原始评分数据（适合脚本集成）。",
    )
    return parser


def _print_human(repo_url: str, result) -> None:
    metrics_dict = result.as_dict()
    review_text = generate_review(metrics_dict)

    print(f"仓库: {repo_url}")
    print("-" * 60)
    print("评分：0-10 分，分数越高越友好，越容易一把跑起来。\n")

    def line(name: str, key: str) -> None:
        data = metrics_dict[key]
        print(f"{name: <10} {data['score']:>2} / 10  —— {data['rationale']}")

    line("README 清晰度", "readme_clarity")
    line("示例完整度", "example_completeness")
    line("复现难度", "reproduction_difficulty")

    print("\n吐槽点评：")
    print(review_text)


def main(argv: list[str] | None = None) -> NoReturn:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        repo_info = fetch_repo_info(args.repo)
    except RepoLoaderError as exc:
        print(f"加载仓库失败: {exc}", file=sys.stderr)
        raise SystemExit(1)

    metrics = compute_all_metrics(repo_info.readme_text)

    if args.json:
        import json

        data = {
            "repo": {
                "owner": repo_info.owner,
                "name": repo_info.name,
                "default_branch": repo_info.default_branch,
                "homepage": repo_info.homepage,
                "description": repo_info.description,
            },
            "metrics": metrics.as_dict(),
            "review": generate_review(metrics.as_dict()),
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        _print_human(args.repo, metrics)

    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()

