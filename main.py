from UI.main_screen import MainScreen, OneKeyFrame, HotKeyFrame
from UI.settings import Settings
from PySide6 import QtWidgets
from PySide6.QtCore import QThread, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow,
                               QSystemTrayIcon, QMenu)
from PySide6.QtGui import QIcon, QAction
from darkdetect import isDark
from updater import check_version
from webbrowser import open_new as web_open
from asyncio import new_event_loop, set_event_loop, run
from json import loads, dumps
from os.path import dirname, join, exists
import sys
import auto_clicker
import press_click
import qdarktheme

__version__ = "1.7.0"


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.basedir = dirname(__file__)
        self.setStyle("Fusion")
        self.setApplicationName("AutoPresser")
        self.setApplicationDisplayName("AutoPresser")
        self.setApplicationVersion(__version__)
        self.setQuitOnLastWindowClosed(False)

        self.old_style = (self.palette(), self.styleSheet())
        self.new_style = (qdarktheme.load_palette(), qdarktheme.load_stylesheet())

        self.window = MainWindow(self)
        self.tray = SystemTrayIcon(QIcon(join(self.basedir, "../images/autopresser_icon.ico")), self)
        self.window.show()
        self.tray.show()



class MainWindow(QMainWindow):
    __slots__ = ("main_screen", "settings", "stack_widget")

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.text_size = 14
        self.old_style = (self.palette(), self.styleSheet())
        self.new_style = (qdarktheme.load_palette(), qdarktheme.load_stylesheet())

        self.settings = Settings(self)
        self.main_screen = MainScreen(self, ScriptStartThread)

        if exists("DataSave/config.json"):
            try:
                with open("DataSave/config.json", "r") as f:
                    settings = loads(f.read())
                    self.text_size = settings["text_size"] if settings.get("text_size") else 14
                    self.settings.settings_app_frame.dropdown_style.setCurrentText(settings.get("style"))
            except Exception as e:
                self.show_err("Exception", f"Error load save:\n{str(e)}")

        self.settings.settings_app_frame.changeStyle()
        self.stack_widget = QtWidgets.QStackedWidget(self)
        self.stack_widget.addWidget(self.main_screen)
        self.stack_widget.addWidget(self.settings)
        self.stack_widget.setCurrentIndex(0)
        self.setCentralWidget(self.stack_widget)
        self.update_app()
        self._change_size_text(self.text_size)
        self._change_size_text_item(self.text_size, self.settings.settings_script_frame.dlg_extra_settings.layout())

    def resizeEvent(self, event, /):
        self.settings.settings_script_frame.resize_dropdown(event.size())

    def get_text_size(self):
        return self.text_size

    def set_text_size(self, size):
        self.text_size = size
        self._change_size_text(size)

    def set_style_app(self, style: str):
        if style == "Old":
            self.master.setPalette(self.old_style[0])
            self.master.setStyleSheet(self.old_style[1])
            self.master.setStyleSheet("""QTabBar::tab:selected {background-color: #3b3b3b;}
                                         QTabBar::tab {background-color: #575656;}
                                         QTabWidget::pane {background-color: #3b3b3b}""")
        elif style == "New":
            self.master.setPalette(self.new_style[0])
            self.master.setStyleSheet(self.new_style[1])
        else:
            if not exists(f"DataSave/Styles/{style}.json"):
                self.show_err("FileNotFound", f"File '{style}.json' not found")
                raise FileNotFoundError
            # Load custom style
            with open(f"DataSave/Styles/{style}.json", "r") as f:
                style = loads(f.read())
                styles = []
                for k, v in style.items():
                    styles.append(f"{k} {v}".replace(",", ";").replace("'", ""))
                    for i in range(len(styles)):
                        if styles[i][:len(k)] == k:
                            styles[i] = f"{k} {v}".replace(",", ";").replace("'", "")
                self.master.setPalette(self.old_style[0])
                self.master.setStyleSheet("""\n""".join(styles))


    def show_info(self, title, message):
        message_box = QtWidgets.QMessageBox()
        message_box.information(self, title, message, QtWidgets.QMessageBox.StandardButton.Ok)
        if message_box == QtWidgets.QMessageBox.StandardButton.Ok:
            message_box.close()

    def show_err(self, title, message):
        message_box = QtWidgets.QMessageBox()
        message_box.critical(self, title, message, QtWidgets.QMessageBox.StandardButton.Ok)
        if message_box == QtWidgets.QMessageBox.StandardButton.Ok:
            message_box.close()

    def _change_size_text(self, text_size):
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
        self.resize(self.get_text_size() * 20, self.get_text_size() * 19.5)

    def _change_size_text_item(self, text_size, item):
        for i in range(item.layout().count()):
            main_widget = item.layout().itemAt(i).widget()
            if main_widget is None:
                main_widget = item.layout().itemAt(i)
            if isinstance(main_widget, MainScreen) or isinstance(main_widget, Settings):
                self._change_size_text_item(text_size, main_widget)
            if isinstance(main_widget, QtWidgets.QTabWidget):
                if not isDark():
                    main_widget.setStyleSheet("""QTabWidget {font-size: %spx;}
                                                 QTabWidget::tab-bar {alignment: center;}
                                                 QTabWidget::pane {border: 2px solid rgba(181, 181, 181, 70);
                                                                   border-radius: 10px; 
                                                                   background-color: rgba(181, 181, 181, 70)}
                                                 QTabBar::tab {border: 1px solid rgba(255, 255, 255, 20);
                                                               background-color: rgba(181, 181, 181, 70);
                                                               border-top-left-radius: 5px; 
                                                               border-top-right-radius: 5px; 
                                                               padding: 5px; margin-bottom: 5px;}
                                                 QTabBar::tab:selected {margin-bottom: 0px;
                                                                        background-color: rgba(181, 181, 181, 100)}""" % text_size)
                else:
                    main_widget.setStyleSheet("""QTabWidget {font-size: %spx;}
                                                 QTabWidget::tab-bar {alignment: center;}
                                                 QTabWidget::pane {border: 1.5px solid rgba(163, 163, 163, 50); 
                                                                   border-radius: 10px}
                                                 QTabBar::tab {border: 1px solid rgba(163, 163, 163, 20); 
                                                               border-top-left-radius: 5px; 
                                                               border-top-right-radius: 5px; 
                                                               padding: 5px; 
                                                               margin-bottom: 5px;}
                                                 QTabBar::tab:selected {margin-bottom: 0px;}""" % text_size)
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
                main_widget.setFixedSize(QSize(self.settings.get_slider_value() * 3.5,
                                                 int((self.settings.get_slider_value() / 2) * 5.1)))
                if isDark():
                    main_widget.setStyleSheet("""* {font-size: %spx;
                                                    border: 1.8px solid black;
                                                    border-radius: 5px;}
                                                 *:focus {border: 1px solid rgba(255, 255, 255, 70);}""" % text_size)
                else:
                    main_widget.setStyleSheet("""* {font-size: %spx;
                                                    border: 1.8px solid rgba(128, 128, 128, 20);
                                                    border-radius: 5px;}
                                                 *:focus {border: 1px solid rgba(128, 128, 128, 90);}""" % text_size)

                format_t = main_widget.document().rootFrame().frameFormat()
                format_t.setTopMargin(self.get_text_size() / 3)
                main_widget.document().rootFrame().setFrameFormat(format_t)
            elif isinstance(main_widget, QtWidgets.QDialog):
                self._change_size_text_item(text_size, main_widget)
            else:
                main_widget.setStyleSheet("""* {font-size: %spx;}""" % text_size)

    def update_app(self):
        info = check_version(__version__)
        if info is None:
            return None
        elif exists("DataSave/config.json"):
            with open("DataSave/config.json", "r") as f:
                settings: dict = loads(f.read())
                if info[0] == settings.get("ignore_version"):
                    return None

        message = QtWidgets.QMessageBox()
        message.setWindowTitle("Update available")
        message.setText(f"{" ".join(info[0])} available! Version now: {__version__}")
        message.setIcon(message.Icon.Information)
        message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ignore |
                                   QtWidgets.QMessageBox.StandardButton.Close|
                                   QtWidgets.QMessageBox.StandardButton.Open)
        btn = message.exec()

        if btn == message.StandardButton.Open:
            web_open(info[1])
        elif btn == message.StandardButton.Close:
            message.close()
        elif btn == message.StandardButton.Ignore:
            type_read = "w"
            if exists("DataSave/config.json"):
                type_read = "r+"
            with open("DataSave/config.json", type_read) as f:
                try:
                    settings: dict = loads(f.read())
                except:
                    settings = {}
                settings.update({"ignore_version": info[0]})
                f.seek(0)
                f.write(dumps(settings))
                f.truncate()


    def add_items_layout(self, layout: QtWidgets.QBoxLayout, widgets: list[QtWidgets.QWidget] = None,
                         layouts: list[QtWidgets.QLayout] = None):
        if widgets:
            for i in widgets:
                if i:
                    layout.addWidget(i)
        if layouts:
            for i in layouts:
                if i:
                    layout.addLayout(i)
        return layout

    def create_layout(self, layout_type: str = "h", widgets: list[QtWidgets.QWidget] = None,
                      layouts: list[QtWidgets.QLayout] = None):
        if layout_type == "v":
            layout = QtWidgets.QVBoxLayout()
        else:
            layout = QtWidgets.QHBoxLayout()
        return self.add_items_layout(layout, widgets, layouts)


