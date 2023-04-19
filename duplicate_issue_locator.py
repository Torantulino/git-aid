import requests
import json
from gensim import corpora, models, similarities
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
import gensim
from gensim.parsing.preprocessing import remove_stopwords
import matplotlib.pyplot as plt
from heapq import nlargest

def fetch_open_issues(owner, repo, since_days=30):
    """Fetch all open issues from the specified GitHub repository."""
    issues = []
    page = 1
    per_page = 100
    since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%dT%H:%M:%SZ')

    headers = {'Authorization': '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'}

    while True:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page={per_page}&page={page}&author={owner}&since={since_date}'
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Error encountered while fetching issues: Status code {response.status_code}")
                break
            fetched_issues = json.loads(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error encountered while fetching issues: {e}")
            break

        if not fetched_issues:
            break

        issues.extend(fetched_issues)
        print(f"Fetched issues: {len(issues)}", end='\r')
        page += 1

    return issues

def extract_issue_texts(issues):
    """Extract issue titles and descriptions from the list of issues."""
    return [f"{issue['title']} {issue['body']}" for issue in issues if 'pull_request' not in issue]

def tokenize(text):
    return gensim.utils.simple_preprocess(remove_stopwords(text), deacc=True)

def create_corpus(issue_texts):
    """Create a dictionary and corpus for similarity computation."""
    dictionary = corpora.Dictionary([tokenize(text) for text in issue_texts])
    return dictionary, [dictionary.doc2bow(tokenize(text)) for text in issue_texts]

def compute_similarity_matrix(corpus):
    """Train a TF-IDF model and compute the similarity matrix."""
    tfidf = models.TfidfModel(corpus)
    return similarities.MatrixSimilarity(tfidf[corpus])



def find_duplicate_issues(issues, issue_texts, similarity_threshold=0.7, top_n=5):
    """Find and print duplicate issues based on the similarity threshold."""
    dictionary, corpus = create_corpus(issue_texts)
    index = compute_similarity_matrix(corpus)

    issue_texts_mapping = {i: issue for i, issue in enumerate(issues) if 'pull_request' not in issue}
    index_mapping = list(issue_texts_mapping.keys())
    num_issues = len(issue_texts)
    num_duplicates = 0
    similarity_sum = 0
    similarity_count = 0
    duplicate_pairs = set()
    similarity_scores = []
    top_pairs = []

    for i in tqdm(range(num_issues), desc="Processing issues"):
        issue1 = issue_texts_mapping[index_mapping[i]]
        similarities = index[corpus[i]]
        for j, issue2 in enumerate(issue_texts):
            if i != j:
                similarity_sum += similarities[j]
                similarity_count += 1
                similarity_scores.append(similarities[j])
                if similarities[j] > similarity_threshold:
                    duplicate_pairs.add(tuple(sorted((issue1['number'], issue_texts_mapping[index_mapping[j]]['number']))))
                    top_pairs.append(((issue1['number'], issue_texts_mapping[index_mapping[j]]['number']), similarities[j], issue1['html_url'], issue_texts_mapping[index_mapping[j]]['html_url']))

    mean_similarity = similarity_sum / similarity_count
    print(f"\nNumber of issues checked: {num_issues}")
    print(f"Number of possible duplicates found: {len(duplicate_pairs)}")
    print(f"Mean similarity: {mean_similarity:.2f}")

    # Get the top N duplicate pairs based on similarity scores
    top_pairs = nlargest(top_n, top_pairs, key=lambda x: x[1])

    print(f"\nTop {top_n} potential duplicate pairs:")
    for pair in top_pairs:
        print(f"Issue {pair[0][0]} and Issue {pair[0][1]} might be duplicates with a similarity score of {pair[1]:.2f}")
        print(f"Link to Issue {pair[0][0]}: {pair[2]}")
        print(f"Link to Issue {pair[0][1]}: {pair[3]}\n")



if __name__ == '__main__':
    owner, repo = 'Torantulino', 'Auto-GPT'
    print("Fetching issues...")
    issues = fetch_open_issues(owner, repo)
    issue_texts = extract_issue_texts(issues)
    find_duplicate_issues(issues, issue_texts)
