import time
import requests
import json
import logging
import os # Added os import
from .config_manager import get_llm_api_key, get_llm_api_endpoint_base, get_llm_model, get_llm_extra_params
import re

# Configure basic logging
logger = logging.getLogger(__name__)

# Path to the prompts file
PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "prompts.json")

def load_prompts():
    """Loads prompts from the JSON file."""
    try:
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        logger.info(f"Successfully loaded prompts from {PROMPTS_FILE}")
        return prompts
    except FileNotFoundError:
        logger.error(f"Prompts file not found: {PROMPTS_FILE}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from prompts file: {PROMPTS_FILE}")
        raise

class LLMHandler:
    def __init__(self):
        """Initializes the HTTP client settings using API key, endpoint URL, model, and extra params from config."""
        self.api_key = get_llm_api_key()
        llm_api_base = get_llm_api_endpoint_base()
        if not llm_api_base:
            raise ValueError("LLM API base endpoint (api_base in config under [llm_api]) is not configured.")
        self.endpoint_url = llm_api_base.rstrip('/') + "/v1/chat/completions"
        
        self.model_name = get_llm_model()
        self.extra_params = get_llm_extra_params()
        self.prompts = load_prompts() # Load prompts
        
        logger.info("LLMHandler initialized for direct HTTP requests.")
        logger.info(f"Using LLM API Endpoint: {self.endpoint_url}")
        logger.info(f"Using LLM model: {self.model_name}")
        if self.extra_params:
            logger.info(f"Using LLM extra params: {self.extra_params}")

    def _make_llm_request(self, prompt, max_tokens=1500, temperature=0.7):
        """Helper function to make a direct HTTP request to the LLM API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json" # Often good practice
        }

        # Base payload structure, assuming OpenAI compatibility for messages, etc.
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.prompts.get("system_prompt", "You are a helpful assistant.")}, # Use loaded system prompt
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False, # Hardcoded as the tool is not built for streaming
            # "n": 1, # Default for most models, can be added to extra_params if needed
            # "stop": None, # Can be added to extra_params if needed
        }

        # Merge extra_params from config (e.g., enable_thinking, top_p, etc.)
        # This allows overriding defaults like temperature or adding new ones.
        if self.extra_params:
            payload.update(self.extra_params)
            logger.debug(f"Payload includes merged extra_params: {self.extra_params}")

        logger.debug(f"Sending payload to LLM ({self.model_name}): {json.dumps(payload, indent=2)[:500]}...") # Log part of the payload

        try:
            request_start_time = time.time()
            response = requests.post(self.endpoint_url, headers=headers, json=payload) # Added timeout (3 minutes)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            response_json = response.json()
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time
            logger.debug(f"LLM request completed in {request_duration:.2f} seconds")
            logger.debug(f"Received LLM response: {json.dumps(response_json, indent=2)[:500]}...")
            
            # Assuming OpenAI-compatible response structure
            if response_json.get("choices") and isinstance(response_json["choices"], list) and len(response_json["choices"]) > 0:
                choice = response_json["choices"][0]
                if choice.get("message") and isinstance(choice["message"], dict) and "content" in choice["message"]:
                    return choice["message"]["content"].strip()
                elif choice.get("text") : # Some models might use "text" like older completion APIs
                    return choice.get("text").strip()
            
            logger.error(f"LLM response did not contain expected content structure. Response: {response_json}")
            raise Exception("LLM response format error: No valid message content found.")

        except requests.exceptions.Timeout as e:
            logger.error(f"LLM API request timed out: {e}")
            raise Exception(f"LLM API request timed out after 180 seconds: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM API HTTP Error: {e.response.status_code} - {e.response.text}")
            try:
                error_details = e.response.json() # Try to get more details if JSON error response
                logger.error(f"LLM API Error Details: {error_details}")
                # You could extract more specific error messages here from error_details if the API provides them
                # e.g., error_details.get('error', {}).get('message')
                raise Exception(f"LLM API returned HTTP {e.response.status_code}. Detail: {error_details}")
            except json.JSONDecodeError:
                 raise Exception(f"LLM API returned HTTP {e.response.status_code}. Response: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API Request Error: {e}")
            raise Exception(f"Failed to make request to LLM API: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM API JSON response: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
            raise Exception(f"LLM API response was not valid JSON: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while querying LLM: {e}")
            # Re-raise to be caught by the main error handler or specific logic
            raise

    def _parse_tags_from_llm_response(self, response_text):
        """Parses a comma-separated list of tags from the LLM response."""
        if not response_text:
            return []
        # Remove any leading/trailing fluff like "Suggested Tags: " or similar
        cleaned_response = response_text.strip()
        if cleaned_response.lower().startswith("suggested tags:"):
            cleaned_response = cleaned_response[len("suggested tags:"):].strip()
        elif cleaned_response.lower().startswith("tags:"):
            cleaned_response = cleaned_response[len("tags:"):].strip()
        
        tags = [tag.strip().lower() for tag in cleaned_response.split(',') if tag.strip()]
        # Further cleaning: remove any potential quotes around individual tags
        tags = [tag.strip('"').strip("'") for tag in tags]
        return list(set(tags)) # Return unique tags

    def generate_tags_for_post(self, title, description, content_preview_length=200):
        """Generates 3-5 relevant tags for a blog post using its title, description, and content preview."""
        logger.info(f"Generating tags for post titled: '{title}'")
        
        # Taking a snippet of content might be too much or too little, 
        # description and title are usually good enough for tags.
        # For now, let's rely on title and description.
        # If content_preview is needed in the future, it can be passed in.

        prompt_template = self.prompts.get("generate_tags")
        if not prompt_template:
            logger.error("Tag generation prompt template not found.")
            return []
        
        prompt = prompt_template.format(title=title, description=description)
        
        try:
            raw_tags_response = self._make_llm_request(prompt, max_tokens=50, temperature=0.6)
            if raw_tags_response:
                generated_tags = self._parse_tags_from_llm_response(raw_tags_response)
                logger.info(f"LLM suggested tags: {generated_tags} for title: '{title}'")
                return generated_tags
            else:
                logger.warning(f"LLM returned empty response for tag generation for title: '{title}'.")
                return []
        except Exception as e:
            logger.error(f"Error generating tags for title '{title}': {e}")
            return [] # Return empty list on error

    def generate_blog_post_details(self, keyword, blog_date):
        """Generates blog post title, description, content, and tags."""
        logger.info(f"Generating blog post for keyword: '{keyword}' on date: {blog_date}")

        # 1. Generate Title
        title_prompt_template = self.prompts.get("generate_title")
        if not title_prompt_template:
            logger.error("Title generation prompt template not found.")
            return None
        title_prompt = title_prompt_template.format(keyword=keyword)
        raw_title_response = self._make_llm_request(title_prompt, max_tokens=40, temperature=0.7)
        if not raw_title_response:
            logger.error("Failed to generate title (empty response from LLM).")
            return None
        cleaned_title = raw_title_response.strip()
        common_prefixes = ["Title:", "Generated Title:", "Here is a title:", "Here's your title:", "Okay, here's a title:"]
        common_suffixes = ["Is this title good?", "I hope this helps."]
        for prefix in common_prefixes:
            if cleaned_title.lower().startswith(prefix.lower()):
                cleaned_title = cleaned_title[len(prefix):].strip()
                break
        for suffix in common_suffixes:
            if cleaned_title.lower().endswith(suffix.lower()):
                cleaned_title = cleaned_title[:-len(suffix)].strip()
                break
        cleaned_title = cleaned_title.strip('"').strip("'").strip()
        if not cleaned_title:
            logger.error(f"Failed to extract a clean title from LLM response: '{raw_title_response}'")
            return None
        generated_title = cleaned_title

        # 2. Generate Description
        description_prompt_template = self.prompts.get("generate_description")
        if not description_prompt_template:
            logger.error("Description generation prompt template not found.")
            # Continue without description if template is missing, or handle as critical error
            generated_description = ""
        else:
            description_prompt = description_prompt_template.format(generated_title=generated_title, keyword=keyword)
            raw_description_response = self._make_llm_request(description_prompt, max_tokens=70, temperature=0.7)
            generated_description = ""
            if raw_description_response:
                cleaned_description = raw_description_response.strip()
                for prefix in common_prefixes: cleaned_description = cleaned_description[len(prefix):].strip() if cleaned_description.lower().startswith(prefix.lower()) else cleaned_description
                for suffix in common_suffixes: cleaned_description = cleaned_description[:-len(suffix)].strip() if cleaned_description.lower().endswith(suffix.lower()) else cleaned_description
                cleaned_description = re.sub(r'\s*\([^)]*\w[^)]*\)\s*$', '', cleaned_description).strip()
                cleaned_description = cleaned_description.strip('"').strip("'").strip()
                generated_description = cleaned_description
            else:
                logger.warning("Failed to generate description (empty response from LLM), proceeding without it.")

        # 3. Generate Content
        content_prompt_template = self.prompts.get("generate_content")
        if not content_prompt_template:
            logger.error("Content generation prompt template not found.")
            return None
        content_prompt = content_prompt_template.format(keyword=keyword, generated_title=generated_title)
        
        generated_content = self._make_llm_request(content_prompt, max_tokens=1200, temperature=0.7)
        if not generated_content:
            logger.error("Failed to generate content.")
            return None

        # 4. Generate Tags using Title and Description
        llm_generated_tags = []
        if generated_title and generated_description:
            llm_generated_tags = self.generate_tags_for_post(generated_title, generated_description)
        else:
            logger.warning(f"Skipping LLM tag generation for keyword '{keyword}' due to missing title or description.")

        logger.info(f"Successfully generated blog post details for keyword: '{keyword}'. Title: '{generated_title}'")
        return {
            "title": generated_title,
            "description": generated_description,
            "content": generated_content,
            "tags": llm_generated_tags
        }

    def expand_keyword_into_subtopics(self, keyword, num_subtopics):
        """Expands a given keyword into a specified number of distinct subtopics.

        Args:
            keyword (str): The main keyword to expand.
            num_subtopics (int): The number of subtopics to generate.

        Returns:
            list[str]: A list of subtopic strings. Returns empty list on failure.
        """
        logger.info(f"Expanding keyword '{keyword}' into {num_subtopics} subtopics.")
        
        prompt_template = self.prompts.get("expand_keyword")
        if not prompt_template:
            logger.error("Keyword expansion prompt template not found.")
            return []
            
        prompt = prompt_template.format(keyword=keyword, num_subtopics=num_subtopics)
        
        response_text = self._make_llm_request(prompt, max_tokens=50 * num_subtopics, temperature=0.6)
        if not response_text:
            logger.error(f"Failed to get subtopics from LLM for keyword '{keyword}'.")
            return []

        subtopics = []
        for line in response_text.split('\n'):
            line = line.strip()
            if not line: continue
            if '.' in line and line.split('.', 1)[0].isdigit():
                topic_text = line.split('.', 1)[1].strip()
            elif ')' in line and line.split(')', 1)[0].isdigit():
                topic_text = line.split(')', 1)[1].strip()
            elif line.startswith('- '):
                topic_text = line[2:].strip()
            else:
                topic_text = line
            if topic_text:
                subtopics.append(topic_text)
        
        if len(subtopics) >= num_subtopics: # Changed to >= to be more lenient if LLM gives more
             logger.info(f"Successfully expanded keyword '{keyword}' into {len(subtopics)} subtopics (requested {num_subtopics}): {subtopics[:num_subtopics]}")
             return subtopics[:num_subtopics] # Return only the number requested
        elif subtopics: # Got some, but not enough
            logger.warning(f"Expected {num_subtopics} subtopics for '{keyword}', but LLM generated {len(subtopics)}. Using what was generated: {subtopics}")
            return subtopics
        else:
            logger.error(f"LLM response for subtopics of '{keyword}' was empty or not in expected format: {response_text}")
            return []

if __name__ == "__main__":
    # This is for basic testing. 
    # Ensure your tool/config.ini is set up with a valid API key.
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    logger.info("Starting LLMHandler test...")
    
    try:
        handler = LLMHandler()

        # Test 1: Generate blog post details
        print("\n--- Test: Generate Blog Post Details ---")
        keyword1 = "Introduction to Docker"
        date1 = "2024-07-28"
        post_details = handler.generate_blog_post_details(keyword1, date1)
        if post_details:
            print(f"  Title: {post_details['title']}")
            print(f"  Description: {post_details['description']}")
            print(f"  Content Preview (first 100 chars): {post_details['content'][:100]}...")
        else:
            print(f"  Failed to generate blog post for '{keyword1}'.")

        # Test 2: Expand keyword into subtopics
        print("\n--- Test: Expand Keyword into Subtopics ---")
        main_keyword = "Advanced Kubernetes Concepts"
        num_needed = 3
        subtopics_list = handler.expand_keyword_into_subtopics(main_keyword, num_needed)
        if subtopics_list:
            print(f"  Generated {len(subtopics_list)} subtopics for '{main_keyword}':")
            for i, topic in enumerate(subtopics_list):
                print(f"    {i+1}. {topic}")
        else:
            print(f"  Failed to expand keyword '{main_keyword}'.")

        # Test 3: Generate blog post for a sub-topic from expansion
        if subtopics_list:
            print("\n--- Test: Generate Blog Post for a Sub-topic ---")
            sub_keyword = subtopics_list[0]
            date2 = "2024-07-29"
            sub_post_details = handler.generate_blog_post_details(sub_keyword, date2)
            if sub_post_details:
                print(f"  Title: {sub_post_details['title']}")
                print(f"  Description: {sub_post_details['description']}")
                print(f"  Content Preview (first 100 chars): {sub_post_details['content'][:100]}...")
            else:
                print(f"  Failed to generate blog post for sub-topic '{sub_keyword}'.")

    except Exception as e:
        print(f"An error occurred during LLMHandler testing: {e}")
        logger.exception("Exception during LLMHandler test run")
    logger.info("LLMHandler test finished.") 