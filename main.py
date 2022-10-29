from threading import Thread
import cv2 as cv
import time
import queue


class VideoStreamWidget(object):
    def __init__(self, src=0):
        self.frames = queue.Queue()
        self.status = None
        self.capture = cv.VideoCapture(src)
        self.new_frame_time = time.monotonic_ns()
        self.prev_frame_time = 0
        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, raw) = self.capture.read()

                # approach1: transform to jpg format and reduce jpg quality
                encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 70]
                result, compressed = cv.imencode(".jpg", raw, encode_param)
                decoded_image = cv.imdecode(compressed, 1)

                # approach2: just reduce resolution
                # decoded_image = cv.resize(raw, (0, 0), fx=0.4, fy=0.4)

                self.frames.put(decoded_image)
            time.sleep(0.03)

    def show_frame(self, frame_rate=25):
        # Display frames in main program
        TIMEOUT = 1 / frame_rate
        if (time.monotonic_ns() - self.new_frame_time) > TIMEOUT * 10.0**9:
            frame = self.frames.get()
            if frame is not None:
                fps = 10.0**9 / (
                            self.new_frame_time - self.prev_frame_time) if self.new_frame_time - self.prev_frame_time > 0 else 0
                fps = str(fps)

                cv.putText(frame, fps, (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv.LINE_AA)
                cv.imshow('frame', frame)
                self.frames.task_done()
                self.prev_frame_time = self.new_frame_time
                self.new_frame_time = time.monotonic_ns()

        key = cv.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv.destroyAllWindows()
            exit(1)


if __name__ == '__main__':
    # video_stream_widget = VideoStreamWidget(src='HD-Colorbar.mp4')
    video_stream_widget = VideoStreamWidget()
    while True:
        try:
            video_stream_widget.show_frame()
        except AttributeError:
            pass


