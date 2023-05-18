import os
import sys
from typing import Callable

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html2text import html2text
from markdown import markdown


load_dotenv()


class PRReviewer:
    def __init__(self):
        print("Initializing PR Reviewer...")

    def message_llm(
        self,
        system_prompt: str,
        prompt: str,
        model="gpt-4",
        temperature=0.7,
        max_tokens=3000,
    ):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0]['message']['content'].strip()

    def extract_pr_info(self, pr_url: str):
        response = requests.get(pr_url)
        soup = BeautifulSoup(response.text, "html.parser")

        diff_url = f"{pr_url}.diff"
        description = soup.select_one(".markdown-body").get_text()
        title = soup.select_one("h1.gh-header-title").get_text().strip()

        return diff_url, description, title

    def fetch_and_parse_diff(self, diff_url: str):
        response = requests.get(diff_url)
        raw_diff = response.text
        return raw_diff

    def review_pull_request(self, pr_url: str, progress_callback: Callable = print):
        diff_url, description, title = self.extract_pr_info(pr_url)

        diff = self.fetch_and_parse_diff(diff_url)

        context_message = f"""The change has the following title: {title}.
{description}
Here are the code changes in unified diff format:
```
{diff}
```

Your task is to:
- Review the code changes and provide feedback.
- If there are any bugs, highlight them.
- Provide details on missed use of best-practices.
- Does the code do what it says in the commit messages?
- Do not highlight minor issues and nitpicks.
- Use bullet points if you have multiple comments.
- Provide security recommendations if there are any."""

        system_prompt = """You are an AI language model designed to assist developers in reviewing code changes in a GitHub pull request. Analyze the provided code changes, title, and description carefully, and provide a comprehensive code review that includes:

- Identifying potential bugs or issues in the code.
- Pointing out any missed best-practices or areas for improvement.
- Assessing whether the code achieves its intended purpose based on the provided context.
- Focusing on significant concerns and avoiding minor nitpicks.
- Presenting your feedback in a clear, concise, and organized manner using bullet points for multiple comments.
- Suggesting security recommendations if applicable.

Remember, your goal is to help the developer improve their code by providing constructive feedback and guidance.
"""
        result = self.message_prreviewer(
            system_prompt=system_prompt, prompt=context_message
        )
        result_html = markdown(result)
        result_text = html2text(result_html).strip()
        print("\nCode Review Results:\n", result_text)


if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

    pr_url = sys.argv[1]  # Replace with the GitHub Pull Request URL you want to review

    code_review_assistant = PRReviewer()
    code_review_assistant.review_pull_request(pr_url)
