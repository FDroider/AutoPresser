from asyncio import sleep
from pyautogui import mouseUp, mouseDown
from pyautogui import keyUp, keyDown
from pyautogui import PyAutoGUIException
from pynput.keyboard import Listener, KeyCode


class MouseControl:
    def __init__(self, button: str, duration: float):
        self.btn_click = button.lower()
        self.duration = duration
        self.mouse_pressed = False

    def start_mouse_down(self):
        self.mouse_pressed = True
        try:
            mouseDown(button=self.btn_click, duration=self.duration)
        except PyAutoGUIException:
            keyDown(key=self.btn_click)

    def stop_mouse_down(self):
        self.mouse_pressed = False
        try:
            mouseUp(button=self.btn_click, duration=self.duration)
        except PyAutoGUIException:
            keyUp(key=self.btn_click)

    def start(self):
        if self.mouse_pressed is True:
            self.stop_mouse_down()
        else:
            self.start_mouse_down()


async def start_one_key(start_key, stop_key, button, duration: float = 0.0):
    global listener, app

    app = MouseControl(button, duration)

    def on_press(key):
        if key == KeyCode(char=start_key):
            app.start()
        elif key == KeyCode(char=stop_key):
            app.stop_mouse_down()
            listener.stop()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, stop_key):
    global listener

    app = MouseControl()

    def on_press(key):
        if key == KeyCode(char=start_key):
            count = 0
            while count < 5:
                if key == KeyCode(char=start_two_key):
                    app.start()
                count += 5
                sleep(1)
        elif key == KeyCode(char=stop_key):
            app.stop_mouse_down()
            listener.stop()

    def on_release(key):
        print("Key on_release", key)

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


async def stop():
    app.stop_mouse_down()
    listener.stop()
