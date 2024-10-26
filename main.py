import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtCore import QFile, QIODevice, QObject

from pathlib import Path
import platform
import subprocess

class GameThread(QThread):
    update_game_data = Signal(str, int)
    def __init__(self, command, open_type):
        # open_type: 0: new game, 1: open game
        super().__init__()
        self.command = command
        self.open_type = open_type
    
    @Slot()
    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.update_game_data.emit(output.strip(), self.open_type)
                # print(output.strip())

class MainWindow:
    new_game_type = "sandbox"
    def __init__(self):
        super(MainWindow, self).__init__()
        qfile = QFile("launcher-ui/mainwindow.ui")
        qfile.open(QFile.ReadOnly)
        qfile.close()
        self.ui = QUiLoader().load(qfile)

        self.ui.setFixedSize(800, 600)

        # 从UI定义中动态创建一个相应的窗口对象
        saved_game_path = Path("SavedGames/")
        files = list(saved_game_path.rglob(f"*game"))
        for file in files:
            self.ui.open_game_name.addItem(str(file.stem))
        
        # 按钮信号槽
        self.ui.open_game_button_box.accepted.connect(self.open_game)
        self.ui.open_game_button_box.rejected.connect(self.exit)
        self.ui.new_game_button_box.accepted.connect(self.new_game)
        self.ui.new_game_button_box.rejected.connect(self.exit)

        # 新建游戏选择框信号槽
        self.ui.new_game_type_sandbox.clicked.connect(lambda: self.change_game_type("sandbox"))
        self.ui.new_game_type_survival.clicked.connect(lambda: self.change_game_type("survival"))

    def exit(self):
        self.ui.close()

    def new_game(self):
        if self.ui.new_game_name.text() == "":
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]panic: game name can not be empty\n")
            return
    
        system = platform.system()
        if system == "Windows":
            msg = "[launcher]info: running command: ./rust-craft-2d.exe --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d.exe --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type, 0)
        elif system == "Linux":
            msg = "[launcher]info: running command: ./rust-craft-2d --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type, 0)
        else:
            msg = "[launcher]panic: unsupported platform: " + system
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
    
    def open_game(self):
        if self.ui.open_game_name.currentItem() == None:
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]panic: game name can not be empty\n")
            return
        system = platform.system()
        if system == "Windows":
            msg = "[launcher]info: running command: ./rust-craft-2d.exe --open " + self.ui.open_game_name.currentItem().text()
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d.exe --open " + self.ui.open_game_name.currentItem().text(), 1)
        elif system == "Linux":
            msg = "[launcher]info: running command: ./rust-craft-2d --open " + self.ui.open_game_name.currentItem().text()
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d --open " + self.ui.open_game_name.currentItem().text(), 1)
        else:
            msg = "[launcher]panic: unsupported platform: " + system
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")
    

    def change_game_type(self, game_type):
        # print("change game type to "+game_type)
        self.new_game_type = game_type
    
    def start_game(self, command, open_type):
        # 开始工作线程
        self.game_thread = GameThread(command, open_type)
        self.game_thread.update_game_data.connect(self.update_game_data)
        self.game_thread.start()
    
    def update_game_data(self, data, open_type):
        # 更新标签的文本
        if open_type == 0:
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + data + "\n")
        else:
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + data + "\n")

 
if __name__ == "__main__":
    app = QApplication(sys.argv)
 
    window = MainWindow()
    window.ui.show()
 
    sys.exit(app.exec())