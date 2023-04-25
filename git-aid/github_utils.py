import re
import sys
import os

from dotenv import load_dotenv
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile
from typing import List, Union

load_dotenv()
GITHUB_API_KEY = os.getenv("GITHUB_READWRITE_TOKEN")

g = Github(GITHUB_API_KEY)

def extract_files_from_url(url: str) -> List[ContentFile]:
    """
    Extracts all files from a given GitHub repository URL.

    :param url: The URL of the GitHub repository.
    :return: A list of ContentFile objects representing all files in the repository.
    """
    repo_path = extract_repopath_from_url(url)
    if not repo_path:
        print("Invalid GitHub repository URL.")
        sys.exit(1)

    print("Accessing repository...")
    repo = g.get_repo(repo_path)
    return get_files_in_repo(repo)


def extract_repopath_from_url(url: str) -> Union[str, None]:
    """
    Extracts the repository path from a GitHub repository URL.

    :param url: The URL of the GitHub repository.
    :return: A string representing the repository path in the format 'owner/repo', or None if the URL is invalid.
    """
    match = re.search(r"github.com/([\w-]+)/([\w-]+)", url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return None

def get_files_in_repo(repo: Repository) -> List[ContentFile]:
    """
    Retrieves all files in a GitHub repository.

    :param repo: A Repository object representing the GitHub repository.
    :return: A list of ContentFile objects representing all files in the repository.
    """
    files = []
    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)

    return files
