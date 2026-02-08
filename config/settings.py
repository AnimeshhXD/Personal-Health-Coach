"""
Configuration Settings for Personal Health Coach - Agentic AI

HPE GenAI for GenZ Challenge - Week 1
"""

# BUDGET MODE CONFIGURATION
# This setting affects:
# - Compression depth and data retention
# - Context size and memory usage  
# - Recommendation detail and verbosity
#
# VALID VALUES: "LOW" | "BALANCED" | "HIGH"
#
# MODE BEHAVIORS:
# LOW: Short summary + 1 recommendation, minimal data retention
# BALANCED: Moderate detail + 2-3 recommendations, balanced data retention
# HIGH: Detailed insights + reasoning, comprehensive data retention


BUDGET_MODE = "LOW"  # CHANGE THIS VALUE TO TEST BUDGET MODES

# AI ACCESS CONFIGURATION
# ScaleDown API configuration for GenAI access
# If live calls are unavailable, the system uses local logic

SCALEDOWN_API_KEY = ""  # Set your ScaleDown API key here  
SCALEDOWN_BASE_URL = "https://api.scaledown.xyz"  # Production URL

# FALLBACK CONFIGURATION
# When API is unavailable, use local recommendation logic

USE_FALLBACK_MODE = False  # Set to False when API key is available

# DATA PROCESSING CONFIGURATION

COMPRESSION_ENABLED = True
EXPLAINABILITY_ENABLED = True
HEALTH_TWIN_ENABLED = True

# MEMORY CONFIGURATION

MAX_STORED_SUMMARIES = 10  # Prevent unlimited memory growth
MEMORY_FILE_PATH = "data/compressed_memory.json"

# LOGGING CONFIGURATION

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
SHOW_COMPRESSION_STATS = True
SHOW_EXPLAINABILITY_LOG = True

# PERFORMANCE CONFIGURATION

MAX_PROCESSING_TIME_SECONDS = 30  # Timeout for data processing
ENABLE_PARALLEL_PROCESSING = False  # For future optimization
