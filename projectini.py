# GitHub issue + project automation for Mycelia
# Requires: GitHub Personal Access Token with `repo` and `project` scopes

import requests
import time
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

ORG = os.getenv("GITHUB_ORG", "mycelia-ai")
REPO = os.getenv("GITHUB_REPO", "mycelia")
PROJECT_NUMBER = int(os.getenv("GITHUB_PROJECT_NUMBER", 1))
API_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

# --- Step 1: Get Project and Repo IDs ---
def get_project_id():
    query = """
    query($org: String!, $projectNumber: Int!) {
      organization(login: $org) {
        projectV2(number: $projectNumber) {
          id
          title
        }
      }
    }
    """
    variables = {
        "org": ORG,
        "projectNumber": PROJECT_NUMBER
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"Failed to fetch project ID: {data['errors']}")

    project = data["data"]["organization"]["projectV2"]
    if not project:
        raise ValueError(f"Project with number {PROJECT_NUMBER} not found in organization {ORG}.")

    logging.info(f"Project ID: {project['id']}, Title: {project['title']}")
    return project["id"]

def get_repo_id():
    query = """
    query($org: String!, $repo: String!) {
      repository(owner: $org, name: $repo) {
        id
      }
    }
    """
    variables = {
        "org": ORG,
        "repo": REPO
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"Failed to fetch repository ID for {ORG}/{REPO}: {data['errors']}.")

    repo = data["data"]["repository"]
    if not repo:
        raise ValueError(f"Repository {ORG}/{REPO} not found.")

    return repo["id"]

# --- Step 0: Clear Project Board ---
def clear_project_board(project_id):
    # Fetch columns for the project using GraphQL
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          id
          title
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue {
                  id
                  title
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"projectId": project_id}
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"Failed to fetch project columns: {data['errors']}")

    project = data["data"]["node"]
    if not project or "items" not in project:
        raise ValueError(f"No items found for project ID {project_id}.")

    items = project["items"]["nodes"]

    for item in items:
        item_id = item["id"]
        logging.info(f"Deleting item: {item['content']['title']} (ID: {item_id})")

        # GraphQL mutation to delete items in the project
        mutation = """
        mutation($itemId: ID!) {
          deleteProjectV2Item(input: {itemId: $itemId}) {
            clientMutationId
          }
        }
        """
        variables = {"itemId": item_id}
        delete_response = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=headers)
        delete_response.raise_for_status()
        logging.info(f"Deleted item: {item['content']['title']} (ID: {item_id})")

# --- Step 2: Create Issue ---
def create_issue(title, body, labels):
    url = f"https://api.github.com/repos/{ORG}/{REPO}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels or []
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    issue = response.json()
    return {"id": issue["id"], "number": issue["number"], "url": issue["html_url"]}

# --- Step 3: Add to Project ---
def add_to_project(project_id, issue_number):
    content_id = get_issue_global_id(issue_number)

    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    variables = {
        "projectId": project_id,
        "contentId": content_id
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"Failed to add content ID {content_id} to project ID {project_id}: {data['errors']}")

    logging.info(f"Added content ID {content_id} to project ID {project_id}.")

def get_issue_global_id(issue_number):
    query = """
    query($org: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $org, name: $repo) {
        issue(number: $issueNumber) {
          id
        }
      }
    }
    """
    variables = {
        "org": ORG,
        "repo": REPO,
        "issueNumber": issue_number
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"Failed to fetch global ID for issue #{issue_number}: {data['errors']}")

    issue = data["data"]["repository"]["issue"]
    if not issue:
        raise ValueError(f"Issue #{issue_number} not found in repository {ORG}/{REPO}.")

    return issue["id"]

