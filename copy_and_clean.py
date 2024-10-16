import os
import shutil
from datetime import datetime

def copy_and_clean():
    # Get the current date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Define source and destination directories
    source_dir = "amazon exports"
    dest_dir = os.path.join("Reports history", today)

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Copy contents of amazon exports to the new directory
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    print(f"Contents copied to: {dest_dir}")

    # Clean up amazon exports directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file != ".gitkeep":
                os.remove(os.path.join(root, file))

    print("Cleaned up amazon exports directory")

if __name__ == "__main__":
    copy_and_clean()

