from threading import Thread
import queue
import av
from aiortc import VideoStreamTrack
import cv2 as cv
import time


class VideoFramesTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()  # don't forget this!
        self.frames = queue.Queue()
        self.capture = cv.VideoCapture(0)
        self.capture.set(cv.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (_, raw) = self.capture.read()
                i420 = cv.cvtColor(raw, cv.COLOR_BGR2YUV_I420)
                # self.frames.put(av.VideoFrame.from_ndarray(raw, format="bgr24"))
                frame = av.VideoFrame.from_ndarray(i420, format="yuv420p")
                reform_frame = frame.reformat(width=1280, height=720, format="yuv420p")
                self.frames.put(reform_frame)
            time.sleep(0.01)

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = self.frames.get()
        if frame:
            frame.pts = pts
            frame.time_base = time_base

            return frame
        else:
            return av.VideoFrame.from_ndarray([], format="yuv420p")
