from os.path import exists
from os import mkdir, makedirs, listdir, remove
from PySide6 import QtWidgets, QtCore, QtGui
from json import dumps, loads
from platform import system
import subprocess
import pywinctl

class Settings(QtWidgets.QWidget):
    __slots__ = ("tab_widget", "settings_script_frame", "settings_app_frame",
                 "settings_layout", "btn_layout")

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.tab_view = QtWidgets.QTabWidget()
        self.tab_view.setObjectName("QTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("QWidget")
        self.tab_view.addTab(self.tab, "Settings script")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("QWidget")
        self.tab_view.addTab(self.tab_2, "Settings app")

        self.btn_back = QtWidgets.QPushButton("Back")
        self.btn_back.setObjectName("QPushButton")
        self.btn_back.clicked.connect(self.back)
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_save.setObjectName("QPushButton")
        self.btn_save.clicked.connect(self.save_settings)

        self.settings_script_frame = SettingsScripFrame(self.master)
        self.settings_app_frame = SettingsAppFrame(self.master)

        self.tab.setLayout(self.settings_script_frame.layout())
        self.tab_2.setLayout(self.settings_app_frame.layout())

        self.settings_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = self.master.create_layout(items=[self.btn_back, self.btn_save])

        self.settings_layout.addWidget(self.tab_view)
        self.settings_layout.addLayout(self.btn_layout)

    def back(self):
        self.master.setWindowTitle("")
        self.master.stack_widget.setCurrentIndex(0)

    def save_settings(self):
        if not exists("DataSave"):
            mkdir("DataSave")
        try:
            with open("DataSave/config.json", "r+") as f:
                try:
                    settings = loads(f.read())
                    settings.update({"text_size": self.settings_app_frame.slider.value(),
                                     "style": self.settings_app_frame.dropdown_style.currentText()})
                except:
                    settings = {"text_size": self.settings_app_frame.slider.value(),
                                "style": self.settings_app_frame.dropdown_style.currentText()}
                f.seek(0)
                f.write(dumps(settings))
                f.truncate()
        except FileNotFoundError:
            with open("DataSave/config.json", "w") as f:
                settings = {"text_size": self.settings_app_frame.slider.value(),
                            "style": self.settings_app_frame.dropdown_style.currentText()}
                f.write(dumps(settings))
        self.master.show_info("Success", "Settings saved")

    def get_slider_value(self):
        return self.settings_app_frame.slider.value()

    def get_script_settings(self):
        return (self.settings_script_frame.dlg_extra_settings.duration_one_key.toPlainText(),
                self.settings_script_frame.dlg_extra_settings.delay_hot_key.toPlainText(),
                self.settings_script_frame.dlg_extra_settings.interval_hot_key.toPlainText())

    def set_script_settings(self, duration_one_key = None, delay_hot_key = None, interval_hot_key = None):
        if duration_one_key:
            self.settings_script_frame.dlg_extra_settings.duration_one_key.setText(duration_one_key)
            self.settings_script_frame.dlg_extra_settings.duration_one_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        if delay_hot_key:
            self.settings_script_frame.dlg_extra_settings.delay_hot_key.setText(delay_hot_key)
            self.settings_script_frame.dlg_extra_settings.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        if interval_hot_key:
            self.settings_script_frame.dlg_extra_settings.interval_hot_key.setText(interval_hot_key)
            self.settings_script_frame.dlg_extra_settings.interval_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)

    def get_select_window(self, index: bool = True):
        if not index:
            return self.settings_script_frame.dropdown_windows.currentText()
        return self.settings_script_frame.dropdown_windows.currentIndex()


