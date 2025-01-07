import streamlit as st
from aiotorrent import Torrent
import asyncio
import tempfile

async def stream_torrent(torrent_file, st):
    torrent = Torrent(torrent_file)
    await torrent.init()
    
    file_to_stream = torrent.files[0]
    st.write(f"Streaming file: {file_to_stream.name}")
    
    async def fetch_status():
        while True:
            st.write("Connection Status:")
            st.write(f"Number of Seeds: {torrent.num_seeds}")
            st.write(f"Number of Peers: {torrent.num_peers}")
            st.write(f"Upload Speed: {torrent.upload_speed} KB/s")
            st.write(f"Download Speed: {torrent.download_speed} KB/s")
            await asyncio.sleep(2)
    
    status_task = asyncio.create_task(fetch_status())
    await torrent.stream(file_to_stream)
    status_task.cancel()
    
    return "video_stream_file.mp4"

def main():
    st.title("Stream Video Torrents with aiotorrent")
    
    torrent_file = st.file_uploader("Upload Torrent File", type=["torrent"])
    
    if torrent_file is not None:
        temp_torrent_file = tempfile.NamedTemporaryFile(delete=False)
        temp_torrent_file.write(torrent_file.read())
        temp_torrent_file.close()
        
        st.write("Streaming video torrent...")
        stream_url = asyncio.run(stream_torrent(temp_torrent_file.name, st))
        
        # Display video using st.video with minimal buffering
        st.video(stream_url, format="video/mp4", start_time=0)

if __name__ == "__main__":
    main()
