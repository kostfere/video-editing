import os
from tkinter import filedialog, messagebox, Button, Label, Entry, Tk, Frame
from moviepy.editor import VideoFileClip
import tkinter as tk

class VideoTrimmerAppSingle:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = ""  # Changed to a single video path
        self.setup_ui()

    def setup_ui(self):
        Label(self.parent, text="Video Trimmer (Single Video)", font=("Arial", 16)).pack(pady=20)

        Button(self.parent, text="Select Video", command=self.select_video).pack(pady=5)
        self.video_label = Label(self.parent, text="No video selected", font=("Arial", 10))
        self.video_label.pack(pady=5)

        # Frame for start and end timestamp inputs
        self.timestamp_frame = Frame(self.parent)
        self.timestamp_frame.pack(pady=5)
        Label(self.timestamp_frame, text="Start timestamp (s):").pack(side=tk.LEFT)
        self.start_timestamp_entry = Entry(self.timestamp_frame, width=10)
        self.start_timestamp_entry.pack(side=tk.LEFT, padx=5)
        Label(self.timestamp_frame, text="End timestamp (s):").pack(side=tk.LEFT)
        self.end_timestamp_entry = Entry(self.timestamp_frame, width=10)
        self.end_timestamp_entry.pack(side=tk.LEFT, padx=5)

        self.preview_button = Button(self.parent, text="Preview Trim", command=self.preview_trim, state="disabled")
        self.preview_button.pack(pady=5)

        self.save_button = Button(self.parent, text="Save Trimmed Video", command=self.save_trimmed_video, state="disabled")
        self.save_button.pack(pady=5)

    def select_video(self):
        file_path = filedialog.askopenfilename(title="Select a video for trimming")
        if file_path:
            self.video_path = file_path
            self.video_label.config(text=os.path.basename(self.video_path))
            self.preview_button["state"] = "normal"
            self.save_button["state"] = "disabled"  # Initially disable save until a preview has been made

    def get_trim_clip(self):
        start = float(self.start_timestamp_entry.get())
        end = float(self.end_timestamp_entry.get())
        clip = VideoFileClip(self.video_path).subclip(start, end)
        return clip

    def preview_trim(self):
        if not self.video_path or not self.start_timestamp_entry.get() or not self.end_timestamp_entry.get():
            messagebox.showerror("Error", "Please select a video and specify both start and end timestamps.")
            return
        try:
            clip = self.get_trim_clip()
            clip.preview()
            self.save_button["state"] = "normal"  # Enable save button after preview
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def save_trimmed_video(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 file", "*.mp4")])
        if output_path:
            clip = self.get_trim_clip()
            clip.write_videofile(output_path)
            messagebox.showinfo("Success", "Trimmed video saved successfully.")

if __name__ == "__main__":
    root = Tk()
    app = VideoTrimmerAppSingle(root)
    root.mainloop()
