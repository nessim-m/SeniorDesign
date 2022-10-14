import switch
import numpy as np
import os
import cv2
import threading
from base_camera import BaseCamera


class CVThread(threading.Thread):
    font = cv2.FONT_HERSHEY_SIMPLEX
    kalman_filter_X = Kalman_filter.Kalman_filter(0.01, 0.1)
    kalman_filter_Y = Kalman_filter.Kalman_filter(0.01, 0.1)
    cameraDiagonalW = 64
    cameraDiagonalH = 48
    videoW = 640
    videoH = 480

class Camera(BaseCamera):
    video_source = 0
    modeSelect = 'none'

    # modeSelect = 'findlineCV'
    # modeSelect = 'findColor'
    # modeSelect = 'watchDog'

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        HUE_1 = invarH + 15
        HUE_2 = invarH - 15
        if HUE_1 > 180: HUE_1 = 180
        if HUE_2 < 0: HUE_2 = 0

        SAT_1 = invarS + 150
        SAT_2 = invarS - 150
        if SAT_1 > 255: SAT_1 = 255
        if SAT_2 < 0: SAT_2 = 0

        VAL_1 = invarV + 150
        VAL_2 = invarV - 150
        if VAL_1 > 255: VAL_1 = 255
        if VAL_2 < 0: VAL_2 = 0

        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d' % (HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d' % (HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def linePosSet_1(self, invar):
        global linePos_1
        linePos_1 = invar

    def linePosSet_2(self, invar):
        global linePos_2
        linePos_2 = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        global mark
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        cvt = CVThread()
        cvt.start()

        while True:
            # read current frame
            _, img = camera.read()

            if Camera.modeSelect == 'none':
                switch.switch(1, 0)
                cvt.pause()
            else:
                if cvt.CVThreading:
                    pass
                else:
                    cvt.mode(Camera.modeSelect, img)
                    cvt.resume()
                img = cvt.elementDraw(img)

            # encode as a jpeg image and return it
            if cv2.imencode('.jpg', img)[0]:
                yield cv2.imencode('.jpg', img)[1].tobytes()

            # Reduce the amount of long video transmission.
            # if cv2.imencode('.jpg', img)[0] :
            #     mark = mark + 1
            #     if (mark % 2) == 0:
            #         if mark >=1000:
            #             mark = 0
            #         yield cv2.imencode('.jpg', img)[1].tobytes()