class SettingsScripFrame(QtWidgets.QFrame):
    __slots__ = ("h_one_key_l", "h_hot_key_l", "h_presets_l", "v_layout")

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.selected_window = None
        self.dlg_extra_settings = ExtraSettings(self.master)
        self.btn_extra_settings = QtWidgets.QPushButton("Open extra settings")
        self.btn_extra_settings.clicked.connect(self.dlg_extra_settings.show)
        self.dropdown_windows = QtWidgets.QComboBox()
        self.dropdown_windows.addItems(self.show_windows())
        self.dropdown_windows.currentIndexChanged.connect(self.set_select_window)
        self.dropdown_windows.setMaximumSize(QtCore.QSize(250, 10))
        self.dropdown_presets = QtWidgets.QComboBox()
        self.dropdown_presets.addItems(self.show_presets())
        self.dropdown_presets.setToolTip("Preset")
        self.btn_select = QtWidgets.QPushButton("Select")
        self.btn_select.clicked.connect(lambda: self.master.main_screen.load_preset(self.dropdown_presets.currentText()))

        self.h_presets_l = self.master.create_layout(items=[self.dropdown_presets, self.btn_select])
        self.v_layout = self.master.create_layout("v", items=[self.btn_extra_settings, self.dropdown_windows,
                                                              self.h_presets_l])
        self.setLayout(self.v_layout)

    def resize_dropdown(self, size):
        self.dropdown_windows.setMaximumSize(QtCore.QSize(int(size.width()/1.15), int(size.height()/18)))

    def show_presets(self):
        presets = []
        if not exists("DataSave/Presets"):
            return ("None",)
        for f in listdir("DataSave/Presets"):
            if f.endswith(".json"):
                presets.append(f[:-5])
        if len(presets) < 1:
            return ("None",)
        return presets

    def show_windows(self):
        windows = ["auto"]
        main_system = system()
        if main_system.lower() == "linux":
            try:
                output = subprocess.check_output(['xprop', '-root', '_NET_CLIENT_LIST']).decode()
                w_ids = output.split("# ")[1].split(", ")
                for w_id in w_ids:
                    title_output = subprocess.check_output(['xprop', '-id', w_id, 'WM_NAME']).decode()
                    title = title_output.split('"')
                    if len(title) >= 3:
                        windows.append(title[1])
            except FileNotFoundError:
                self.master.show_err("FileNotFoundError", "xprop not found. Install it for window search to work")
            except Exception as e:
                self.master.show_err("Unknown error", f"{e}")
        elif main_system.lower() == "windows":
            wins = pywinctl.getAllAppsNames()
            for w in wins:
                windows.append(w)
        return windows

    def update_list_windows(self):
        self.dropdown_windows.currentIndexChanged.disconnect()
        self.dropdown_windows.clear()
        windows = self.show_windows()
        self.dropdown_windows.addItems(windows)
        if self.selected_window in windows:
            self.dropdown_windows.setCurrentText(self.selected_window)
        self.dropdown_windows.currentIndexChanged.connect(self.set_select_window)

    def update_list_presets(self):
        self.dropdown_presets.clear()
        self.dropdown_presets.addItems(self.show_presets())

    def set_select_window(self):
        self.selected_window = self.dropdown_windows.currentText()

class ExtraSettings(QtWidgets.QDialog):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.lb_one_key = QtWidgets.QLabel("Settings for one key option")
        self.duration_one_key = QtWidgets.QTextEdit()
        self.duration_one_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.duration_one_key.setPlaceholderText("Duration")
        self.duration_one_key.setToolTip("Duration")
        self.lb_hot_key = QtWidgets.QLabel("Settings for hot key option")
        self.delay_hot_key = QtWidgets.QTextEdit()
        self.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.delay_hot_key.setPlaceholderText("Delay")
        self.delay_hot_key.setToolTip("Delay")
        self.interval_hot_key = QtWidgets.QTextEdit()
        self.interval_hot_key.setPlaceholderText("Interval")
        self.interval_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.interval_hot_key.setToolTip("Interval")
        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.close)

        self.h_one_key_l = self.master.create_layout(items=[self.duration_one_key])
        self.h_hot_key_l = self.master.create_layout(items=[self.delay_hot_key, self.interval_hot_key])
        self.v_layout = self.master.create_layout("v", [self.lb_one_key, self.h_one_key_l,
                                                        self.lb_hot_key, self.h_hot_key_l,
                                                        self.btn_close])
        self.setLayout(self.v_layout)

