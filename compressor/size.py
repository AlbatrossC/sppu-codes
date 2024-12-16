import os
import subprocess

def get_git_branches():
    """Return a list of all local branches in the repository."""
    # Run the 'git branch' command to get local branches
    result = subprocess.run(['git', 'branch', '--list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error getting branches: {result.stderr}")
        return []
    
    branches = result.stdout.splitlines()
    return [branch.strip('*').strip() for branch in branches]  # Clean up branch names

def get_branch_size(branch_name):
    """Return the size of the files in the given branch."""
    # Checkout the branch to make sure we calculate its size
    subprocess.run(['git', 'checkout', branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Get the size of the working directory
    size = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            size += os.path.getsize(file_path)
    
    # Convert size to MB for easier readability
    size_in_mb = size / (1024 * 1024)
    return size_in_mb

def main():
    """Main function to compute sizes of all branches."""
    if not os.path.isdir('.git'):
        print("This is not a git repository.")
        return
    
    branches = get_git_branches()
    if not branches:
        print("No branches found.")
        return
    
    branch_sizes = {}
    for branch in branches:
        print(f"Calculating size for branch: {branch}...")
        size = get_branch_size(branch)
        branch_sizes[branch] = size
        print(f"Size of branch '{branch}': {size:.2f} MB")
    
    print("\nSummary of all branch sizes:")
    for branch, size in branch_sizes.items():
        print(f"Branch: {branch}, Size: {size:.2f} MB")
if __name__ == "__main__":
    main()
