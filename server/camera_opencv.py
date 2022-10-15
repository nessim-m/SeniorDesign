import os

import cv2

from base_camera import BaseCamera

import threading


class CVThread(threading.Thread):
    '''''

    This class is used to process OpenCV's task of analyzing video frames in the background

    '''

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0

        super(CVThread, self).__init__(*args, **kwargs)

        self.__flag = threading.Event()

        self.__flag.clear()

    def mode(self, imgInput):
        '''''

        This method is used to pass in video frames that need to be processed

        '''

        self.imgCV = imgInput

        self.resume()

    def elementDraw(self, imgInput):
        '''''

        Draw elements on the screen

        '''

        return imgInput

    def doOpenCV(self, frame_image):
        '''''

        Add content to be processed by OpenCV here

        '''

        self.pause()

    def pause(self):
        '''''

        Block the thread and wait for the next frame to be processed

        '''

        self.__flag.clear()

        self.CVThreading = 0

    def resume(self):
        '''''

        Resuming the thread

        '''

        self.__flag.set()

    def run(self):
        '''''

        Processing video frames in a background thread

        '''

        while 1:
            self.__flag.wait()

        self.CVThreading = 1

        self.doOpenCV(self.imgCV)


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):

        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))

        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):

        Camera.video_source = source

    @staticmethod
    def frames():

        camera = cv2.VideoCapture(Camera.video_source)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        ''''' 

        Instantiate CVThread()

        '''

        cvt = CVThread()

        cvt.start()

        while True:

            # read current frame

            _, img = camera.read()

            if cvt.CVThreading:

                ''''' 

               If OpenCV is processing video frames, skip

                '''

                pass

            else:

                ''''' 

 If OpenCV is not processing video frames, give the thread that processes the video frame a new video frame and resume the processing thread

                '''

                cvt.mode(img)

                cvt.resume()

            ''''' 

            Draw elements on the screen 

            '''

            img = cvt.elementDraw(img)

            # encode as a jpeg image and return it

            yield cv2.imencode('.jpg', img)[1].tobytes()
