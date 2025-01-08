import streamlit as st
import libtorrent as lt
import os
import time
import tempfile
import subprocess

def download_torrent(magnet_link, torrent_file):
    """
    Download the torrent content using libtorrent and return the downloaded file path.
    """
    session = lt.session()
    session.listen_on(6881, 6891)
    params = {
        'save_path': tempfile.mkdtemp(),
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
    }

    if magnet_link:
        handle = lt.add_magnet_uri(session, magnet_link, params)
    elif torrent_file:
        info = lt.torrent_info(torrent_file)
        handle = session.add_torrent({'save_path': params['save_path']})

    st.write("Downloading torrent...")
    while not handle.has_metadata():
        time.sleep(1)

    while handle.status().state != lt.torrent_status.seeding:
        status = handle.status()
        progress = status.progress * 100
        st.progress(progress / 100)
        time.sleep(1)

    files = handle.get_torrent_info().files()
    file_path = os.path.join(params['save_path'], files[0].path)
    return file_path

def stream_video(video_path):
    """
    Stream the video file in Streamlit.
    """
    st.video(video_path)

def main():
    st.title("Torrent Video Streaming App")
    
    # Input options for magnet link or torrent file
    magnet_link = st.text_input("Enter Magnet Link:")
    torrent_file = st.file_uploader("Upload Torrent File", type=['torrent'])

    if st.button("Start Streaming"):
        if not magnet_link and not torrent_file:
            st.error("Please provide either a magnet link or upload a torrent file.")
            return
        
        with st.spinner("Downloading torrent..."):
            file_path = download_torrent(magnet_link, torrent_file)
            st.success("Download complete!")

        # Check if the downloaded file is a video
        if not file_path.endswith(('.mp4', '.mkv', '.avi')):
            st.error("The downloaded file is not a supported video format.")
            return
        
        st.info(f"Streaming: {os.path.basename(file_path)}")
        stream_video(file_path)

if __name__ == "__main__":
    main()
