# LinkedIn Ghostwriter AI Agent Tutorial

This tutorial will guide you through setting up and running the LinkedIn Ghostwriter AI Agent, a powerful tool that automatically researches, writes, checks quality, and publishes LinkedIn posts about quantitative finance.

## Overview

The LinkedIn Ghostwriter AI Agent is an open-source project that leverages modern AI tools to automate LinkedIn content creation. It was used to grow a LinkedIn account to 900 followers in just 7 weeks (CoachQuant) by creating high-quality, relevant content in the quantitative finance domain.

The agent uses a sophisticated architecture built on:
- **LangGraph & LangChain**: For orchestrating the agent workflows
- **MCP (Multi-Client Provider)**: For authentication and tool management
- **MongoDB**: For vector search and episodic memory storage
- **OpenAI**: For text embeddings and language models
- **Exa**: For web search capabilities
- **Composio**: For LinkedIn publishing tools

## Prerequisites

Before setting up the LinkedIn Ghostwriter AI Agent, ensure you have:

1. **Python 3.x**: The project is built on Python, so you'll need a recent version installed
2. **pip**: Python's package manager for installing dependencies
3. **MongoDB**: Either a local instance or MongoDB Atlas account
4. **API Keys/Access**:
   - OpenAI API key
   - Exa AI API key
   - Composio MCP access
   - LinkedIn organization access
5. **Node.js**: Required for running the LinkedIn integration verification script

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-ghostwriter.git
   cd linkedin-ghostwriter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the root directory based on the provided `.env.example`:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your specific credentials:

### Required Environment Variables

