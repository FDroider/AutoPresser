from asyncio import new_event_loop, set_event_loop
from asyncio import run
from json import loads
from UI import MainScreen, Settings
from UI import OneKeyFrame, HotKeyFrame
from os.path import exists
from PySide6 import QtWidgets
from PySide6.QtCore import QThread, QSize
from PySide6.QtWidgets import QApplication, QMainWindow
import sys
import auto_clicker
import press_click


try:
    from ctypes import windll

    myappid = 'droid_android.auto_presser.1_5_0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(QMainWindow):
    __slots__ = ("main_screen", "settings", "stack_widget")

    def __init__(self):
        super().__init__()
        self.text_size = 14

        if exists("DataSave/config.json"):
            try:
                with open("DataSave/config.json", "r") as f:
                    settings = loads(f.read())
                    self.text_size = settings["text_size"]
            except Exception as e:
                self.show_err("Exception", f"Error load save:\n{str(e)}")

        self.settings = Settings(self)
        self.main_screen = MainScreen(self, ScriptStartThread)
        self.setWindowTitle("Auto Clicker/Presser")
        self.stack_widget = QtWidgets.QStackedWidget(self)
        self.stack_widget.addWidget(self.main_screen)
        self.stack_widget.addWidget(self.settings)
        self.stack_widget.setCurrentIndex(0)
        self.setCentralWidget(self.stack_widget)
        self.change_size_text(self.text_size)

    def get_text_size(self):
        return self.text_size

    def set_text_size(self, size):
        self.text_size = size
        self.change_size_text(self.text_size)

    def show_info(self, title, message):
        message_box = QtWidgets.QMessageBox()
        message_box.information(self, title, message, QtWidgets.QMessageBox.StandardButton.Ok)
        if message_box == QtWidgets.QMessageBox.StandardButton.Ok:
            message_box.close()

    def show_err(self, title, message):
        message_box = QtWidgets.QMessageBox()
        message_box.critical(self, title, message,
                             QtWidgets.QMessageBox.StandardButton.Ok)
        if message_box == QtWidgets.QMessageBox.StandardButton.Ok:
            message_box.close()

    def change_size_text(self, text_size):
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is None:
                widget = self.layout().itemAt(i)
            if isinstance(widget, QtWidgets.QStackedWidget):
                for i in range(widget.layout().count()):
                    try:
                        widget = self.layout().itemAt(i).widget()
                    except AttributeError:
                        continue
                    self._change_size_text_item(text_size, widget)
            else:
                try:
                    self._change_size_text_item(text_size, widget)
                except Exception as e:
                    self.show_err("Exception", str(e))

    def _change_size_text_item(self, text_size, item):
        for i in range(item.layout().count()):
            main_widget = item.layout().itemAt(i).widget()
            if main_widget is None:
                main_widget = item.layout().itemAt(i)
            if isinstance(main_widget, MainScreen) or isinstance(main_widget, Settings):
                self._change_size_text_item(text_size, main_widget)
            if isinstance(main_widget, QtWidgets.QTabWidget):
                main_widget.setStyleSheet("""QTabWidget {font-size: %spx;}
                                             QTabWidget::tab-bar {alignment: center;}
                                             QTabWidget::pane {border: 1px solid rgba(255, 255, 255, 20); 
                                             border-radius: 10px; background-color: #3b3b3b}
                                             QTabBar::tab {background-color: #575656; 
                                             border: 1px solid rgba(255, 255, 255, 20); 
                                             border-top-left-radius: 5px; border-top-right-radius: 5px; 
                                             padding: 5px; margin-bottom: 5px;}
                                             QTabBar::tab:selected {background-color: #3b3b3b; margin-bottom: 0px;}
                                             # background-color: #435473;""" % text_size)
                main_widget.widget(0).setStyleSheet("""* {font-size: %spx;}""" % text_size)
                main_widget.widget(1).setStyleSheet("""* {font-size: %spx;}""" % text_size)
                self._change_size_text_item(text_size, main_widget.widget(0))
                self._change_size_text_item(text_size, main_widget.widget(1))
            elif isinstance(main_widget, OneKeyFrame) or isinstance(main_widget, HotKeyFrame):
                self._change_size_text_item(text_size, main_widget)
            elif isinstance(main_widget, QtWidgets.QVBoxLayout) or isinstance(main_widget, QtWidgets.QHBoxLayout)\
                    or isinstance(main_widget, QtWidgets.QFormLayout):
                self._change_size_text_item(text_size, main_widget)
            elif isinstance(main_widget, QtWidgets.QTextEdit):
                main_widget.setMaximumSize(QSize(self.settings.get_slider_value() * 3.5,
                                                 int((self.settings.get_slider_value() / 2) * 4.5)))
                main_widget.setStyleSheet("""* {font-size: %spx;
                                                border: 1.8px solid black;
                                                border-radius: 5px;
                                                color: #f5f5f5;}
                                             *:focus {border: 1px solid rgba(255, 255, 255, 70);}""" % text_size)

                format_t = main_widget.document().rootFrame().frameFormat()
                format_t.setTopMargin(self.get_text_size() / 3)
                main_widget.document().rootFrame().setFrameFormat(format_t)
            else:
                main_widget.setStyleSheet("""* {font-size: %spx;}""" % text_size)
        self.resize(self.get_text_size() * 7.5, self.get_text_size() * 17.5)


class AlertDialog(QtWidgets.QMessageBox):
    ...


class ScriptStartThread(QThread):
    def __init__(self, parent, type_key: int, script: int):
        super().__init__()
        self.parent = parent
        self.type_key = type_key
        self.script = script
        self.script_name = press_click if self.script == 0 else auto_clicker
        self.loop_script = new_event_loop()

    def start_one_key(self, script_name):
        if self.parent.dropdown_btn.currentIndex() == 3:
            self.loop_script.run_until_complete(
                script_name.start_one_key(self.parent.one_key_frame.entry.toPlainText(),
                                          self.parent.entry.toPlainText().lower(),
                                          self.parent.get_options_one_key()))
        else:
            self.loop_script.run_until_complete(
                script_name.start_one_key(self.parent.one_key_frame.entry.toPlainText(),
                                          self.parent.dropdown_btn.currentText().lower(),
                                          self.parent.get_options_one_key()))

    def start_two_key(self, script_name):
        if self.parent.dropdown_btn.currentIndex() == 3:
            self.loop_script.run_until_complete(
                script_name.start_two_keys(self.parent.hot_key_frame.dropdown.currentText().lower(),
                                           self.parent.hot_key_frame.entry.toPlainText().lower(),
                                           self.parent.entry.toPlainText().lower(),
                                           self.parent.get_options_hot_key()))
        else:
            self.loop_script.run_until_complete(
                script_name.start_two_keys(self.parent.hot_key_frame.dropdown.currentText().lower(),
                                           self.parent.hot_key_frame.entry.toPlainText().lower(),
                                           self.parent.dropdown_btn.currentText().lower(),
                                           self.parent.get_options_hot_key()))

    def run(self):
        set_event_loop(self.loop_script)
        if self.type_key == 0:
            self.start_one_key(self.script_name)
        else:
            self.start_two_key(self.script_name)

    def stop(self):
        run(self.script_name.stop())
        self.loop_script.stop()
        self.terminate()


def start():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
