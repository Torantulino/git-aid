# Duplicate Issue Finder & GPT-4 Issue Responder

This repository contains two Python scripts to help manage GitHub issues for a given repository:

1. `duplicate_issue_finder.py`: Helps in finding potential duplicate issues in a GitHub repository.
2. `gpt_issue_responder.py`: Uses OpenAI's GPT-4 model to generate responses to GitHub issues and posts them as comments.

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
