import openai
import logging
from .config_manager import get_openai_api_key, get_openai_api_base, get_llm_model

# Configure basic logging
logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self):
        """Initializes the LLM client using API key, base URL, and model from config."""
        self.api_key = get_openai_api_key()
        self.api_base = get_openai_api_base()
        self.model_name = get_llm_model()
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base # This will be None if not set in config, openai lib handles it
        )
        logger.info("LLMHandler initialized.")
        if self.api_base:
            logger.info(f"Using API base: {self.api_base}")
        logger.info(f"Using LLM model: {self.model_name}")

    def _make_llm_request(self, prompt, max_tokens=1500, temperature=0.7):
        """Helper function to make a request to the LLM."""
        try:
            logger.debug(f"Sending prompt to LLM ({self.model_name}): {prompt[:100]}...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes technical blog posts in English."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                n=1,
                stop=None
            )
            logger.debug("Received response from LLM.")
            return response.choices[0].message.content.strip()
        except openai.APIConnectionError as e:
            logger.error(f"LLM API Connection Error: {e}")
            raise Exception(f"Failed to connect to LLM API: {e}")
        except openai.APIStatusError as e:
            logger.error(f"LLM API Status Error (code {e.status_code}): {e.response}")
            raise Exception(f"LLM API returned an error: {e.status_code} - {e.response}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while querying LLM: {e}")
            raise Exception(f"An unexpected error occurred: {e}")

    def generate_blog_post_details(self, keyword, blog_date):
        """Generates blog post title, description, and content for a given keyword and date.

        Args:
            keyword (str): The keyword/topic for the blog post.
            blog_date (str): The publication date for the blog post (YYYY-MM-DD).

        Returns:
            dict: A dictionary with 'title', 'description', and 'content'.
                  Returns None if generation fails.
        """
        logger.info(f"Generating blog post for keyword: '{keyword}' on date: {blog_date}")

        # 1. Generate Title
        title_prompt = f"Generate a concise and engaging blog post title (max 10 words) in English for a technical article about \"{keyword}\". The article is for a general technical audience. Return ONLY the title itself, without any surrounding text, explanations, or quotation marks."
        raw_title_response = self._make_llm_request(title_prompt, max_tokens=40, temperature=0.7) # Increased max_tokens slightly just in case
        
        if not raw_title_response:
            logger.error("Failed to generate title (empty response from LLM).")
            return None
        
        # Post-processing: Try to extract the cleanest possible title.
        # Remove common chatty prefixes/suffixes and strip quotes.
        # This can be made more robust if specific patterns are common.
        cleaned_title = raw_title_response.strip()
        
        # Attempt to remove common LLM conversational fluff if it appears before or after a quoted title or a clear title line.
        # For example, "Here is a good title: \"My Title\"" or "\"My Title\" - I hope this helps!"
        # A more robust way could be regex to find content within quotes if quotes are consistently used by the model for the title itself.
        # For now, a simpler stripping and then quote removal.
        
        # First, strip common leading/trailing non-title text (heuristic)
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

        # Remove surrounding quotes, if any, after stripping other fluff
        cleaned_title = cleaned_title.strip('"').strip("'").strip()

        if not cleaned_title:
            logger.error(f"Failed to extract a clean title from LLM response: '{raw_title_response}'")
            return None
        generated_title = cleaned_title

        # 2. Generate Description (for front matter)
        description_prompt = f"Write a brief SEO-friendly meta description (max 30 words) in English for a technical blog post titled \"{generated_title}\" which discusses \"{keyword}\"."
        generated_description = self._make_llm_request(description_prompt, max_tokens=60, temperature=0.7)
        if not generated_description:
            logger.warning("Failed to generate description, proceeding without it.")
            generated_description = ""

        # 3. Generate Content
        # We can refine this prompt further based on desired style, length, etc.
        content_prompt = (
            f"Write a technical blog post in English, approximately 500-800 words, about \"{keyword}\".\n"
            f"The title of the post is \"{generated_title}\".\n"
            f"The blog post is intended for a technical audience but should be accessible.\n"
            f"Structure the post with an introduction, several main points or sections with clear headings (using Markdown like ## Heading), and a conclusion.\n"
            f"Ensure the content is informative, well-structured, and engaging.\n"
            f"Do not include the title or any Jekyll front matter in the output, only the main content of the blog post itself starting from the introduction."
        )
        generated_content = self._make_llm_request(content_prompt, max_tokens=1200, temperature=0.7)
        if not generated_content:
            logger.error("Failed to generate content.")
            return None

        logger.info(f"Successfully generated blog post details for keyword: '{keyword}'. Title: '{generated_title}'")
        return {
            "title": generated_title,
            "description": generated_description,
            "content": generated_content
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
        prompt = (
            f"The primary keyword for a series of technical blog posts is \"{keyword}\". "
            f"I need to create {num_subtopics} distinct blog posts based on this primary keyword, where each post delves into a specific aspect or sub-topic related to \"{keyword}\". "
            f"Please suggest {num_subtopics} unique sub-topics. "
            f"Each sub-topic should be suitable as a focus for a standalone technical blog post of 500-800 words. "
            f"Return ONLY a numbered list of these sub-topics, each on a new line. For example:\n"
            f"1. First sub-topic\n"
            f"2. Second sub-topic\n"
            f"..."
        )
        
        response_text = self._make_llm_request(prompt, max_tokens=50 * num_subtopics, temperature=0.6)
        if not response_text:
            logger.error(f"Failed to get subtopics from LLM for keyword '{keyword}'.")
            return []

        subtopics = []
        for line in response_text.split('\n'):
            line = line.strip()
            if not line: continue
            # Attempt to strip numbering like "1. ", "1) ", "- ", etc.
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
        
        if len(subtopics) == num_subtopics:
            logger.info(f"Successfully expanded keyword '{keyword}' into {len(subtopics)} subtopics: {subtopics}")
            return subtopics
        elif subtopics: # Got some, but maybe not enough
            logger.warning(f"Expected {num_subtopics} subtopics for '{keyword}', but LLM generated {len(subtopics)}. Using what was generated: {subtopics}")
            return subtopics
        else:
            logger.error(f"LLM response for subtopics of '{keyword}' was empty or not in expected format: {response_text}")
            return []

if __name__ == "__main__":
    # This is for basic testing. 
    # Ensure your tool/config.ini is set up with a valid API key.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
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