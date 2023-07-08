import os
import shutil

def copy_files_with_prefix(root_folder, destination_folder):
    subfolders = next(os.walk(root_folder))[1]
    for prefix in subfolders:
        prefix_folder = os.path.join(root_folder, prefix)
        for foldername, subfolders, filenames in os.walk(prefix_folder):
            for filename in filenames:
                if filename.endswith('.SEC') or filename.endswith('.BIN'):
                    new_filename = f"{prefix}_{filename}"
                    src_path = os.path.join(foldername, filename)
                    dst_path = os.path.join(destination_folder, new_filename)
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied: {src_path} to {dst_path}")



# Specify the root folder and destination folder paths
root_folder = '/Users/andretavares/Desktop/Luminescência'
destination_folder = '/Users/andretavares/Desktop/Treated luminescence'

# Create the destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Call the function to copy files with the prefix
copy_files_with_prefix(root_folder, destination_folder)


sec_folder = os.path.join(destination_folder, 'SEC')
bin_folder = os.path.join(destination_folder, 'BIN')

# Create the SEC and BIN folders if they don't exist
os.makedirs(sec_folder, exist_ok=True)
os.makedirs(bin_folder, exist_ok=True)

def move_files_to_folders(destination_folder):
    for foldername, subfolders, filenames in os.walk(destination_folder):
        for filename in filenames:
            if filename.endswith('.SEC'):
                src_path = os.path.join(foldername, filename)
                dst_folder = os.path.join(destination_folder, 'SEC')
                dst_path = os.path.join(dst_folder, filename)
                os.makedirs(dst_folder, exist_ok=True)
                shutil.move(src_path, dst_path)
                print(f"Moved .sec file: {src_path} to {dst_path}")
            elif filename.endswith('.BIN'):
                src_path = os.path.join(foldername, filename)
                dst_folder = os.path.join(destination_folder, 'BIN')
                dst_path = os.path.join(dst_folder, filename)
                os.makedirs(dst_folder, exist_ok=True)
                shutil.move(src_path, dst_path)
                print(f"Moved .bin file: {src_path} to {dst_path}")

# Specify the destination folder path
destination_folder = '/Users/andretavares/Desktop/Treated luminescence'

# Call the function to move files to folders
move_files_to_folders(destination_folder)