| Variable | Description | Where to Obtain |
|----------|-------------|----------------|
| `OPENAI_API_KEY` | API key for OpenAI services | [OpenAI Platform](https://platform.openai.com/) |
| `MONGODB_URI` | Connection string for MongoDB | MongoDB Atlas dashboard or local MongoDB instance |
| `EXA_API_KEY` | API key for Exa web search | [Exa AI Platform](https://exa.ai/) |
| `COMPOSIO_MCP_URL` | URL for Composio MCP server | Provided by Composio when you register |
| `COMPOSIO_LINKEDIN_TOOL` | Tool identifier for LinkedIn publishing | Provided by Composio |
| `ORGANIZATION_URN` | LinkedIn organization identifier | Format: "urn:li:organization:yourOrgId" |
| `VISIBILITY_ENUM` | Post visibility setting | Options: "PUBLIC", "CONNECTIONS" |
| `LIFECYCLE_STATE` | Post lifecycle state | Typically "PUBLISHED" |

### Optional Environment Variables

| Variable | Description |
|----------|-------------|
| `LANGSMITH_API_KEY` | For LangSmith tracing (optional) |
| `LANGSMITH_TRACING` | Enable/disable LangSmith tracing |

> **Note**: The variables `API_USERNAME` and `API_PASSWORD` are defined in the example but are currently unused by the application. You can leave these blank or omit them entirely.

### Verifying LinkedIn Integration

Before running the agent, it's important to verify that your LinkedIn integration is properly configured. The application now includes automatic verification at startup, but you can also manually verify the integration:

1. **Automatic Verification**: The application automatically verifies the LinkedIn integration at startup, checking:
   - The LinkedIn MCP connection is properly configured
   - The expected LinkedIn tool (specified by `COMPOSIO_LINKEDIN_TOOL`) is available
   - The tool has the necessary permissions
   - The organization URN is properly formatted

2. **Manual Verification**: You can manually verify the LinkedIn integration using the provided script:
   ```bash
   node get_composio_integration.js
   ```
   
   This script will:
   - Connect to Composio using your API key
   - Fetch details about your LinkedIn integration
   - Verify that the integration is properly configured for LinkedIn
   - Check for required permissions
   - Validate that the integration matches your .env configuration
   - Confirm the integration is active and has the expected tool

   If any issues are found, the script will provide specific error messages to help you troubleshoot.

## Running the Agent

Once you've configured your environment variables and verified your LinkedIn integration, you can run the agent with:

```bash
python main.py
```

This will start the agent, which will:
1. Initialize the LangGraph structure
2. Connect to the MCP clients (local and Composio)
3. Set up the MongoDB store with OpenAI embeddings
4. Execute the workflow to create and publish a LinkedIn post

## Understanding the Workflow

The LinkedIn Ghostwriter Agent follows a structured workflow:

1. **Supervisor Node**: Orchestrates the entire process, deciding which node to activate next
2. **Researcher Node**: Uses Exa's web search API to find recent news articles about quantitative finance
3. **Writer Node**: Drafts a LinkedIn post based on the research
4. **Quality Node**: Ensures the post is unique by comparing it with previously published content using vector search
5. **Publisher Node**: Publishes the post to LinkedIn using Composio's tools
6. **Memory Storage**: Stores details of the published post for future reference and uniqueness checks

The workflow is implemented as a state graph where each node processes the current state and passes it to the next node as determined by the supervisor.

## Architecture Details

### State Management

The agent uses a simple message-based state system, where each node adds messages to the state that are passed through the graph. The `State` class is a `TypedDict` with a single field `messages` that contains a list of messages.

### MongoDB Integration

The project uses MongoDB for:
1. **Checkpointing**: Saving the state of the graph execution
2. **Vector Search**: Comparing new posts with previously published content
3. **Episodic Memory**: Storing details about published posts

The MongoDB store is configured with OpenAI embeddings to enable semantic search capabilities.

### MCP Client Setup

The agent uses a `MultiServerMCPClient` to connect to two different tool providers:
1. A local MCP server that provides the Exa search tool (connection name: `linkedin_tools_stdio`)
2. Composio's MCP server that provides LinkedIn publishing tools (connection name: `linkedin_mcp`)

The LinkedIn integration is specifically accessed through the `linkedin_mcp` connection, which provides the `LINKEDIN_MCP_CREATE_LINKED_IN_POST` tool for publishing content to LinkedIn. This tool is defined in `linkedin_news_post/chains/publisher_chain.py` and is used by the publisher node to post content to LinkedIn.

## Customization

If you want to customize the agent's behavior, you can modify:

1. **Prompts and Chains**: Located in `linkedin_news_post/chains/` directory
2. **Node Logic**: Located in `linkedin_news_post/nodes/` directory
3. **Search Parameters**: Modify the `search_and_content` function in `linkedin_news_post/mcp_server.py`
4. **Memory Schema**: Adjust the `Article` model in `linkedin_news_post/nodes/publisher_node.py`

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Double-check your API keys and credentials in the `.env` file
2. **MongoDB Connection Issues**: Ensure your MongoDB instance is running or your Atlas connection string is correct
3. **MCP Tool Errors**: Verify that your Composio MCP URL and tool identifiers are correct
4. **Rate Limiting**: If you encounter rate limiting from OpenAI or Exa, consider implementing backoff strategies
5. **LinkedIn Integration Issues**: If you encounter issues with LinkedIn posting:
   - Run `node get_composio_integration.js` to verify your integration
   - Check that the `COMPOSIO_LINKEDIN_TOOL` value in your `.env` file matches the actual tool name in Composio
   - Verify that your LinkedIn organization URN is correctly formatted
   - Ensure your integration has the necessary permissions (e.g., `w_member_social`)
   - Check that the integration status is "active" in Composio

### Debugging

You can enable more verbose logging by modifying the logging configuration in the code. The supervisor node also prints state messages to the console, which can be helpful for debugging.

For LinkedIn integration issues, the application now includes detailed logging of the verification process in the `graph.py` file. Check the logs for any warnings or errors related to the LinkedIn integration.

## Conclusion

The LinkedIn Ghostwriter AI Agent demonstrates the power of combining various AI tools and services to create a fully automated content creation and publishing workflow. By following this tutorial, you should be able to set up and run the agent to grow your own LinkedIn presence with high-quality, automated content.

For more advanced usage or contributions to the project, refer to the code documentation and comments within each file.