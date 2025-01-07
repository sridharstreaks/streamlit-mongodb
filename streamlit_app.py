import os
import libtorrent as lt
import time
import tempfile
import streamlit as st

def add_torrent(handle, magnet_or_file, save_path):
    # Create a torrent session
    session = lt.session()
    session.listen_on(6881, 6891)
    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True,
    }

    # Handle magnet links or torrent files
    if magnet_or_file.startswith("magnet:"):
        params['url'] = magnet_or_file
    else:
        info = lt.torrent_info(magnet_or_file)
        params['ti'] = info

    return session.add_torrent(params), session


def download_torrent(torrent_handle, session, status_callback=None, sequential_download=False):
    torrent_handle.set_sequential_download(sequential_download)

    while not torrent_handle.status().is_seeding:
        status = torrent_handle.status()
        if status_callback:
            status_callback(status)
        time.sleep(1)


def stream_video(torrent_handle, save_path):
    # Wait until sufficient pieces are downloaded
    while True:
        status = torrent_handle.status()
        if status.progress > 0.05:  # Begin streaming after 5% completion
            video_file = os.path.join(save_path, torrent_handle.name())
            st.video(video_file)
            break
        time.sleep(1)


def main():
    st.title("Torrent Video Streamer and Downloader")
    
    input_type = st.radio("Select Input Type:", ["Magnet Link", "Torrent File"])
    save_path = st.text_input("Enter Save Path:", value=tempfile.gettempdir())
    magnet_or_file = None

    if input_type == "Magnet Link":
        magnet_or_file = st.text_input("Enter Magnet Link:")
    else:
        torrent_file = st.file_uploader("Upload Torrent File:")
        if torrent_file:
            magnet_or_file = torrent_file.name
            with open(magnet_or_file, "wb") as f:
                f.write(torrent_file.getvalue())

    mode = st.radio("Select Mode:", ["Download", "Stream"])
    if st.button("Start"):
        if magnet_or_file:
            torrent_handle, session = add_torrent(magnet_or_file, save_path)
            
            def show_status(status):
                st.write(f"Filename: {status.name}")
                st.write(f"Download Speed: {status.download_rate / 1000:.2f} KB/s")
                st.write(f"Upload Speed: {status.upload_rate / 1000:.2f} KB/s")
                st.write(f"Peers: {status.num_peers}")
                st.write(f"Seeds: {status.num_seeds}")
                st.write(f"Progress: {status.progress * 100:.2f}%")
                st.write(f"Total Size: {status.total_wanted / (1024 ** 2):.2f} MB")
                st.write("---")

            if mode == "Download":
                download_torrent(torrent_handle, session, status_callback=show_status)
                st.success("Download completed!")
            elif mode == "Stream":
                download_torrent(torrent_handle, session, status_callback=show_status, sequential_download=True)
                stream_video(torrent_handle, save_path)
        else:
            st.error("Please provide a valid input.")

if __name__ == '__main__':
    main()
