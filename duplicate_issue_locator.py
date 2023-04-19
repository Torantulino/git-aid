import requests
import json
from gensim import corpora, models, similarities
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta

def fetch_open_issues(owner, repo, since_days=30):
    """Fetch all open issues from the specified GitHub repository."""
    issues = []
    page = 1
    per_page = 100
    since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%dT%H:%M:%SZ')

    while True:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page={per_page}&page={page}&creator={owner}&since={since_date}'
        response = requests.get(url)
        fetched_issues = json.loads(response.text)

        if not fetched_issues:
            break

        issues.extend(fetched_issues)
        print(f"Fetched issues: {len(issues)}", end='\r')
        page += 1

    return issues

def extract_issue_texts(issues):
    """Extract issue titles and descriptions from the list of issues."""
    return [f"{issue['title']} {issue['body']}" for issue in issues]

def create_corpus(issue_texts):
    """Create a dictionary and corpus for similarity computation."""
    dictionary = corpora.Dictionary([gensim.utils.simple_preprocess(text) for text in issue_texts])
    return dictionary, [dictionary.doc2bow(gensim.utils.simple_preprocess(text)) for text in issue_texts]

def compute_similarity_matrix(corpus):
    """Train a TF-IDF model and compute the similarity matrix."""
    tfidf = models.TfidfModel(corpus)
    return similarities.MatrixSimilarity(tfidf[corpus])

def find_duplicate_issues(issues, issue_texts, similarity_threshold=0.8):
    """Find and print duplicate issues based on the similarity threshold."""
    dictionary, corpus = create_corpus(issue_texts)
    index = compute_similarity_matrix(corpus)

    num_issues = len(issues)
    num_duplicates = 0
    similarity_sum = 0
    similarity_count = 0
    duplicate_pairs = set()

    for i in tqdm(range(num_issues), desc="Processing issues"):
        issue1 = issues[i]
        similarities = index[corpus[i]]
        for j, issue2 in enumerate(issues):
            if i != j:
                similarity_sum += similarities[j]
                similarity_count += 1
                if similarities[j] > similarity_threshold:
                    duplicate_pairs.add(tuple(sorted((issue1['number'], issue2['number']))))
                    print(f"Issue {issue1['number']} and Issue {issue2['number']} might be duplicates with a similarity score of {similarities[j]:.2f}", flush=True)

    mean_similarity = similarity_sum / similarity_count
    print(f"\nNumber of issues checked: {num_issues}")
    print(f"Number of possible duplicates found: {len(duplicate_pairs)}")
    print(f"Mean similarity: {mean_similarity:.2f}")

if __name__ == '__main__':
    owner, repo = 'Torantulino', 'Auto-GPT'
    print("Fetching issues...")
    issues = fetch_open_issues(owner, repo)
    issue_texts = extract_issue_texts(issues)
    find_duplicate_issues(issues, issue_texts)
