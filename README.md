# LinkedIn Ghostwriter AI Agent - Aviation MRO Focus

An open-source LinkedIn Ghostwriter AI Agent powered by MCP (Multi-Client Provider) and LangChain, specifically configured to generate articles about **aviation maintenance and MRO (Maintenance, Repair, and Overhaul) operations**. This agent leverages modern tools for agent orchestration, web search, authentication, vector search, and episodic memory management to create relevant and unique content.

## Overview

This project constructs a state graph-based workflow for a LinkedIn Ghostwriter Agent using a combination of:

- **LangGraph & LangChain**: To orchestrate the agent workflows.
- **MCP (Multi-Client Provider)**: For authentication and tool management (e.g., LinkedIn posting via Composio).
- **MongoDB + OpenAI Embeddings**: For vector-based search (ensuring article uniqueness) and checkpointing the state/episodic memory.
- **Exa API**: For performing web searches to find relevant news and information.
- **Agents**: A supervisor delegates tasks across different nodes—researcher, writer, quality control, and publisher.
- **Configuration**: Centralized settings in `linkedin_news_post/config.py` and secrets management via `.env`.
- **Logging & Error Handling**: Improved throughout the application for better monitoring and debugging.

The agent follows these basic steps focused on the aviation MRO domain:

1.  **Research**: Search for recent news articles related to aviation maintenance and MRO using the Exa API.
2.  **Writing**: Draft a LinkedIn article based on the research findings.
3.  **Quality Check**: Ensure that the article is unique by comparing it with previously published content using vector search against the MongoDB store.
4.  **Publish**: Post the final content to LinkedIn using Composio's MCP tools via the `linkedin_mcp` connection.
5.  **Memory Storage**: Store details of the episode (research, draft, final post) for future reference and context.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd linkedin-ghostwriter
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your actual API keys and credentials. Key variables include:
        *   `OPENAI_API_KEY`: Your OpenAI API key.
        *   `MONGODB_URI`: Connection string for your MongoDB instance.
        *   `EXA_API_KEY`: Your Exa API key for web searches.
        *   `COMPOSIO_MCP_URL`: Your Composio MCP endpoint URL.
        *   `COMPOSIO_LINKEDIN_TOOL`: The name of the LinkedIn posting tool provided by Composio (should be set to `LINKEDIN_MCP_CREATE_LINKED_IN_POST`).
        *   `ORGANIZATION_URN`: Your LinkedIn Organization URN for posting.
        *   `VISIBILITY_ENUM`: LinkedIn post visibility (e.g., `PUBLIC`).
        *   `LIFECYCLE_STATE`: LinkedIn post state (e.g., `PUBLISHED`).
        *   *(Optional)* `LANGSMITH_API_KEY` and `LANGSMITH_TRACING` for LangSmith tracing.
        *   *(Optional)* `API_USERNAME` and `API_PASSWORD` if needed for specific integrations.

4.  **Review Configuration:**
    *   Check the `linkedin_news_post/config.py` file. While secrets are in `.env`, this file contains other operational parameters like default models, search settings (days back, number of results), database/collection names, etc. Adjust these values if needed for your specific use case.

5.  **Verify LinkedIn Integration:**
    *   The application now includes automatic verification of the LinkedIn integration at startup. This ensures that:
        *   The LinkedIn MCP connection is properly configured
        *   The expected LinkedIn tool (specified by `COMPOSIO_LINKEDIN_TOOL`) is available
        *   The tool has the necessary permissions
        *   The organization URN is properly formatted
    *   You can also manually verify the LinkedIn integration using the provided script:
        ```bash
        node get_composio_integration.js
        ```
    *   This script will check your Composio LinkedIn integration and provide detailed information about its configuration, including:
        *   Integration ID, name, and status
        *   Available scopes/permissions
        *   Organization URN
        *   Available tools
    *   If any issues are found, the script will provide specific error messages to help you troubleshoot.

## Usage

To run the LinkedIn Ghostwriter agent:

```bash
python main.py
```

The agent will then execute the workflow defined in the LangGraph state machine: researching, writing, quality checking, and publishing an article focused on aviation maintenance/MRO.

## Architecture

### Core Components

-   **StateGraph & State**:
    The graph is constructed using LangGraph's `StateGraph` that defines nodes (agents) and edges (workflow connections). The `State` defines the type or structure of data that flows through the graph.

-   **Nodes**:
    -   `supervisor_node`: Oversees and delegates work based on the aviation MRO focus.
    -   `researcher_node`: Searches for relevant news articles using Exa's Web API.
    -   `writer_node`: Drafts articles tailored to the aviation MRO domain.
    -   `quality_node`: Validates the article's uniqueness using vector search against MongoDB.
    -   `publisher_node`: Publishes the article on LinkedIn via Composio/MCP.
    -   `tool_node`: Wraps external tools provided by the MCP client (Exa, LinkedIn).

-   **MCP Client & Tools**:
    The agent uses a `MultiServerMCPClient` to obtain external tools (like LinkedIn posting) via different transport channels, including a connection to Composio's MCP URL defined in `.env`.

-   **MongoDB Store**:
    The `MongoDBBaseStore` provides persistence and checkpointing capabilities using a custom index configuration built on OpenAI embeddings—facilitating vector search to check article uniqueness against past posts.

-   **Embedding Configuration**:
    Uses the OpenAI embedding model (`text-embedding-ada-002` or as configured) to convert text into vector representations for similarity searches.

### Graph Workflow

1.  The workflow begins at the `START` node, transitioning to the `supervisor_node`.
2.  The supervisor delegates tasks: researching aviation MRO news (`researcher_node`), writing a draft (`writer_node`), checking uniqueness (`quality_node`), and finally publishing (`publisher_node`).
3.  The `tool_node` provides the necessary external API access (Exa, LinkedIn) via MCP.
4.  Results and episodic memory data are stored in MongoDB throughout the process.
