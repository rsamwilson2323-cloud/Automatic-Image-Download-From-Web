# ===================== FIX FOR LIBRARY BUG =====================
import pathlib
if not hasattr(pathlib.Path, "isdir"):
    pathlib.Path.isdir = pathlib.Path.is_dir

# ===================== IMPORTS =====================
from bing_image_downloader import downloader
import os
import re
import shutil
import tempfile
import hashlib

# ===================== MAIN FOLDER =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PATH = os.path.join(BASE_DIR, "image bank")
os.makedirs(MAIN_PATH, exist_ok=True)

# ===================== USER INPUT =====================
search_name = input("Enter the image name to search: ").strip()
quantity = int(input("Enter the number of images to download: "))

# ===================== USER FOLDER =====================
user_folder = os.path.join(MAIN_PATH, search_name)
os.makedirs(user_folder, exist_ok=True)

# ===================== FIND NEXT IMAGE NUMBER =====================
existing_files = os.listdir(user_folder)
numbers = []

for f in existing_files:
    match = re.match(r"Image_(\d+)\.", f)
    if match:
        numbers.append(int(match.group(1)))

start_num = max(numbers) + 1 if numbers else 1

# ===================== HASH FUNCTION =====================
def get_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Store existing hashes
existing_hashes = set()
for file in existing_files:
    full_path = os.path.join(user_folder, file)
    if os.path.isfile(full_path):
        existing_hashes.add(get_hash(full_path))

count = start_num
added = 0

print("\nDownloading images... Please wait 🔄")

# ===================== DOWNLOAD LOOP =====================
while added < quantity:

    temp_dir = tempfile.mkdtemp()

    # Small fast batch download
    downloader.download(
        search_name,
        limit=quantity,   # Only small batch
        output_dir=temp_dir,
        adult_filter_off=True,
        force_replace=True,
        timeout=60,
        verbose=False
    )

    downloaded_folder = os.path.join(temp_dir, search_name)

    if os.path.exists(downloaded_folder):

        for file in os.listdir(downloaded_folder):

            if added >= quantity:
                break

            src = os.path.join(downloaded_folder, file)

            if not os.path.isfile(src):
                continue

            file_hash = get_hash(src)

            # Skip duplicate images
            if file_hash in existing_hashes:
                continue

            ext = os.path.splitext(file)[1]
            new_name = f"Image_{count}{ext}"

            shutil.move(src, os.path.join(user_folder, new_name))

            existing_hashes.add(file_hash)
            count += 1
            added += 1

    shutil.rmtree(temp_dir)

    # Safety break (avoid infinite loop if Bing only returns duplicates)
    if added == 0:
        break

# ===================== DONE =====================
print("\n✅ Download completed")
print(f"📁 Folder : {user_folder}")
print(f"🆕 New Images Added : {added}")

input("\nPress ENTER to exit...")
