import os
import shutil
from tkinter import Tk, filedialog, messagebox, Button, Label
from tkinter.ttk import Progressbar
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip
import threading

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.video_path = ""
        self.picture_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Video Frame Processor")
        self.root.geometry("500x300")
        
        Label(self.root, text="Video Frame Processor", font=("Arial", 16)).pack(pady=20)
        
        Button(self.root, text="Select Video", command=self.select_video).pack(pady=5)
        Button(self.root, text="Select Picture", command=self.select_picture).pack(pady=5)
        self.process_button = Button(self.root, text="Start Processing", command=self.start_processing, state="disabled")
        self.process_button.pack(pady=5)
        
        self.progress = Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=20)
        
    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="Select the original video file you wish to process")
        if self.video_path:
            self.process_button["state"] = "disabled"  # Disable processing until a picture is selected
            
    def select_picture(self):
        self.picture_path = filedialog.askopenfilename(title="Now, please select a picture for future processing steps")
        if self.picture_path and self.video_path:
            self.process_button["state"] = "normal"  # Enable processing once both files are selected
            
    def start_processing(self):
        self.process_button["state"] = "disabled"  # Prevent starting another process until the current one finishes
        threading.Thread(target=self.process_video).start()
        
    def clear_directory(self, directory: str) -> None:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    def process_video(self):
        frames_dir = "frames"
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        output_video_path = f"{video_name}_processed.mp4"
        self.clear_directory(frames_dir)
        self.split_video_into_frames(self.video_path, frames_dir)
        self.create_video_from_frames(frames_dir, output_video_path, self.video_path)
        messagebox.showinfo("Success", "Video processing completed successfully.")
        self.progress['value'] = 0  # Reset progress bar
        self.process_button["state"] = "normal"  # Re-enable the button

    def split_video_into_frames(self, video_path: str, output_dir: str) -> None:
        clip = VideoFileClip(video_path)
        total_frames = int(clip.fps * clip.duration)
        for i, frame in enumerate(clip.iter_frames()):
            frame_path = os.path.join(output_dir, f"frame_{i+1:05d}.jpg")
            clip.img = frame
            clip.save_frame(frame_path, t=i/clip.fps)
            self.progress['value'] = (i+1) / total_frames * 100
            self.root.update_idletasks()  # Update the progress bar

    def create_video_from_frames(self, frames_dir: str, output_video_path: str, original_video_path: str) -> None:
        frame_files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')])
        original_clip = VideoFileClip(original_video_path)
        fps = original_clip.fps
        clip = ImageSequenceClip(frame_files, fps=fps)
        
        if hasattr(original_clip, 'audio') and original_clip.audio is not None:
            original_audio = original_clip.audio
            clip = clip.set_audio(original_audio.subclip(0, clip.duration))
        
        clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

if __name__ == "__main__":
    root = Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
