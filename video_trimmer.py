from tkinter import filedialog, messagebox, simpledialog, Button
from moviepy.editor import VideoFileClip

class VideoTrimmerApp:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        load_button = Button(self.parent, text="Load Video", command=self.load_video)
        load_button.pack(pady=10)

        trim_button = Button(self.parent, text="Trim Video", command=self.trim_video)
        trim_button.pack(pady=10)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)
            messagebox.showinfo("Success", "Video loaded successfully!")

    def trim_video(self):
        if hasattr(self, 'video_clip'):
            start_time = simpledialog.askfloat("Input", "Enter start time (seconds)", minvalue=0, maxvalue=self.video_clip.duration)
            end_time = simpledialog.askfloat("Input", "Enter end time (seconds)", minvalue=0, maxvalue=self.video_clip.duration)
            if start_time is not None and end_time is not None and start_time < end_time:
                trimmed_clip = self.video_clip.subclip(start_time, end_time)
                save_path = filedialog.asksaveasfilename(defaultextension=".mp4")
                if save_path:
                    trimmed_clip.write_videofile(save_path)
                    messagebox.showinfo("Success", "Video trimmed and saved successfully!")
            else:
                messagebox.showerror("Error", "Invalid start or end time.")
        else:
            messagebox.showerror("Error", "No video loaded.")
