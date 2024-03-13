import tkinter as tk
from tkinter import filedialog, messagebox, Label, Entry, Button
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk

class VideoTrimmerApp:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.load_button = Button(self.parent, text="Load Video", command=self.load_video)
        self.load_button.pack(pady=10)

        self.trim_button = Button(self.parent, text="Trim Video", command=self.trim_video, state=tk.DISABLED)
        self.trim_button.pack(pady=10)

        self.video_label = Label(self.parent, text="No video loaded")
        self.video_label.pack(pady=10)

        self.start_time_label = Label(self.parent, text="Start time (seconds):")
        self.start_time_entry = Entry(self.parent)
        self.end_time_label = Label(self.parent, text="End time (seconds):")
        self.end_time_entry = Entry(self.parent)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)
            messagebox.showinfo("Success", "Video loaded successfully!")
            self.trim_button.config(state=tk.NORMAL)
            self.show_video_frame()
            self.show_time_inputs()

    def show_video_frame(self):
        # Display the first frame of the video
        frame = self.video_clip.get_frame(0)
        image = Image.fromarray(frame)
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Keep a reference!

    def show_time_inputs(self):
        self.start_time_label.pack()
        self.start_time_entry.pack()
        self.end_time_label.config(text=f"End time (seconds, max {self.video_clip.duration}):")
        self.end_time_label.pack()
        self.end_time_entry.pack()

    def trim_video(self):
        start_time = float(self.start_time_entry.get())
        end_time = float(self.end_time_entry.get())
        if start_time < end_time <= self.video_clip.duration:
            trimmed_clip = self.video_clip.subclip(start_time, end_time)
            save_path = filedialog.asksaveasfilename(defaultextension=".mp4")
            if save_path:
                trimmed_clip.write_videofile(save_path)
                messagebox.showinfo("Success", "Video trimmed and saved successfully!")
        else:
            messagebox.showerror("Error", "Invalid start or end time.")
