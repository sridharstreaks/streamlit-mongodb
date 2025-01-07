import streamlit as st
import libtorrent as lt
import time
import os

from pathlib import Path

# Helper function to handle torrent streaming
def stream_torrent(magnet_link, save_path="downloads"):
    # Initialize a session
    ses = lt.session()
    ses.listen_on(6881, 6891)

    # Add the magnet link to the session
    params = {
        "save_path": save_path,
        "storage_mode": lt.storage_mode_t.storage_mode_allocate,
    }
    handle = lt.add_magnet_uri(ses, magnet_link, params)
    st.write("Downloading metadata...")

    # Wait until metadata is downloaded
    while not handle.has_metadata():
        time.sleep(1)
        st.write("Waiting for metadata...")

    # Retrieve video file info
    st.write("Metadata downloaded!")
    info = handle.get_torrent_info()
    files = info.files()
    file_paths = [f.path for f in files]

    # Find the largest video file (or let the user pick)
    video_files = [f for f in file_paths if f.endswith(('.mp4', '.mkv', '.avi'))]
    if not video_files:
        st.error("No video files found in this torrent.")
        return None

    st.write("Available video files:")
    selected_file = st.selectbox("Select a video file:", video_files)

    # Start downloading the video file
    st.write("Downloading video...")
    file_index = file_paths.index(selected_file)
    handle.prioritize_files([1 if i == file_index else 0 for i in range(len(file_paths))])

    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        st.write(f"Progress: {s.progress * 100:.2f}%")
        time.sleep(1)

    st.success("Download complete!")
    return Path(save_path) / selected_file


# Streamlit Web App
def main():
    st.title("Torrent Video Streaming App")
    
    # Input for Magnet Link
    magnet_link = st.text_input("Enter the Magnet Link:")
    if magnet_link:
        st.write("Processing...")
        
        # Temporary folder to save video
        save_path = "downloads"
        os.makedirs(save_path, exist_ok=True)
        
        # Start torrent streaming
        video_path = stream_torrent(magnet_link, save_path=save_path)
        
        # Stream video using streamlit-player
        if video_path:
            st.video(str(video_path))

if __name__ == "__main__":
    main()
