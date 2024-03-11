import os
import shutil
from tkinter import (
    Tk,
    filedialog,
    messagebox,
    Button,
    Label,
    Scrollbar,
    Listbox,
    VERTICAL,
)
from tkinter.ttk import Progressbar
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip
import threading
from PIL import Image

import requests
import base64
import os
from typing import Dict, Any

from a1111_api import api_change_face


class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.video_paths = []
        self.picture_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Video Frame Processor")
        self.root.geometry("600x400")

        Label(self.root, text="Video Frame Processor", font=("Arial", 16)).pack(pady=20)

        Button(self.root, text="Select Videos", command=self.select_videos).pack(pady=5)
        self.videos_listbox = Listbox(self.root, height=4, width=50, exportselection=0)
        self.videos_listbox.pack(pady=5)

        Button(self.root, text="Select Picture", command=self.select_picture).pack(
            pady=5
        )
        self.picture_label = Label(self.root, text="", font=("Arial", 10))
        self.picture_label.pack(pady=5)

        self.process_button = Button(
            self.root,
            text="Start Processing",
            command=self.start_processing,
            state="disabled",
        )
        self.process_button.pack(pady=5)

        self.progress = Progressbar(
            self.root, orient="horizontal", length=200, mode="determinate"
        )
        self.progress.pack(pady=20)

        self.status_label = Label(self.root, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def select_videos(self):
        file_paths = filedialog.askopenfilenames(
            title="Select the original video files you wish to process"
        )
        self.video_paths = list(file_paths)
        self.update_videos_listbox()
        self.check_ready_to_process()

    def select_picture(self):
        self.picture_path = filedialog.askopenfilename(
            title="Now, please select a picture for future processing steps"
        )
        if self.picture_path:
            self.picture_label.config(text=os.path.basename(self.picture_path))
        self.check_ready_to_process()

    def update_videos_listbox(self):
        self.videos_listbox.delete(0, "end")
        for path in self.video_paths:
            self.videos_listbox.insert("end", os.path.basename(path))

    def check_ready_to_process(self):
        if self.video_paths and self.picture_path:
            self.process_button["state"] = "normal"
        else:
            self.process_button["state"] = "disabled"

    def start_processing(self):
        self.process_button["state"] = "disabled"
        threading.Thread(target=self.process_videos).start()

    def edit_frames(self, input_dir: str, output_dir: str) -> None:
        """

        Parameters:
        - input_dir: Directory containing the input frames.
        - output_dir: Directory where the processed frames will be saved.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        frames = [f for f in os.listdir(input_dir) if f.endswith(".jpg")]
        total_frames = len(frames)
        for i, frame_file in enumerate(frames, start=1):
            full_frame_path = os.path.join(input_dir, frame_file)

            api_change_face(full_frame_path, self.picture_path)

            self.status_label.config(text=f"Editing frame {i}/{total_frames}")
            self.root.update_idletasks()  # Ensure the UI updates are reflected immediately

    def process_videos(self):
        total_videos = len(self.video_paths)
        for i, video_path in enumerate(self.video_paths, start=1):
            self.status_label.config(text=f"Processing video {i}/{total_videos}")
            self.process_video(video_path)
        messagebox.showinfo("Success", "All videos processed successfully.")
        self.progress["value"] = 0
        self.status_label.config(text="")
        self.process_button["state"] = "normal"

    def process_video(self, video_path):
        frames_dir = "frames"
        edited_frames_dir = "edited_frames"  # Directory for black and white frames
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_video_path = f"{video_name}_processed.mp4"
        self.clear_directory(frames_dir)
        self.clear_directory(edited_frames_dir)  # Ensure the directory is ready
        self.split_video_into_frames(video_path, frames_dir)
        self.edit_frames(frames_dir, edited_frames_dir)
        self.create_video_from_frames(
            edited_frames_dir, output_video_path, video_path
        )  # Use the edited frames

    def clear_directory(self, directory: str) -> None:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    def split_video_into_frames(self, video_path: str, output_dir: str) -> None:
        clip = VideoFileClip(video_path)
        total_frames = int(clip.fps * clip.duration)
        for i, frame in enumerate(clip.iter_frames()):
            frame_path = os.path.join(output_dir, f"frame_{i+1:05d}.jpg")
            clip.img = frame
            clip.save_frame(frame_path, t=i / clip.fps)
            self.progress["value"] = (i + 1) / total_frames * 100
            self.root.update_idletasks()  # Update the progress bar
            # Update the status label with frame processing status
            self.status_label.config(
                text=f"Splitting frame {i+1}/{total_frames} of {os.path.basename(video_path)}"
            )
            self.root.update_idletasks()  # Ensure the UI updates are reflected immediately

    def create_video_from_frames(
        self, frames_dir: str, output_video_path: str, original_video_path: str
    ) -> None:
        frame_files = sorted(
            [
                os.path.join(frames_dir, f)
                for f in os.listdir(frames_dir)
                if f.endswith(".jpg")
            ]
        )
        original_clip = VideoFileClip(original_video_path)
        fps = original_clip.fps
        clip = ImageSequenceClip(frame_files, fps=fps)

        if hasattr(original_clip, "audio") and original_clip.audio is not None:
            original_audio = original_clip.audio
            clip = clip.set_audio(original_audio.subclip(0, clip.duration))

        clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    root = Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
