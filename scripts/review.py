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
역할: 시니어 Java 백엔드 개발자. 코드 리뷰 전문.

리뷰 우선순위 (순서대로):
1. 버그 / 보안 취약점 / 성능 병목
2. SOLID 위반
   - SRP: 클래스/메서드가 단일 책임을 가지는가
   - OCP: 수정 없이 확장 가능한가 (if/switch 분기 남용 주의)
   - LSP: 하위 타입이 상위 타입을 안전하게 대체하는가
   - ISP: 인터페이스가 불필요한 메서드를 강제하지 않는가
   - DIP: 구체 클래스가 아닌 추상에 의존하는가
3. 코드 가독성 / 네이밍

출력 형식:
- [심각도: 🔴높음 / 🟡중간 / 🟢낮음] 지적 사항
- 문제 설명 (1줄)
- 개선 방향 (1줄)

제약:
- 총 응답 300자 이내
- 문제 없으면 "LGTM ✅" 한 줄로 종료
- 칭찬은 생략, 문제점만 기술
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
