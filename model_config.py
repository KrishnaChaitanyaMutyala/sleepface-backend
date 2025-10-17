"""
Model Configuration - Easy to add new models and update settings
"""
from llm_service import ModelType

# Default model priority (can be changed via API or config)
DEFAULT_MODEL_PRIORITY = [
    ModelType.RULE_BASED,        # Always available, free
    ModelType.HUGGINGFACE_FREE,  # Free API (requires API key)
    ModelType.OLLAMA_LOCAL,      # Free local model (requires Ollama installation)
]

# Model configurations
MODEL_CONFIGS = {
    ModelType.RULE_BASED: {
        "name": "Rule-Based AI",
        "description": "Free rule-based logic for insights and recommendations",
        "cost": "Free",
        "privacy": "Local",
        "setup_required": False,
        "api_key_required": False
    },
    ModelType.HUGGINGFACE_FREE: {
        "name": "Hugging Face Free",
        "description": "Free AI models via Hugging Face Inference API",
        "cost": "Free (with rate limits)",
        "privacy": "External API",
        "setup_required": True,
        "api_key_required": True,
        "setup_instructions": [
            "1. Get free API key from https://huggingface.co/settings/tokens",
            "2. Set HUGGINGFACE_API_KEY environment variable",
            "3. Restart the backend"
        ]
    },
    ModelType.OLLAMA_LOCAL: {
        "name": "Ollama Local",
        "description": "Run AI models locally on your machine",
        "cost": "Free",
        "privacy": "Completely Local",
        "setup_required": True,
        "api_key_required": False,
        "setup_instructions": [
            "1. Install Ollama from https://ollama.ai",
            "2. Run: ollama pull llama2",
            "3. Start Ollama service: ollama serve",
            "4. Restart the backend"
        ]
    }
}

# Easy way to add new models
def add_custom_model(model_name: str, provider_class, config: dict):
    """
    Add a new model to the system
    
    Example:
        add_custom_model("my_custom_model", MyCustomProvider, {
            "name": "My Custom Model",
            "description": "Custom AI model",
            "cost": "Free",
            "privacy": "Local"
        })
    """
    # This would be implemented to dynamically add models
    pass

def get_model_info(model_type: ModelType) -> dict:
    """Get information about a specific model"""
    return MODEL_CONFIGS.get(model_type, {
        "name": "Unknown Model",
        "description": "Model information not available",
        "cost": "Unknown",
        "privacy": "Unknown"
    })

def get_all_model_info() -> dict:
    """Get information about all available models"""
    return {model.value: get_model_info(model) for model in ModelType}

