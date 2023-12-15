from moviepy.editor import VideoFileClip
import whisper
from datetime import timedelta
import os
import shutil
import streamlit as st

def is_video_file(file_name):
    video_extensions = [".mp4", ".mov"]
    file_extension = os.path.splitext(file_name)[1]
    return file_extension in video_extensions

def transcribe_audio(path, srt_filename, txt_filename):
    model = whisper.load_model("base")  # Change this to your desired model
    print("Whisper model loaded.")
    transcribe = model.transcribe(audio=path)
    segments = transcribe['segments']

    with open(srt_filename, 'a', encoding='utf-8') as srtFile, open(txt_filename, 'a', encoding='utf-8') as txtFile:
        for segment in segments:
            startTime = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
            endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
            text = segment['text']
            segmentId = segment['id'] + 1
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
            srtFile.write(segment)
            txtFile.write(text + "\n")

def convert_mp4_to_wav(video_file_path, audio_file_path):
    video = VideoFileClip(video_file_path)
    video.audio.write_audiofile(audio_file_path, codec='pcm_s16le')

def main():
    st.title("Video & Audio Transcription")

    file = st.file_uploader("Upload your video or audio (MP4, WAV, MP3, MOV format)", type=["mp4", "wav", "mp3", "mov"])

    if file is not None:
        video_directory = './videos'
        audio_directory = './audios'
        srt_directory = './srtfiles'
        txt_directory = './textfiles'
        archive_directory = './archives'

        os.makedirs(video_directory, exist_ok=True)
        os.makedirs(audio_directory, exist_ok=True)
        os.makedirs(srt_directory, exist_ok=True)
        os.makedirs(txt_directory, exist_ok=True)
        os.makedirs(archive_directory, exist_ok=True)

        file_path = os.path.join(video_directory, file.name)
        audio_path = os.path.join(audio_directory, f"{os.path.splitext(file.name)[0]}.wav")
        srt_path = os.path.join(srt_directory, f"{os.path.splitext(file.name)[0]}.srt")
        txt_path = os.path.join(txt_directory, f"{os.path.splitext(file.name)[0]}.txt")

        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        if is_video_file(file.name):
            convert_mp4_to_wav(file_path, audio_path)
            audio_to_transcribe = audio_path
        else:
            audio_to_transcribe = file_path

        if not st.session_state.get(f"transcribed_{file.name}", False):
            with st.spinner("Transcript video to audio in progress ..."):
                transcribe_audio(audio_to_transcribe, srt_path, txt_path)
                st.session_state[f"transcribed_{file.name}"] = True

            shutil.move(file_path, os.path.join(archive_directory, file.name))
            st.success("The transcription was successfully completed.")

        try:
            srt_data = open(srt_path, "rb").read()
            st.download_button(
                label="Convert in SRT file",
                data=srt_data,
                file_name=f"{os.path.splitext(file.name)[0]}.srt",
                mime="application/x-subrip",
            )

            txt_data = open(txt_path, "rb").read()
            st.download_button(
                label="Convert in text file",
                data=txt_data,
                file_name=f"{os.path.splitext(file.name)[0]}.txt",
                mime="text/plain",
            )
        except Exception as e:
            st.error(f"Une erreur s'est produite: {e}")

if __name__ == '__main__':
    main()

