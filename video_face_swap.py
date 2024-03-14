import os
import shutil
from tkinter import filedialog, messagebox, Button, Label, Listbox, ttk, Scale, Label
from moviepy.editor import VideoFileClip, ImageSequenceClip
import threading
from a1111_api import api_change_face
import time
import tkinter as tk


class VideoProcessorApp:
    def __init__(self, parent):
        self.parent = parent  # Use the parent frame from the tab
        self.face_restorer = tk.StringVar(value="None")
        self.desired_fps_var = tk.IntVar(value=12)
        self.video_paths = []
        self.picture_paths = []
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

        # FPS Input
        Label(self.parent, text="Desired FPS (1-60):", font=("Arial", 12)).pack(pady=5)
        self.desired_fps_var = tk.IntVar(value=12)  # Default FPS value
        self.desired_fps_spinbox = tk.Spinbox(
            self.parent, from_=1, to=60, textvariable=self.desired_fps_var, wrap=True
        )
        self.desired_fps_spinbox.pack(pady=5)

        Button(self.parent, text="Select Pictures", command=self.select_picture).pack(
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

        # CodeFormer weight selection
        Label(self.parent, text="CodeFormer Weight:", font=("Arial", 10)).pack(pady=5)
        self.codeformer_weight_scale = Scale(
            self.parent,
            from_=0,
            to=1,
            resolution=0.01,
            orient="horizontal",
            label="1 = Max Effect",
        )
        self.codeformer_weight_scale.set(0.5)  # Default value
        self.codeformer_weight_scale.pack(pady=5)

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
        file_paths = (
            filedialog.askopenfilenames(  # Changed to allow multiple file selection
                title="Now, please select pictures for face swapping"
            )
        )
        self.picture_paths = list(file_paths)  # Update to store multiple paths
        if self.picture_paths:
            selected_files = ", ".join(
                [os.path.basename(path) for path in self.picture_paths]
            )
            self.picture_label.config(
                text=selected_files
            )  # Update label to show selected files
        self.check_ready_to_process()

    def update_videos_listbox(self):
        self.videos_listbox.delete(0, "end")
        for path in self.video_paths:
            self.videos_listbox.insert("end", os.path.basename(path))

    def check_ready_to_process(self):
        if self.video_paths and self.picture_paths:
            self.process_button["state"] = "normal"
        else:
            self.process_button["state"] = "disabled"

    def start_processing(self):
        self.process_button["state"] = "disabled"
        self.clear_process_log()  # Clear the process log before starting
        threading.Thread(target=self.process_videos).start()

    def clear_process_log(self):
        self.log_listbox.delete(0, tk.END)  # Clear all entries in the log listbox

    def edit_frames(
        self, input_dir: str, output_dir: str, video_path: str, picture_path: str
    ) -> None:
        """

        Parameters:
        - input_dir: Directory containing the input frames.
        - output_dir: Directory where the processed frames will be saved.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        frames = [f for f in os.listdir(input_dir) if f.endswith(".jpg")]
        total_frames = len(frames)
        start_time = time.time()  # Start time for the entire process
        for i, frame_file in enumerate(frames, start=1):
            full_frame_path = os.path.join(input_dir, frame_file)

            api_change_face(
                full_frame_path,
                picture_path,
                face_restorer=self.face_restorer.get(),
                codeformer_weight_scale=self.codeformer_weight_scale.get(),
            )

            progress = (i / total_frames) * 100
            elapsed_time = time.time() - start_time
            self.status_label.config(
                text=f"Editing frame {i}/{total_frames} of {os.path.basename(video_path)} "
                f"with picture: {os.path.basename(picture_path)} - {progress:.2f}% complete"
                f" - Elapsed time: {elapsed_time:.2f} seconds"
            )
            self.parent.update_idletasks()  # Ensure the UI updates are reflected immediately

    def process_videos(self):
        start_time = time.time()
        for video_path in self.video_paths:
            for picture_path in self.picture_paths:
                self.status_label.config(
                    text=f"Processing video: {os.path.basename(video_path)} "
                    f"with picture: {os.path.basename(picture_path)}"
                )
                self.process_video(video_path, picture_path)

        # After processing, automatically delete the frames and edited_frames directories
        self.delete_directory("frames")
        self.delete_directory("edited_frames")

        end_time = time.time()  # End time after the function execution
        execution_time = end_time - start_time  # Calculate the execution time

        self.log_listbox.insert(
            "end", f"Execution time for process_videos: {execution_time} seconds"
        )
        self.log_listbox.see("end")  # Auto-scroll to the end of the listbox

        messagebox.showinfo(
            "Success", "All video and picture combinations processed successfully."
        )
        self.status_label.config(text="")
        self.process_button["state"] = "normal"

    def delete_directory(self, directory: str) -> None:
        """Delete the specified directory."""
        if os.path.exists(directory):
            shutil.rmtree(directory)

    def process_video(self, video_path, picture_path: str):
        start_time_overall = time.time()  # Start time for the entire process

        frames_dir = "frames"
        edited_frames_dir = "edited_frames"
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # Extract the picture name without its file extension
        picture_name = os.path.splitext(os.path.basename(picture_path))[0]

        # Updated output video path to include the picture name for face swapping
        output_video_path = (
            f"content/{video_name}_{picture_name}"
            f"_fps{self.desired_fps_var.get()}"
            f"_FR{self.face_restorer.get()}"
            f"_CF_weight{self.face_restorer.get()}.mp4"
        )

        # Clear directories
        start_time = time.time()
        self.clear_directory(frames_dir)
        self.clear_directory(edited_frames_dir)
        self.display_time("Clear directories", start_time, video_name)

        # Split video into frames
        start_time = time.time()
        self.split_video_into_frames(video_path, frames_dir, self.desired_fps_var.get())
        self.display_time("Split video into frames", start_time, video_name)

        # Edit frames
        start_time = time.time()
        self.edit_frames(frames_dir, edited_frames_dir, video_path, picture_path)
        self.display_time("Edit frames", start_time, video_name)

        # Create video from frames
        start_time = time.time()
        self.create_video_from_frames(
            edited_frames_dir, output_video_path, video_path, self.desired_fps_var.get()
        )
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

    def split_video_into_frames(
        self, video_path: str, output_dir: str, desired_fps: int
    ) -> None:
        clip = VideoFileClip(video_path)
        actual_fps = clip.fps

        # Ensure desired FPS is within the valid range and adjust if necessary
        desired_fps = max(1, min(desired_fps, actual_fps))

        frame_extraction_interval = int(actual_fps / desired_fps)
        # Calculate the total number of frames that will be extracted
        total_extracted_frames = int((clip.duration * actual_fps) / frame_extraction_interval) + 1

        extracted_frame_count = 0  # Initialize the count of extracted frames

        for i, frame in enumerate(clip.iter_frames()):
            if i % frame_extraction_interval == 0:
                extracted_frame_count += 1  # Increment the extracted frame count
                frame_path = os.path.join(output_dir, f"frame_{extracted_frame_count:05d}.jpg")
                # No need to set clip.img = frame; directly save the frame using save_frame
                clip.save_frame(frame_path, t=i / actual_fps)

                # Update the status label with frame processing status
                percentage = (extracted_frame_count / total_extracted_frames) * 100
                self.status_label.config(
                    text=f"Splitting frame {extracted_frame_count} of {os.path.basename(video_path)}. "
                    f"(estimated extracted frames: {total_extracted_frames}) - {percentage:.2f}% complete"
                )
                self.parent.update_idletasks()


    def create_video_from_frames(
        self,
        frames_dir: str,
        output_video_path: str,
        original_video_path: str,
        user_selected_fps: int,
    ) -> None:
        import os
        from moviepy.editor import ImageSequenceClip, VideoFileClip

        # Retrieve the sorted list of frame files
        frame_files = sorted(
            [
                os.path.join(frames_dir, f)
                for f in os.listdir(frames_dir)
                if f.endswith(".jpg")
            ]
        )

        # Load the original clip to get its FPS and duration
        original_clip = VideoFileClip(original_video_path)
        original_fps = original_clip.fps
        original_duration = original_clip.duration

        # If you want to maintain the duration of the original video, calculate the new FPS
        # based on the total number of frames and the original video's duration.
        # This ensures that the duration of the video created from the frames matches the original duration.
        total_frame_files = len(frame_files)
        if total_frame_files > 0 and original_duration > 0:
            # Calculate the new FPS to maintain the original video duration
            new_fps = total_frame_files / original_duration
        else:
            # Fallback to original FPS or user-selected FPS if calculation is not feasible
            new_fps = min(user_selected_fps, original_fps)

        # Create a clip from the sequence of frames with the calculated FPS
        clip = ImageSequenceClip(frame_files, fps=new_fps)

        # Check if the original video has audio and add it to the new clip
        if original_clip.audio is not None:
            clip = clip.set_audio(original_clip.audio)

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_video_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the video file with the specified codecs
        clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")



if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
