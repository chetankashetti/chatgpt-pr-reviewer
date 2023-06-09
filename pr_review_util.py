from itertools import islice
import os
import requests
import openai
from github import Github

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up GitHub API
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
PY_GH_TOKEN = Github(GITHUB_ACCESS_TOKEN)
GITHUB_API_BASE_URL = "https://api.github.com"


def fetch_prs(repo):
    # Fetch open pull requests for a repository
    url = f"{GITHUB_API_BASE_URL}/repos/{repo}/pulls?state=open"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()


def fetch_pr_diff(repo, pr_number):
    # Fetch the diff for a pull request
    repo = PY_GH_TOKEN.get_repo(repo)
    pr = repo.get_pull(pr_number)
    files = list(islice(pr.get_files(), 51))
    diff = ''
    for file in files:
        patch = file.patch
        diff += patch
    print('Test', diff)
    return diff


def fetch_pr_commits(repo, pr_number):
    # Fetch the list of commits for a pull request
    url = f"{GITHUB_API_BASE_URL}/repos/{repo}/pulls/{pr_number}/commits"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()


def review_pr(pr, diff_content):
    # Generate a ChatGPT review for a PR with diff content
    prompt = f"Review the following pull request and only report issues else reply with a LGTM message:\nTitle: {pr['title']}\nDescription: {pr['body']}\nDiff:\n{diff_content}\n"
    response = openai.Completion.create(
        engine="text-davinci-002", prompt=prompt, max_tokens=200, n=1, stop=None, temperature=0.5)
    return response.choices[0].text.strip()


def post_review_comment(repo, pr, review):
    # Post the review as a comment on the PR
    url = f"{GITHUB_API_BASE_URL}/repos/{repo}/issues/{pr['number']}/comments"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    data = {"body": review}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
