import time
import threading
import os

import robotLight
import switch
import socket

# websocket
import asyncio
import websockets

import json
import app

OLED_connection = 1

try:
    import OLED

    screen = OLED.OLED_ctrl()
    screen.start()
    screen.screen_show(1, 'ADEEPT.COM')
except:
    OLED_connection = 0
    print('OLED disconnected')
    pass

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")


def update_code():
    # Update local to be consistent with remote
    projectPath = thisPath[:-7]
    with open(f'{projectPath}/config.json', 'r') as f1:
        config = json.load(f1)
        if not config['production']:
            print('Update code')
            # Force overwriting local code
            if os.system(f'cd {projectPath} && sudo git fetch --all && sudo git reset --hard origin/master && sudo git pull') == 0:
                print('Update successfully')
                print('Restarting...')
                os.system('sudo reboot')


def wifi_check():
    global mark_test
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        update_code()
        if OLED_connection:
            screen.screen_show(2, 'IP:' + ipaddr_check)
            screen.screen_show(3, 'AP MODE OFF')
        mark_test = 1  # 如果小车曾经连接网络成功了，标志为1
    except:
        if mark_test == 1:
            mark_test = 0
            move.destroy()  # motor stop.

        ap_threading = threading.Thread(target=ap_thread)  # Define a thread for data receiving
        ap_threading.setDaemon(True)  # 'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()  # Thread starts
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 10%')
        RL.setColor(0, 16, 50)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 30%')
        RL.setColor(0, 16, 100)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 50%')
        RL.setColor(0, 16, 150)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 70%')
        RL.setColor(0, 16, 200)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 90%')
        RL.setColor(0, 16, 255)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 100%')
        RL.setColor(35, 255, 35)
        if OLED_connection:
            screen.screen_show(2, 'IP:192.168.12.1')
            screen.screen_show(3, 'AP MODE ON')


async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)


async def recv_msg(websocket):
    global speed_set, modeSelect
    move.setup()
    direction_command = 'no'
    turn_command = 'no'

    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }

        data = ''
        data = await websocket.recv()
        # try:
        #     data = await websocket.recv()
        # except:
        #     print("WEB interface disconnected!")
        #     move.destroy()      # motor stop.
        #     scGear.moveInit()   # servo  back initial position.

        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')

        if not data:
            continue

        if not functionMode:
            if OLED_connection:
                screen.screen_show(5, 'Functions OFF')
        else:
            pass

        print(data)
        response = json.dumps(response)
        await websocket.send(response)


async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)


def test_Network_Connection():
    while True:
        try:
            print("test Network Connection status")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            s.close()
        except:
            print("error!!")
            move.destroy()

        time.sleep(0.5)


if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()

    HOST = ''
    PORT = 10223  # Define port serial
    BUFSIZ = 1024  # Define buffer size
    ADDR = (HOST, PORT)

    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()

    # Prevent the problem that the car cannot stop after the Raspberry Pi accidentally disconnects from the network.
    # testNC_threading=threading.Thread(target=test_Network_Connection)
    # testNC_threading.setDaemon(False)
    # testNC_threading.start()

    try:
        RL = robotLight.RobotLight()
        RL.start()
        RL.breath(70, 70, 255)
    except:
        print(
            'Use "sudo pip3 install rpi_ws281x" to install WS_281x package\n使用"sudo pip3 install rpi_ws281x"命令来安装rpi_ws281x')
        pass

    while 1:
        wifi_check()
        try:  # Start server,waiting for client
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            # print('...connected from :', addr)
            break
        except Exception as e:
            print(e)
            RL.setColor(0, 0, 0)

        try:
            RL.setColor(0, 80, 255)
        except:
            pass
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
        RL.setColor(0, 0, 0)
        move.destroy()
