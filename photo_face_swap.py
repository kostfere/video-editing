import os
import shutil
from tkinter import filedialog, messagebox, Button, Label, Listbox, Tk
import threading
import tkinter as tk

from a1111_api import (
    api_change_face,
)


class PhotoProcessorApp:
    def __init__(self, parent):
        self.parent = parent  # Use the parent frame
        self.photo_paths = []
        self.picture_path = ""
        self.setup_ui()

    def setup_ui(self):
        Label(self.parent, text="Face Swap for Photos", font=("Arial", 16)).pack(
            pady=20
        )

        Button(self.parent, text="Select Photos", command=self.select_photos).pack(
            pady=5
        )
        self.photos_listbox = Listbox(
            self.parent, height=4, width=50, exportselection=0
        )
        self.photos_listbox.pack(pady=5)

        Button(self.parent, text="Select Picture", command=self.select_picture).pack(
            pady=5
        )
        self.picture_label = Label(self.parent, text="", font=("Arial", 10))
        self.picture_label.pack(pady=5)

        self.process_button = Button(
            self.parent,
            text="Start Processing",
            command=self.start_processing,
            state="disabled",
        )
        self.process_button.pack(pady=5)

        # Log display
        Label(self.parent, text="Process Log", font=("Arial", 12)).pack(pady=5)
        self.log_listbox = Listbox(self.parent, height=10, width=120)
        self.log_listbox.pack(pady=5)

    def select_photos(self):
        file_paths = filedialog.askopenfilenames(
            title="Select photos for face swapping"
        )
        self.photo_paths = list(file_paths)
        self.update_photos_listbox()
        self.check_ready_to_process()

    def select_picture(self):
        self.picture_path = filedialog.askopenfilename(
            title="Select a picture for face swapping"
        )
        if self.picture_path:
            self.picture_label.config(text=os.path.basename(self.picture_path))
        self.check_ready_to_process()

    def update_photos_listbox(self):
        self.photos_listbox.delete(0, "end")
        for path in self.photo_paths:
            self.photos_listbox.insert("end", os.path.basename(path))

    def check_ready_to_process(self):
        if self.photo_paths and self.picture_path:
            self.process_button["state"] = "normal"
        else:
            self.process_button["state"] = "disabled"

    def start_processing(self):
        self.process_button["state"] = "disabled"
        self.clear_process_log()
        threading.Thread(target=self.process_photos).start()

    def process_photos(self):
        # Ensure the content directory exists
        content_dir = "content"
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)

        edited_frames_dir = "edited_frames"
        if not os.path.exists(edited_frames_dir):
            os.makedirs(edited_frames_dir)

        for photo_path in self.photo_paths:
            self.log_listbox.insert(
                tk.END, f"Processing {os.path.basename(photo_path)}..."
            )
            self.parent.update_idletasks()  # Ensure the UI updates are reflected immediately

            # Call the API to process and save the photo in edited_frames directory
            api_change_face(photo_path, self.picture_path)

            # Generate the new file name with _processed suffix
            new_file_name = (
                os.path.splitext(os.path.basename(photo_path))[0] + "_processed.jpg"
            )
            processed_file_path = os.path.join(
                edited_frames_dir, os.path.basename(photo_path)
            )  # The path in edited_frames
            content_file_path = os.path.join(
                content_dir, new_file_name
            )  # The new path in content directory

            # Move the processed file to the content directory with the new name
            shutil.move(processed_file_path, content_file_path)

            self.log_listbox.insert(
                tk.END, f"Finished processing {os.path.basename(photo_path)}"
            )
            self.log_listbox.yview(tk.END)

        # Delete the edited_frames directory after processing is complete
        if os.path.exists(edited_frames_dir):
            shutil.rmtree(edited_frames_dir)

        messagebox.showinfo("Success", "All photos processed successfully.")
        self.process_button["state"] = "normal"


if __name__ == "__main__":
    root = Tk()
    app = PhotoProcessorApp(root)
    root.mainloop()
