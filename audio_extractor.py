import os
import tkinter as tk
from tkinter import filedialog, messagebox, Button, Label
from moviepy.editor import VideoFileClip
from threading import Thread

class AudioExtractorApp:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.load_button = Button(self.parent, text="Load Video", command=self.load_video)
        self.load_button.pack(pady=10)

        self.extract_button = Button(self.parent, text="Extract Audio", command=self.extract_audio, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

        self.filename_label = Label(self.parent, text="No video loaded")
        self.filename_label.pack(pady=2)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)
            self.extract_button.config(state=tk.NORMAL)

            filename = os.path.basename(self.video_path)
            self.filename_label.config(text=f"Loaded: {filename}")

    def extract_audio(self):
        if self.video_path:
            save_path = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                     filetypes=[("MP3 files", "*.mp3")],
                                                     initialfile=os.path.splitext(os.path.basename(self.video_path))[0] + "_audio")
            if save_path:
                self.extract_button.config(state=tk.DISABLED)
                self.filename_label.config(text="Extracting audio... Please wait.")
                self.parent.update()

                extract_thread = Thread(target=self.start_extraction, args=(save_path,), daemon=True)
                extract_thread.start()

    def start_extraction(self, save_path):
        audio_clip = self.video_clip.audio
        audio_clip.write_audiofile(save_path)
        self.on_extraction_complete(save_path)

    def on_extraction_complete(self, save_path):
        self.parent.after(0, self.extract_button.config, {"state": tk.NORMAL})
        self.parent.after(0, self.filename_label.config, {"text": f"Audio extracted: {os.path.basename(save_path)}"})
        self.parent.after(0, messagebox.showinfo, "Success", "Audio extracted and saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioExtractorApp(root)
    root.mainloop()
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Button, Label
from moviepy.editor import VideoFileClip
from threading import Thread

class AudioExtractorApp:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.load_button = Button(self.parent, text="Load Video", command=self.load_video)
        self.load_button.pack(pady=10)

        self.extract_button = Button(self.parent, text="Extract Audio", command=self.extract_audio, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

        self.filename_label = Label(self.parent, text="No video loaded")
        self.filename_label.pack(pady=2)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)
            self.extract_button.config(state=tk.NORMAL)

            filename = os.path.basename(self.video_path)
            self.filename_label.config(text=f"Loaded: {filename}")

    def extract_audio(self):
        if self.video_path:
            save_path = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                     filetypes=[("MP3 files", "*.mp3")],
                                                     initialfile=os.path.splitext(os.path.basename(self.video_path))[0] + "_audio")
            if save_path:
                self.extract_button.config(state=tk.DISABLED)
                self.filename_label.config(text="Extracting audio... Please wait.")
                self.parent.update()

                extract_thread = Thread(target=self.start_extraction, args=(save_path,), daemon=True)
                extract_thread.start()

    def start_extraction(self, save_path):
        audio_clip = self.video_clip.audio
        audio_clip.write_audiofile(save_path)
        self.on_extraction_complete(save_path)

    def on_extraction_complete(self, save_path):
        self.parent.after(0, self.extract_button.config, {"state": tk.NORMAL})
        self.parent.after(0, self.filename_label.config, {"text": f"Audio extracted: {os.path.basename(save_path)}"})
        self.parent.after(0, messagebox.showinfo, "Success", "Audio extracted and saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioExtractorApp(root)
    root.mainloop()
