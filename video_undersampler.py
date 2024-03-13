import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from moviepy.editor import VideoFileClip
from threading import Thread
from pathlib import Path


class UnderSamplerApp:
    def __init__(self, parent):
        self.parent = parent
        self.selected_videos = []
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.parent, text="Video UnderSampler", font=("Arial", 16)).pack(
            pady=20
        )

        input_frame = tk.Frame(self.parent)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Target FPS:", font=("Arial", 12)).pack(
            side=tk.LEFT, padx=5
        )

        self.fps_entry = tk.Entry(input_frame, width=10)
        self.fps_entry.pack(side=tk.LEFT, padx=5)
        self.fps_entry.insert(0, "24")  # Default value

        self.select_button = tk.Button(
            input_frame, text="Select Videos", command=self.select_videos
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.convert_button = tk.Button(
            input_frame,
            text="Convert",
            command=self.initiate_conversion,
            state="disabled",
        )
        self.convert_button.pack(side=tk.RIGHT, padx=5)

        # Display selected video filenames
        self.video_list = scrolledtext.ScrolledText(self.parent, height=4, width=50)
        self.video_list.pack(pady=10, padx=10, fill="x")
        self.video_list.configure(font=("Arial", 10), state="disabled")

        # Label for displaying the name of the video being processed
        self.current_video_label = tk.Label(self.parent, text="", font=("Arial", 10))
        self.current_video_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(
            self.parent, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

    def select_videos(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Videos",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")),
        )
        if file_paths:
            self.selected_videos = file_paths
            self.update_video_list()
            self.convert_button["state"] = "normal"

    def update_video_list(self):
        self.video_list.configure(state="normal")
        self.video_list.delete("1.0", tk.END)
        for video in self.selected_videos:
            self.video_list.insert(tk.END, f"{Path(video).name}\n")
        self.video_list.configure(state="disabled")

    def initiate_conversion(self):
        try:
            target_fps = int(self.fps_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid FPS value.")
            return

        self.start_processing(self.selected_videos, target_fps)


    def start_processing(self, videos, target_fps):
        total_videos = len(videos)
        self.progress_bar["maximum"] = 100
        self.convert_button["state"] = "disabled"  # Disable the convert button to prevent multiple clicks
        thread = Thread(
            target=self.process_videos,
            args=(
                videos,
                target_fps,
                lambda n: self.update_progress_bar(n, total_videos),
            ),
            daemon=True,
        )
        thread.start()
        self.progress_bar.after(100, lambda: self.check_thread(thread))


    def process_videos(self, videos, target_fps, progress_callback):
        for i, video_path in enumerate(videos):
            video_name = Path(video_path).name
            # Update the label to show the name of the current video being processed
            self.current_video_label.configure(text=f"Processing: {video_name}")
            try:
                clip = VideoFileClip(video_path)
                target_fps = max(1, target_fps)
                new_clip = clip.set_fps(target_fps).set_audio(clip.audio)
                output_path = Path(video_path).with_name(
                    Path(video_path).stem + f"_undersampled_{target_fps}fps.mp4"
                )
                new_clip.write_videofile(
                    str(output_path), codec="libx264", audio_codec="aac"
                )
            except Exception as e:
                print(f"Error processing {video_path}: {e}")
            finally:
                progress_callback(i + 1)

    def update_progress_bar(self, n_processed, total):
        progress = int((n_processed / total) * 100)
        self.progress_bar["value"] = progress
        self.progress_bar.update_idletasks()

    def check_thread(self, thread):
        if thread.is_alive():
            self.parent.after(100, lambda: self.check_thread(thread))
        else:
            self.on_processing_complete()
            self.progress_bar["value"] = 0


    def on_processing_complete(self):
        self.convert_button["state"] = "normal"  # Re-enable the convert button
        messagebox.showinfo("Processing Complete", "All videos have been processed.")
        self.progress_bar["value"] = 0  # Reset the progress bar
        self.current_video_label.configure(text="")  # Clear the current video name label

if __name__ == "__main__":
    root = tk.Tk()
    app = UnderSamplerApp(root)
    root.mainloop()
