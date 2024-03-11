import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
from moviepy.editor import VideoFileClip
from threading import Thread
from pathlib import Path

def process_videos(videos, target_fps, progress_callback):
    for i, video_path in enumerate(videos):
        try:
            clip = VideoFileClip(video_path)
            target_fps = max(1, target_fps)
            new_clip = clip.set_fps(target_fps).set_audio(clip.audio)
            output_path = Path(video_path).with_name(Path(video_path).stem + f"_undersampled_{target_fps}fps.mp4")
            new_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
        except Exception as e:
            print(f"Error processing {video_path}: {e}")
        finally:
            progress_callback(i + 1)

def update_progress_bar(n_processed, total, progress_bar):
    progress = int((n_processed / total) * 100)
    progress_bar['value'] = progress
    progress_bar.update_idletasks()

def on_processing_complete():
    messagebox.showinfo("Processing Complete", "All videos have been processed.")

def start_processing(videos, target_fps, progress_bar):
    total_videos = len(videos)
    progress_bar['maximum'] = 100
    thread = Thread(target=process_videos, args=(videos, target_fps, lambda n: update_progress_bar(n, total_videos, progress_bar)), daemon=True)
    thread.start()
    progress_bar.after(100, check_thread, thread)

def check_thread(thread):
    if thread.is_alive():
        root.after(100, check_thread, thread)
    else:
        on_processing_complete()
        progress_bar['value'] = 0

def select_videos():
    file_paths = filedialog.askopenfilenames(title="Select Videos", filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
    if not file_paths:
        return
    target_fps = simpledialog.askinteger("Input", "Enter the desired FPS:", minvalue=1, maxvalue=60)
    if target_fps is not None:
        start_processing(file_paths, target_fps, progress_bar)

root = tk.Tk()
root.title("Video Undersampler")

frame = tk.Frame(root)
frame.pack(pady=20)

select_button = tk.Button(frame, text="Select Videos and Set FPS", command=select_videos)
select_button.pack(side=tk.TOP, fill=tk.X, expand=True)

progress_bar = ttk.Progressbar(frame, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(side=tk.TOP, pady=10)

root.mainloop()
