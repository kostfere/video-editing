from video_face_swap import VideoProcessorApp
from photo_face_swap import PhotoProcessorApp
from video_undersampler import UnderSamplerApp
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

        # Tab for PhotoProcessorApp
        tab2_frame = ttk.Frame(tab_control)
        tab_control.add(tab2_frame, text="Face Swap for Photos")
        self.photo_face_swap_app = PhotoProcessorApp(tab2_frame)

        # Tab for UnderSamplerApp
        tab3_frame = ttk.Frame(tab_control)
        tab_control.add(tab3_frame, text="Video Undersampler")
        self.undersampler_app = UnderSamplerApp(tab3_frame)

        # # Tab for VideoTrimmerApp
        # tab4_frame = ttk.Frame(tab_control)
        # tab_control.add(tab4_frame, text="Video Trimmer")
        # self.video_trimmer_app = VideoTrimmerApp(tab4_frame)

        tab_control.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()
