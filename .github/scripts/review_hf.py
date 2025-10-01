import os
import requests
from github import Auth
from github import Github

# 환경 변수
repo_name = os.environ["GITHUB_REPOSITORY"]
pr_number = int(os.environ["PR_NUMBER"])

# GitHub API 클라이언트
auth = Auth.Token(os.environ["GITHUB_TOKEN"])
g = Github(auth=auth)
#g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# PR diff 가져오기
diff = requests.get(pr.diff_url).text

# Hugging Face Inference API 설정
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

payload = {
    "inputs": f"다음은 GitHub Pull Request의 diff입니다:\n{diff}\n\n이 코드를 리뷰해줘. 개선할 점을 bullet point로 정리해줘."
}

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code != 200:
    review_comment = f"⚠️ 모델 호출 실패: {response.text}"
else:
    try:
        review_comment = response.json()[0]["generated_text"]
    except Exception:
        review_comment = str(response.json())

# PR에 코멘트 작성
pr.create_issue_comment(f"🤖 AI 코드리뷰 (Hugging Face):\n\n{review_comment}")