class SettingsAppFrame(QtWidgets.QFrame):
    __slots__ = ("v_layout",)

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.lb_style = QtWidgets.QLabel("Styles")
        self.lb_style.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.dropdown_style = QtWidgets.QComboBox()
        self.dropdown_style.addItems(self.show_styles())
        self.dropdown_style.currentIndexChanged.connect(self.changeStyle)
        self.btn_select = QtWidgets.QPushButton("Create style")
        self.btn_select.clicked.connect(self.open_style_dlg)
        self.btn_change = QtWidgets.QPushButton("Change style")
        self.btn_change.clicked.connect(lambda: self.open_style_dlg(self.dropdown_style.currentText())
                                        if self.dropdown_style.currentIndex() not in (0, 1)
                                        else None)
        self.btn_delete = QtWidgets.QPushButton("Delete Style")
        self.btn_delete.clicked.connect(lambda: self.delete_style(self.dropdown_style.currentText())
                                        if self.dropdown_style.currentIndex() not in (0, 1)
                                        else None)
        self.lb_text_size = QtWidgets.QLabel("Text size")
        self.lb_text_size.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.slider = QtWidgets.QSlider(QtGui.Qt.Orientation.Horizontal)
        self.slider.setValue(self.master.get_text_size())
        self.slider.setMinimum(11)
        self.slider.setMaximum(25)
        self.slider.sliderReleased.connect(lambda: self.master.set_text_size(self.slider.value()))
        self.slider.valueChanged.connect(self.change_size)
        self.slider.setToolTip(f"{self.slider.value()}px")

        self.h_layout_style = self.master.create_layout(items=[self.dropdown_style, self.btn_select])
        self.h_layout_change = self.master.create_layout(items=[self.btn_delete, self.btn_change])
        self.v_layout = self.master.create_layout("v", [self.lb_style, self.h_layout_style, self.h_layout_change,
                                                        self.lb_text_size, self.slider])

        self.setLayout(self.v_layout)

    def change_size(self):
        self.lb_text_size.setStyleSheet("""QLabel {font-size: %spx;}""" % self.slider.value())
        self.slider.setToolTip(f"{self.slider.value()}px")

    def show_styles(self):
        styles = ["Default", "Old version"]
        if not exists("DataSave/Styles"):
            return styles
        for f in listdir("DataSave/Styles"):
            if f.endswith(".json"):
                styles.append(f[:-5])
        return styles

    def update_styles(self):
        currentText = self.dropdown_style.currentText()
        self.dropdown_style.currentIndexChanged.disconnect()
        self.dropdown_style.clear()
        styles = self.show_styles()
        self.dropdown_style.addItems(styles)
        self.dropdown_style.currentIndexChanged.connect(self.changeStyle)
        if currentText not in styles:
            self.dropdown_style.setCurrentIndex(1)
        else:
            self.dropdown_style.setCurrentText(currentText)

    def delete_style(self, style_name: str):
        if exists(f"DataSave/Styles/{style_name}.json"):
            remove(f"DataSave/Styles/{style_name}.json")
        self.update_styles()

    def changeStyle(self):
        if self.dropdown_style.currentIndex() == 1:
            self.master.set_style_app("Old")
        elif self.dropdown_style.currentIndex() == 0:
            self.master.set_style_app("New")
        else:
            try:
                self.master.set_style_app(self.dropdown_style.currentText())
            except FileNotFoundError:
                self.update_styles()

    def open_style_dlg(self, style_name: str = None):
        if style_name and not exists(f"DataSave/Styles/{style_name}.json"):
            self.master.show_err("FileNotFound", f"File {style_name}.json not found")
            self.update_styles()
            return
        dlg = SettingsColor(self.slider.value(), self, style_name)
        dlg.exec()


