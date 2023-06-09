"""
This script uses the OpenAI GPT-4 model to generate responses to GitHub issues and posts them as comments.
"""

import os
import json
import time
import requests
import openai
from dotenv import load_dotenv
from typing import List, Dict, Union
import logging
import argparse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

GITHUB_READWRITE_TOKEN = os.getenv("GITHUB_READWRITE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_API_BASE_URL = "https://api.github.com"

openai.api_key = OPENAI_API_KEY

class GitHubAPIError(Exception):
    pass

class GPT4Error(Exception):
    pass

def get_latest_issues(repo_owner: str, repo_name: str) -> List[Dict[str, Union[str, int]]]:
    url = f"{GITHUB_API_BASE_URL}/repos/{repo_owner}/{repo_name}/issues"
    headers = {"Authorization": f"token {GITHUB_READWRITE_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise GitHubAPIError(f"Failed to fetch issues: {response.content}")

def get_issue_comments(repo_owner: str, repo_name: str, issue_number: int) -> List[Dict[str, str]]:
    url = f"{GITHUB_API_BASE_URL}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {GITHUB_READWRITE_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise GitHubAPIError(f"Failed to fetch comments: {response.content}")

def generate_gpt4_response(prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are AI-GitHub-Issue-Helper.\nYour job is to take in a GitHub issue from the user and respond.""",
        },
        {"role": "user", "content": prompt},
    ]

    # logging.info(f"Generating response for prompt: {prompt}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )
    except Exception as e:
        raise GPT4Error(f"Error generating response: {e}")

    return response.choices[0].message["content"]

def post_github_comment(repo_owner: str, repo_name: str, issue_number: int, body: str) -> None:
    disclaimer = "\n\n---\n\n*This response was generated by [AI-GitHub-Interlocutor](https://github.com/Torantulino/AGI) and may not be accurate or appropriate. The author of this repository and the creator of the AI model assume no responsibility or liability for any consequences arising from the use of the information provided in this response. 🤖*"
    body += disclaimer

    url = f"{GITHUB_API_BASE_URL}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {GITHUB_READWRITE_TOKEN}"}
    data = {"body": body}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        logging.info(f"Comment posted on issue {issue_number}")
    else:
        raise GitHubAPIError(f"Failed to post comment: {response.content}")

def display_comments_and_ai_response(issue: Dict[str, Union[str, int]], repo_owner: str, repo_name: str) -> str:
    comments = get_issue_comments(repo_owner, repo_name, issue["number"])

    full_text = issue["body"] + "\n\n".join(
        [comment["body"] for comment in comments]
    )

    prompt = f"GitHub issue: {issue['title']}\n {full_text}"
    response = generate_gpt4_response(prompt)
    
    print("===========================================================================")
    print(f"Issue {issue['number']}:\n{prompt}\n-------------------------------------------------------------\nAI-generated response:\n{response}")
    print("===========================================================================")

    return response

def user_confirmation() -> bool:
    user_input = input("Post this response? (Y/N): ")
    return user_input.lower() == 'y'

def process_issue(issue: Dict[str, Union[str, int]], repo_owner: str, repo_name: str) -> None:
    comments = get_issue_comments(repo_owner, repo_name, issue["number"])

    bot_already_commented = any(
        [True for comment in comments if comment["user"]["login"] == repo_owner]
    )

    if not bot_already_commented:
        response = display_comments_and_ai_response(issue, repo_owner, repo_name)
        if user_confirmation():
            post_github_comment(repo_owner, repo_name, issue["number"], response)
        else:
            logging.info(f"Skipped posting response on issue {issue['number']}")
    else:
        logging.info(f"Bot already commented on issue {issue['number']}")

def main() -> None:
    parser = argparse.ArgumentParser(description="AI GitHub Issue Helper")
    parser.add_argument("repo_owner", help="GitHub repository owner's username")
    parser.add_argument("repo_name", help="GitHub repository name")

    args = parser.parse_args()

    try:
        issues = get_latest_issues(args.repo_owner, args.repo_name)
        logging.info(f"Found {len(issues)} issues")

        for issue in issues:
            process_issue(issue, args.repo_owner, args.repo_name)

    except (GitHubAPIError, GPT4Error) as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

