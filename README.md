# Duplicate Issue Finder & GPT-4 Issue Responder

This repository contains Three Python scripts to help manage GitHub issues for a given repository:

1. `duplicate_issue_finder.py`: Helps in finding potential duplicate issues in a GitHub repository.
2. `gpt_issue_responder.py`: Uses OpenAI's GPT-4 model to generate responses to GitHub issues and posts them as comments.
3. `pr_reviewer.py`: Uses OpenAI's language model to assist developers in reviewing code changes in a GitHub pull request by identifying potential bugs or issues, suggesting missed best-practices, and assessing the code's intended purpose.

⚠️ Warning - Experimental. `gpt_issue_responder` posts to GitHub using your account, use at your own risk ⚠️

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/user/duplicate-issue-finder-and-gpt-issue-responder.git
cd duplicate-issue-finder-and-gpt-issue-responder
pip install -r requirements.txt
```

Create a `.env` file in the project root directory and add your GitHub Read-only token and Read/Write token:

```dotenv
GITHUB_READONLY_TOKEN=<your_readonly_token>
GITHUB_READWRITE_TOKEN=<your_readwrite_token>
OPENAI_API_KEY=<your_openai_api_key>
```

Replace `<your_readonly_token>`, `<your_readwrite_token>` and `<your_openai_api_key>` with your respective tokens and API key.
You only need the `GITHUB_READWRITE_TOKEN` if you plan to use `gpt_issue_responder`.

## Usage

### Duplicate Issue Finder

To find duplicate issues in a GitHub repository, run the `duplicate_issue_finder.py` script with the repository owner and name as command-line arguments:

```bash
python duplicate_issue_finder.py <owner> <repo>
```

Replace `<owner>` and `<repo>` with the correct repository owner and name.

The script will fetch open issues from the specified repository and calculate the similarity between each pair of issues. Issues with similarity scores above a certain threshold are considered potential duplicates.

### GPT-4 Issue Responder
⚠️ Warning - Experimental. This script posts comments to GitHub using your account, use at your own risk ⚠️

To respond to GitHub issues using GPT-4, run the `gpt_issue_responder.py` script with the repository owner and name as command-line arguments:

```bash
python gpt_issue_responder.py <owner> <repo>
```

Replace `<owner>` and `<repo>` with the correct repository owner and name.

The script will fetch the latest issues from the specified repository, generate AI responses using GPT-4, and display them in the command prompt. You can choose to post the AI-generated responses as comments on the respective issues or skip them.
### GPT-4 PR-Reviewer
To use the PR Reviewer script, run the `pr_reviewer.py`file with the pull request URL as a command-line argument:
```bash
python pr_reviewer.py <pull_request_url>
```
Replace `<pull_request_url>` with the URL of the GitHub pull request you want to review.

The script will extract the diff URL, title, and description of the pull request, and fetch the code changes in unified diff format. It will then generate a prompt for the OpenAI language model that asks it to analyze the code changes, identify potential bugs or issues, suggest missed best-practices, and assess whether the code achieves its intended purpose.

The language model will generate a comprehensive code review that includes feedback and guidance on how to improve the code, which will be displayed in the terminal.

Note that you will need to set your OpenAI API key as an environment variable `OPENAI_API_KEY` before running the script. You can obtain an API key from the OpenAI website.

Remember, the goal of the PR Reviewer script is to help developers improve their code by providing constructive feedback and guidance. Use the feedback provided by the script to improve the quality and security of your code.
