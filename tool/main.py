import argparse
import logging
import sys
import os
from datetime import datetime
# No longer importing openai specific exceptions directly

# Relative imports for package structure
from .config_manager import get_setting, get_llm_api_key # Updated function name
from .date_utils import generate_dates
from .llm_handler import LLMHandler
from .file_generator import create_jekyll_post_file, POSTS_DIR
from .git_utils import git_add_commit, git_push

# Determine project root for logging configuration, assuming main.py is in tool/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_LOG_FILE_NAME = "blog_generation_tool.log" # Default if not in config

def setup_logging():
    """Configures logging to file and console."""
    log_file_name = get_setting("log_file", DEFAULT_LOG_FILE_NAME)
    log_file_path = os.path.join(PROJECT_ROOT, log_file_name) # Place log in project root

    # Create logs directory if it doesn't exist (e.g. tool/logs/)
    # Or simply place it in project root as per current log_file_path
    # For simplicity, placing in project root for now.

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(name)s - %(module)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout) # Also log to console
        ],
        datefmt='%H:%M:%S'
    )
    # Set higher level for noisy libraries if needed, e.g.:
    # logging.getLogger("openai").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.info(f"Logging initialized. Log file at: {log_file_path}")

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Automated Jekyll Blog Post Generator")
    parser.add_argument("--start_date", required=True, help="Start date for blog posts (YYYY-MM-DD)")
    parser.add_argument("--end_date", required=True, help="End date for blog posts (YYYY-MM-DD)")
    parser.add_argument("--keywords", nargs='+', required=True, help="List of keywords/topics for blog posts")
    # parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use") # Future: make model configurable
    parser.add_argument("--tags", nargs='*', help="Optional default tags to add to all posts")
    parser.add_argument("--no_push", action="store_true", help="Generate posts and commit, but do not push to remote.")

    args = parser.parse_args()

    logger.info(f"Starting blog generation with parameters:")
    logger.info(f"  Start Date: {args.start_date}")
    logger.info(f"  End Date: {args.end_date}")
    logger.info(f"  Keywords: {args.keywords}")
    if args.tags:
        logger.info(f"  Default Tags: {args.tags}")
    if args.no_push:
        logger.info("  Git push will be skipped.")

    try:
        # Early check for API key to fail fast
        get_llm_api_key() # Updated function call
        logger.info("LLM API key found in configuration.")

        blog_dates = generate_dates(args.start_date, args.end_date)
        if not blog_dates:
            logger.error("No dates generated. Please check your start and end dates.")
            return
        logger.info(f"Generated {len(blog_dates)} target dates for posts.")

        keywords_queue = list(args.keywords)
        llm = LLMHandler()
        generated_files_count = 0
        total_posts_to_generate = len(blog_dates)

        for i, post_date in enumerate(blog_dates):
            logger.info(f"\nProcessing post {i+1}/{total_posts_to_generate} for date: {post_date.strftime('%Y-%m-%d')}")
            
            current_keyword = ""
            if keywords_queue:
                current_keyword = keywords_queue.pop(0)
                logger.info(f"Using keyword: '{current_keyword}'")
            else:
                # If original keywords run out, try to use the last keyword to generate subtopics
                if args.keywords: # Check if there were any initial keywords
                    last_main_keyword = args.keywords[-1] # Use the last provided main keyword for expansion
                    remaining_posts = total_posts_to_generate - i
                    logger.info(f"Keywords exhausted. Attempting to expand last main keyword '{last_main_keyword}' for {remaining_posts} remaining posts.")
                    subtopics = llm.expand_keyword_into_subtopics(last_main_keyword, remaining_posts)
                    if subtopics:
                        logger.info(f"Generated subtopics: {subtopics}")
                        keywords_queue.extend(subtopics)
                        if keywords_queue:
                            current_keyword = keywords_queue.pop(0)
                            logger.info(f"Using newly generated subtopic: '{current_keyword}'")
                        else:
                            logger.error("Failed to get a keyword from newly generated subtopics list.")
                            break # Stop if no more keywords can be obtained
                    else:
                        logger.error(f"Failed to expand keyword '{last_main_keyword}'. Stopping generation.")
                        break # Stop if expansion fails
                else:
                    logger.error("No initial keywords provided and queue is empty. Cannot proceed.")
                    break
            
            if not current_keyword:
                logger.warning(f"No keyword available for date {post_date.strftime('%Y-%m-%d')}. Skipping.")
                continue

            post_details = llm.generate_blog_post_details(current_keyword, post_date.strftime('%Y-%m-%d'))
            if not post_details:
                logger.error(f"Failed to generate blog post details for keyword '{current_keyword}'. Skipping.")
                continue

            # Tags processing:
            # Start with LLM generated tags (which might be an empty list)
            current_post_tags = post_details.get("tags", []) 
            logger.info(f"LLM suggested tags: {current_post_tags}")
            
            # Ensure all tags are lowercase, unique, and sorted
            final_post_tags = sorted(list(set([tag.lower() for tag in current_post_tags if tag]))) # Filter out empty tags if any
            logger.info(f"Final tags for post '{post_details['title']}': {final_post_tags}")

            blog_file_path = create_jekyll_post_file(
                title=post_details["title"],
                post_date_obj=post_date,
                description=post_details["description"],
                content=post_details["content"],
                tags=final_post_tags # Use the combined and cleaned tags
            )

            if blog_file_path:
                logger.info(f"Blog post file created: {blog_file_path}")
                commit_success = git_add_commit(blog_file_path, post_date, post_details["title"])
                if commit_success:
                    logger.info(f"Successfully committed: {post_details['title']}")
                    generated_files_count += 1
                else:
                    logger.error(f"Failed to commit blog post: {post_details['title']}. Check Git status.")
                    # Decide if we should stop or continue. For now, continue.
            else:
                logger.error(f"Failed to create blog post file for keyword '{current_keyword}'.")

        logger.info(f"\nFinished processing all dates. Generated {generated_files_count} blog posts.")

        if generated_files_count > 0 and not args.no_push:
            logger.info("Attempting to push changes to remote repository...")
            push_success = git_push()
            if push_success:
                logger.info("Successfully pushed changes.")
            else:
                logger.error("Failed to push changes. Please push manually.")
        elif args.no_push:
            logger.info("Skipping git push as per --no_push flag.")
        elif generated_files_count == 0:
            logger.info("No posts were generated, skipping git push.")

    except FileNotFoundError as e:
        logger.error(f"Configuration or essential file not found: {e}")
        logger.error("Please ensure tool/config.ini exists and is correctly set up (copy from tool/config.example.ini) with the [llm_api] section.")
    except ValueError as e: # Catches issues from generate_dates, config validation, etc.
        logger.error(f"Configuration error or invalid input: {e}")
    # Generic Exception will catch errors from LLMHandler (e.g., HTTP errors, timeouts)
    except Exception as e:
        # This will now catch errors from LLMHandler (e.g., HTTP errors, timeouts, response parsing issues)
        # as well as any other unexpected errors.
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True) # Log traceback
    finally:
        logging.info("Blog generation process finished.")

if __name__ == "__main__":
    main() 