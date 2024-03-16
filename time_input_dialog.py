import tkinter.simpledialog
import tkinter as tk
from moviepy.editor import VideoFileClip
import os


class TimeInputDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent, title, video_paths):
        self.video_paths = video_paths
        self.video_durations = self.get_video_durations(video_paths)  # Fetch durations
        self.times = {}  # This will store the start and end times
        super().__init__(parent, title=title)

    def get_video_durations(self, video_paths):
        """Get the duration of each video."""
        durations = {}
        for path in video_paths:
            with VideoFileClip(path) as clip:
                durations[path] = clip.duration
        return durations

    def body(self, frame):
        tk.Label(frame, text="Video File").grid(row=0, column=0)
        tk.Label(frame, text="Start Time (s)").grid(row=0, column=1)
        tk.Label(frame, text="End Time (s)").grid(row=0, column=2)
        self.entries = []
        for i, path in enumerate(self.video_paths, start=1):
            tk.Label(frame, text=os.path.basename(path)).grid(row=i, column=0)

            # Prefill the start time with 0 and end time with video duration
            start_entry = tk.Entry(frame)
            start_entry.insert(0, "0")  # Default start time
            start_entry.grid(row=i, column=1)

            end_entry = tk.Entry(frame)
            end_time = str(int(self.video_durations.get(path, 0)))  # Default end time
            end_entry.insert(0, end_time)
            end_entry.grid(row=i, column=2)

            self.entries.append((start_entry, end_entry))
        return frame

    def apply(self):
        self.times = {
            path: {
                "start": float(start.get() if start.get() else 0),
                "end": float(end.get() if end.get() else self.video_durations[path]),
            }
            for path, (start, end) in zip(self.video_paths, self.entries)
        }
