import streamlit as st
import libtorrent as lt
import time
import os

# Set up a directory for temporary storage
temp_dir = "temp_video"
os.makedirs(temp_dir, exist_ok=True)

# Initialize session state for libtorrent session and handle
if "torrent_session" not in st.session_state:
    st.session_state.torrent_session = lt.session()
    st.session_state.torrent_handle = None
    st.session_state.streaming = False  # To track if the video is being streamed

def start_torrent_stream(magnet_link, save_path):
    """Start streaming a torrent video."""
    ses = st.session_state.torrent_session
    ses.apply_settings({'listen_interfaces': '0.0.0.0:6881,[::]:6881'})
    params = lt.add_torrent_params()
    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t(2)
    params.url = magnet_link
    params.flags |= lt.torrent_flags.sequential_download  # Enable sequential download
    handle = ses.add_torrent(params)
    st.session_state.torrent_handle = handle
    st.write("Downloading Metadata...")
    while not handle.has_metadata():
        time.sleep(1)
    # Set priorities for the first few pieces (e.g., first 25%)
    torrent_info = handle.torrent_file()
    for i in range(min(25, torrent_info.num_pieces())):
        handle.piece_priority(i, 7)  # 7 = highest priority
    st.write("Metadata Imported, Starting Stream...")
    st.session_state.streaming = True  # Set streaming flag to True

def monitor_and_stream_video():
    """Monitor download progress and stream video."""
    handle = st.session_state.torrent_handle
    if handle is None:
        st.warning("No active stream. Start a new session.")
        return

    # Get the torrent info and save path
    torrent_info = handle.torrent_file()
    video_path = os.path.join(temp_dir, torrent_info.files().file_path(0))  # Get the first file in the torrent
    buffer_placeholder = st.empty()  # Placeholder for buffering message
    progress_placeholder = st.empty()  # Placeholder for progress information
    video_placeholder = st.empty()  # Placeholder for video playback

    buffer_threshold = torrent_info.total_size() * (5/100)  # Require at least 5% for buffer
    buffer_ready = False
    
    while st.session_state.streaming:
        s = handle.status()
        downloaded_bytes = s.total_done

        if not buffer_ready:
            if downloaded_bytes < buffer_threshold:
                buffer_placeholder.warning("Buffering... Please wait for more data to download.")
            else:
                buffer_placeholder.empty()
                buffer_ready = True
                # Start video playback once buffer is ready
                if os.path.exists(video_path) and os.path.isfile(video_path):
                    video_placeholder.video(video_path)

        # Update progress
        progress_placeholder.write(
            f"Progress: {s.progress * 100:.2f}% (Down: {s.download_rate / 1000:.1f} kB/s, Up: {s.upload_rate / 1000:.1f} kB/s"
            f", Seeds: {s.num_seeds}, Peers: {s.num_peers})"
        )

        if s.progress >= 1:  # Check if download is complete
            st.success("Full video download completed.")
            st.session_state.streaming = False
            break

        time.sleep(2)  # Reduce the polling frequency to avoid unnecessary reruns

# Streamlit UI
st.title("Stream Torrent Video")
magnet_link = st.text_input("Enter Magnet Link:")

if st.button("Start Stream") and magnet_link:
    st.write("Initializing stream...")
    start_torrent_stream(magnet_link, temp_dir)

if st.session_state.streaming:
    monitor_and_stream_video()

    # Optional cleanup button to remove temporary files
    if st.button("Reset"):
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        st.success("Temporary files cleared.")
        st.rerun
