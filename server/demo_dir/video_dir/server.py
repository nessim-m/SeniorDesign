# import socket
# import os
#
# HOST = '192.168.1.139'  # Standard loopback interface address (localhost)
# PORT = 5000     # Port to listen on (non-privileged ports are > 1023)
#
# dataFromClient = ""
#
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             #conn.sendall(b"hi!!?")
#             data = conn.recv(1024)
#             print(data)
#             if not data:
#                 break
#             dataFromClient = data.decode('utf-8')
#             #print('sending data recieved back...')
#             conn.sendall(data)
#             break
#
# os.system(f"{dataFromClient}")

import socket
from importlib import import_module
import os
from flask import Flask, render_template, Response, send_from_directory
from flask_cors import *
# import camera driver

from camera_opencv import Camera
import threading

HOST = '192.168.1.139'  # Standard loopback interface address (localhost)
PORT = 5001     # Port to listen on (non-privileged ports are > 1023)

dataFromClient = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            #conn.sendall(b"hi!!?")
            data = conn.recv(1024)
            print(data)
            if not data:
                break
            dataFromClient = data.decode('utf-8')
            if (dataFromClient ==  'start'):
                start()
            #print('sending data recieved back...')
            conn.sendall(data)
            break

def start():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    camera = Camera()

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/api/img/<path:filename>')
def sendimg(filename):
    return send_from_directory(dir_path+'/dist/img', filename)

@app.route('/js/<path:filename>')
def sendjs(filename):
    return send_from_directory(dir_path+'/dist/js', filename)

@app.route('/css/<path:filename>')
def sendcss(filename):
    return send_from_directory(dir_path+'/dist/css', filename)

@app.route('/api/img/icon/<path:filename>')
def sendicon(filename):
    return send_from_directory(dir_path+'/dist/img/icon', filename)

@app.route('/fonts/<path:filename>')
def sendfonts(filename):
    return send_from_directory(dir_path+'/dist/fonts', filename)

@app.route('/<path:filename>')
def sendgen(filename):
    return send_from_directory(dir_path+'/dist', filename)

@app.route('/')
def index():
    return send_from_directory(dir_path+'/dist', 'index.html')

class webapp:
    def __init__(self):
        self.camera = camera

    def modeselect(self, modeInput):
        Camera.modeSelect = modeInput

    def colorFindSet(self, H, S, V):
        camera.colorFindSet(H, S, V)

    def thread(self):
        app.run(host='0.0.0.0', threaded=True)

    def startthread(self):
        fps_threading=threading.Thread(target=self.thread)         #Define a thread for FPV and OpenCV
        fps_threading.setDaemon(False)                             #'True' means it is a front thread,it would close when the mainloop() closes
        fps_threading.start()