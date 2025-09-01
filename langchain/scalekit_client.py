"""
Shared Scalekit client configuration module for langchain tools.
Provides a centralized scalekit client instance for use across langchain tools.
"""

import os
import scalekit.client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize shared scalekit client
scalekit_client = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL", "https://kindle-dev.scalekit.cloud"),
)

# Also expose the connect interface for convenience
connect = scalekit_client.connect