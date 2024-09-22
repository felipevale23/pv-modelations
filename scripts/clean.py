
import os
import shutil
import glob

# Directories and patterns to clean
dirs_to_remove = ['build', 'dist', '*.egg-info']
egg_files_to_remove = glob.glob('*.egg')  # Finds all .egg files in the current directory

def clean():
    # Remove specified directories
    for dir_path in dirs_to_remove:
        for directory in glob.glob(dir_path):  # Use glob to match patterns like *.egg-info
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print(f"Removed {directory}")
            else:
                print(f"{directory} does not exist")

    # Remove .egg files
    for egg_file in egg_files_to_remove:
        if os.path.exists(egg_file):
            os.remove(egg_file)
            print(f"Removed {egg_file}")
        else:
            print(f"{egg_file} does not exist")

if __name__ == "__main__":
    clean()
