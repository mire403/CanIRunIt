"""
Utilities for loading README and basic metadata from a GitHub repository.

This module focuses on:
 - Parsing GitHub HTTPS URLs
 - Using the GitHub REST API (no auth required for public repos)
 - Fallback strategies for locating README files
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import base64
import json
import re
from urllib.parse import urlparse

import requests


GITHUB_API_BASE = "https://api.github.com"


@dataclass
class RepoInfo:
    owner: str
    name: str
    default_branch: Optional[str]
    readme_text: Optional[str]
    homepage: Optional[str]
    description: Optional[str]


class RepoLoaderError(RuntimeError):
    """Domain-specific error when we fail to load repo information."""


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parse a GitHub HTTPS URL and return (owner, repo_name).

    Supported formats:
      - https://github.com/owner/repo
      - https://github.com/owner/repo/
      - https://github.com/owner/repo.git
      - git@github.com:owner/repo.git (partial support)
    """
    if url.startswith("git@github.com:"):
        # SSH style: git@github.com:owner/repo.git
        path = url.split("git@github.com:", 1)[1]
        if path.endswith(".git"):
            path = path[: -len(".git")]
        parts = path.strip("/").split("/")
    else:
        parsed = urlparse(url)
        if parsed.netloc.lower() != "github.com":
            raise RepoLoaderError(f"仅支持 GitHub 仓库链接，目前是: {url}")
        parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise RepoLoaderError(f"无法从链接中解析出 owner/repo: {url}")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]
    return owner, repo


def _github_get(path: str) -> requests.Response:
    url = f"{GITHUB_API_BASE}{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers, timeout=10)
    return resp


def fetch_repo_info(url: str) -> RepoInfo:
    """Fetch README and basic metadata for a GitHub repo."""
    owner, repo = parse_github_url(url)

    # Get repo metadata
    meta_resp = _github_get(f"/repos/{owner}/{repo}")
    if meta_resp.status_code != 200:
        raise RepoLoaderError(
            f"无法获取仓库信息 (HTTP {meta_resp.status_code}): {meta_resp.text}"
        )

    meta = meta_resp.json()
    default_branch = meta.get("default_branch")
    description = meta.get("description")
    homepage = meta.get("homepage")

    # Get README via GitHub API (content is base64-encoded)
    readme_resp = _github_get(f"/repos/{owner}/{repo}/readme")
    readme_text: Optional[str] = None

    if readme_resp.status_code == 200:
        data = readme_resp.json()
        content = data.get("content")
        encoding = data.get("encoding")
        if encoding == "base64" and content:
            readme_text = base64.b64decode(content).decode("utf-8", errors="replace")
    else:
        # fallback: try to fetch raw README from common names on default branch
        if default_branch:
            for filename in ("README.md", "Readme.md", "README", "readme.md"):
                raw_url = (
                    f"https://raw.githubusercontent.com/{owner}/{repo}/"
                    f"{default_branch}/{filename}"
                )
                resp = requests.get(raw_url, timeout=10)
                if resp.status_code == 200:
                    readme_text = resp.text
                    break

    return RepoInfo(
        owner=owner,
        name=repo,
        default_branch=default_branch,
        readme_text=readme_text,
        homepage=homepage,
        description=description,
    )

