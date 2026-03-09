# 📸 Automatic Image Download From Web

Automatic Image Download From Web is a Python automation tool that **downloads images from Bing based on a search keyword**, organizes them into structured folders, and prevents duplicate downloads.

This tool is useful for **creating image datasets for machine learning, research, and computer vision projects**.

---

# ✨ Features

🔎 **Search and download images by keyword**

📁 Automatically creates an **image bank folder**

📂 Creates a **separate folder for each keyword**

🔢 Automatically continues numbering
`Image_1, Image_2, Image_3 ...`

🚫 Prevents duplicate images using **MD5 hashing**

⚡ Fast **batch image downloading**

💻 Works with **Python 3.8+ on Windows, macOS, and Linux**

---

# 📂 Project Structure

```id="x1bnkp"
Automatic-Image-Download-From-Web
│
├── automatic image download from web.py
├── README.md
├── requirements.txt
│
└── image bank
      ├── python
      │     ├── Image_1.jpg
      │     ├── Image_2.jpg
      │     └── ...
      │
      └── dogs
            ├── Image_1.png
            ├── Image_2.png
            └── ...
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```id="vfwx2s"
git clone https://github.com/rsamwilson2323-cloud/Automatic-Image-Download-From-Web.git
cd Automatic-Image-Download-From-Web
```

---

## 2️⃣ Install Dependencies

```id="mdqkso"
pip install -r requirements.txt
```

---

# 📦 Requirements

```id="08o1ql"
bing-image-downloader==1.1.1
```

⚠️ Version **1.1.1** is recommended to avoid the known **Path.isdir bug**.

---

# ▶️ Usage

Run the script:

```id="izp9bt"
python "automatic image download from web.py"
```

The program will ask for:

```
Enter the image name to search: cats
Enter the number of images to download: 10
```

Images will be saved in:

```
image bank/cats/
```

---

# 🧠 How It Works

1️⃣ The script asks for a **search keyword** and number of images.
2️⃣ It creates the **image bank folder** if it does not exist.
3️⃣ A **subfolder for the keyword** is created automatically.
4️⃣ Images are downloaded using **bing-image-downloader**.
5️⃣ **MD5 hashing** is used to detect and skip duplicate images.
6️⃣ Images are renamed sequentially.

---

# 📌 Example Output

```
Enter the image name to search: python
Enter the number of images to download: 5

Download completed
Folder : image bank/python
Images : Image_1 to Image_5
```

If you run again:

```
Enter the image name to search: python
Enter the number of images to download: 4
```

Result:

```
Images : Image_6 to Image_9
```

---

# 🛡 Duplicate Handling

The script calculates **MD5 hashes** of downloaded images to detect duplicates and avoid saving the same image multiple times.

This ensures that the dataset contains **only unique images**.

---

# 🚀 Future Improvements

Possible improvements for the project:

🔹 Multi-threaded downloading for faster speed
🔹 GUI version using **Tkinter or PyQt**
🔹 Image resizing and format conversion
🔹 Dataset export with **CSV labels**
🔹 Support for additional search engines

---

# 👨‍💻 Author

**Sam Wilson**

🌐 GitHub
https://github.com/rsamwilson2323-cloud

💼 LinkedIn
https://www.linkedin.com/in/sam-wilson-14b554385

---

# 📜 License

This project is licensed under the **MIT License**.
