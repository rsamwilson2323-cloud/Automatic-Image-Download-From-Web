# ===================== FIX FOR LIBRARY BUG =====================
import pathlib
if not hasattr(pathlib.Path, "isdir"):
    pathlib.Path.isdir = pathlib.Path.is_dir

# ===================== IMPORTS =====================
import os
import re
import io
import json
import shutil
import hashlib
import tempfile
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from six.moves.urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm
from icrawler.builtin import BingImageCrawler
from icrawler.downloader import ImageDownloader

try:
    from bing_image_downloader import downloader as bing_downloader
except Exception:
    bing_downloader = None

# ===================== SETTINGS =====================
MIN_SIZE = 200          # skip images smaller than 200x200 px
MIN_BYTES = 3000        # skip tiny files

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

# ===================== CHECK EXISTING IMAGES =====================
def is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.load()          # full decode, catches truncated/corrupt files
        return True
    except Exception:
        return False

broken_folder = os.path.join(user_folder, "_broken")
broken_count = 0
for f in os.listdir(user_folder):
    full = os.path.join(user_folder, f)
    if os.path.isfile(full) and not is_valid_image(full):
        os.makedirs(broken_folder, exist_ok=True)
        shutil.move(full, os.path.join(broken_folder, f))
        broken_count += 1
        print(f"   🗑️  Broken image moved to _broken: {f}")
if broken_count:
    print(f"   Found {broken_count} unreadable image(s) in your folder.\n")

# ===================== FIND NEXT IMAGE NUMBER =====================
existing_files = [f for f in os.listdir(user_folder)
                  if os.path.isfile(os.path.join(user_folder, f))]
numbers = []

for f in os.listdir(user_folder):
    match = re.match(r"Image_(\d+)\.", f)
    if match:
        numbers.append(int(match.group(1)))
if os.path.isdir(broken_folder):
    for f in os.listdir(broken_folder):          # avoid reusing numbers
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

# ===================== SHARED STATE =====================
state = {"count": start_num, "added": 0, "skipped": 0, "rejected": 0}
lock = threading.Lock()
bar = tqdm(total=quantity, desc="Downloading", unit="img", ncols=80)

KEEP_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", "BMP": ".bmp"}

# ===================== SAVE FUNCTIONS (same saving method) =====================
def prepare_image(data):
    """Fully decode the image. Return (bytes_to_save, extension) or None if bad."""
    if len(data) < MIN_BYTES:
        return None
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format
        img.load()                         # full decode -> rejects truncated files
        w, h = img.size
    except Exception:
        return None

    if w < MIN_SIZE or h < MIN_SIZE:
        return None

    # Already a universally-viewable format: keep the original bytes
    if fmt in KEEP_FORMATS:
        return data, KEEP_FORMATS[fmt]

    # WEBP / other formats: convert so every viewer can open it
    try:
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            img.convert("RGBA").save(buf, "PNG")
            return buf.getvalue(), ".png"
        img.convert("RGB").save(buf, "JPEG", quality=95)
        return buf.getvalue(), ".jpg"
    except Exception:
        return None


def save_bytes(data):
    """Check image -> skip duplicates -> save as Image_N."""
    with lock:
        if state["added"] >= quantity:
            return False

        result = prepare_image(data)
        if result is None:
            state["rejected"] += 1
            return False
        out_bytes, ext = result

        file_hash = hashlib.md5(out_bytes).hexdigest()

        # Skip duplicate images
        if file_hash in existing_hashes:
            state["skipped"] += 1
            tqdm.write("   ⚠️  Duplicate skipped")
            return False

        new_name = f"Image_{state['count']}{ext}"
        with open(os.path.join(user_folder, new_name), "wb") as f:
            f.write(out_bytes)

        existing_hashes.add(file_hash)
        state["count"] += 1
        state["added"] += 1
        bar.update(1)
        tqdm.write(f"   ✅ Saved {new_name}   ({state['added']}/{quantity})")
        return True


def save_file(path):
    """Used by icrawler / bing_image_downloader results (files on disk)."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        save_bytes(data)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def done():
    return state["added"] >= quantity

# ===================== PRIVATE SESSION (SafeSearch OFF) =====================
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "DNT": "1",
}

def make_session():
    """Fresh session every time: no old cookies or history (incognito-like)."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.cookies.set("SRCHHPGUSR", "ADLT=OFF", domain=".bing.com")   # SafeSearch off
    return s

