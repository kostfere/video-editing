import os
import shutil
from tkinter import filedialog, messagebox, Button, Label, Listbox, ttk
from moviepy.editor import VideoFileClip, ImageSequenceClip
import threading
from a1111_api import api_change_face
import time
import tkinter as tk


class VideoProcessorApp:
    def __init__(self, parent):
        self.parent = parent  # Use the parent frame from the tab
        self.face_restorer = tk.StringVar(value="None")
        self.video_paths = []
        self.picture_path = ""
        self.setup_ui()

    def setup_ui(self):

        Label(self.parent, text="Face Swap For Videos", font=("Arial", 16)).pack(
            pady=20
        )

        Button(self.parent, text="Select Videos", command=self.select_videos).pack(
            pady=5
        )
        self.videos_listbox = Listbox(
            self.parent, height=4, width=50, exportselection=0
        )
        self.videos_listbox.pack(pady=5)

        Button(self.parent, text="Select Picture", command=self.select_picture).pack(
            pady=5
        )
        self.picture_label = Label(self.parent, text="", font=("Arial", 10))
        self.picture_label.pack(pady=5)

        Label(self.parent, text="Select Face Restorer:", font=("Arial", 10)).pack(
            pady=5
        )
        face_restorer_options = ["None", "GFPGAN", "CodeFormer"]
        face_restorer_dropdown = ttk.Combobox(
            self.parent,
            textvariable=self.face_restorer,
            values=face_restorer_options,
            state="readonly",
        )
        face_restorer_dropdown.pack(pady=5)

        self.process_button = Button(
            self.parent,
            text="Start Processing",
            command=self.start_processing,
            state="disabled",
        )
        self.process_button.pack(pady=5)

        self.status_label = Label(self.parent, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Add a Listbox to display processing times
        Label(self.parent, text="Process Log", font=("Arial", 12)).pack(pady=5)
        self.log_listbox = Listbox(self.parent, height=10, width=120)
        self.log_listbox.pack(pady=5)

    def select_videos(self):
        file_paths = filedialog.askopenfilenames(
            title="Select the original video files you wish to process"
        )
        self.video_paths = list(file_paths)
        self.update_videos_listbox()
        self.check_ready_to_process()

    def select_picture(self):
        self.picture_path = filedialog.askopenfilename(
            title="Now, please select a picture for face swapping"
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
        self.clear_process_log()  # Clear the process log before starting
        threading.Thread(target=self.process_videos).start()

    def clear_process_log(self):
        self.log_listbox.delete(0, tk.END)  # Clear all entries in the log listbox

    def edit_frames(self, input_dir: str, output_dir: str, video_path: str) -> None:
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

            api_change_face(
                full_frame_path,
                self.picture_path,
                face_restorer=self.face_restorer.get(),
            )

            self.status_label.config(
                text=f"Editing frame {i}/{total_frames} of {os.path.basename(video_path)}"
            )
            self.parent.update_idletasks()  # Ensure the UI updates are reflected immediately

    def process_videos(self):
        total_videos = len(self.video_paths)
        for i, video_path in enumerate(self.video_paths, start=1):
            self.status_label.config(text=f"Processing video {i}/{total_videos}")
            self.process_video(video_path)
        messagebox.showinfo("Success", "All videos processed successfully.")
        self.status_label.config(text="")
        self.process_button["state"] = "normal"

        # After processing, automatically delete the frames and edited_frames directories
        self.delete_directory("frames")
        self.delete_directory("edited_frames")

    def delete_directory(self, directory: str) -> None:
        """Delete the specified directory."""
        if os.path.exists(directory):
            shutil.rmtree(directory)

    def process_video(self, video_path):
        start_time_overall = time.time()  # Start time for the entire process

        frames_dir = "frames"
        edited_frames_dir = "edited_frames"
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # Extract the picture name without its file extension
        picture_name = os.path.splitext(os.path.basename(self.picture_path))[0]

        # Updated output video path to include the picture name for face swapping
        output_video_path = f"content/{video_name}_{picture_name}.mp4"

        # Clear directories
        start_time = time.time()
        self.clear_directory(frames_dir)
        self.clear_directory(edited_frames_dir)
        self.display_time("Clear directories", start_time, video_name)

        # Split video into frames
        start_time = time.time()
        self.split_video_into_frames(video_path, frames_dir)
        self.display_time("Split video into frames", start_time, video_name)

        # Edit frames
        start_time = time.time()
        self.edit_frames(frames_dir, edited_frames_dir, video_path)
        self.display_time("Edit frames", start_time, video_name)

        # Create video from frames
        start_time = time.time()
        self.create_video_from_frames(edited_frames_dir, output_video_path, video_path)
        self.display_time("Create video from frames", start_time, video_name)

        self.display_time("Total processing time", start_time_overall, video_path)
        self.log_listbox.insert(tk.END, "-" * 60)

    def display_time(self, task_name: str, start_time: float, video_name: str) -> None:
        elapsed_time = time.time() - start_time
        message = f"[{video_name}] {task_name} took {elapsed_time:.2f} seconds"
        print(message)  # Continue to print to the console if desired

        # Log the message in the UI Listbox
        self.log_listbox.insert(tk.END, message)
        # self.log_listbox.insert(tk.END, "-" * 60)
        self.log_listbox.yview(tk.END)

    def clear_directory(self, directory: str) -> None:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    def split_video_into_frames(self, video_path: str, output_dir: str) -> None:
        clip = VideoFileClip(video_path)
        total_frames = int(clip.fps * clip.duration) + 1
        for i, frame in enumerate(clip.iter_frames()):
            frame_path = os.path.join(output_dir, f"frame_{i+1:05d}.jpg")
            clip.img = frame
            clip.save_frame(frame_path, t=i / clip.fps)

            # Update the status label with frame processing status
            self.status_label.config(
                text=f"Splitting frame {i+1}/{total_frames} of {os.path.basename(video_path)}"
            )
            self.parent.update_idletasks()  # Ensure the UI updates are reflected immediately

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
            clip = clip.set_audio(
                original_audio.subclip(0, min(clip.duration, original_audio.duration))
            )
        output_dir = os.path.dirname(output_video_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    root = Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