class SettingsColor(QtWidgets.QDialog):
    __slots__ = ("h_layout_window", "h_layout_button", "h_layout_text", "h_layout_dropdown", "h_layout_tab", "v_layout")

    def __init__(self, text_size, master, style_name):
        super().__init__()
        self.master = master
        self.master_main = master.master
        self.size_var = self.master_main.get_text_size()
        self.resize(self.size_var * 20, self.size_var * 15.4)
        self.styles = {}
        self.app = QtWidgets.QApplication.instance()
        self.dlg_color = QtWidgets.QColorDialog()
        self.setWindowTitle("Create style")
        self.style_name_fld = QtWidgets.QTextEdit()
        self.style_name_fld.setMaximumHeight(int((text_size / 2) * 5))
        self.style_name_fld.setStyleSheet("""* {font-size: %spx;
                                            border: 1.8px solid black;
                                            border-radius: 5px;}
                                         *:focus {border: 1px solid rgba(255, 255, 255, 70);}""" % text_size)
        self.style_name_fld.setPlaceholderText("Name style")
        self.style_name_fld.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.style_name_fld.setMinimumSize(QtCore.QSize(50, 35))

        if style_name:
            with open(f"DataSave/Styles/{style_name}.json", "r") as f:
                self.styles = loads(f.read())
            self._update_stylesheet()
            self.style_name_fld.setText(style_name)
            self.style_name_fld.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)

        self.window_style_items = self.create_option("Window", "Select color", "QMainWindow", ("background-color",))
        self.btn_style_items = self.create_option("Button", "Select color", "QPushButton", ("background-color",))

        self.frame_button_extra = ExtraButtonOption(self)
        self.frame_button_extra.setHidden(True)
        self.btn_button_extra = QtWidgets.QPushButton("Extra options")
        self.btn_button_extra.clicked.connect(lambda: self._open_extra(self.frame_button_extra))

        self.text_style_items = self.create_option("Text", "Select color", "QLabel", ("color",))
        self.dropdown_style_items = self.create_option("Dropdown", "Select color", "QComboBox", ("background-color",))

        self.frame_dropdown_extra = ExtraDropdownOption(self)
        self.frame_dropdown_extra.setHidden(True)
        self.btn_dropdown_extra = QtWidgets.QPushButton("Extra options")
        self.btn_dropdown_extra.clicked.connect(lambda: self._open_extra(self.frame_dropdown_extra))

        self.tab_style_items = self.create_option("Tab", "Select color", "QTabWidget::pane", ("background-color",))

        self.frame_tab_extra = ExtraTabOption(self)
        self.frame_tab_extra.setHidden(True)
        self.btn_tab_extra = QtWidgets.QPushButton("Extra options")
        self.btn_tab_extra.clicked.connect(lambda: self._open_extra(self.frame_tab_extra))

        self.btnBox = QtWidgets.QDialogButtonBox((QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                                  QtWidgets.QDialogButtonBox.StandardButton.Cancel))
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.h_layout_window = self.master_main.create_layout(items=self.window_style_items)
        self.h_layout_button = self.master_main.create_layout(items=self.btn_style_items)
        self.h_layout_text = self.master_main.create_layout(items=self.text_style_items)
        self.h_layout_dropdown = self.master_main.create_layout(items=self.dropdown_style_items)
        self.h_layout_tab = self.master_main.create_layout(items=self.tab_style_items)

        self.v_layout = self.master_main.create_layout("v", [self.style_name_fld, self.h_layout_window,
                                                             self.h_layout_button, self.btn_button_extra,
                                                             self.frame_button_extra, self.h_layout_text,
                                                             self.h_layout_dropdown, self.btn_dropdown_extra,
                                                             self.frame_dropdown_extra, self.h_layout_tab,
                                                             self.btn_tab_extra, self.frame_tab_extra,
                                                             self.btnBox])
        self.setLayout(self.v_layout)

    def _parent_select(self):
        pass

    def _stylesheet_select(self, color=None, obj_name: str = None, options: tuple = None):
        for i in options:
            if self.styles.get(obj_name):
                self.styles.get(obj_name).update({i: f"{color.name()}"})
            else:
                self.styles.update({obj_name: {i: f"{color.name()}"}})
        self._update_stylesheet()

    def _update_stylesheet(self):
        styles = []
        for k, v in self.styles.items():
            styles.append(f"{k} {v}".replace(",", ";").replace("'", ""))
            for i in range(len(styles)):
                if styles[i][:len(k)] == k:
                    styles[i] = f"{k} {v}".replace(",", ";").replace("'", "")

        self.setStyleSheet("""\n""".join(styles))
        self.update()

    def accept(self):
        if self.style_name_fld.toPlainText().replace(" ", "") == "":
            self.master_main.show_err("ValueError", "Enter name for style!")
            return

        if not exists("DataSave/Styles"):
            makedirs("DataSave/Styles")
        with open(f"DataSave/Styles/{self.style_name_fld.toPlainText()}.json", "w") as f:
            f.write(dumps(self.styles))

        self.master.update_styles()
        self.close()

    def _open_extra(self, frame: QtWidgets.QFrame):
        if frame.isHidden():
            frame.setHidden(False)
            if frame == self.frame_tab_extra:
                self.resize(self.size_var * 20, self.size_var * 42.4)
            else:
                self.resize(self.size_var * 20, self.size_var * 35.4)
        else:
            frame.setHidden(True)
            self.resize(self.size_var * 20, self.size_var * 15.4)

    def create_option(self, label_text: str, button_text: str, obj_name: str, options: tuple = None):
        items = [QtWidgets.QLabel(label_text), QtWidgets.QPushButton(button_text)]
        items[1].clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(), obj_name, options))
        return items


class ExtraButtonOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_button_text", "h_layout_button_hover", "h_layout_button_disabled", "v_layout")

    def __init__(self, master):
        super().__init__()
        self.master_main = master.master_main

        self.btn_text_items = master.create_option("Button text", "Select color", "QPushButton", ("color",))
        self.btn_hover_items = master.create_option("Button hover", "Select color", "QPushButton::hover", ("background-color",))
        self.btn_disabled_items = master.create_option("Button disabled", "Select color", "QPushButton::disabled", ("background-color",))

        self.h_layout_button_text = self.master_main.create_layout(items=self.btn_text_items)
        self.h_layout_button_hover = self.master_main.create_layout(items=self.btn_hover_items)
        self.h_layout_button_disabled = self.master_main.create_layout(items=self.btn_disabled_items)

        self.v_layout = self.master_main.create_layout("v", [self.h_layout_button_text, self.h_layout_button_hover,
                                                             self.h_layout_button_disabled])
        self.setLayout(self.v_layout)

class ExtraDropdownOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_dropdown_text", "h_layout_dropdown_hover", "h_layout_dropdown_disabled", "v_layout")

    def __init__(self, master):
        super().__init__()
        self.master_main = master.master_main

        self.dropdown_text_items = master.create_option("Dropdown text", "Select color", "QComboBox", ("color",))
        self.dropdown_hover_items = master.create_option("Dropdown hover", "Select color", "QComboBox::hover", ("background-color",))
        self.dropdown_disabled_items = master.create_option("Dropdown disabled", "Select color", "QComboBox::disabled", ("background-color",))

        self.h_layout_dropdown_text = self.master_main.create_layout(items=self.dropdown_text_items)
        self.h_layout_dropdown_hover = self.master_main.create_layout(items=self.dropdown_hover_items)
        self.h_layout_dropdown_disabled = self.master_main.create_layout(items=self.dropdown_disabled_items)

        self.v_layout = self.master_main.create_layout("v", [self.h_layout_dropdown_text, self.h_layout_dropdown_hover,
                                                             self.h_layout_dropdown_disabled])
        self.setLayout(self.v_layout)


class ExtraTabOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_tab_bar", "h_layout_tab_bar_text", "h_layout_tab_bar_hover", "h_layout_tab_bar_selected",
                 "h_layout_tab_bar_disabled", "v_layout")

    def __init__(self, master):
        super().__init__()
        self.master_main = master.master_main

        self.tab_bar_items = master.create_option("Tab bar", "Select color", "QTabBar::tab", ("background-color",))
        self.tab_bar_text_items = master.create_option("Tab bar text", "Select color", "QTabBar::tab", ("color",))
        self.tab_bar_hover_items = master.create_option("Tab bar hover", "Select color", "QTabBar::tab:hover", ("background-color",))
        self.tab_bar_selected_items = master.create_option("Tab bar selected", "Select color", "QTabBar::tab:selected", ("background-color",))
        self.tab_bar_disabled_items = master.create_option("Tab bar disabled", "Select color", "QTabBar::tab:disabled", ("background-color",))
        self.tab_disabled_items = master.create_option("Tab disabled", "Select color", "QTabWidget::pane:disabled", ("background-color",))

        self.h_layout_tab_bar = self.master_main.create_layout(items=self.tab_bar_items)
        self.h_layout_tab_bar_text = self.master_main.create_layout(items=self.tab_bar_text_items)
        self.h_layout_tab_bar_hover = self.master_main.create_layout(items=self.tab_bar_hover_items)
        self.h_layout_tab_bar_selected = self.master_main.create_layout(items=self.tab_bar_selected_items)
        self.h_layout_tab_bar_disabled = self.master_main.create_layout(items=self.tab_bar_disabled_items)
        self.h_layout_tab_disabled = self.master_main.create_layout(items=self.tab_disabled_items)

        self.v_layout = self.master_main.create_layout("v", [self.h_layout_tab_bar, self.h_layout_tab_bar_text,
                                                             self.h_layout_tab_bar_hover, self.h_layout_tab_bar_selected,
                                                             self.h_layout_tab_bar_disabled, self.h_layout_tab_disabled])
        self.setLayout(self.v_layout)