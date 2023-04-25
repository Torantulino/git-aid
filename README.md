# Git-Aid: AI-Assisted GitHub Utilities

This repository contains a collection of AI-assisted utilities to improve your experience with GitHub. These utilities include tools for finding duplicate issues, generating responses to issues, extracting information about repositories, and assisting with reviewing pull requests.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
    1. [Duplicate Issue Finder](#duplicate-issue-finder)
    2. [GPT-4 Issue Responder](#gpt-4-issue-responder)
    3. [Software Architecture Generator](#software-architecture-generator)
    4. [README Generator](#readme-generator)
    5. [GitHub Repository Information Extractor](#github-repository-information-extractor)
    6. [Pull Request Reviewer](#pull-request-reviewer)
4. [Contributing](#contributing)

## Requirements

This project requires Python 3.6+ and the following Python packages:

- BeautifulSoup4
- Gensim
- Html2text
- Markdown
- Matplotlib
- Numpy
- OpenAI
- Python-dotenv
- Requests
- TQDM
- Unidiff

Please refer to the `requirements.txt` file for the complete list of dependencies and their respective versions.

## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/AI-Assisted-GitHub-Utilities.git
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory and add your GitHub Read-only token, Read/Write token, and OpenAI API key:

```
GITHUB_READ_ONLY_TOKEN=your_read_only_token
GITHUB_READ_WRITE_TOKEN=your_read_write_token
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Duplicate Issue Finder

To find duplicate issues in a GitHub repository, use the `duplicate_issue_finder.py` script with the repository owner and name as command-line arguments, plus any additional options:

```
python duplicate_issue_finder.py owner repo_name --days 30 --threshold 0.8 --top_n 10
```

### GPT-4 Issue Responder

To generate responses to GitHub issues using OpenAI's GPT-4 model and post them as comments, run the `gpt_issue_responder.py` script with the repository owner and name as command-line arguments:

```
python gpt_issue_responder.py owner repo_name
```

### Software Architecture Generator

To generate a software architecture from a given repository URL, run the `architecture_generator.py` script with the repository URL as an argument:

```
python architecture_generator.py https://github.com/owner/repo_name
```

### README Generator

To generate a README file for a GitHub repository using OpenAI's GPT-3.5 Turbo model, run the `docs_generator.py` script with the GitHub repository URL as input:

```
python docs_generator.py https://github.com/owner/repo_name
```

### GitHub Repository Information Extractor

To extract information about a GitHub repository using the GitHub API, import and use the functions from `github_info_extractor.py`:

```python
from github_info_extractor import extract_files_from_url, extract_repopath_from_url, get_files_in_repo

files = extract_files_from_url("https://github.com/owner/repo_name")
repo_path = extract_repopath_from_url("https://github.com/owner/repo_name")
all_files = get_files_in_repo(repo_path)
```

### Pull Request Reviewer

To assist with reviewing GitHub pull requests using OpenAI's GPT-4 language model, run the `pr_reviewer.py` script with the pull request URL as an argument:

```
python pr_reviewer.py https://github.com/owner/repo_name/pull/123
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request, report bugs, or suggest new features.

_This README file was generated automatically by this repository._