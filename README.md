📸 Automatic Image Download From Web

A Python automation tool that quickly downloads images from Bing based on a search term, organizes them into a structured dataset, prevents duplicates, and continues numbering automatically — ideal for building image datasets for machine learning, projects, and research.

🔥 Features

🔎 Search and download images by keyword

📁 Automatically creates an image bank folder

📂 Creates a separate folder for each keyword

🔢 Automatically continues numbering (Image_1, Image_2, etc.)

🚫 Avoids duplicate images using MD5 hashing

⚡ Fast batch downloading

💻 Works with Python 3.8+ on Windows, macOS, Linux

🗂 Repository Structure
Automatic-Image-Download-From-Web/
│
├── automatic image download from web.py
├── README.md
├── requirements.txt
│
└── image bank/
      ├── python/
      │     ├── Image_1.jpg
      │     ├── Image_2.jpg
      │     └── ...
      └── dogs/
            ├── Image_1.png
            ├── Image_2.png
            └── ...
🧰 Requirements

Install the required library:

pip install bing-image-downloader==1.1.1
Library	Version
Python	3.8+
bing-image-downloader	1.1.1

⚠️ Version 1.1.1 of bing-image-downloader is recommended to avoid the known Path.isdir bug.

▶️ How to Use

Clone this repository:

git clone https://github.com/rsamwilson2323-cloud/Automatic-Image-Download-From-Web.git

Navigate into the project folder:

cd Automatic-Image-Download-From-Web

Install required dependency:

pip install bing-image-downloader==1.1.1

Run the script:

python "automatic image download from web.py"

Follow the prompts:

Enter the image name to search: cats
Enter the number of images to download: 10

Check your images in:

image bank/cats/
🧠 How It Works

The script:

Prompts the user for a search keyword and number of images.

Creates the image bank directory (next to the script).

Creates a subfolder for the keyword.

Downloads images using bing-image-downloader.

Avoids duplicate images by comparing MD5 hashes.

Renames images sequentially — preserving previous downloads.

📌 Example Output
Enter the image name to search: python
Enter the number of images to download: 5

Download completed
Folder : image bank/python
Images : Image_1 to Image_5

If you run again with “python” and download 4 more:

Images : Image_6 to Image_9
🛡 Duplicate Handling

The script uses md5 hashing to detect and skip images that are already downloaded, ensuring only unique images are added.

📈 Future Improvements

Here are some ideas you might add later:

🔹 Multi-threaded downloading

🔹 GUI version (Tkinter / PyQt)

🔹 Resize and format conversions

🔹 Integrated dataset export (CSV / labels)

🔹 Support for other search engines

🧾 requirements.txt

You can include this in your repo:

bing-image-downloader==1.1.1
🧑‍💻 Author

Sam Wilson

🔗 GitHub: https://github.com/rsamwilson2323-cloud

🔗 LinkedIn: https://www.linkedin.com/in/sam-wilson-14b554385
