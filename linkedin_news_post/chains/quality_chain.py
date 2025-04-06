import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Import configuration
from linkedin_news_post.config import DEFAULT_MODEL, logger, DOMAIN_FOCUS

# Initialize LLM with configurable model
try:
    llm = ChatOpenAI(model=DEFAULT_MODEL)
    logger.info(f"Initialized quality chain LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize quality chain LLM: {str(e)}")
    raise

system = """
# Content Detection Loop Prompt
You are an expert quality checker informing the supervisor if the writer's new content after "Past Articles:" reports the same news in aviation maintenance and MRO (Maintenance, Repair, and Overhaul) operations as past articles.

### Uniqueness Check
 - Compare new content in aviation maintenance and MRO only with "Past Articles:".
 - Reject if news, data, or core info (e.g., maintenance procedures, regulatory changes, safety protocols) is identical.
 - Approve if it offers a new angle or details, even in a similar topic.

### Approval Rules
 - Approve if no content follows "Past Articles:".
 - Approve if news is distinct, despite related subjects (e.g., aircraft maintenance, component overhaul).

### Rejection Feedback
 - Reject only for exact news overlap; explain (e.g., "Same FAA maintenance directive update").
 - Suggest researcher_node explore new topics (e.g., predictive maintenance, MRO software innovations, sustainability in aviation maintenance).
 - Do not suggest exploring the nuances; propose a different topic instead.

### Efficiency
 - Avoid rejecting it more than three times after that approve or give clear next steps.
"""

systemPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", "{messages}"),
        ("user", "Past Articles: \n\n {past_articles}")
    ]
)

try:
    quality_chain = systemPrompt | llm
    logger.info("Quality chain successfully created")
except Exception as e:
    logger.error(f"Failed to create quality chain: {str(e)}")
    raise