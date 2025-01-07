import streamlit as st
import requests
import time
import os
import tempfile

def download_torrent_file(magnet_link):
    # Use webtorrent to download the video file from the magnet link
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, 'output.mp4')
        command = f"webtorrent '{magnet_link}' --out '{temp_dir}' --dl-select 0"
        os.system(command)
        return file_path

def generate_video_html(file_path):
    video_html = f"""
    <video width='100%' height='auto' controls>
        <source src='{file_path}' type='video/mp4'>
        Your browser does not support the video tag.
    </video>
    """
    return video_html

st.title('Torrent Video Streamer')

option = st.selectbox('Select Input Type', ['Magnet Link', 'Torrent File'])

if option == 'Magnet Link':
    magnet_link = st.text_input('Enter Magnet Link')
    if st.button('Stream Video'):
        if magnet_link:
            file_path = download_torrent_file(magnet_link)
            st.markdown('Streaming video...')
            st.markdown(generate_video_html(file_path), unsafe_allow_html=True)
        else:
            st.error('Please enter a valid magnet link')

elif option == 'Torrent File':
    torrent_file = st.file_uploader('Upload Torrent File', type=['torrent'])
    if st.button('Stream Video'):
        if torrent_file:
            with open('temp.torrent', 'wb') as f:
                f.write(torrent_file.read())
            file_path = download_torrent_file('temp.torrent')
            st.markdown('Streaming video...')
            st.markdown(generate_video_html(file_path), unsafe_allow_html=True)
            os.remove('temp.torrent')
        else:
            st.error('Please upload a valid torrent file')