class ScriptStartThread(QThread):
    def __init__(self, master, type_key: int, script: int, window_name):
        super().__init__()
        self.master = master
        self.type_key = type_key
        self.script = script
        self.script_name = press_click if self.script == 0 else auto_clicker
        self.window_name = window_name
        self.loop_script = new_event_loop()

    def start_one_key(self, script_name):
        if self.master.dropdown_btn.currentIndex() == 3:
            self.loop_script.run_until_complete(
                script_name.start_one_key(self.master.one_key_frame.entry.toPlainText(),
                                          self.master.entry.toPlainText().lower(),
                                          self.master.get_options_one_key(), self.window_name))
        else:
            self.loop_script.run_until_complete(
                script_name.start_one_key(self.master.one_key_frame.entry.toPlainText(),
                                          self.master.dropdown_btn.currentText().lower(),
                                          self.master.get_options_one_key(), self.window_name))

    def start_two_key(self, script_name):
        if self.master.dropdown_btn.currentIndex() == 3:
            self.loop_script.run_until_complete(
                script_name.start_two_keys(self.master.hot_key_frame.dropdown.currentText().lower(),
                                           self.master.hot_key_frame.entry.toPlainText().lower(),
                                           self.master.entry.toPlainText().lower(),
                                           self.master.get_options_hot_key(), self.window_name))
        else:
            self.loop_script.run_until_complete(
                script_name.start_two_keys(self.master.hot_key_frame.dropdown.currentText().lower(),
                                           self.master.hot_key_frame.entry.toPlainText().lower(),
                                           self.master.dropdown_btn.currentText().lower(),
                                           self.master.get_options_hot_key(), self.window_name))

    def run(self):
        set_event_loop(self.loop_script)
        try:
            if self.type_key == 0:
                self.start_one_key(self.script_name)
            else:
                self.start_two_key(self.script_name)
        except FileNotFoundError as e:
            self.master.master.show_err("FileNotFoundError", f"{e}")
            run(self.script_name.stop())

    def stop(self):
        try:
            run(self.script_name.stop())
            self.loop_script.stop()
        except Exception as e:
            self.master.master.show_err("Exception", f"{e}")
        self.terminate()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon=icon, parent=parent)
        self.default_icon = self.icon()
        self.active_icon = QIcon(join(parent.basedir, "../images/autopresser_icon_active.ico"))
        self.main_window = parent.window
        self.menu = QMenu()
        self.start_script_act = QAction("Start script")
        self.start_script_act.triggered.connect(self.start_script)
        self.stop_script_act = QAction("Stop script")
        self.stop_script_act.setVisible(False)
        self.stop_script_act.triggered.connect(self.stop_script)
        self.update_act = QAction("Check update")
        self.update_act.triggered.connect(self.check_update)
        self.open_act = QAction("Open")
        self.open_act.triggered.connect(self.main_window.show)
        self.quit_act = QAction("Close")
        self.quit_act.triggered.connect(parent.quit)
        self.menu.addActions((self.start_script_act, self.stop_script_act,
                              self.menu.addSeparator(),
                              self.update_act, self.open_act,
                              self.menu.addSeparator(),
                              self.quit_act))
        self.setContextMenu(self.menu)

    def start_script(self):
        if self.main_window.main_screen.start_script() is None:
            return
        self.start_script_act.setVisible(False)
        self.stop_script_act.setVisible(True)

    def stop_script(self):
        self.main_window.main_screen.stop_script()
        self.start_script_act.setVisible(True)
        self.stop_script_act.setVisible(False)

    def check_update(self):
        upd = self.main_window.update_app()
        if upd is None:
            self.main_window.show_info("Update", "You are using the latest version")


def main():
    app = Application()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
