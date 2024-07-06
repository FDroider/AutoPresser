from os.path import exists, dirname, join
from os import mkdir, makedirs, listdir
from PySide6 import QtWidgets, QtCore, QtGui
import json


class MainScreen(QtWidgets.QWidget):
    __slots__ = ("tab_widget", "one_key_frame", "hot_key_frame", "group_btn",
                 "key_layout", "chose_script_l", "v_layout")

    def __init__(self, parent, starter_script):
        super().__init__(parent)
        basedir = dirname(__file__)
        pixmapi = getattr(QtWidgets.QStyle, "SP_DialogSaveButton")

        self.master = parent
        self.starter_script_thread = starter_script

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setObjectName("QTabWidget")
        self.tab_widget.resize(300, 200)
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("QWidget")
        self.tab_widget.addTab(self.tab, "One key")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("QWidget")
        self.tab_widget.addTab(self.tab_2, "Hot key")

        self.one_key_frame = OneKeyFrame()
        self.hot_key_frame = HotKeyFrame()

        self.dropdown_btn = QtWidgets.QComboBox()
        self.dropdown_btn.setObjectName("QComboBox")
        self.dropdown_btn.addItems(["Right", "Middle", "Left", "Key"])
        self.dropdown_btn.currentIndexChanged.connect(self.change_dropdown_btn)
        self.dropdown_btn.setFixedSize(QtCore.QSize(100, 30))

        self.entry = QtWidgets.QTextEdit()
        self.entry.setObjectName("QTextEdit")
        self.entry.setFixedSize(QtCore.QSize(42, 30))
        self.entry.setVisible(False)
        self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)

        self.btn_settings = QtWidgets.QPushButton("Settings")
        self.btn_settings.setObjectName("QPushButton")
        self.btn_settings.setIcon(QtGui.QIcon(join(basedir, "771203.png")))
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_save.setObjectName("QPushButton")
        self.btn_save.setIcon(QtGui.QIcon(self.style().standardIcon(pixmapi)))
        self.btn_save.clicked.connect(self.save_settings_script)
        self.btn_save_presets = QtWidgets.QPushButton("Save preset")
        self.btn_save_presets.clicked.connect(self.open_save_dlg)
        self.btn_save_presets.setObjectName("QPushButton")
        self.btn_save_presets.setIcon(QtGui.QIcon(join(basedir, "10057635.png")))
        self.btn_start = QtWidgets.QPushButton("Start script")
        self.btn_start.setObjectName("QPushButton")
        self.btn_start.clicked.connect(self.start_script)

        if exists("DataSave/config_script.json"):
            with open("DataSave/config_script.json", "r") as f:
                settings = json.loads(f.read())
                for i in settings.items():
                    i = i[0]
                    try:
                        if i[0:4] == "bind":
                            if i[5:] == "one_key":
                                self.one_key_frame.entry.setText(settings[i])
                                self.one_key_frame.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                            else:
                                self.hot_key_frame.dropdown.setCurrentText(settings[i][:-2])
                                self.hot_key_frame.entry.setText(settings[i][-1])
                                self.hot_key_frame.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                        else:
                            if i[0:7] == "one_key":
                                if i[8:] == "duration":
                                    self.master.settings.settings_script_frame.duration_one_key.setText(
                                        settings[i])
                                    self.master.settings.settings_script_frame.duration_one_key.setAlignment(
                                        QtGui.Qt.AlignmentFlag.AlignCenter)
                                continue
                            elif i[0:7] == "hot_key":
                                match i[8:]:
                                    case "delay":
                                        self.master.settings.settings_script_frame.delay_hot_key.setText(
                                            settings[i])
                                        self.master.settings.settings_script_frame.delay_hot_key.setAlignment(
                                            QtGui.Qt.AlignmentFlag.AlignCenter)
                                    case "interval":
                                        self.master.settings.settings_script_frame.interval_hot_key.setText(
                                            settings[i])
                                        self.master.settings.settings_script_frame.interval_hot_key.setAlignment(
                                            QtGui.Qt.AlignmentFlag.AlignCenter)
                                continue
                            else:
                                if i == "button":
                                    self.dropdown_btn.setCurrentText(settings[i])
                                else:
                                    self.entry.setText(settings[i])
                                    self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                    except Exception as e:
                       print(e)

        self.dropdown_script = QtWidgets.QComboBox()
        self.dropdown_script.setObjectName("QComboBox")
        self.dropdown_script.addItems(["Presser", "AutoClicker"])
        self.dropdown_script.setCurrentIndex(0)

        self.group_btn = QtWidgets.QHBoxLayout()
        self.key_layout = QtWidgets.QHBoxLayout()
        self.chose_script_l = QtWidgets.QHBoxLayout()
        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.key_layout.addWidget(self.dropdown_btn)
        self.key_layout.addWidget(self.entry)

        self.group_btn.addWidget(self.btn_settings)
        self.group_btn.addWidget(self.btn_save)
        self.group_btn.addWidget(self.btn_save_presets)

        self.chose_script_l.addWidget(self.btn_start)
        self.chose_script_l.addWidget(self.dropdown_script)

        self.v_layout.addWidget(self.tab_widget)
        self.v_layout.addLayout(self.key_layout)
        self.v_layout.addLayout(self.group_btn)
        self.v_layout.addLayout(self.chose_script_l)

        self.tab.setLayout(self.one_key_frame.layout())
        self.tab_2.setLayout(self.hot_key_frame.layout())
        self.setLayout(self.v_layout)

    def get_options_one_key(self):
        return self.master.settings.settings_script_frame.duration_one_key.toPlainText()

    def get_options_how_key(self):
        return self.master.settings.settings_script_frame.delay_hot_key.toPlainText()

    def open_settings(self):
        self.master.stack_widget.setCurrentIndex(1)

    def change_dropdown_btn(self):
        if self.dropdown_btn.currentIndex() == 3:
            self.entry.setVisible(True)
        else:
            self.entry.setVisible(False)

    def start_script(self):
        if self.dropdown_btn.currentIndex() == 3:
            if self.entry.toPlainText().lower().replace(" ", "") == "":
                return
        if self.dropdown_script.currentIndex() == 0:
            if self.one_key_frame.entry.toPlainText().replace(" ", "") == "":
                return
        else:
            if self.hot_key_frame.entry.toPlainText().replace(" ", "") == "":
                return
        self.dropdown_script.setDisabled(True)
        self.starter_script = self.starter_script_thread(self, self.tab_widget.currentIndex(),
                                                         self.dropdown_script.currentIndex())
        self.starter_script.start()
        self.dropdown_script.setDisabled(True)
        self.tab_widget.setDisabled(True)
        self.btn_start.setText("Stop script")
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.stop_script)

    def stop_script(self):
        self.starter_script.stop()
        self.tab_widget.setDisabled(False)
        self.dropdown_script.setDisabled(False)
        self.btn_start.setText("Start script")
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.start_script)

    def save_settings_script(self):
        if not exists("DataSave"):
            mkdir("DataSave")
        settings = {"bind_one_key": self.one_key_frame.get_value_entry(),
                    "bind_hot_key": f"{self.hot_key_frame.get_extra_key()}+{self.hot_key_frame.get_value_entry()}",
                    "button": self.dropdown_btn.currentText(),
                    "button_key": self.entry.toPlainText(),
                    "one_key_duration": self.master.settings.settings_script_frame.duration_one_key.toPlainText(),
                    "hot_key_delay": self.master.settings.settings_script_frame.delay_hot_key.toPlainText(),
                    "hot_key_interval": self.master.settings.settings_script_frame.interval_hot_key.toPlainText()}
        try:
            with open("DataSave/config_script.json", "w") as f:
                f.write(json.dumps(settings))
            self.master.show_info("Success", "Settings saved")
        except Exception as e:
            self.master.show_err("Exception", str(e))

    def open_save_dlg(self):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Save preset")
        layout = QtWidgets.QVBoxLayout()
        filename = QtWidgets.QTextEdit()
        filename.setPlaceholderText("File name")
        filename.setFixedSize(QtCore.QSize(200, 30))
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                             QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(lambda: self.save_preset(filename.toPlainText()) if filename.toPlainText().replace(" ", "") != ""
                                 else self.master.show_err("ValueError", "Enter file name!"))
        btn_box.rejected.connect(dlg.close)
        layout.addWidget(filename)
        layout.addWidget(btn_box)
        dlg.setLayout(layout)
        dlg.exec()

    def save_preset(self, filename):
        if not exists("DataSave/Presets"):
            makedirs("DataSave/Presets")
        settings = {"bind_one_key": self.one_key_frame.get_value_entry(),
                    "bind_hot_key": f"{self.hot_key_frame.get_extra_key()}+{self.hot_key_frame.get_value_entry()}",
                    "button": self.dropdown_btn.currentText(),
                    "button_key": self.entry.toPlainText(),
                    "one_key_dur": self.master.settings.settings_script_frame.duration_one_key.toPlainText(),
                    "hot_key_delay": self.master.settings.settings_script_frame.delay_hot_key.toPlainText(),
                    "hot_key_interval": self.master.settings.settings_script_frame.interval_hot_key.toPlainText()}
        try:
            with open(f"DataSave/Presets/{filename}.json", "w") as f:
                f.write(json.dumps(settings))
            self.master.show_info("Success", "Settings saved")
        except Exception as e:
            self.master.show_err("Exception", str(e))
        self.master.settings.settings_script_frame.update_list_presets()

    def load_preset(self, filename):
        if not exists(f"DataSave/Presets/{filename}.json"):
            self.master.show_err("FileNotFound", f"'{filename}.json' not founded or removed")
            return
        try:
            with open(f"DataSave/Presets/{filename}.json", "r") as f:
                settings = json.loads(f.read())
                self.one_key_frame.entry.setText(settings["bind_one_key"])
                self.one_key_frame.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                self.hot_key_frame.dropdown.setCurrentText(settings["bind_hot_key"][:-2])
                self.hot_key_frame.entry.setText(settings["bind_hot_key"][-1])
                self.hot_key_frame.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                self.master.settings.settings_script_frame.duration_one_key.setText(settings["one_key_dur"])
                self.master.settings.settings_script_frame.duration_one_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                self.master.settings.settings_script_frame.delay_hot_key.setText(settings["hot_key_delay"])
                self.master.settings.settings_script_frame.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                self.master.settings.settings_script_frame.interval_hot_key.setText(settings["hot_key_interval"])
                self.master.settings.settings_script_frame.interval_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                self.dropdown_btn.setCurrentText(settings["button"])
                self.entry.setText(settings["button_key"])
                self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            self.master.show_err("Exception", str(e))


class OneKeyFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.lb = QtWidgets.QLabel("Enter activation key")
        self.lb.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry = QtWidgets.QTextEdit()
        self.entry.setStyleSheet("""*:focus {border: 1px solid rgba(255, 255, 255, 70);}""")
        self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry.setFixedSize(QtCore.QSize(42, 30))
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.v_layout.addWidget(self.lb)
        self.h_layout.addWidget(self.entry)
        self.v_layout.addLayout(self.h_layout)

    def get_value_entry(self):
        return self.entry.toPlainText()


class HotKeyFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setVisible(False)

        self.lb = QtWidgets.QLabel("Enter activation keys")
        self.lb.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.addItems(["Ctrl", "Alt", "Shift"])
        self.dropdown.setCurrentIndex(0)
        self.dropdown.setFixedSize(QtCore.QSize(100, 20))
        self.entry = QtWidgets.QTextEdit()
        self.entry.setStyleSheet("""*:focus {border: 1px solid rgba(255, 255, 255, 70);}""")
        self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry.setFixedSize(QtCore.QSize(42, 30))
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.v_layout.addWidget(self.lb)
        self.v_layout.addLayout(self.h_layout)
        self.h_layout.addWidget(self.dropdown)
        self.h_layout.addWidget(self.entry)

    def get_extra_key(self):
        return self.dropdown.currentText()

    def get_value_entry(self):
        return self.entry.toPlainText()


