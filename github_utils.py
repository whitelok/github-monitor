import requests
import time
from typing import Dict, List, Optional, Any, Union


def get_github_issues(
    owner: str,
    repo: str,
    state: str = "open",
    token: Optional[str] = None,
    per_page: int = 100,
    max_pages: int = 10
) -> List[Dict[str, Any]]:
    """
    获取指定GitHub仓库的issues
    
    参数:
        owner: 仓库所有者用户名或组织名
        repo: 仓库名称
        state: issue状态，可选值为 'open', 'closed', 'all'
        token: GitHub个人访问令牌(PAT)，如果提供会提高API速率限制
        per_page: 每页返回的issue数量
        max_pages: 最大获取页数，用于限制API调用次数
    
    返回:
        包含issue信息的字典列表
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    params = {
        "state": state,
        "per_page": per_page,
        "page": 1
    }
    
    all_issues = []
    
    for page in range(1, max_pages + 1):
        params["page"] = page
        
        response = requests.get(url, headers=headers, params=params)
        
        # 检查API调用限制
        if response.status_code == 403 and "API rate limit exceeded" in response.text:
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                print(f"API限制达到，等待{sleep_time}秒...")
                time.sleep(sleep_time)
                # 重试当前请求
                response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        issues = response.json()
        
        # 过滤掉PR，因为GitHub API的issues端点也会返回PR
        issues = [issue for issue in issues if "pull_request" not in issue]
        
        all_issues.extend(issues)
        
        # 如果返回的issues少于per_page，说明已经到达最后一页
        if len(issues) < per_page:
            break
    
    return all_issues


def get_github_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    token: Optional[str] = None,
    per_page: int = 100,
    max_pages: int = 10,
    include_files: bool = True
) -> List[Dict[str, Any]]:
    """
    获取指定GitHub仓库的Pull Requests，可选包含修改的文件
    
    参数:
        owner: 仓库所有者用户名或组织名
        repo: 仓库名称
        state: PR状态，可选值为 'open', 'closed', 'all'
        token: GitHub个人访问令牌(PAT)，如果提供会提高API速率限制
        per_page: 每页返回的PR数量
        max_pages: 最大获取页数，用于限制API调用次数
        include_files: 是否包含每个PR修改的文件列表
    
    返回:
        包含PR信息的字典列表，每个PR包含修改的文件信息
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    params = {
        "state": state,
        "per_page": per_page,
        "page": 1
    }
    
    all_prs = []
    
    for page in range(1, max_pages + 1):
        params["page"] = page
        
        response = requests.get(url, headers=headers, params=params)
        
        # 检查API调用限制
        if response.status_code == 403 and "API rate limit exceeded" in response.text:
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                print(f"API限制达到，等待{sleep_time}秒...")
                time.sleep(sleep_time)
                # 重试当前请求
                response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        prs = response.json()
        
        # 如果需要文件信息，为每个PR获取修改的文件
        if include_files:
            for pr in prs:
                pr["files"] = get_pr_files(owner, repo, pr["number"], token)
        
        all_prs.extend(prs)
        
        # 如果返回的PRs少于per_page，说明已经到达最后一页
        if len(prs) < per_page:
            break
    
    return all_prs


def get_pr_files(
    owner: str,
    repo: str,
    pr_number: int,
    token: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    获取特定PR修改的文件列表
    
    参数:
        owner: 仓库所有者用户名或组织名
        repo: 仓库名称
        pr_number: Pull Request编号
        token: GitHub个人访问令牌(PAT)
    
    返回:
        包含文件修改信息的字典列表
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    all_files = []
    page = 1
    per_page = 100
    
    while True:
        params = {
            "page": page,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        # 检查API限制
        if response.status_code == 403 and "API rate limit exceeded" in response.text:
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                print(f"API限制达到，等待{sleep_time}秒...")
                time.sleep(sleep_time)
                # 重试
                response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        files = response.json()
        all_files.extend(files)
        
        # GitHub API通过HTTP头部的Link字段指示分页
        if len(files) < per_page:
            break
        
        page += 1
    
    return all_files