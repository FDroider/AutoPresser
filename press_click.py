from keyboard import press, release
from pyautogui import mouseUp, mouseDown
from pyautogui import PyAutoGUIException
from pynput.keyboard import Listener, KeyCode, HotKey


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
            press(self.btn_click)

    def stop_mouse_down(self):
        self.mouse_pressed = False
        try:
            mouseUp(button=self.btn_click, duration=self.duration)
        except PyAutoGUIException:
            release(self.btn_click)

    def start(self):
        if self.mouse_pressed is True:
            self.stop_mouse_down()
        else:
            self.start_mouse_down()


async def start_one_key(start_key, stop_key, button, duration: float = 0.0):
    global listener, app

    if duration == "":
        duration = 0.0

    app = MouseControl(button, duration)

    def on_press(key):
        if key == KeyCode(char=start_key):
            app.start()
        elif key == KeyCode(char=stop_key):
            app.stop_mouse_down()
            listener.stop()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, stop_key, button, duration: float = 0.0):
    global listener, app

    if duration == "":
        duration = 0.0

    app = MouseControl(button, duration)

    hotkey = HotKey((HotKey.parse(f"<{start_key}>+{start_two_key}")),
                    on_activate=app.start)

    def on_press(f):
        return lambda k: f(listener.canonical(k))

    with Listener(on_press=on_press(hotkey.press), on_release=on_press(hotkey.release)) as listener:
        listener.join()


async def stop():
    app.stop_mouse_down()
    listener.stop()
