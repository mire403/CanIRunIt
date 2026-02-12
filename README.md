## CanIRunIt 🧪 – “这个仓库我能一把跑起来吗？”

CanIRunIt 是一个给 GitHub 仓库做 **「能不能一把跑起来」体检** 的小工具。  
目标只有一个：**你贴个仓库链接，我帮你判断——这玩意到底好不好跑、README 到底写没写人话。** 🧐

- **输入**：一个 GitHub 仓库链接（HTTPS / SSH 都 OK）  
- **输出**：
  - ⭐ **README 清晰度**：结构清不清楚、有没有标题、有没写清楚这是个啥  
  - 📚 **示例完整度**：有没有代码块、有没有命令、有没有 Usage / Examples 这种板块  
  - 🏃 **复现难度**：依赖、环境、运行命令写得清不清楚，能不能靠复制粘贴一把起飞  
  - 😈 **吐槽点评**：一段带点毒舌又不失客观的中文点评，帮你快速评估这个仓库敢不敢推荐给同事

---

## 功能一览 🎯

- **README 自动解析**
  - 从 GitHub API 自动获取仓库 README 内容
  - 支持多种 README 文件名（`README.md` / `Readme.md` / `README` 等）
  - 支持 HTTPS 链接和部分 SSH 链接（`git@github.com:owner/repo.git`）

- **三大评分维度**
  - **README 清晰度（0–10）**
    - 判断是否有标题、关键板块（安装 / 使用 / 示例 / 环境）
    - 根据字数粗略判断是「认真写」还是「随便糊」
  - **示例完整度（0–10）**
    - 检查是否有 markdown 代码块 ```...```
    - 检测 README 里有没有类似 `pip install` / `python main.py` 这种命令
  - **复现难度（0–10）**
    - 有没有写如何安装依赖
    - 有没有提供一键运行命令
    - 是否说明了 Python 版本 / OS / GPU 等环境要求

- **LLM 风格吐槽生成（规则版伪 LLM 🤖）**
  - 根据三项分数拼接成一段「看起来像 LLM 写的」中文评语
  - 语气风格介于「认真 code review」和「温柔吐槽」之间

- **多种输出模式**
  - 终端友好的 **人类可读输出**
  - 适合二次集成的 **JSON 输出**（配合你自己的可视化 / Bot / Web 面板）

---

## 安装 🚀

### 1. 克隆仓库

```bash
git clone https://github.com/yourname/CanIRunIt.git
cd CanIRunIt
```

> 如果你就是在本地开发，直接 `cd C:\Users\leno\Desktop\CanIRunIt` 即可。

### 2. 安装依赖

建议在虚拟环境中安装：

```bash
pip install -r requirements.txt
```

当前依赖非常轻量：

- `requests`：用来请求 GitHub API 和 RAW README 内容

### 3.（可选）安装成全局命令 `readmejudge` 🧑‍💻

如果你有 `pyproject.toml` / `setup.cfg` 之类的打包工具，可以配置一个 `console_scripts`：

```toml
[project.scripts]
readmejudge = "CanIRunIt.cli:main"
```

然后：

```bash
pip install .
```

之后就可以在任意位置直接敲：

```bash
readmejudge https://github.com/owner/repo
```

---

## 基本使用示例 📦

### 方式一：直接用模块入口运行

```bash
python -m CanIRunIt.cli https://github.com/owner/repo
```

预期输出示例（示意）：

```text
仓库: https://github.com/owner/repo
------------------------------------------------------------
评分：0-10 分，分数越高越友好，越容易一把跑起来。

README 清晰度     7 / 10  —— README 字数适中，信息量还可以；检测到 5 个标题，结构还算清晰；安装/使用/示例等关键板块都有提到。
示例完整度       6 / 10  —— 有明显的示例/使用说明板块；检测到 2 段代码块；README 中给出了 1 个命令示例。
复现难度         8 / 10  —— 明确给出了依赖安装命令；提供了可以直接复制粘贴的运行命令；对环境版本/依赖条件有比较明确的说明；有提醒注意事项，算是比较贴心。

吐槽点评：
README 的整体结构和说明算是相当在线，基本属于“看一眼就懂在干嘛”的水平。 示例给得比较走心，从安装到跑起来都有可以直接抄的代码块，体验友好。
复现难度不高，依赖、环境、运行命令都写得比较清楚，踩坑概率可控。综合来看，这个仓库的“能不能一把跑起来”指数如上，如果你打算在团队里推广它，建议先自己亲手踩一轮坑，再考虑安利给同事。
```

