import streamlit as st
import libtorrent as lt
import os
import time
import tempfile
from threading import Thread

def download_torrent_sequentially(magnet_link, torrent_file, file_ready_callback):
    """
    Download the torrent sequentially and trigger the callback once enough pieces are ready.
    """
    session = lt.session()
    session.listen_on(6881, 6891)

    params = {
        'save_path': tempfile.mkdtemp(),
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }

    # Add the torrent (magnet link or file)
    if magnet_link:
        handle = lt.add_magnet_uri(session, magnet_link, params)
    elif torrent_file:
        info = lt.torrent_info(torrent_file)
        handle = session.add_torrent({'save_path': params['save_path']})

    # Enable sequential downloading
    handle.set_sequential_download(True)

    # Wait until metadata is downloaded
    st.write("Downloading metadata...")
    while not handle.has_metadata():
        time.sleep(1)

    torrent_info = handle.get_torrent_info()
    files = torrent_info.files()
    file_path = os.path.join(params['save_path'], files[0].path)

    st.write("Starting sequential download...")
    while handle.status().state != lt.torrent_status.seeding:
        status = handle.status()
        progress = status.progress * 100
        st.progress(progress / 100)

        # Trigger the callback if enough pieces are downloaded
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            file_ready_callback(file_path)

        time.sleep(1)

    return file_path

def stream_video(file_path):
    """
    Stream the video file in Streamlit.
    """
    st.video(file_path)

def main():
    st.title("Torrent Video Streaming App")

    # Input options for magnet link or torrent file
    magnet_link = st.text_input("Enter Magnet Link:")
    torrent_file = st.file_uploader("Upload Torrent File", type=['torrent'])

    # Video path placeholder
    video_path_placeholder = st.empty()

    if st.button("Start Streaming"):
        if not magnet_link and not torrent_file:
            st.error("Please provide either a magnet link or upload a torrent file.")
            return

        def file_ready_callback(file_path):
            """
            Callback to update the video path once enough pieces are ready.
            """
            video_path_placeholder.video(file_path)

        # Start the sequential download in a separate thread
        download_thread = Thread(
            target=download_torrent_sequentially, 
            args=(magnet_link, torrent_file, file_ready_callback)
        )
        download_thread.start()

if __name__ == "__main__":
    main()
