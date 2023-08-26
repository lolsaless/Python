import zipfile
import os

def convert_heic_to_jpg(zip_path, output_path):
    # Extract the zip file
    extract_folder = "extracted_images"
    
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Assuming there's a single main directory inside the ZIP
    main_folder = os.listdir(extract_folder)[0]
    main_folder_path = os.path.join(extract_folder, main_folder)

    # Rename HEIC files to JPG
    for root, _, files in os.walk(main_folder_path):
        for file in files:
            if file.lower().endswith('.heic'):
                original_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file.replace('.HEIC', '.JPG').replace('.heic', '.jpg'))
                os.rename(original_file_path, new_file_path)

    # Compress the files into a new zip file
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for root, _, files in os.walk(main_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_folder)
                zipf.write(file_path, arcname=arcname)

# Example usage:
# convert_heic_to_jpg("path_to_input_zip.zip", "path_to_output_zip.zip")
