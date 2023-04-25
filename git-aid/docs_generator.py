import base64
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import openai
import openai.error
from dotenv import load_dotenv
from github import Github
from github.ContentFile import ContentFile
from tqdm import tqdm

load_dotenv()
GITHUB_API_KEY = os.getenv("GITHUB_READWRITE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    system_prompt,
    user_prompt,
    model="gpt-4",
    temperature=0.7,
    max_tokens=2500,
    retries=5,
):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for i in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0]["message"]["content"].strip()
        except openai.error.RateLimitError as e:
            if i < retries - 1:
                wait_time = 2**i
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e


def summarize_file_gpt3(file_content, file_name):
    content = base64.b64decode(file_content.content).decode("utf-8")
    if len(content) > 4096:
        content = content[:4096]

    prompt = f"Summarize the following file:\n\n{file_name}\n\n{content}"
    summary = message_llm(
        "Please provide a summary of the given code.", prompt, model="gpt-3.5-turbo"
    )

    return summary


def generate_readme_gpt4(summaries):
    system_prompt = "Your task is to write professional readmes to be displayed on GitHub projects. The user will provide you with a summary of every single file in the repository, pick the relevant information from these to create a well formatted and decorated readme. Ignore irrelevant files."
    prompt = "Generate a detailed, professional and well decorated ReadMe for this GitHub project based on the following file summaries (ignore irrelevant files):\n\n"
    prompt += "\n".join(f"{i+1}. {summary}" for i, summary in enumerate(summaries))
    readme_content = message_llm(
        system_prompt=system_prompt, user_prompt=prompt, model="gpt-3.5-turbo"
    )

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
    with ThreadPoolExecutor() as executor:
        summaries = list(
            tqdm(
                executor.map(summarize_file_gpt3, files, (file.name for file in files)),
                total=len(files),
                desc="Processing Files",
            )
        )

    print("Generating README.md content...")
    readme_content = generate_readme_gpt4(summaries)

    print("Writing README.md to disk...")

    # Create the output directory if it doesn't exist
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the README.md file to the output directory
    with open(os.path.join(output_dir, "README.md"), "w") as readme_file:
        readme_file.write(readme_content)

    print("README.md has been successfully generated!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python docs_generator.py <repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    main(repo_url)
