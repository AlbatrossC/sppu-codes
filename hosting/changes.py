import os
import shutil
import subprocess

# Constants
DEVELOPMENT_REPO_URL = "https://github.com/AlbatrossC/sppu-codes.git"
HOSTING_REPO_PATH = r"C:\Users\jadha\OneDrive\Desktop\Sppucodes Hosting"  # Path to your hosting repo folder
DEV_REMOTE_NAME = "dev"

def run_command(command, cwd=None):
    """
    Runs a shell command and prints output or errors.
    """
    result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def delete_old_files(directory):
    """
    Deletes all files and folders in the specified directory except `.git`.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if item == ".git":
            continue
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  # Remove file or symlink
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directory
    print(f"All old files in '{directory}' have been deleted, except for the .git folder.")

def sync_repositories():
    """
    Sync changes from the development repository to the hosting repository.
    """
    if not os.path.exists(HOSTING_REPO_PATH):
        print(f"Error: Hosting repository path '{HOSTING_REPO_PATH}' does not exist.")
        return

    print("Navigating to hosting repository...")
    os.chdir(HOSTING_REPO_PATH)

    # Step 1: Delete all old files except `.git`
    print("Deleting old files from the hosting repository...")
    delete_old_files(HOSTING_REPO_PATH)

    # Step 2: Add the development repository as a remote
    print("Adding development repository as remote...")
    run_command(f"git remote add {DEV_REMOTE_NAME} {DEVELOPMENT_REPO_URL}")

    # Step 3: Pull changes from the development repository
    print("Pulling changes from the development repository...")
    if run_command(f"git pull {DEV_REMOTE_NAME} main --allow-unrelated-histories"):
        print("Successfully merged changes from the development repository.")

    # Step 4: Push changes to the hosting repository
    print("Pushing merged changes to the hosting repository...")
    if run_command("git push origin main"):
        print("Successfully updated the hosting repository.")

# Execute the script
sync_repositories()
