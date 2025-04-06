"""
Configuration settings for the LinkedIn News Post application.
This module centralizes configuration values that were previously hardcoded
throughout the application.
"""
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Model configuration
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4o")

# MongoDB configuration
try:
    MONGODB_URI = os.environ["MONGODB_URI"]
except KeyError:
    logger.error("MONGODB_URI environment variable is not set")
    MONGODB_URI = None

DB_NAME = os.environ.get("DB_NAME", "checkpointing_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "store")
DEFAULT_TTL_MINUTES = int(os.environ.get("DEFAULT_TTL_MINUTES", 10))

# Search configuration
DEFAULT_SEARCH_LIMIT = int(os.environ.get("DEFAULT_SEARCH_LIMIT", 3))
DEFAULT_LIST_LIMIT = int(os.environ.get("DEFAULT_LIST_LIMIT", 10))
DEFAULT_MAX_LIST_LIMIT = int(os.environ.get("DEFAULT_MAX_LIST_LIMIT", 100))

# Exa API configuration
try:
    EXA_API_KEY = os.environ["EXA_API_KEY"]
except KeyError:
    logger.error("EXA_API_KEY environment variable is not set")
    EXA_API_KEY = None

# Search parameters
SEARCH_DAYS_BACK = int(os.environ.get("SEARCH_DAYS_BACK", 30))
SEARCH_NUM_RESULTS = int(os.environ.get("SEARCH_NUM_RESULTS", 10))
SEARCH_MAX_CHARACTERS = int(os.environ.get("SEARCH_MAX_CHARACTERS", 400))
SEARCH_CATEGORY = os.environ.get("SEARCH_CATEGORY", "news")

# Calculate date ranges for search
TODAY = datetime.now()
DEFAULT_START_DATE = (TODAY - timedelta(days=SEARCH_DAYS_BACK)).isoformat() + ".000Z"
DEFAULT_END_DATE = TODAY.isoformat() + ".000Z"

# LinkedIn API configuration
try:
    ORGANIZATION_URN = os.environ["ORGANIZATION_URN"]
    VISIBILITY_ENUM = os.environ["VISIBILITY_ENUM"]
    LIFECYCLE_STATE = os.environ["LIFECYCLE_STATE"]
    COMPOSIO_LINKEDIN_TOOL = os.environ["COMPOSIO_LINKEDIN_TOOL"]
    COMPOSIO_LINKEDIN_APP = os.environ.get("COMPOSIO_LINKEDIN_APP", "LINKEDIN") # Default to "LINKEDIN" if not set
    COMPOSIO_LINKEDIN_ENTITY = os.environ.get("COMPOSIO_LINKEDIN_ENTITY", "melsawah@me.com") # No default, let it be None if not set
except KeyError as e:
    logger.error(f"Required LinkedIn environment variable {e} is not set")
    # Set defaults for development
    ORGANIZATION_URN = os.environ.get("ORGANIZATION_URN", "urn:li:organization:0000000")
    VISIBILITY_ENUM = os.environ.get("VISIBILITY_ENUM", "PUBLIC")
    LIFECYCLE_STATE = os.environ.get("LIFECYCLE_STATE", "PUBLISHED")
    COMPOSIO_LINKEDIN_TOOL = os.environ.get("COMPOSIO_LINKEDIN_TOOL", "LINKEDIN_CREATE_LINKED_IN_POST")

# MCP configuration
try:
    COMPOSIO_MCP_URL = os.environ["COMPOSIO_MCP_URL"]
except KeyError:
    logger.error("COMPOSIO_MCP_URL environment variable is not set")
    COMPOSIO_MCP_URL = None


# Domain focus configuration

if not COMPOSIO_LINKEDIN_ENTITY:
    logger.warning("COMPOSIO_LINKEDIN_ENTITY environment variable is not set. MCP connection might require it.")
DOMAIN_FOCUS ="""
🎯 **DOMAIN_FOCUS for Research & Content Targeting**

**Industry:** Aviation Technology / Aerospace Software  
**Product Type:** ERP (Enterprise Resource Planning) System  
**Core Product:** A next-generation ERP platform for aviation maintenance and operations  

**Mission:**  
Revolutionize how aviation companies manage maintenance, operations, compliance, and resource planning—by replacing outdated legacy systems with modular, cloud-native, user-first software.

**Key Differentiators:**  
- Built by aviation professionals with deep domain expertise  
- Designed for usability—minimal training, maximum efficiency  
- Modular microservices architecture for flexibility and speed  
- Fast onboarding and easy data migration  
- Aligns with the operational needs of MROs, fleet managers, and airline tech teams  

**Primary Audience:**  
- Maintenance, Repair, Overhaul (MRO) providers  
- Aviation operations managers  
- Airline and charter fleet managers  
- Aviation tech directors and engineers  
- Aircraft maintenance planners  
- Part 145 organizations  

**Secondary Audience:**  
- Aviation software consultants  
- Digital transformation leaders in aviation  
- Aviation regulators and compliance officers  
- Investors and decision-makers in aviation innovation  

**Content Focus for LinkedIn:**  
- Trends in aviation digital transformation  
- ERP modernization in aerospace  
- Pain points of legacy systems in aviation  
- Insights from aviation experts and engineers  
- Real-world stories of operational improvement  
- Visuals and UI/UX previews of the platform  
- Team and culture behind the tech  

❗ **Important Note:**  
Do **not** research, reference, mention, or publish articles about **direct or indirect competitors**. Focus only on industry trends, customer pain points, thought leadership, and AirNxt’s unique perspective.
"""