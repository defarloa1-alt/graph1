#!/usr/bin/env python3
"""
Chrystallum Configuration Loader
Loads API keys from .env, config.py, or environment variables
Priority: environment variables > config.py > defaults
"""

import os
import sys
from pathlib import Path

# Load .env so PPLX_API_KEY etc. are available
try:
    from dotenv import load_dotenv
    _root = Path(__file__).resolve().parents[1]
    load_dotenv(_root / ".env")
except ImportError:
    pass

# Try to load from config.py first
try:
    import config as user_config
    _HAS_CONFIG_FILE = True
except ImportError:
    _HAS_CONFIG_FILE = False
    user_config = None


def get_config(key: str, default=None):
    """
    Get configuration value from environment or config.py
    
    Priority:
    1. Environment variable
    2. config.py
    3. Provided default
    
    Args:
        key: Configuration key (e.g., 'OPENAI_API_KEY')
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    # First check environment
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Then check config.py
    if _HAS_CONFIG_FILE and hasattr(user_config, key):
        return getattr(user_config, key)
    
    # Finally return default
    return default


# API Keys
OPENAI_API_KEY = get_config("OPENAI_API_KEY")
# Perplexity: PPLX_API_KEY (official) or PERPLEXITY_API_KEY (legacy)
PERPLEXITY_API_KEY = get_config("PPLX_API_KEY") or get_config("PERPLEXITY_API_KEY")

# Neo4j Configuration
NEO4J_URI = get_config("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = get_config("NEO4J_USERNAME", get_config("NEO4J_USER", "neo4j"))
NEO4J_PASSWORD = get_config("NEO4J_PASSWORD")
NEO4J_DATABASE = get_config("NEO4J_DATABASE", "neo4j")

# Wikidata
WIKIDATA_SPARQL_ENDPOINT = get_config(
    "WIKIDATA_SPARQL_ENDPOINT",
    "https://query.wikidata.org/sparql"
)


def validate_agent_config(require_openai=True, require_perplexity=False, require_neo4j=True):
    """
    Validate required configuration for agents
    
    Args:
        require_openai: Whether OpenAI API key is required
        require_perplexity: Whether Perplexity API key is required
        require_neo4j: Whether Neo4j credentials are required
        
    Raises:
        ValueError: If required configuration is missing
    """
    errors = []
    
    if require_openai and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required but not set")
    
    if require_perplexity and not PERPLEXITY_API_KEY:
        errors.append("PERPLEXITY_API_KEY is required but not set")
    
    if require_neo4j and not NEO4J_PASSWORD:
        errors.append("NEO4J_PASSWORD is required but not set")
    
    if errors:
        error_msg = "\n".join([
            "Configuration Error:",
            *[f"  - {err}" for err in errors],
            "",
            "Setup Instructions:",
            "  1. Copy config.py.example to config.py",
            "  2. Add your API keys to config.py",
            "  OR",
            "  1. Copy .env.example to .env",
            "  2. Add your API keys to .env",
            "  3. Run: source .env (Linux/Mac) or copy values to environment (Windows)",
            "",
            "Get API keys from:",
            "  - OpenAI: https://platform.openai.com/api-keys",
            "  - Perplexity: https://www.perplexity.ai/settings/api"
        ])
        raise ValueError(error_msg)


def print_config_status():
    """Print current configuration status (for debugging)"""
    print("Configuration Status:")
    print(f"  Config file found: {_HAS_CONFIG_FILE}")
    print(f"  OPENAI_API_KEY: {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
    print(f"  PERPLEXITY_API_KEY: {'✓ Set' if PERPLEXITY_API_KEY else '✗ Missing'}")
    print(f"  NEO4J_URI: {NEO4J_URI}")
    print(f"  NEO4J_USERNAME: {NEO4J_USERNAME}")
    print(f"  NEO4J_PASSWORD: {'✓ Set' if NEO4J_PASSWORD else '✗ Missing'}")
    print(f"  NEO4J_DATABASE: {NEO4J_DATABASE}")


if __name__ == "__main__":
    print("Chrystallum Configuration Loader")
    print("=" * 60)
    print_config_status()
    
    print("\nValidation Tests:")
    
    try:
        validate_agent_config(require_openai=True, require_neo4j=True)
        print("✓ Agent configuration valid")
    except ValueError as e:
        print(f"✗ Agent configuration invalid:\n{e}")
    
    try:
        validate_agent_config(require_perplexity=True)
        print("✓ Discovery configuration valid")
    except ValueError as e:
        print(f"✗ Discovery configuration invalid:\n{e}")
