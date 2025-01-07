import streamlit as st
import libtorrent as lt
import time
import threading
import os
from pathlib import Path
from flask import Flask, Response, send_file

# Flask app for streaming video
app = Flask(__name__)

# Global variable to store the selected video file path
video_file_path = None


# Function to stream video chunks
@app.route("/stream")
def stream_video():
    if video_file_path is None:
        return "No video selected", 404
    return send_file(video_file_path, mimetype="video/mp4")


def start_flask_app():
    app.run(host="0.0.0.0", port=8000)


# Helper function to handle torrent streaming
def stream_torrent(magnet_link, save_path="downloads"):
    global video_file_path
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

    # Start downloading the selected video file
    file_index = file_paths.index(selected_file)
    file_entry = files[file_index]

    st.write("Preparing to stream video...")
    file_offset = file_entry.offset
    file_size = file_entry.size

    piece_length = info.piece_length()
    first_piece = file_offset // piece_length
    last_piece = (file_offset + file_size) // piece_length

    # Prioritize pieces for the selected video file
    for i in range(first_piece, last_piece + 1):
        handle.piece_priority(i, 7)  # Set high priority for video pieces

    # Wait until enough buffer is available
    buffer_pieces = 10  # Number of pieces to buffer before playback
    while sum(1 for i in range(first_piece, first_piece + buffer_pieces) if handle.have_piece(i)) < buffer_pieces:
        s = handle.status()
        st.write(f"Buffering... {s.progress * 100:.2f}%")
        time.sleep(1)

    st.success("Buffering complete! Starting video stream...")
    video_file_path = Path(save_path) / selected_file
    return video_file_path


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

        # Stream video using an embedded HTML5 video player
        if video_path:
            st.markdown(
                f"""
                <video width="700" controls autoplay>
                    <source src="http://localhost:8000/stream" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                """,
                unsafe_allow_html=True,
            )


# Start Flask in a separate thread
flask_thread = threading.Thread(target=start_flask_app, daemon=True)
flask_thread.start()

if __name__ == "__main__":
    main()
