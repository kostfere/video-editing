from video_face_swap import VideoProcessorApp
from audio_extractor import AudioExtractorApp
from video_trimmer import VideoTrimmerApp

# from video_trimmer import VideoTrimmerApp
import tkinter as tk
from tkinter import (
    ttk,
)


class CombinedApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Video Processing Application")
        self.root.geometry("800x600")

        tab_control = ttk.Notebook(self.root)

        # Tab for VideoProcessorApp
        tab1_frame = ttk.Frame(tab_control)
        tab_control.add(tab1_frame, text="Face Swap for Videos")
        self.face_swap_app = VideoProcessorApp(tab1_frame)

        # Tab for VideoTrimmerApp
        tab4_frame = ttk.Frame(tab_control)
        tab_control.add(tab4_frame, text="Video Trimmer")
        self.video_trimmer_app = VideoTrimmerApp(tab4_frame)

        # Tab for VideoTrimmerApp
        tab2_frame = ttk.Frame(tab_control)
        tab_control.add(tab2_frame, text="Audio Extractor")
        self.audio_extractor_app = AudioExtractorApp(tab2_frame)

        tab_control.pack(expand=1, fill="both")



if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()
