import os
import tkinter as tk
from tkinter import filedialog, messagebox, Label, Entry, Button
from moviepy.editor import VideoFileClip
from threading import Thread
from PIL import Image, ImageTk


class VideoTrimmerApp:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.load_button = Button(
            self.parent, text="Load Video", command=self.load_video
        )
        self.load_button.pack(pady=10)

        self.trim_button = Button(
            self.parent, text="Trim Video", command=self.trim_video, state=tk.DISABLED
        )
        self.trim_button.pack(pady=10)

        # Separate label for displaying the filename
        self.filename_label = Label(self.parent, text="No video loaded")
        self.filename_label.pack(pady=2)

        # Update the video label to display the video frame only
        self.video_label = Label(self.parent)
        self.video_label.pack(pady=10)

        self.start_time_label = Label(self.parent, text="Start time (seconds):")
        self.start_time_entry = Entry(self.parent)
        self.end_time_label = Label(self.parent, text="End time (seconds):")
        self.end_time_entry = Entry(self.parent)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)
            self.trim_button.config(state=tk.NORMAL)
            self.show_video_frame()
            self.show_time_inputs()

            # Extract filename from the path and display it in the filename label
            filename = os.path.basename(self.video_path)
            self.filename_label.config(text=f"Loaded: {filename}")

    def show_video_frame(self):
        # Display the first frame of the video
        frame = self.video_clip.get_frame(0)
        image = Image.fromarray(frame)
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.video_label.config(image=photo)
        self.video_label.image = photo  # Keep a reference!

    def show_time_inputs(self):
        self.start_time_label.pack()
        self.start_time_entry.pack()
        self.end_time_label.config(
            text=f"End time (seconds, max {self.video_clip.duration}):"
        )
        self.end_time_label.pack()
        self.end_time_entry.pack()

    def trim_video(self):
        start_time = float(self.start_time_entry.get())
        end_time = float(self.end_time_entry.get())
        if start_time < end_time <= self.video_clip.duration:
            file_name, file_extension = os.path.splitext(
                os.path.basename(self.video_path)
            )
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                initialfile=f"{file_name}_trimmed{file_extension}",
            )
            if save_path:
                # Disable the trim button to prevent multiple clicks
                self.trim_button.config(state=tk.DISABLED)
                self.filename_label.config(text="Trimming in progress... Please wait.")
                self.parent.update()

                # Start the trimming process in a separate thread
                trim_thread = Thread(
                    target=self.start_trim,
                    args=(start_time, end_time, save_path),
                    daemon=True,
                )
                trim_thread.start()
        else:
            messagebox.showerror("Error", "Invalid start or end time.")

    def start_trim(self, start_time, end_time, save_path):
        trimmed_clip = self.video_clip.subclip(start_time, end_time)
        trimmed_clip.write_videofile(save_path)
        self.on_trim_complete(save_path)

    def on_trim_complete(self, save_path):
        # This method will be called once trimming is complete
        # Use after to schedule the UI updates back on the main thread
        self.parent.after(0, self.trim_button.config, {"state": tk.NORMAL})
        self.parent.after(
            0,
            self.filename_label.config,
            {"text": f"Trimming completed: {os.path.basename(save_path)}"},
        )
        self.parent.after(
            0, messagebox.showinfo, "Success", "Video trimmed and saved successfully!"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTrimmerApp(root)
    root.mainloop()