# --- Step 3.1: Link Sub-Issues ---
def link_sub_issue(parent_issue_number, child_issue_number):
    parent_issue_id = get_issue_global_id(parent_issue_number)
    child_issue_id = get_issue_global_id(child_issue_number)

    url = "https://api.github.com/graphql"
    query = """
    mutation($issueId: ID!, $subIssueId: ID!) {
      addSubIssue(input: { issueId: $issueId, subIssueId: $subIssueId }) {
        issue {
          title
        }
        subIssue {
          title
        }
      }
    }
    """
    variables = {
        "issueId": parent_issue_id,
        "subIssueId": child_issue_id
    }
    headers_with_features = headers.copy()
    headers_with_features["GraphQL-Features"] = "sub_issues"
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers_with_features)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        logging.error(f"Failed to link sub-issue ID {child_issue_number} to parent issue ID {parent_issue_number}: {data['errors']}")
    else:
        logging.info(f"Linked sub-issue ID {child_issue_number} to parent issue ID {parent_issue_number}. Response: {data}")

def close_and_delete_issue(issue_number):
    issue_id = get_issue_global_id(issue_number)

    # Close the issue using GraphQL
    query_close = """
    mutation($issueId: ID!) {
      updateIssue(input: {id: $issueId, state: CLOSED}) {
        issue {
          id
        }
      }
    }
    """
    variables_close = {"issueId": issue_id}
    response_close = requests.post(API_URL, json={"query": query_close, "variables": variables_close}, headers=headers)
    response_close.raise_for_status()
    logging.info(f"Closed issue ID {issue_number}")

    # Delete the issue using GraphQL
    query_delete = """
    mutation($issueId: ID!) {
      deleteIssue(input: {issueId: $issueId}) {
        clientMutationId
      }
    }
    """
    variables_delete = {"issueId": issue_id}
    response_delete = requests.post(API_URL, json={"query": query_delete, "variables": variables_delete}, headers=headers)
    response_delete.raise_for_status()
    logging.info(f"Deleted issue ID {issue_number}")