class SettingsScripFrame(QtWidgets.QFrame):
    def __init__(self, master):
        super().__init__()
        self.master = master

        self.lb_one_key = QtWidgets.QLabel("Settings for one key option")
        self.duration_one_key = QtWidgets.QTextEdit()
        self.duration_one_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.duration_one_key.setPlaceholderText("Duration")
        self.lb_hot_key = QtWidgets.QLabel("Settings for hot key option")
        self.delay_hot_key = QtWidgets.QTextEdit()
        self.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.delay_hot_key.setPlaceholderText("Delay")
        self.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.interval_hot_key = QtWidgets.QTextEdit()
        self.interval_hot_key.setPlaceholderText("Interval")
        self.interval_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.dropdown_presets = QtWidgets.QComboBox()
        self.dropdown_presets.addItems(self.show_presets())
        self.btn_upd = QtWidgets.QPushButton("Update")
        self.btn_upd.clicked.connect(self.update_list_presets)
        self.btn_select = QtWidgets.QPushButton("Select")
        self.btn_select.clicked.connect(lambda: self.master.main_screen.load_preset(self.dropdown_presets.currentText()))

        self.h_one_key_l = QtWidgets.QHBoxLayout()

        self.h_one_key_l.addWidget(self.duration_one_key)

        self.h_hot_key_l = QtWidgets.QHBoxLayout()

        self.h_hot_key_l.addWidget(self.delay_hot_key)
        self.h_hot_key_l.addWidget(self.interval_hot_key)

        self.h_presets_l = QtWidgets.QHBoxLayout()

        self.h_presets_l.addWidget(self.dropdown_presets)
        self.h_presets_l.addWidget(self.btn_upd)
        self.h_presets_l.addWidget(self.btn_select)

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.v_layout.addWidget(self.lb_one_key)
        self.v_layout.addLayout(self.h_one_key_l)
        self.v_layout.addWidget(self.lb_hot_key)
        self.v_layout.addLayout(self.h_hot_key_l)
        self.v_layout.addLayout(self.h_presets_l)

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

    def update_list_presets(self):
        self.dropdown_presets.clear()
        self.dropdown_presets.addItems(self.show_presets())


