from PIL import Image, ImageTk
import tkinter as tk
import threading
import time
import cv2


def seticon(root: tk.Wm, path: str) -> None:
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)

    root.wm_iconphoto(False, image)  # type: ignore


def replace_options(
    option_menu: tk.OptionMenu, variable: tk.StringVar, new_options: list[str]
):
    option_menu["menu"].delete(0, "end")

    for option in new_options:
        option_menu["menu"].add_command(
            label=option, command=lambda value=option: variable.set(value)
        )

    variable.set(new_options[0])


class VideoPlayer(tk.Canvas):
    def __init__(
        self, master: tk.Misc, video_path: str, target_width: int, target_height: int
    ) -> None:
        # super init later

        self.target_width = target_width
        self.target_height = target_height
        self.video_path = video_path

        self.running = True

        self.video = cv2.VideoCapture(video_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1 / self.fps

        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        super().__init__(master, width=self.width, height=self.height)

    def start(self) -> None:
        threading.Thread(target=self.update_frame).start()

    def reset_video(self) -> None:
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def update_frame(self) -> None:
        while True:
            frame_loaded, frame = self.video.read()
            if frame_loaded:
                # Convert frame from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert frame to PhotoImage
                image = Image.fromarray(frame).resize(
                    (self.target_width, self.target_height)
                )
                photo = ImageTk.PhotoImage(image)

                # Update canvas
                self.create_image(0, 0, image=photo, anchor=tk.NW)
                self.photo = photo  # Keep a reference

                # Control frame rate
                time.sleep(self.frame_delay)
            else:
                self.reset_video()

    def __del__(self) -> None:
        if self.video.isOpened():
            self.video.release()