tasks = {
  "Core System Foundations": [
    "Initialize Git repository and monorepo layout with essential directories and files.",
    "Create base docker-compose.yml with core services: NATS JetStream, Dapr placement service, Prometheus, Grafana.",
    "Add Makefile and .env.example for local bootstrapping and developer setup.",
    "Create Dapr component definitions for pubsub, state, and bindings.",
    "Implement first agent (agent_hello) using FastAPI + Dapr pubsub to validate local message routing.",
    "Set up .github folder with CI/CD scaffolding and GitHub Actions for linting and container builds.",
    "Configure Prometheus scraping and basic Grafana dashboards for agent health and message throughput."
  ],

  "Agent SDK and Runtime Development": [
    "Scaffold agent_runtime base Python module to be shared across all agents.",
    "Implement pluggable adapters for pubsub, state backend, MCP interface, and health ping.",
    "Enable agent runtime to support both Dapr and direct NATS interaction interchangeably.",
    "Add agent registration with a centralized tool registry for publishing tool info and health.",
    "Add startup lifecycle hooks for tool registration, logging, and state initialization.",
    "Implement CLI subcommand: `mycelia agent init <name>` to generate an agent skeleton.",
    "Ensure CLI supports local development mode with hot-reload via uvicorn.",
    "Document adapter API and usage for external agents."
  ],

  "Initial Agent Implementations": [
    "Create daily_briefing agent to fetch calendar events, news, summarize with LLM, and store reports.",
    "Create spotify_sync agent to sync Last.fm scrobbles with Spotify playlists and store sync stats.",
    "Create echo_bot agent to reply to messages with basic metadata for pubsub/debug testing.",
    "Create tool_registry agent to manage tool registration, health info, and discovery endpoints."
  ],

  "Supabase Integration": [
    "Design Supabase schema for users, agents, tasks, workflows, registry, and job logs.",
    "Configure Supabase authentication via access token and session refresh.",
    "Integrate Supabase client into agents for task tracking and state persistence.",
    "Support Realtime subscriptions for frontend logs and events.",
    "Add connector support for bring-your-own Postgres deployments.",
    "Validate schema migration flow for local and production environments."
  ],

  "MCP Protocol Support": [
    "Install and configure `fastapi-mcp` in agent_runtime.",
    "Define /tools endpoint with dynamic registration via decorators.",
    "Implement /execute endpoint to run tool functions via REST or pubsub.",
    "Ensure agents broadcast MCP tool metadata to the registry.",
    "Add MCP metadata support for tool schemas, output types, and permissions.",
    "Build MCP message router for orchestrator to trigger distributed tool execution."
  ],

  "Observability Enhancements": [
    "Define scrape targets in Prometheus for Dapr, NATS, and all agents.",
    "Create Grafana dashboards for agent uptime, pubsub latency, and workflow execution time.",
    "Add structured logging to agent_runtime with correlation IDs.",
    "Implement status heartbeat messages from agents to tool_registry.",
    "Expose OpenTelemetry traces from each agent (optional)."
  ],

  "Workflow Engine Development": [
    "Design a YAML-based schema for declarative workflows.",
    "Support sequential and parallel task execution.",
    "Enable step chaining with output forwarding between tools.",
    "Implement execution engine via Dapr workflows or internal orchestrator.",
    "Add retry policies and timeout configuration per step.",
    "Store workflow run state in Supabase and display logs in the frontend.",
    "Build a library of reusable workflows like daily_sync.yaml and summarize_docs.yaml."
  ],

  "Frontend MVP Development": [
    "Initialize React project with Tailwind, shadcn/ui, and Supabase auth.",
    "Build login/register screen and session management.",
    "Create dashboard to list agents, their tools, and current status.",
    "Develop task manager to run tasks, see results, and monitor status.",
    "Implement workflow editor to choose steps and trigger via UI.",
    "Add logs/events stream via Supabase Realtime or WebSocket.",
    "Create agent registration UI and tool manifest browser."
  ],

  "Infrastructure and Connector Support": [
    "Define YAML-based connector plugin spec for agents and tools.",
    "Support pluggable state backends like Supabase, Redis, CosmosDB, and Postgres.",
    "Support pluggable vector stores like Pinecone, Qdrant, and Weaviate.",
    "Add support for external graph databases like Neo4J, Dgraph, and TerminusDB.",
    "Define override configurations in infra-profiles for Azure, bare-metal, etc.",
    "Test swapping default Dapr/Supabase config with user-supplied components."
  ],

  "Developer Experience and CLI Tooling": [
    "Add `mycelia init` to scaffold agents, tools, connectors, and workflows.",
    "Add `mycelia run agent` with development mode, hot reload, and port watcher.",
    "Add `mycelia workflow run` to test workflows locally.",
    "Support `.mycelia` config file for local development profiles.",
    "Build plugin loader to extend CLI with custom commands.",
    "Integrate CLI with GitHub repo and project board auto-linking."
  ],

  "Release v1.0 Tasks": [
    "Implement CI/CD pipeline using GitHub Actions for linting, testing, building, and image pushing.",
    "Push agent images to GitHub Container Registry.",
    "Secure agent-to-agent and CLI-to-agent communication using token authentication.",
    "Write developer documentation, API docs, and CLI reference.",
    "Publish landing page and quickstart guide on mycelia.dev.",
    "Enable issue templates and GitHub Projects automation."
  ]
}


# Main execution with logging
if __name__ == "__main__":
    try:
        project_id = get_project_id()
        logging.info("Fetched project ID successfully.")

        # Clear the project board
        clear_project_board(project_id)
        logging.info("Cleared project board.")

        for epic, subtasks in tasks.items():
            epic_issue = create_issue(f"Epic: {epic}", f"Tracking work for **{epic}**.", [])
            add_to_project(project_id, epic_issue["number"])
            logging.info(f"Created epic: {epic_issue['url']}")
            time.sleep(1)

            for task in subtasks:
                body = f"Subtask of #{epic_issue['number']}\n\n## Task\n{task}\n"
                sub = create_issue(task, body, [])
                add_to_project(project_id, sub["number"])
                link_sub_issue(epic_issue["number"], sub["number"])
                logging.info(f"  ↳ Created and linked sub-issue: {sub['url']}")
                time.sleep(1)

        logging.info("✔️ All epics and sub-issues created, linked, and added to project.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
