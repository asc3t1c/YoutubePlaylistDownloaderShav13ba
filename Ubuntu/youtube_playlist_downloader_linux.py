#!/usr/bin/python
# 2025 by nu11secur1ty
# O's support Ubuntu

import os
import shutil
import yt_dlp
from tqdm import tqdm
import time
import sys
import signal

pbar = None  # Global progress bar

def progress_hook(d):
    """Display progress bar for each file"""
    global pbar
    if d['status'] == 'downloading':
        if pbar is None:
            total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            filename = os.path.basename(d.get('filename', ''))
            pbar = tqdm(total=total_bytes, unit='B', unit_scale=True,
                        desc=filename, leave=True)
        else:
            bytes_downloaded = d.get('downloaded_bytes', 0)
            pbar.n = bytes_downloaded
            pbar.refresh()
    elif d['status'] == 'finished':
        if pbar:
            pbar.n = pbar.total
            pbar.close()
            pbar = None
            print(f"✅ Finished: {os.path.basename(d.get('filename', ''))}\n")

def detect_ffmpeg():
    """Check if ffmpeg is installed"""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)
    print("⚠️  FFmpeg not found! Install it with:")
    print("   sudo apt install ffmpeg   (Debian/Ubuntu)")
    print("   sudo dnf install ffmpeg   (Fedora)")
    print("   sudo pacman -S ffmpeg     (Arch)")
    sys.exit(1)

def get_video_format_choice():
    print("\nSelect video quality:")
    print("1. Best available")
    print("2. 1080p")
    print("3. 720p")
    print("4. 480p")
    print("5. 360p")
    choice = input("Enter choice (1-5): ").strip()
    mapping = {
        "1": "bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080]+bestaudio/best",
        "3": "bestvideo[height<=720]+bestaudio/best",
        "4": "bestvideo[height<=480]+bestaudio/best",
        "5": "bestvideo[height<=360]+bestaudio/best"
    }
    return mapping.get(choice, "bestvideo+bestaudio/best")

def get_audio_quality_choice():
    print("\nSelect audio quality:")
    print("1. Best available")
    print("2. 192kbps")
    print("3. 128kbps")
    choice = input("Enter choice (1-3): ").strip()
    mapping = {
        "1": "best",
        "2": "192",
        "3": "128"
    }
    return mapping.get(choice, "best")

def download_playlist(playlist_url, download_type):
    base_dir = os.getcwd()
    ffmpeg_path = detect_ffmpeg()

    if download_type == "mp3":
        folder = os.path.join(base_dir, "Music")
        os.makedirs(folder, exist_ok=True)
        audio_quality = get_audio_quality_choice()
        ydl_opts = {
            "ffmpeg_location": ffmpeg_path,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder, "%(playlist_title)s - %(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": audio_quality,
                }
            ],
            "quiet": True,
        }
    else:
        folder = os.path.join(base_dir, "Videos")
        os.makedirs(folder, exist_ok=True)
        video_format = get_video_format_choice()
        ydl_opts = {
            "ffmpeg_location": ffmpeg_path,
            "format": video_format,
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(folder, "%(playlist_title)s - %(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            start_time = time.time()
            ydl.download([playlist_url])
            end_time = time.time()
            print(f"\n⏱️ Total time: {round(end_time - start_time, 2)} seconds\n")
    except KeyboardInterrupt:
        if pbar:
            pbar.close()
        print("\n❌ Download interrupted by user. Exiting cleanly...\n")
        sys.exit(0)

def main():
    # Handle Ctrl+C globally
    def signal_handler(sig, frame):
        global pbar
        if pbar:
            pbar.close()
        print("\n❌ Download interrupted by user. Exiting cleanly...\n")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print("🐧 YouTube Playlist Downloader (Linux Edition)")
    playlist_url = input("Enter the playlist URL: ").strip()

    print("\nChoose download format:")
    print("1. MP4 (Video)")
    print("2. MP3 (Audio)")
    choice = input("Enter choice (1 or 2): ").strip()

    download_type = "mp3" if choice == "2" else "mp4"
    print(f"\n📥 Downloading playlist as {download_type.upper()} ...\n")
    download_playlist(playlist_url, download_type)
    print("\n✅ All downloads complete!\n")

if __name__ == "__main__":
    main()
