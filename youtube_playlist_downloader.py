#!/usr/bin/python
# 2025-2026 by nu11secur1ty
# O's support Windows 10,11
import os
import shutil
import yt_dlp
from tqdm import tqdm
import time
import sys
import signal
import re

pbar = None  # Global progress bar

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def progress_hook(d):
    """Display progress bar for each file"""
    global pbar
    if d['status'] == 'downloading':
        if pbar is None:
            total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            filename = os.path.basename(d.get('filename', ''))
            if total_bytes > 0:
                pbar = tqdm(
                    total=total_bytes,
                    unit='B',
                    unit_scale=True,
                    desc=sanitize_filename(filename[:40]),  # Limit filename length
                    leave=False
                )
    elif d['status'] == 'finished':
        if pbar:
            pbar.close()
            pbar = None
            print(f"✅ Finished: {sanitize_filename(os.path.basename(d.get('filename', '')))}")
    elif d['status'] == 'error':
        if pbar:
            pbar.close()
            pbar = None
        print(f"❌ Error downloading: {d.get('filename', 'Unknown')}")

def detect_ffmpeg():
    """Check system or local ffmpeg"""
    # Check system PATH
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    
    # Check common locations
    local_paths = [
        os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.getcwd(), "ffmpeg.exe"),
        os.path.join(os.path.expanduser("~"), "ffmpeg", "bin", "ffmpeg.exe"),
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg"
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_video_format_choice():
    """Get video quality preference from user"""
    print("\n📺 Select video quality:")
    print("1. Best available")
    print("2. 1080p")
    print("3. 720p")
    print("4. 480p")
    print("5. 360p")
    print("6. 144p")
    
    choice = input("Enter choice (1-6): ").strip()
    
    mapping = {
        "1": "bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080]+bestaudio/best",
        "3": "bestvideo[height<=720]+bestaudio/best",
        "4": "bestvideo[height<=480]+bestaudio/best",
        "5": "bestvideo[height<=360]+bestaudio/best",
        "6": "bestvideo[height<=144]+bestaudio/best"
    }
    
    return mapping.get(choice, "bestvideo+bestaudio/best")

def get_audio_quality_choice():
    """Get audio quality preference from user"""
    print("\n🎵 Select audio quality:")
    print("1. Best available")
    print("2. 320kbps")
    print("3. 256kbps")
    print("4. 192kbps")
    print("5. 128kbps")
    
    choice = input("Enter choice (1-5): ").strip()
    
    mapping = {
        "1": "0",  # Best quality
        "2": "320",
        "3": "256",
        "4": "192",
        "5": "128"
    }
    
    return mapping.get(choice, "0")

def get_playlist_info(playlist_url):
    """Get playlist information without downloading"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in info:
                playlist_title = info.get('title', 'Unknown_Playlist')
                video_count = len(info['entries'])
                return playlist_title, video_count
            else:
                return "Unknown_Playlist", 1
    except Exception as e:
        print(f"⚠️ Could not get playlist info: {e}")
        return "Unknown_Playlist", 0

def download_playlist(playlist_url, download_type):
    """Main download function"""
    base_dir = os.getcwd()
    ffmpeg_path = detect_ffmpeg()

    # Check FFmpeg
    if not ffmpeg_path:
        print("❌ FFmpeg not found!")
        print("Please install FFmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt install ffmpeg")
        print("\nOr place ffmpeg.exe in one of these locations:")
        print("  - Current folder")
        print("  - ./ffmpeg/bin/ folder")
        sys.exit(1)
    else:
        print(f"✅ FFmpeg found: {ffmpeg_path}\n")

    # Get playlist info
    print("📋 Fetching playlist information...")
    playlist_title, video_count = get_playlist_info(playlist_url)
    print(f"📀 Playlist: {playlist_title}")
    print(f"🎬 Videos found: {video_count}\n")

    # Confirm download
    confirm = input(f"Download {video_count} videos? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Download cancelled.")
        sys.exit(0)

    # Decide folder and quality
    if download_type == "mp3":
        folder = os.path.join(base_dir, "Music", sanitize_filename(playlist_title))
        os.makedirs(folder, exist_ok=True)
        audio_quality = get_audio_quality_choice()
        print(f"\n🎵 Audio quality: {audio_quality}kbps")
    else:
        folder = os.path.join(base_dir, "Videos", sanitize_filename(playlist_title))
        os.makedirs(folder, exist_ok=True)
        video_format = get_video_format_choice()
        print(f"\n📹 Video format: {video_format}")

    print(f"📁 Save location: {folder}\n")
    print("🚀 Starting download...\n")

    # yt-dlp options
    if download_type == "mp3":
        ydl_opts = {
            "ffmpeg_location": ffmpeg_path,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder, "%(playlist_index)s - %(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": audio_quality,
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                }
            ],
            "quiet": True,
            "no_warnings": False,
            "ignoreerrors": True,  # Skip failed videos
            "extract_flat": False,
        }
    else:  # mp4
        ydl_opts = {
            "ffmpeg_location": ffmpeg_path,
            "format": video_format,
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(folder, "%(playlist_index)s - %(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": False,
            "ignoreerrors": True,  # Skip failed videos
            "extract_flat": False,
        }

    try:
        start_time = time.time()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        
        end_time = time.time()
        elapsed = end_time - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        print(f"\n⏱️ Total download time: {minutes}m {seconds}s")
        print(f"✅ All downloads complete!")
        
        # Show file count
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        print(f"📁 Saved {len(files)} files in: {folder}")
        
    except KeyboardInterrupt:
        if pbar:
            pbar.close()
        print("\n❌ Download interrupted by user. Exiting cleanly...\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def main():
    # Handle Ctrl+C globally
    def signal_handler(sig, frame):
        global pbar
        if pbar:
            pbar.close()
        print("\n❌ Download interrupted by user. Exiting cleanly...\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Clear screen and show banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 50)
    print("🎬 YouTube Playlist Downloader 🎧")
    print("=" * 50)
    print()
    
    # Get playlist URL
    playlist_url = input("📌 Enter playlist URL: ").strip()
    
    if not playlist_url:
        print("❌ No URL provided. Exiting...")
        sys.exit(0)

    print("\n📥 Choose download format:")
    print("1. MP4 (Video)")
    print("2. MP3 (Audio)")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice not in ["1", "2"]:
        print("❌ Invalid choice. Exiting...")
        sys.exit(0)

    download_type = "mp3" if choice == "2" else "mp4"
    
    print(f"\n🎯 Downloading playlist as {download_type.upper()}...\n")
    download_playlist(playlist_url, download_type)

if __name__ == "__main__":
    main()
