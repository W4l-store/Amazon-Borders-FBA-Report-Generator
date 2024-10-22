import os
import sys
import subprocess
import shutil

def check_and_install_dotenv():
    try:
        import dotenv
    except ImportError:
        print("python-dotenv is not installed. Attempting to install it...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
            print("python-dotenv installed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to install python-dotenv. Please install it manually and try again.")
            sys.exit(1)

def check_current_directory():
    current_dir = os.getcwd()
    if any(os.path.isdir(os.path.join(current_dir, item)) for item in os.listdir(current_dir) if item != '.env'):
        print("Error: The current directory contains other folders. Please run this script in an empty directory.")
        sys.exit(1)

def check_env_file():
    if not os.path.isfile('.env'):
        print("Error: .env file not found in the current directory.")
        sys.exit(1)

def clone_repository(repo_url, target_dir):
    print(f"Cloning repository into {target_dir}...")
    subprocess.check_call(['git', 'clone', repo_url, target_dir])

def copy_env_file(target_dir):
    shutil.copy('.env', target_dir)
    print(".env file copied to the new directory.")

def main():
    # Check and install dotenv if necessary
    check_and_install_dotenv()

    # Now we can safely import dotenv
    from dotenv import load_dotenv

    # Check current directory and .env file
    check_current_directory()
    check_env_file()

    # Load environment variables
    load_dotenv()
    repo_url = os.getenv('GITHUB_REPO_URL')
    if not repo_url:
        print("Error: GITHUB_REPO_URL is not set in the .env file.")
        sys.exit(1)

    # Extract the repository name from the URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Create the target directory path
    target_dir = os.path.join(os.getcwd(), repo_name)

    # Clone repository
    clone_repository(repo_url, target_dir)

    # Copy .env file to the new directory
    copy_env_file(target_dir)

    print("Project cloned successfully.")

if __name__ == "__main__":
    main()