### 方式二：输出 JSON 方便集成 🤝

```bash
python -m CanIRunIt.cli --json https://github.com/owner/repo
```

返回类似：

```json
{
  "repo": {
    "owner": "owner",
    "name": "repo",
    "default_branch": "main",
    "homepage": null,
    "description": "Some project"
  },
  "metrics": {
    "readme_clarity": {
      "score": 7,
      "rationale": "README 字数适中，信息量还可以；检测到 5 个标题，结构还算清晰；安装/使用/示例等关键板块都有提到。"
    },
    "example_completeness": {
      "score": 6,
      "rationale": "有明显的示例/使用说明板块；检测到 2 段代码块；README 中给出了 1 个命令示例。"
    },
    "reproduction_difficulty": {
      "score": 8,
      "rationale": "明确给出了依赖安装命令；提供了可以直接复制粘贴的运行命令；对环境版本/依赖条件有比较明确的说明；有提醒注意事项，算是比较贴心。"
    }
  },
  "review": "README 的整体结构和说明算是相当在线，基本属于“看一眼就懂在干嘛”的水平。 示例给得比较走心，从安装到跑起来都有可以直接抄的代码块，体验友好。 复现难度不高，依赖、环境、运行命令都写得比较清楚，踩坑概率可控。综合来看，这个仓库的“能不能一把跑起来”指数如上，如果你打算在团队里推广它，建议先自己亲手踩一轮坑，再考虑安利给同事。"
}
```

你可以在自己的工具里直接 `subprocess` 调用，或者后续改成 Python 库方式集成。

---

## 代码结构深度解析 🧬

项目结构：

```text
CanIRunIt/
├── CanIRunIt/
│   ├── __init__.py
│   ├── repo_loader.py
│   ├── metrics.py
│   ├── llm_review.py
│   └── cli.py
├── README.md
└── requirements.txt
```

下面分模块简单深挖一下实现思路。

### `repo_loader.py` – 仓库与 README 加载器 🌐

核心职责：

- 解析各种 GitHub 仓库链接（包含 `.git` / 末尾 `/` 等情况）
- 调用 GitHub REST API 获取：
  - 仓库基础信息（`/repos/{owner}/{repo}`）
  - README 内容（`/repos/{owner}/{repo}/readme`）
- 在 API 没拿到 README 时，尝试访问 RAW 链接兜底

关键数据结构示例：

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RepoInfo:
    owner: str
    name: str
    default_branch: Optional[str]
    readme_text: Optional[str]
    homepage: Optional[str]
    description: Optional[str]
```

解析 GitHub 链接的逻辑支持：

- `https://github.com/owner/repo`
- `https://github.com/owner/repo/`
- `https://github.com/owner/repo.git`
- `git@github.com:owner/repo.git`

当通过 API 获取 README 失败时，会尝试访问：

- `https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/README.md`
- `Readme.md` / `README` / `readme.md` 等常见命名

失败时会抛出 `RepoLoaderError`，方便 CLI 友好提示用户。

### `metrics.py` – README 评分引擎 📊

这是整个项目的「大脑」，目前采用的是**可解释的启发式规则**，而不是黑盒模型。  
这样做的好处：

- 评分逻辑透明，你可以根据自己喜好调整权重或规则
- 便于后续替换为 LLM、Embedding、甚至自定义规则引擎

核心数据结构：

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class MetricResult:
    score: int
    rationale: str

@dataclass
class AllMetrics:
    readme_clarity: MetricResult
    example_completeness: MetricResult
    reproduction_difficulty: MetricResult

    def as_dict(self) -> Dict[str, Dict[str, object]]:
        ...
