import os
import datetime
import re
import logging
from .config_manager import get_setting

logger = logging.getLogger(__name__)

# Assuming the script is in tool/ and _posts/ is in the parent directory (project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
POSTS_DIR = os.path.join(PROJECT_ROOT, "_posts")

def slugify(text):
    """Convert a string to a URL-friendly slug.
    Lowercase, remove non-alphanumeric characters (except hyphens),
    and replace spaces with hyphens.
    """
    if not text: # Handle empty title case
        return "untitled"
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove non-alphanumeric, non-space, non-hyphen
    text = re.sub(r'[\s_]+', '-', text)    # Replace spaces and underscores with hyphens
    text = re.sub(r'--+', '-', text)       # Replace multiple hyphens with single
    text = text.strip('-')
    return text if text else "untitled" # Ensure not empty after stripping

def create_jekyll_post_file(title, post_date_obj, description, content, tags):
    """Creates a Jekyll-compatible Markdown file for a blog post.

    Args:
        title (str): The title of the blog post.
        post_date_obj (datetime.date): The publication date of the post.
        description (str): A short description for the front matter.
        content (str): The main Markdown content of the post.
        tags (list[str]): A list of tags for the post.

    Returns:
        str: The absolute path to the created file, or None if an error occurs.
    """
    logger.info(f"Preparing to create post file for title: '{title}' for date: {post_date_obj.strftime('%Y-%m-%d')}")

    # Get settings from config
    layout = get_setting("default_layout", "post")
    # post_image_url = get_setting("default_post_image", "") # Using manually_added_selection example, use that format for now.
    # The example provided: post-image: "http://jekyllcn.com/img/logo-2x.png"
    # For now, let's make it configurable or leave it based on your example's style
    # We decided to leave post-image blank for now or make it an empty string.
    # However, the example you provided has it. I will use an empty string as a placeholder.
    post_image_url = "" # As per earlier discussion, to be left blank or configurable. Using empty string for now.

    slug = slugify(title)
    if not slug:
        logger.error("Generated slug is empty, cannot create filename.")
        return None
        
    date_str = post_date_obj.strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    # Ensure _posts directory exists
    try:
        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
            logger.info(f"Created directory: {POSTS_DIR}")
    except OSError as e:
        logger.error(f"Error creating directory {POSTS_DIR}: {e}")
        return None

    # Prepare front matter
    processed_tags = []
    if tags:
        for tag in tags:
            cleaned_tag = tag.strip()
            if not cleaned_tag: # Skip empty tags after stripping
                logger.warning(f"Empty tag found and skipped for post titled '{title}'.")
                continue
            if ":" in cleaned_tag:
                logger.warning(f"Tag '{cleaned_tag}' for post titled '{title}' contains a colon and will be skipped.")
                continue
            processed_tags.append(cleaned_tag)
    
    front_matter_tags = "\n".join([f"- {tag}" for tag in processed_tags]) if processed_tags else ""
    
    front_matter = (
        "---\n"
        f"title: \"{title}\"\n"
        f"layout: {layout}\n"
        f"description: \"{description}\"\n"
    )
    if front_matter_tags:
        front_matter += f"tags:\n{front_matter_tags}\n"
    front_matter += "---\n\n"

    full_content = front_matter + content

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        logger.info(f"Successfully created blog post: {filepath}")
        return filepath
    except IOError as e:
        logger.error(f"Error writing to file {filepath}: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    logger.info("Starting FileGenerator test...")

    # Example usage
    test_title = "My Awesome Test Post! (Special Chars & Spaces)"
    test_date = datetime.date(2024, 7, 28)
    test_description = "This is a test post to check file generation."
    test_content = ("# Main Heading\n\nThis is some paragraph text.\n\n"
                      "## Sub Heading\n\nMore text and a list:\n- Item 1\n- Item 2")
    test_tags = ["test", "jekyll", "python utility"]

    # Test 1: Create a post
    print("\n--- Test: Create Jekyll Post File ---")
    created_file_path = create_jekyll_post_file(
        test_title,
        test_date,
        test_description,
        test_content,
        test_tags
    )

    if created_file_path:
        print(f"  Blog post created at: {created_file_path}")
        # You might want to manually check the file content and _posts directory.
        # For cleanup, you could os.remove(created_file_path) here.
        # Example: os.remove(created_file_path)
    else:
        print("  Failed to create blog post file.")

    # Test 2: Post with no tags
    print("\n--- Test: Create Post with No Tags ---")
    test_title_no_tags = "Post Without Any Tags"
    test_date_no_tags = datetime.date(2024, 7, 29)
    created_file_no_tags = create_jekyll_post_file(
        test_title_no_tags,
        test_date_no_tags,
        "A post with no tags field in front matter.",
        "Content for no tags post.",
        [] # Empty list for tags
    )
    if created_file_no_tags:
        print(f"  Blog post (no tags) created at: {created_file_no_tags}")
    else:
        print("  Failed to create blog post file (no tags).")

    # Test 3: Post with an empty title (should become 'untitled')
    print("\n--- Test: Create Post with Empty Title ---")
    test_date_empty_title = datetime.date(2024, 7, 30)
    created_file_empty_title = create_jekyll_post_file(
        "", 
        test_date_empty_title, 
        "Description for untitled post.", 
        "Content for untitled post.", 
        ["untitled"]
    )
    if created_file_empty_title:
        print(f"  Blog post (empty title) created at: {created_file_empty_title}")
    else:
        print("  Failed to create blog post file (empty title).")

    logger.info("FileGenerator test finished.") 