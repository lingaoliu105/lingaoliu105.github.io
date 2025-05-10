import subprocess
import logging
import os
import datetime
from .config_manager import get_setting # Changed back to relative import

logger = logging.getLogger(__name__)

# Assuming scripts are run from the project root or tool/ dir is in PYTHONPATH
# and .git directory is in the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def _run_git_command(command, working_dir=PROJECT_ROOT, env=None):
    """Helper function to run a Git command and log its output."""
    logger.debug(f"Running Git command: {' '.join(command)} in {working_dir}")
    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=working_dir,
            env=env,
            text=True # For Python 3.7+
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logger.info(f"Git command successful: {' '.join(command)}")
            if stdout:
                logger.debug(f"Git stdout:\n{stdout}")
            return True, stdout.strip()
        else:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Git stderr:\n{stderr}")
            if stdout:
                logger.error(f"Git stdout:\n{stdout}")
            return False, stderr.strip()
    except FileNotFoundError:
        logger.error("Git command not found. Ensure Git is installed and in your PATH.")
        return False, "Git command not found."
    except Exception as e:
        logger.error(f"An unexpected error occurred while running Git command: {e}")
        return False, str(e)

def _get_current_branch():
    """Determines the current active Git branch."""
    success, output = _run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if success and output:
        logger.info(f"Determined current Git branch: {output}")
        return output
    else:
        logger.warning("Could not determine current Git branch. Will attempt to push to remote's default (HEAD).")
        # Fallback to pushing to HEAD which usually means the remote's default branch
        # Or we could default to 'main' or make it configurable if this often fails.
        return "HEAD" # Pushing to HEAD usually resolves to the remote's default branch

def git_add_commit(file_path, commit_date_obj, commit_message_title):
    """Adds a file to Git and commits it with a specific author/committer date.

    Args:
        file_path (str): The absolute path to the file to add and commit.
        commit_date_obj (datetime.date): The date to use for the commit.
        commit_message_title (str): The title for the commit message (e.g., blog post title).

    Returns:
        bool: True if successful, False otherwise.
    """
    logger.info(f"Attempting to git add and commit file: {file_path} for date: {commit_date_obj}")

    commit_time_str = get_setting("git_commit_time", "10:00:00")
    commit_datetime_str = f"{commit_date_obj.strftime('%Y-%m-%d')} {commit_time_str}"

    # Ensure file_path is relative to the git repository root for `git add`
    # if it's passed as absolute. `file_path` from `file_generator` should be absolute.
    relative_file_path = os.path.relpath(file_path, PROJECT_ROOT)

    add_command = ["git", "add", relative_file_path]
    success, _ = _run_git_command(add_command)
    if not success:
        logger.error(f"git add failed for {relative_file_path}")
        return False

    commit_env = os.environ.copy()
    commit_env["GIT_AUTHOR_DATE"] = commit_datetime_str
    commit_env["GIT_COMMITTER_DATE"] = commit_datetime_str
    
    commit_message = f"Add post: {commit_message_title}"
    commit_command = ["git", "commit", "-m", commit_message]
    
    success, _ = _run_git_command(commit_command, env=commit_env)
    if not success:
        logger.error(f"git commit failed for {relative_file_path}. Attempting to git reset HEAD -- {relative_file_path} to unstage.")
        # Attempt to unstage the file if commit fails to avoid partial state
        reset_command = ["git", "reset", "HEAD", "--", relative_file_path]
        _run_git_command(reset_command) # Log result but don't let this failure override commit failure
        return False
    
    logger.info(f"Successfully added and committed {relative_file_path} with commit date {commit_datetime_str}")
    return True

def git_push(remote_name="origin"):
    """Pushes changes to the specified remote and the current active branch."""
    current_branch = _get_current_branch()
    # If _get_current_branch returned None or empty (though it falls back to HEAD),
    # handle it here, though the fallback to HEAD is a reasonable default.
    if not current_branch: # Should not happen with HEAD fallback, but as a safeguard
        logger.error("Cannot git push: failed to determine current branch and no fallback.")
        return False
        
    logger.info(f"Attempting to git push to {remote_name}/{current_branch}")
    push_command = ["git", "push", remote_name, current_branch]
    success, _ = _run_git_command(push_command)
    
    if success:
        logger.info(f"Successfully pushed to {remote_name}/{current_branch}")
    else:
        logger.error(f"git push to {remote_name}/{current_branch} failed.")
    return success

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Starting GitUtils test...")

    # Before running this test, ensure:
    # 1. You are in a Git repository.
    # 2. `tool/config.ini` exists and is readable (for git_commit_time).
    # 3. You might want to create a dummy file to test add/commit.

    # Test 1: Create a dummy file and try to commit it
    print("\n--- Test: Git Add and Commit ---")
    dummy_file_name = "test_git_commit.txt"
    dummy_file_path = os.path.join(PROJECT_ROOT, dummy_file_name)
    
    try:
        with open(dummy_file_path, "w") as f:
            f.write("This is a test file for git_utils.py.\n")
        print(f"  Created dummy file: {dummy_file_path}")

        test_commit_date = datetime.date(2023, 1, 15)
        test_title = "Test Commit for GitUtils"
        
        # Need to initialize config for get_setting to work if not run via main script
        # For standalone test, ensure tool/config.ini has [settings] git_commit_time=HH:MM:SS
        # If config_manager.get_config() fails, this test will fail.

        commit_success = git_add_commit(dummy_file_path, test_commit_date, test_title)
        if commit_success:
            print(f"  Successfully added and committed {dummy_file_name}.")
            print(f"  Run 'git log -1 --pretty=fuller' to check author/commit dates for the last commit.")
        else:
            print(f"  Failed to add and commit {dummy_file_name}.")

        # Test 2: Try to push (this will likely require credentials or setup)
        # print("\n--- Test: Git Push ---")
        # print("  Attempting to push. This might fail if remote is not configured or credentials are required.")
        # push_success = git_push() # Use default remote/branch
        # if push_success:
        #     print("  Push successful.")
        # else:
        #     print("  Push failed. This is expected if remote is not set up for automated push.")

    except Exception as e:
        logger.error(f"Error during GitUtils test: {e}")
        print(f"An error occurred: {e}")
    finally:
        # Clean up the dummy file
        if os.path.exists(dummy_file_path):
            # Optional: Reset the commit if you want to keep the history clean after testing
            # subprocess.run(["git", "reset", "HEAD^", "--hard"], cwd=PROJECT_ROOT)
            os.remove(dummy_file_path)
            # And remove it from git staging if it wasn't committed but was added
            subprocess.run(["git", "rm", "--cached", dummy_file_name], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"  Cleaned up dummy file: {dummy_file_path}")

    logger.info("GitUtils test finished.") 