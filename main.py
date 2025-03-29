import github_utils
import os

if __name__ == "__main__":
    # 用你的访问令牌替换，或者设置为None（但有API速率限制）
    github_token = os.environ.get("GITHUB_TOKEN", None) 
    
    # 获取issues
    issues = github_utils.get_github_issues(
        owner="vllm-project",
        repo="vllm",
        state="open",
        token=github_token,
        max_pages=1  # 限制为第一页以便快速测试
    )
    print(f"获取到 {len(issues)} 个issues")
    if issues:
        print(f"第一个issue标题: {issues[0]['title']}")
        
    # 获取PRs
    prs = github_utils.get_github_pull_requests(
        owner="vllm-project",
        repo="vllm",
        state="open",
        token=github_token,
        max_pages=1,  # 限制为第一页以便快速测试
        include_files=True
    )
    print(f"获取到 {len(prs)} 个PRs")
    if prs:
        print(f"第一个PR标题: {prs[0]['title']}")
        print(f"修改的文件数: {len(prs[0]['files'])}")
        if prs[0]['files']:
            # 显示前5个修改的文件
            for i, file in enumerate(prs[0]['files'][:5]):
                print(f"  文件 {i+1}: {file['filename']} (状态: {file['status']}, 修改: +{file.get('additions', 0)} -{file.get('deletions', 0)})")