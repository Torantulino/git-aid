from concurrent.futures import ThreadPoolExecutor
import os
import openai
import sys

from tqdm import tqdm
from llm_utils import message_llm
from github_utils import extract_files_from_url
from dotenv import load_dotenv
from github import Github

load_dotenv()
GITHUB_API_KEY = os.getenv("GITHUB_READWRITE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

g = Github(GITHUB_API_KEY)
openai.api_key = OPENAI_API_KEY

JSON_SCHEMA = """{
  "file": [
    {
      "Filename": "example.py",
      "description": "A brief explanation of the file's purpose."
    },
    ...
  "functions": [
    {
      "function": "def example_function(example: str) -> str:",
      "description": "A brief explanation of the function."
    },
    ...
  ],
  "classes": [
    {
      "name": "class_name",
      "description": "A brief explanation of the class."
    },
    ...
  ],
  "global_variables": [
    {
      "name": "global_variable_name",
      "description": "A brief explanation of the global variable."
    },
    ...
  ],
  "constants": [
    {
      "name": "constant_name",
      "description": "A brief explanation of the constant."
    },
    ...
  ],
  ],
  ]
}"""

SYSTEM_PROMPT = f"""Given a Python script, provide a JSON object containing all functions, classes, global variables, module-level constants, that can be referenced from outside the file. Organize the elements into separate categories and include a brief explanation for each element.

Add typing to all functions listed.

Only respond with JSON in the format below with no explanation:

Output format:
{JSON_SCHEMA}
"""

def generate_architecture(file_name, file_contents):
    # Given a file, generate an architecture
    user_prompt = f"""File: {file_name}\n\n{file_contents}"""
    return message_llm(SYSTEM_PROMPT, user_prompt)

def main(repo_url):
    # Given the provided repo, scrape all files and generate an architetcture for each one
    files = extract_files_from_url(repo_url)

    print("Generating Architectures...")
    architectures = []
    with ThreadPoolExecutor() as executor:
        architectures = list(
            tqdm(
                executor.map(generate_architecture, files, (file.name for file in files)),
                total=len(files),
                desc="Processing Files",
            )
        )
    
    print("Writing to file...")
    # Create output folder
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Create a folder named after the repo
    repo_name = repo_url.split("/")[-1]
    repo_dir = os.path.join(output_dir, repo_name)
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    # Save all the architectures to individual files
    for file, architecture in zip(files, architectures):
        file_path = os.path.join(repo_dir, file.name)
        with open(file_path, "w") as f:
            f.write(architecture)
    
    print("Finished!")
        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python architecture_generator.py <repo_url>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    main(repo_url)


