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
from importlib import import_module
import os
from flask import Flask, render_template, Response

from camera_opencv import Camera

HOST = '192.168.1.139'  # Standard loopback interface address (localhost)
PORT = 5001  # Port to listen on (non-privileged ports are > 1023)

dataFromClient = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            # conn.sendall(b"hi!!?")
            data = conn.recv(1024)
            print(data)
            if not data:
                break
            dataFromClient = data.decode('utf-8')
            if 'start' in dataFromClient:
                print('its here-----')
                app = Flask(__name__)
            # print('sending data recieved back...')
            conn.sendall(data)
            break


# def start():
#     camera = Camera()


def gen(camera):
    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'

               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def video_feed():
    return Response(gen(Camera()),

                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
