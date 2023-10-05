import pytube
import subprocess
import os
import sys

def download_audio(url, save_path):
    yt = pytube.YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()

    if audio_stream is None:
        audio_streams_dash = yt.streams.filter(type='audio', progressive=False)
        if audio_streams_dash:
            audio_stream = audio_streams_dash.first()

    if audio_stream is None:
        return None
    
    audio_file_path = audio_stream.download(output_path=save_path)
    return audio_file_path

def merge_audio_with_video(video_file, audio_file, output_path):
    subprocess.run(
        ['ffmpeg', '-hwaccel', 'cuda', '-i', video_file, '-i', audio_file, '-c', 'copy', '-map', '0', '-map', '1:a?', '-shortest', output_path],
        check=True
    )

def remove_file_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# Get command-line arguments
if len(sys.argv) < 3:
    print("Insufficient arguments. Please specify the video URL and format.")
    print("Usage example: python3 download_you.py https://www.youtube.com/watch?v=ozqhwa9K0gk 1080p MP4")
    sys.exit(1)

# Get video URL, resolution, and format
video_url = sys.argv[1]
resolution = sys.argv[2]
format = sys.argv[3] if len(sys.argv) > 3 else 'mp4'

# Set the file path for saving files
video_file_path = os.path.dirname(os.path.abspath(__file__))

# Download the audio file
audio_file_path = download_audio(video_url, video_file_path)

if audio_file_path:
    print(f'Audio file saved at: {audio_file_path}')
else:
    print('Failed to download the audio file.')

# Download the video file
yt = pytube.YouTube(video_url)
streams_dash = yt.streams.filter(progressive=False)
video_stream_dash = None
audio_stream_dash = None

for stream in streams_dash:
    if stream.resolution == resolution:
        if stream.type == 'video':
            video_stream_dash = stream
        elif stream.type == 'audio':
            audio_stream_dash = stream
        if video_stream_dash and audio_stream_dash:
            break

if video_stream_dash:
    video_file = video_stream_dash.download(output_path=video_file_path)
    print(f'Video file saved at: {video_file}')
else:
    print(f'Failed to find an available video stream with resolution {resolution}.')
    sys.exit(1)

# Merge audio and video if there's an audio file
if audio_file_path:
    output_path = os.path.join(video_file_path, f'output_{resolution}.{format}')
    merge_audio_with_video(video_file, audio_file_path, output_path)
    print(f'{format} file with added audio saved at: {output_path}')
else:
    output_path = video_file
    print(f'{format} file without audio added saved at: {output_path}')

# Delete original files (video and audio) if they were downloaded
remove_file_if_exists(video_file)
remove_file_if_exists(audio_file_path)

print('Program completed.')




