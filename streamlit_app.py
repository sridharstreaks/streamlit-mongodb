import streamlit as st
from aiotorrent import Torrent
import asyncio
import tempfile

async def stream_torrent(torrent_file):
    torrent = Torrent(torrent_file)
    await torrent.init()
    await torrent.stream(torrent.files[0])

def main():
    st.title("Stream Video Torrents with aiotorrent")
    
    torrent_file = st.file_uploader("Upload Torrent File", type=["torrent"])
    
    if torrent_file is not None:
        temp_torrent_file = tempfile.NamedTemporaryFile(delete=False)
        temp_torrent_file.write(torrent_file.read())
        temp_torrent_file.close()
        
        st.write("Streaming video torrent...")
        asyncio.run(stream_torrent(temp_torrent_file.name))

if __name__ == "__main__":
    main()
