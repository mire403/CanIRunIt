"""
Heuristic metrics for judging repository README quality and reproduction ease.

Scores are intentionally simple and explainable:
 - README clarity: structure, sections, length, headings
 - Example completeness: presence and quality of code examples / commands
 - Reproduction difficulty: install/run steps, environment notes, pitfalls
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import re


SECTION_HINTS = {
    "install": ["install", "installation", "安装", "依赖"],
    "usage": ["usage", "how to use", "用法", "使用", "使用方法"],
    "examples": ["example", "examples", "示例", "样例", "例子"],
    "requirements": ["requirements", "依赖", "环境", "prerequisite", "前置"],
    "run": ["run", "运行", "启动", "命令"],
}


@dataclass
class MetricResult:
    score: int  # 0-10
    rationale: str


@dataclass
class AllMetrics:
    readme_clarity: MetricResult
    example_completeness: MetricResult
    reproduction_difficulty: MetricResult

    def as_dict(self) -> Dict[str, Dict[str, object]]:
        return {
            "readme_clarity": {
                "score": self.readme_clarity.score,
                "rationale": self.readme_clarity.rationale,
            },
            "example_completeness": {
                "score": self.example_completeness.score,
                "rationale": self.example_completeness.rationale,
            },
            "reproduction_difficulty": {
                "score": self.reproduction_difficulty.score,
                "rationale": self.reproduction_difficulty.rationale,
            },
        }


def _normalize_text(text: str) -> str:
    return text.lower()


def _find_headings(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            # markdown heading
            headings.append(re.sub(r"^#+\s*", "", line))
    return headings


def score_readme_clarity(readme: Optional[str]) -> MetricResult:
    if not readme or not readme.strip():
        return MetricResult(0, "完全没有 README，没法怪我打零分。")

    text = readme
    norm = _normalize_text(text)
    headings = _find_headings(text)

    score = 3  # baseline for just having content
    reasons: List[str] = []

    # Length heuristic
    words = re.findall(r"\w+", text)
    word_count = len(words)
    if word_count < 50:
        reasons.append("README 字数非常少，更像是占位符。")
        score += 0
    elif word_count < 200:
        reasons.append("README 有一点点说明，但还是偏短。")
        score += 2
    elif word_count < 800:
        reasons.append("README 字数适中，信息量还可以。")
        score += 4
    else:
        reasons.append("README 字数很多，信息量应该不小。")
        score += 3

    # Structure: headings and key sections
    if headings:
        reasons.append(f"检测到 {len(headings)} 个标题，结构还算清晰。")
        score += min(3, len(headings))
    else:
        reasons.append("几乎没有使用标题，结构比较散。")

    # Check for key sections
    section_hits = 0
    for label, keywords in SECTION_HINTS.items():
        if any(k in norm for k in keywords):
            section_hits += 1
    if section_hits >= 3:
        reasons.append("安装/使用/示例等关键板块都有提到。")
        score += 3
    elif section_hits >= 1:
        reasons.append("只覆盖了部分关键板块。")
        score += 1
    else:
        reasons.append("关键的安装/使用等说明基本缺失。")

    score = max(0, min(10, score))
    return MetricResult(score=score, rationale="；".join(reasons))


def score_example_completeness(readme: Optional[str]) -> MetricResult:
    if not readme or not readme.strip():
        return MetricResult(0, "没有 README，更别提示例了。")

    text = readme
    norm = _normalize_text(text)

    code_blocks = re.findall(r"```[\s\S]*?```", text)
    inline_code = re.findall(r"`([^`]+)`", text)

    score = 1  # baseline for existing README
    reasons: List[str] = []

    # Look for obvious example / usage sections
    has_example_section = any(k in norm for k in SECTION_HINTS["examples"])
    has_usage_section = any(k in norm for k in SECTION_HINTS["usage"])

    if has_example_section or has_usage_section:
        reasons.append("有明显的示例/使用说明板块。")
        score += 4
    else:
        reasons.append("缺少专门的示例/Usage 板块。")

    # Code block richness
    if code_blocks:
        reasons.append(f"检测到 {len(code_blocks)} 段代码块。")
        if len(code_blocks) >= 3:
            score += 4
        elif len(code_blocks) >= 1:
            score += 2
    else:
        reasons.append("没有 markdown 代码块，示例偏少。")

    # Inline commands (pip install, python main.py, etc.)
    command_like = [
        c
        for c in inline_code
        if re.search(r"\b(pip|python|git|docker|npm|yarn)\b", c.lower())
    ]
    if command_like:
        reasons.append(f"README 中给出了 {len(command_like)} 个命令示例。")
        score += 2

    score = max(0, min(10, score))
    return MetricResult(score=score, rationale="；".join(reasons))


def score_reproduction_difficulty(readme: Optional[str]) -> MetricResult:
    if not readme or not readme.strip():
        return MetricResult(2, "没有任何说明，想跑起来基本全靠猜。")

    text = readme
    norm = _normalize_text(text)

    score = 3  # baseline
    reasons: List[str] = []

    # Installation instructions
    install_keywords = ["pip install", "poetry add", "conda install", "npm install"]
    if any(k in norm for k in install_keywords):
        reasons.append("明确给出了依赖安装命令。")
        score += 3
    elif any(k in norm for k in SECTION_HINTS["install"]):
        reasons.append("有安装相关说明，但缺少具体命令或细节。")
        score += 2
    else:
        reasons.append("基本没有提怎么安装依赖。")

    # Run / entrypoint commands
    run_keywords = [
        "python -m",
        "python main.py",
        "docker run",
        "docker compose",
        "npm start",
        "yarn start",
    ]
    if any(k in norm for k in run_keywords):
        reasons.append("提供了可以直接复制粘贴的运行命令。")
        score += 3
    elif any(k in norm for k in SECTION_HINTS["run"]):
        reasons.append("有运行相关说明，但缺少清晰命令。")
        score += 1
    else:
        reasons.append("没有告诉你到底该怎么启动这个项目。")

    # Environment hints (Python version, OS, GPU, etc.)
    env_hits = 0
    if re.search(r"python\s*[0-9.]+", norm):
        env_hits += 1
    if any(k in norm for k in ["windows", "linux", "macos", "ubuntu"]):
        env_hits += 1
    if any(k in norm for k in ["cuda", "gpu", "显卡", "显存"]):
        env_hits += 1
    if env_hits >= 2:
        reasons.append("对环境版本/依赖条件有比较明确的说明。")
        score += 2
    elif env_hits == 1:
        reasons.append("只给出了一点点环境信息。")
        score += 1
    else:
        reasons.append("几乎没提运行环境，容易踩坑。")

    # Danger / pitfalls
    if any(k in norm for k in ["warning", "注意", "caution", "小心"]):
        reasons.append("有提醒注意事项，算是比较贴心。")
        score += 1

    score = max(0, min(10, score))
    # Higher score = easier reproduction; transform into "difficulty" wording
    difficulty_score = score
    return MetricResult(
        score=difficulty_score,
        rationale="；".join(reasons),
    )


def compute_all_metrics(readme: Optional[str]) -> AllMetrics:
    """Compute all metrics from the given README content."""
    return AllMetrics(
        readme_clarity=score_readme_clarity(readme),
        example_completeness=score_example_completeness(readme),
        reproduction_difficulty=score_reproduction_difficulty(readme),
    )

