# Automated Jekyll Blog Post Generator

This tool automates the generation of technical blog posts for a Jekyll-based website using Large Language Models (LLMs) via the OpenAI API (or compatible endpoints).
It takes a date range and a list of keywords, generates articles at random intervals within the date range, and prepares them as Markdown files with appropriate Jekyll front matter. It also handles committing each post to Git with the correct authorship date and can push all changes to a remote repository.

## Features

- **Automated Content Generation**: Creates blog titles, descriptions, and full Markdown content using an LLM.
- **Jekyll Compatibility**: Generates files with standard Jekyll front matter (`title`, `layout`, `description`, `tags`, `post-image`).
- **Configurable Date Range & Intervals**: Specify start and end dates, with posts generated at random 1-5 day intervals.
- **Keyword-Driven Topics**: Uses a list of keywords to guide content generation.
- **Keyword Expansion**: If the number of posts exceeds keywords, it can use the LLM to expand a keyword into multiple sub-topics.
- **Customizable LLM Model**: Specify the LLM model (e.g., `gpt-3.5-turbo`, `gpt-4`) in a configuration file.
- **Git Integration**: 
    - Commits each generated post individually.
    - Sets the `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` for each commit to match the post's publication date.
    - Can automatically push all changes to a remote repository.
- **Configuration File**: Manages API keys, API base URL, model name, and other settings externally.
- **Logging**: Comprehensive logging to both console and a file.

## Directory Structure

```
. (project_root)/
├── _posts/                     # Jekyll posts directory (created if not present)
├── tool/
│   ├── __init__.py             # Marks 'tool' as a Python package
│   ├── main.py                 # Main executable script
│   ├── config_manager.py       # Handles reading config.ini
│   ├── date_utils.py           # Generates publication dates
│   ├── llm_handler.py          # Interacts with the LLM API
│   ├── file_generator.py       # Creates Jekyll Markdown files
│   ├── git_utils.py            # Handles Git operations
│   ├── config.ini              # Your local configuration (API keys, model, etc.)
│   └── config.example.ini      # Example configuration file
└── README.md                   # This file
```

## Setup and Installation

1.  **Python Version**: Ensure you have Python 3.8 or newer installed.

2.  **Clone Repository (Optional)**: If you haven't already, clone this repository.
    ```bash
    # git clone <your-repository-url>
    # cd <repository-name>
    ```

3.  **Create and Activate Virtual Environment (Recommended)**:
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

4.  **Install Dependencies**: The primary dependency is the `openai` library.
    ```bash
    pip install openai
    ```

5.  **Configure the Tool**:
    *   Navigate to the `tool/` directory.
    *   Copy `config.example.ini` to `config.ini`:
        ```bash
        cp tool/config.example.ini tool/config.ini 
        ```
        (or use `copy` on Windows: `copy tool\config.example.ini tool\config.ini`)
    *   Edit `tool/config.ini` and fill in your details:
        *   `api_key`: Your OpenAI API key (or key for a compatible service).
        *   `api_base` (Optional): If you are using a proxy or a non-OpenAI service that mimics the OpenAI API, set its base URL here (e.g., `https://your-custom-endpoint.com/v1`).
        *   `model`: The LLM model you wish to use (e.g., `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`). Defaults to `gpt-3.5-turbo` if not specified.
        *   You can also review other settings like `default_layout`, `git_commit_time`, and `log_file`.

## Usage

Run the main script from the **project root directory** using the `python -m` command for package execution.

**Command Format**:

```bash
python -m tool.main --start_date YYYY-MM-DD --end_date YYYY-MM-DD --keywords "Keyword One" "Keyword Two" "Another Topic" [OPTIONS]
```

**Required Arguments**:

*   `--start_date YYYY-MM-DD`: The earliest date for generating blog posts.
*   `--end_date YYYY-MM-DD`: The latest date for generating blog posts.
*   `--keywords "Keyword1" "Keyword2" ...`: A list of one or more keywords. Each keyword will be used as a topic for a blog post. If more posts are scheduled than keywords provided, the script will attempt to expand the last keyword into sub-topics.

**Optional Arguments**:

*   `--tags "tag1" "tag2" ...`: A list of default tags to be added to the front matter of every generated post.
*   `--no_push`: If this flag is present, the script will generate posts and commit them locally but will skip the final `git push` command.

**Example**:

```bash
python -m tool.main --start_date 2024-09-01 --end_date 2024-09-15 --keywords "Introduction to Docker" "Docker Networking" "Docker Compose Basics" --tags docker devops containerization
```

This command will generate blog posts on the topics "Introduction to Docker", "Docker Networking", etc., between September 1st and September 15th, 2024, with random 1-5 day intervals. Each post will also include the tags "docker", "devops", and "containerization".

## Logging

- Logs are printed to the console during execution.
- Detailed logs are also saved to a file in the project root directory. The default log file is `blog_generation_tool.log` (can be changed in `config.ini` via the `log_file` setting under `[settings]`).

## Important Notes

*   **Git `safe.directory`**: If you encounter a `fatal: detected dubious ownership in repository` error during Git operations, you may need to add your repository directory to Git's list of safe directories. The error message itself usually provides the command to run, e.g.:
    ```bash
    git config --global --add safe.directory /path/to/your/lingaoliu105.github.io
    ```
    Replace `/path/to/your/lingaoliu105.github.io` with the actual absolute path to your project.
*   **API Costs**: Be mindful of the costs associated with LLM API usage, especially when generating many articles or using more advanced models.

## Future Enhancements (Ideas)

- Allow specifying different LLM models per keyword.
- Option to review and edit generated content before file creation/commit.
- More sophisticated `post-image` handling (e.g., searching for relevant images or using LLM to suggest image prompts).
- Support for different output formats or blog platforms.
- Interactive mode for providing parameters.
