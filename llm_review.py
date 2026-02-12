"""
Lightweight "LLM-style" review generator.

To keep this project simple and dependency-free, we do not call any external
LLM API here. Instead, this module generates opinionated, slightly humorous
comments based on the metric scores.

If you want to plug in a real LLM (e.g. OpenAI), you can replace the
`generate_review` implementation with an API call using the structured
metrics as input.
"""

from __future__ import annotations

from typing import Dict


def _bucket(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "mid"
    if score >= 3:
        return "low"
    return "very_low"


def generate_review(metrics: Dict[str, Dict[str, object]]) -> str:
    """
    Generate a human-readable roast + praise paragraph in Chinese based on
    the metric scores and rationales.
    """
    rc = metrics["readme_clarity"]
    ec = metrics["example_completeness"]
    rd = metrics["reproduction_difficulty"]

    rc_bucket = _bucket(int(rc["score"]))
    ec_bucket = _bucket(int(ec["score"]))
    rd_bucket = _bucket(int(rd["score"]))

    parts = []

    # README clarity commentary
    if rc_bucket == "high":
        parts.append("README 的整体结构和说明算是相当在线，基本属于“看一眼就懂在干嘛”的水平。")
    elif rc_bucket == "mid":
        parts.append("README 还能看懂，但信息有点散，第一次来的同学可能要多扫几遍才能理顺。")
    elif rc_bucket == "low":
        parts.append("README 比较随缘，看得出作者是知道要写点什么，但明显没太用心整理。")
    else:
        parts.append("README 几乎是谜语人级别，要不是你贴了仓库链接，我都怀疑这是个空壳项目。")

    # Example completeness commentary
    if ec_bucket == "high":
        parts.append("示例给得比较走心，从安装到跑起来都有可以直接抄的代码块，体验友好。")
    elif ec_bucket == "mid":
        parts.append("有一些示例，但覆盖面一般，复杂一点的场景就得自己脑补了。")
    elif ec_bucket == "low":
        parts.append("示例偏少，大概属于“作者自己知道怎么用，所以没写太细”的那一挂。")
    else:
        parts.append("几乎没什么像样的示例，完全是“你先装着，怎么用你自己悟”。")

    # Reproduction difficulty commentary
    if rd_bucket == "high":
        parts.append("复现难度不高，依赖、环境、运行命令都写得比较清楚，踩坑概率可控。")
    elif rd_bucket == "mid":
        parts.append("想跑起来一般问题不大，但环境版本或细节上可能要多试几次。")
    elif rd_bucket == "low":
        parts.append("要完整跑通这个项目，估计要和报错日志做一阵子朋友。")
    else:
        parts.append("复现难度偏地狱，几乎全靠个人修为和搜索引擎加持。")

    parts.append(
        "综合来看，这个仓库的“能不能一把跑起来”指数如上，"
        "如果你打算在团队里推广它，建议先自己亲手踩一轮坑，再考虑安利给同事。"
    )

    return " ".join(parts)

