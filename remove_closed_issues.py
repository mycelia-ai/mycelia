import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Securely fetch GitHub token from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

ORG = "mycelia-ai"
REPO = "mycelia"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

def get_closed_issues():
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{ORG}/{REPO}/issues?state=closed&per_page=30&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_issues = response.json()
        if not page_issues:
            break
        issues.extend(page_issues)
        page += 1
    return issues

def delete_issue(issue_id):
    url = "https://api.github.com/graphql"
    query = """
    mutation($issueId: ID!, $clientMutationId: String!) {
      deleteIssue(input: {issueId: $issueId, clientMutationId: $clientMutationId}) {
        clientMutationId
      }
    }
    """
    variables = {
        "issueId": issue_id,
        "clientMutationId": "delete-issue"
    }
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        logging.error(f"Failed to delete issue ID {issue_id}: {data['errors']}")
    else:
        logging.info(f"Deleted issue ID {issue_id}")

if __name__ == "__main__":
    try:
        closed_issues = get_closed_issues()
        logging.info(f"Found {len(closed_issues)} closed issues.")

        for issue in closed_issues:
            delete_issue(issue["node_id"])

        logging.info("✔️ All closed issues have been deleted.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