```

三个评分函数分别是：

- `score_readme_clarity(readme: Optional[str]) -> MetricResult`
- `score_example_completeness(readme: Optional[str]) -> MetricResult`
- `score_reproduction_difficulty(readme: Optional[str]) -> MetricResult`

公开的汇总函数：

```python
from CanIRunIt.metrics import compute_all_metrics

metrics = compute_all_metrics(readme_text)
```

里面会做的事情包括：

- 按字数区间粗略评估 README 是否像样：
  - `< 50`：几乎等于没写
  - `50–200`：有一点说明，但偏短
  - `200–800`：比较正常的 README
  - `> 800`：信息量很大（也可能啰嗦）
- 统计 Markdown 标题数量，判断结构是否清晰
- 搜索安装 / 用法 / 示例 / 环境相关关键词
- 提取 ``` 代码块 ``` 和 `行内代码` 中的命令行示例
- 检测 `python 3.x`、`Windows/Linux/MacOS`、`CUDA/GPU` 等环境提示

每个评分函数都会返回：

- `score`：0–10 的整数
- `rationale`：中文字符串，解释为什么是这个分数（方便你后续可视化或展示）

### `llm_review.py` – 假装 LLM 在点评 🤡

当前实现**没有调用真实 LLM**，而是：

- 根据三项评分做区间划分 （高 / 中 / 低 / 极低）
- 针对每个区间准备几段预设文案
- 最后把几段文案拼成一段完整的「评价 + 吐槽」文本

对外暴露一个函数：

```python
from CanIRunIt.llm_review import generate_review

review = generate_review(metrics.as_dict())
```

你未来可以在这里：

- 替换为真实 `OpenAI` / `DeepSeek` / 其他大模型 的 API 调用
- 把 `metrics.as_dict()` 丢到 prompt 里，生成更个性化的长文点评

### `cli.py` – 命令行入口 🧵

这是整个工具的对外入口，负责：

- 解析命令行参数
- 调用 `repo_loader` 获取仓库信息
- 调用 `metrics` 算分
- 调用 `llm_review` 生成吐槽
- 根据参数选择人类可读输出 / JSON 输出

关键入口函数：

```python
def main(argv: list[str] | None = None) -> NoReturn:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_info = fetch_repo_info(args.repo)
    metrics = compute_all_metrics(repo_info.readme_text)

    if args.json:
        ...
    else:
        _print_human(args.repo, metrics)
```

你也可以在 Python 代码里直接调用：

```python
from CanIRunIt.repo_loader import fetch_repo_info
from CanIRunIt.metrics import compute_all_metrics
from CanIRunIt.llm_review import generate_review

repo = fetch_repo_info("https://github.com/owner/repo")
metrics = compute_all_metrics(repo.readme_text)
print(metrics.as_dict())
print(generate_review(metrics.as_dict()))
```

---

## 适用场景 💡

- **评估开源项目引入成本**
  - 决定要不要把某个 GitHub 仓库引入到团队项目里
  - 快速扫一眼「好不好跑起来」「文档写得行不行」

- **帮助新人筛选学习项目**
  - 给实习生 / 新人一个项目列表前，先跑一遍 CanIRunIt
  - 把「复现难度太高」的项目提前标记出来

- **构建自己的工具链**
  - 和 CI / Bot / GitHub App 集成
  - 自动在 PR 或 Issue 里贴上 README 体检结果

---

## 未来规划 🛣️

- ✅ 基础版评分类与 CLI
- ⏳ 接入真实 LLM，根据 README 内容 + 代码结构做更深入点评
- ⏳ 支持对 `examples/`、`docs/` 目录等进一步分析
- ⏳ 出一个 Web 小页面，把评分和吐槽可视化成「能跑指数雷达图」 🕹️

---

## 许可证 📄

目前可根据你的实际使用需求选择合适的开源协议（例如 MIT / Apache-2.0 等），
在仓库根目录添加相应的 `LICENSE` 文件即可。

如果你基于这个项目做了更好玩的东西，欢迎提 Issue / PR，一起把「能不能一把跑起来」这件事做到极致。 😄

