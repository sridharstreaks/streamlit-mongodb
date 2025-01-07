import libtorrent as lt
import time
import os
import tempfile
import streamlit as st

# Create a single session object
ses = lt.session()
ses.listen_on(6881, 6891)

# Function to handle torrent downloads
def download_torrent(ses, torrent_info, save_path):  # Accept session as argument
    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t(2),
        'ti': torrent_info
    }
    
    h = ses.add_torrent(params)
    s = h.status()

    st.text(f'Starting, saving to {save_path}')

    while not s.is_seeding:
        s = h.status()

        state_str = ['queued', 'checking', 'downloading metadata', \
                     'downloading', 'finished', 'seeding', 'allocating']
        st.text(f'\r{s.name}: {s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers}) {state_str[s.state]}')

        alerts = ses.pop_alerts()
        for a in alerts:
            if a.category() & lt.alert.category_t.error_notification:
                print(a)

        time.sleep(1)

    st.text("Download complete")

# Function to handle torrent streaming
def stream_torrent(ses, torrent_info, save_path):  # Accept session as argument
    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t(2),
        'ti': torrent_info,
        'flags': lt.torrent_flags_t.sequential_download
    }

    h = ses.add_torrent(params)
    s = h.status()
    
    st.text(f'Starting streaming, saving to {save_path}')

    # Wait for metadata to be available
    while (not s.has_metadata):
        time.sleep(0.1)
        s = h.status()
        
    # Get the largest file
    largest_file_index = -1
    largest_file_size = -1
    for i, f in enumerate(torrent_info.files()):
        if f.size > largest_file_size:
            largest_file_size = f.size
            largest_file_index = i

    # Prioritize pieces for streaming
    h.file_priority(largest_file_index, 7)
    num_pieces = torrent_info.num_pieces()

    # Start streaming after downloading sufficient initial pieces
    streamed = False
    while not streamed:
        s = h.status()
        state_str = ['queued', 'checking', 'downloading metadata', \
                     'downloading', 'finished', 'seeding', 'allocating']
        st.text(f'\r{s.name}: {s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers}) {state_str[s.state]}')

        alerts = ses.pop_alerts()
        for a in alerts:
            print(a)

        if s.num_pieces > num_pieces * 0.05:  # Example: 5% of pieces downloaded
            streamed = True
            file_path = os.path.join(save_path, torrent_info.files()[largest_file_index].path)
            st.video(file_path)
        time.sleep(1)

# Streamlit app
st.title('Torrent Stream/Download App')

# Handle file upload
uploaded_file = st.file_uploader("Choose a torrent file", type="torrent")
if uploaded_file is not None:
    e = lt.bdecode(uploaded_file.getvalue())
    torrent_info = lt.torrent_info(e)

# Handle magnet link input
magnet_link = st.text_input("Or paste a magnet link here")
if magnet_link:
    params = {
        'save_path': tempfile.mkdtemp(),  # Create temporary save path
        'storage_mode': lt.storage_mode_t(2)
    }
    h = ses.add_torrent(params, magnet_link)  # Use existing session here
    
    # Wait for metadata to be available
    while not h.has_metadata():
        time.sleep(0.1)
        s = h.status()
        st.text(f"Retrieving metadata: {s.name}")
    
    torrent_info = h.get_torrent_info()

# Choose between download or stream
option = st.radio("Choose an option:", ('Download', 'Stream'))

if option == 'Download' and uploaded_file is not None or magnet_link:
    save_path = st.text_input("Enter save path:", tempfile.gettempdir())
    if st.button('Start Download'):
        download_torrent(ses, torrent_info, save_path)  # Pass session object

elif option == 'Stream' and uploaded_file is not None or magnet_link:
    if st.button('Start Streaming'):
        save_path = tempfile.mkdtemp()  # Create temporary save path for streaming
        stream_torrent(ses, torrent_info, save_path)  # Pass session object
