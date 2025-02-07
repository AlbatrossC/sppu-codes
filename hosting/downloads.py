import os
import shutil
import zipfile

"""Deletes all .zip files in the downloads folder."""
def delete_old_zip_files(downloads_path):
    for file in os.listdir(downloads_path):
        if file.endswith(".zip"):
            os.remove(os.path.join(downloads_path, file))
            print(f"Deleted old zip file: {file}")

"""Compresses a folder into a zip archive."""
def compress_folder(source_folder, destination_zip):
    with zipfile.ZipFile(destination_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arcname)
    print(f"Compressed {source_folder} -> {destination_zip}")

"""Main function to manage compression workflow."""
def main():
    base_dir = os.getcwd()
    answers_path = os.path.join(base_dir, "answers")
    downloads_path = os.path.join(base_dir, "downloads")
    
    os.makedirs(downloads_path, exist_ok=True)
    
    delete_old_zip_files(downloads_path)
    
    if os.path.exists(answers_path):
        for folder in os.listdir(answers_path):
            folder_path = os.path.join(answers_path, folder)
            if os.path.isdir(folder_path):
                zip_name = f"{folder}.zip"
                zip_path = os.path.join(downloads_path, zip_name)
                compress_folder(folder_path, zip_path)
    else:
        print("'answers' directory not found!")

if __name__ == "__main__":
    main()