class SettingsAppFrame(QtWidgets.QFrame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.lb_lang = QtWidgets.QLabel("Language")
        self.lb_lang.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.dropdown_lang = QtWidgets.QComboBox()
        self.lb_text_size = QtWidgets.QLabel("Text size")
        self.lb_text_size.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.slider = QtWidgets.QSlider(QtGui.Qt.Orientation.Horizontal)
        self.slider.setValue(self.master.get_text_size())
        self.slider.setMinimum(11)
        self.slider.setMaximum(25)
        self.slider.valueChanged.connect(self.change_size)
        self.slider.setToolTip(f"{self.slider.value()}px")

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.v_layout.addWidget(self.lb_lang)
        self.v_layout.addWidget(self.dropdown_lang)
        self.v_layout.addWidget(self.lb_text_size)
        self.v_layout.addWidget(self.slider)

    def change_size(self):
        self.lb_text_size.setStyleSheet(""".QLabel {font-size: %spx;}""" % self.slider.value())
        self.slider.setToolTip(f"{self.slider.value()}px")
        self.master.set_text_size(self.slider.value())


class Settings(QtWidgets.QWidget):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.setWindowTitle("Settings")
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
        self.btn_layout = QtWidgets.QHBoxLayout()

        self.settings_layout.addWidget(self.tab_view)
        self.btn_layout.addWidget(self.btn_back)
        self.btn_layout.addWidget(self.btn_save)
        self.settings_layout.addLayout(self.btn_layout)

    def back(self):
        self.master.stack_widget.setCurrentIndex(0)

    def save_settings(self):
        settings = {"lang_app": None,
                    "text_size": self.settings_app_frame.slider.value()}
        if not exists("DataSave"):
            mkdir("DataSave")
        with open("DataSave/config.json", "w") as f:
            f.write(json.dumps(settings))
        self.master.show_info("Success", "Settings saved")

    def get_slider_value(self):
        return self.settings_app_frame.slider.value()