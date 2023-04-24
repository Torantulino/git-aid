import base64
import os
import re
import sys

import openai
from dotenv import load_dotenv
from github import Github
from github.ContentFile import ContentFile
from tqdm import tqdm  # Import the tqdm library

load_dotenv()
# Set your GitHub and OpenAI API keys
GITHUB_API_KEY = os.getenv("GITHUB_READWRITE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the API clients
g = Github(GITHUB_API_KEY)
openai.api_key = OPENAI_API_KEY


def get_files_in_repo(repo):
    files = []
    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)

    return files


def message_llm(
    system_prompt, user_prompt, model="gpt-4", temperature=0.7, max_tokens=3000
):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0]["message"]["content"].strip()


def summarize_file_gpt3(file_content):
    content = base64.b64decode(file_content.content).decode("utf-8")
    if len(content) > 4096:
        content = content[:4096]  # Truncate to 4096 tokens

    prompt = f"Summarize the following code:\n\n{content}\n\nSummary: "
    summary = message_llm(
        "Please provide a summary of the given code.", prompt, model="gpt-3.5-turbo"
    )

    return summary


def generate_readme_gpt4(summaries):
    prompt = "Generate detailed documentation for a project based on the following file summaries:\n\n"
    prompt += "\n".join(f"{i+1}. {summary}" for i, summary in enumerate(summaries))
    readme_content = message_llm(
        "Please generate detailed documentation for the project.", prompt, model="gpt-4"
    )  # Replace with the actual GPT-4 model name when available

    return readme_content


def extract_repo_from_url(url):
    match = re.search(r"github.com/([\w-]+)/([\w-]+)", url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return None


def main(repo_url):
    repo_path = extract_repo_from_url(repo_url)
    if not repo_path:
        print("Invalid GitHub repository URL.")
        sys.exit(1)

    print("Accessing repository...")
    repo = g.get_repo(repo_path)
    files = get_files_in_repo(repo)

    print("Summarizing files...")
    summaries = []
    for file in tqdm(
        files, desc="Processing Files"
    ):  # Wrap the loop with tqdm progress bar
        summary = summarize_file_gpt3(file)
        summaries.append(summary)

    print("Generating README.md content...")
    readme_content = generate_readme_gpt4(summaries)

    print("Writing README.md to disk...")
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_content)

    print("README.md has been successfully generated!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_readme.py <repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    main(repo_url)
