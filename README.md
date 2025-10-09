# 🎬 YoutubePlaylistDownloader - Shav13ba (Final Edition)

A **Python-based YouTube Playlist Downloader** that allows users to download entire playlists in **MP4 (video)** or **MP3 (audio)** formats, choose quality, and automatically organize files into **Videos** or **Music** folders.  

---

## **Features**

- Download **full YouTube playlists**  
- Choose **MP4 (video)** or **MP3 (audio)**  
- Select **video quality** (Best, 1080p, 720p, 480p, 360p)  
- Select **audio quality** (Best, 192kbps, 128kbps)  
- **Progress bars** with live download progress  
- **Automatic folders**: Videos → `Videos`, Audio → `Music`  
- **Safe exit** on `Ctrl + C`  
- Compatible with **Windows 11**  
- Downloads files in the **current directory**  

---

## **Setup Instructions**

### 1️⃣ Prerequisites

- Python 3.10+ installed  
- FFmpeg installed (or placed in a folder `ffmpeg/bin` next to the script)
- Get FFmpeg ZIP from [link](https://www.gyan.dev/ffmpeg/builds/)
- Extract all FFmpeg `EXE` file in the root dir of the program.
 
**Install Python dependencies:**

```bash
pip install yt-dlp tqdm
```

---

### 2️⃣ Folder Structure

Place the FFmpeg folder next to the script:

```
YouTubeDownloader/
├── youtube_playlist_downloader_final_folders.py
├── ffmpeg/
│   └── bin/
│       ├── ffmpeg.exe
│       └── ffprobe.exe
```

---

### 3️⃣ Running the Downloader

1. Open Command Prompt in the script folder  
2. Run:

```bash
python youtube_playlist_downloader_final_folders.py
```

3. Paste your **playlist URL**  
4. Choose **MP4 or MP3**  
5. Select **quality**  
6. Downloaded files will appear in **Videos/** or **Music/**  

---

### 4️⃣ Notes

- Press **Ctrl + C** to safely cancel downloads  
- Ensure FFmpeg is installed or in the `ffmpeg/bin` folder for MP4/MP3 conversion  
- Large playlists will show progress bars for each video/audio  

---

### 5️⃣ License

MIT License – free to use and modify  

---

### 6️⃣ Contact

Created by: nu11secur1ty
