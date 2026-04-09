import os
import subprocess
import anthropic
import requests

# ── 1. PR diff 추출 ──────────────────────────────────────────
base = os.environ["BASE_SHA"]
head = os.environ["HEAD_SHA"]

diff = subprocess.check_output(
    ["git", "diff", f"{base}...{head}", "--unified=5"],
    text=True
)

# diff가 너무 길면 Claude context 초과 방지
MAX_DIFF_CHARS = 15_000
if len(diff) > MAX_DIFF_CHARS:
    diff = diff[:MAX_DIFF_CHARS] + "\n\n[... diff truncated ...]"

# ── 2. Claude API 호출 ───────────────────────────────────────
client = anthropic.Anthropic()

system_prompt = """
당신은 시니어 개발자로서 코드 리뷰를 수행합니다.
아래 규칙을 따르세요:
- 버그, 보안 취약점, 성능 문제를 최우선으로 지적
- 코드 스타일은 심각한 경우만 언급
- 잘 작성된 부분은 칭찬
- 한국어로 작성, Markdown 형식 사용
- 응답은 300자 이내로 간결하게
"""

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"다음 PR diff를 리뷰해주세요:\n\n```diff\n{diff}\n```"
    }],
    system=system_prompt
)

review_comment = message.content[0].text

# ── 3. PR에 코멘트 등록 ──────────────────────────────────────
repo = os.environ["REPO"]
pr_number = os.environ["PR_NUMBER"]
token = os.environ["GH_TOKEN"]

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}
body = f"## 🤖 Claude Code Review\n\n{review_comment}"

resp = requests.post(url, headers=headers, json={"body": body})
resp.raise_for_status()
print(f"✅ 코멘트 등록 완료: {resp.json()['html_url']}")
