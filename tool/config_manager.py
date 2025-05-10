import configparser
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

def get_config():
    """Reads and returns the configuration from config.ini."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}. "
            f"Please copy tool/config.example.ini to tool/config.ini and fill in your details."
        )
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def get_llm_api_key():
    """Returns the LLM API key from the config."""
    config = get_config()
    api_key = config.get("llm_api", "api_key", fallback=None)
    if not api_key or api_key == "YOUR_API_KEY":
        raise ValueError("LLM API key (api_key) is not configured in tool/config.ini under [llm_api].")
    return api_key

def get_llm_api_endpoint_base():
    """Returns the LLM API base endpoint URL from the config, if set."""
    config = get_config()
    return config.get("llm_api", "api_base", fallback=None)

def get_llm_model():
    """Returns the LLM model name from the config, with a default."""
    config = get_config()
    return config.get("llm_api", "model", fallback="default-model")

def get_llm_extra_params():
    """Reads and parses a JSON string of extra LLM parameters from the config.
    Returns a dictionary of parameters, or an empty dictionary if not set or invalid JSON.
    """
    config = get_config()
    params_json_str = config.get("llm_api", "llm_extra_params_json", fallback=None)
    if not params_json_str:
        return {}
    try:
        params_dict = json.loads(params_json_str)
        if not isinstance(params_dict, dict):
            print(f"Warning: llm_extra_params_json in config.ini was '{params_json_str}' which is not a valid JSON object (e.g., {{...}}). Ignoring.")
            return {}
        return params_dict
    except json.JSONDecodeError:
        print(f"Warning: Failed to parse llm_extra_params_json in config.ini: '{params_json_str}'. Invalid JSON. Ignoring.")
        return {}

def get_setting(key, fallback=None):
    """Returns a specific setting from the [settings] section of the config."""
    config = get_config()
    return config.get("settings", key, fallback=fallback)

if __name__ == "__main__":
    # Example usage:
    try:
        print(f"LLM API Key: {get_llm_api_key()}")
        api_base = get_llm_api_endpoint_base()
        if api_base:
            print(f"LLM API Endpoint Base: {api_base}")
        else:
            print("LLM API Endpoint Base: Not set.")
        print(f"LLM Model: {get_llm_model()}")
        extra_params = get_llm_extra_params()
        if extra_params:
            print(f"LLM Extra Params: {extra_params}")
        
        print(f"Default Layout: {get_setting('default_layout', 'post')}")
        print(f"Git Commit Time: {get_setting('git_commit_time', '10:00:00')}")
        print(f"Log File: {get_setting('log_file', 'generation.log')}")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 