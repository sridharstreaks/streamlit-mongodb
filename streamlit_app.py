import streamlit as st
import subprocess
import os
import tempfile
import time

def stream_torrent(torrent, torrent_type='magnet'):
    # Create a temporary directory to store the torrent files
    temp_dir = tempfile.mkdtemp()
    
    # Prepare the webtorrent command
    if torrent_type == 'magnet':
        command = ['webtorrent', torrent, '--out', temp_dir]
    else:
        command = ['webtorrent', torrent, '--out', temp_dir]

    # Start the webtorrent process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process, temp_dir

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
            process, temp_dir = stream_torrent(magnet_link, 'magnet')
            st.markdown('Streaming video...')
        else:
            st.error('Please enter a valid magnet link')

elif option == 'Torrent File':
    torrent_file = st.file_uploader('Upload Torrent File', type=['torrent'])
    if st.button('Stream Video'):
        if torrent_file:
            with open('temp.torrent', 'wb') as f:
                f.write(torrent_file.read())
            process, temp_dir = stream_torrent('temp.torrent', 'file')
            st.markdown('Streaming video...')
            os.remove('temp.torrent')
        else:
            st.error('Please upload a valid torrent file')

# Check if the video file is available to stream
if 'process' in locals():
    while True:
        try:
            video_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp4')]
            if video_files:
                video_path = os.path.join(temp_dir, video_files[0])
                st.markdown(generate_video_html(video_path), unsafe_allow_html=True)
                break
        except Exception as e:
            pass
        time.sleep(1)
