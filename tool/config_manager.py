import configparser
import os

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

def get_openai_api_key():
    """Returns the OpenAI API key from the config."""
    config = get_config()
    api_key = config.get("openai", "api_key", fallback=None)
    if not api_key or api_key == "YOUR_OPENAI_API_KEY":
        raise ValueError("OpenAI API key is not configured in tool/config.ini.")
    return api_key

def get_openai_api_base():
    """Returns the OpenAI API base URL from the config, if set."""
    config = get_config()
    return config.get("openai", "api_base", fallback=None)

def get_llm_model():
    """Returns the LLM model name from the config, with a default."""
    config = get_config()
    # Fallback to gpt-3.5-turbo if not specified, as it's a common default
    return config.get("openai", "model", fallback="gpt-3.5-turbo")

def get_setting(key, fallback=None):
    """Returns a specific setting from the [settings] section of the config."""
    config = get_config()
    return config.get("settings", key, fallback=fallback)

if __name__ == "__main__":
    # Example usage:
    try:
        print(f"OpenAI API Key: {get_openai_api_key()}")
        api_base = get_openai_api_base()
        if api_base:
            print(f"OpenAI API Base: {api_base}")
        else:
            print("OpenAI API Base: Not set, will use OpenAI default.")
        print(f"LLM Model: {get_llm_model()}")
        
        print(f"Default Layout: {get_setting('default_layout', 'post')}")
        print(f"Git Commit Time: {get_setting('git_commit_time', '10:00:00')}")
        print(f"Log File: {get_setting('log_file', 'generation.log')}")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 