# ===================== METHOD 1: requests + BeautifulSoup + lxml =====================
def method_requests():
    session = make_session()
    seen_urls = set()
    first = 0
    empty_pages = 0

    def fetch(link):
        if done():
            return
        try:
            p = urlparse(link)
            referer = f"{p.scheme}://{p.netloc}/"
            r = session.get(link, timeout=15, headers={"Referer": referer})
            if r.status_code != 200:
                return
            if not r.headers.get("Content-Type", "").lower().startswith("image"):
                return
            expected = r.headers.get("Content-Length")
            if expected and expected.isdigit() and len(r.content) < int(expected):
                return                      # incomplete download
            save_bytes(r.content)
        except Exception:
            pass

    while not done() and empty_pages < 3 and first < 1000:
        page_url = (f"https://www.bing.com/images/async?q={quote_plus(search_name)}"
                    f"&first={first}&count=35&adlt=off&mmasync=1")
        try:
            r = session.get(page_url, timeout=20)
            soup = BeautifulSoup(r.text, "lxml")
        except Exception as e:
            tqdm.write(f"   ❌ Page error: {e}")
            empty_pages += 1
            first += 35
            continue

        links = []
        for a in soup.select("a.iusc"):
            try:
                url = json.loads(a.get("m"))["murl"]
                if url not in seen_urls:
                    seen_urls.add(url)
                    links.append(url)
            except Exception:
                continue

        if not links:
            empty_pages += 1
        else:
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(fetch, links))

        first += 35

# ===================== METHOD 2: icrawler =====================
class LiveDownloader(ImageDownloader):
    def process_meta(self, task):
        if not task.get("success") or not task.get("filename"):
            return
        src = os.path.join(self.storage.root_dir, task["filename"])
        if os.path.isfile(src):
            save_file(src)

def method_icrawler():
    variants = [search_name, f"{search_name} photo", f"{search_name} hd"]
    for keyword in variants:
        if done():
            break
        temp_dir = tempfile.mkdtemp()
        try:
            crawler = BingImageCrawler(
                downloader_cls=LiveDownloader,
                storage={"root_dir": temp_dir},
                downloader_threads=4,
                log_level=logging.CRITICAL
            )
            crawler.session.headers.update(HEADERS)
            crawler.session.cookies.set("SRCHHPGUSR", "ADLT=OFF", domain=".bing.com")
            crawler.crawl(keyword=keyword, max_num=(quantity - state["added"]) + 10)
        except Exception as e:
            tqdm.write(f"   ❌ icrawler error: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)

# ===================== METHOD 3: bing-image-downloader =====================
def method_bing_downloader():
    if bing_downloader is None:
        return
    temp_dir = tempfile.mkdtemp()
    try:
        bing_downloader.download(
            search_name,
            limit=(quantity - state["added"]) + 10,
            output_dir=temp_dir,
            adult_filter_off=True,
            force_replace=True,
            timeout=60,
            verbose=False
        )
        folder = os.path.join(temp_dir, search_name)
        if os.path.isdir(folder):
            for file in sorted(os.listdir(folder)):
                if done():
                    break
                save_file(os.path.join(folder, file))
    except Exception as e:
        tqdm.write(f"   ❌ bing-image-downloader error: {e}")
    shutil.rmtree(temp_dir, ignore_errors=True)

# ===================== RUN =====================
print(f"\nSearching for '{search_name}' (private mode, SafeSearch off)... 🔄\n")

for name, method in [("requests + BeautifulSoup", method_requests),
                     ("icrawler", method_icrawler),
                     ("bing-image-downloader", method_bing_downloader)]:
    if done():
        break
    tqdm.write(f"➡️  Trying method: {name}")
    try:
        method()
    except Exception as e:
        tqdm.write(f"   ❌ {name} failed: {e}")

bar.close()

# ===================== FINAL CHECK =====================
bad_after = 0
for f in os.listdir(user_folder):
    full = os.path.join(user_folder, f)
    if os.path.isfile(full) and not is_valid_image(full):
        bad_after += 1

# ===================== DONE =====================
print("\n✅ Download completed")
print(f"📁 Folder : {user_folder}")
print(f"🆕 New Images Added : {state['added']}")
if state["skipped"]:
    print(f"♻️  Duplicates Skipped : {state['skipped']}")
if state["rejected"]:
    print(f"🚫 Broken/too-small images rejected : {state['rejected']}")
if bad_after:
    print(f"⚠️  {bad_after} file(s) in the folder still cannot be opened.")
else:
    print("🔍 Final check: every image in the folder opens correctly.")
if state["added"] < quantity:
    print(f"⚠️  Only {state['added']} of {quantity} could be downloaded.")

input("\nPress ENTER to exit...")
