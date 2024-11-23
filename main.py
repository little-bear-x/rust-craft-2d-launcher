import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtCore import QFile, QIODevice, QObject

from pathlib import Path
import platform
import subprocess
import os
import random

LAUNCHER_VERSION = "rust-craft-2d 0.4.0 (demo)"

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

        self.update_saved_games()
        
        # 按钮信号槽
        self.ui.new_game_start_button.clicked.connect(self.new_game)
        self.ui.open_game_update_list.clicked.connect(self.update_saved_games)
        self.ui.open_game_start_button.clicked.connect(self.open_game)
        self.ui.open_game_delete_button.clicked.connect(self.delete_game)

        # 新建游戏选择框信号槽
        self.ui.new_game_type_sandbox.clicked.connect(lambda: self.change_game_type("sandbox"))
        self.ui.new_game_type_survival.clicked.connect(lambda: self.change_game_type("survival"))

        # Tab信号槽
        self.ui.main_tab.currentChanged.connect(self.update_saved_games)

        # 随即seed按钮信号槽
        self.ui.new_game_seed_random.clicked.connect(self.random_seed)

    def exit(self):
        self.ui.close()

    def random_seed(self):
        self.ui.new_game_seed_input.setText(str(random.randint(0, 2147483647)))

    def new_game(self):
        print(self.ui.new_game_seed_input.text())
        if self.ui.new_game_name.text() == "":
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]panic: game name can not be empty\n")
            return

        if self.ui.new_game_seed_input.text() == "":
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]panic: seed can not be empty\n")
            return
        try:
            game_seed = int(self.ui.new_game_seed_input.text())
        except ValueError:
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]panic: seed must be a number\n")
            return
        if game_seed < -1 or game_seed > 2147483647:
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]panic: seed must be between -1 and 2147483647\n")
            return
    
        system = platform.system()
        if system == "Windows":
            game_version = os.popen("./rust-craft-2d.exe --version").read().splitlines()[0]
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]info Starting...game version: " + game_version + " | launcher version: " + LAUNCHER_VERSION + "\n")
            if LAUNCHER_VERSION != game_version:
                self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]warn: The launcher version does not match the game version! This may cause errors!\n")
                
            msg = "[launcher]info: running command: ./rust-craft-2d.exe --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type + " --seed " + str(game_seed)
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d.exe --new " + self.ui.new_game_name.text() + 
                                " --gametype " + self.new_game_type + 
                                " --seed " + str(game_seed), 
                            0)
        elif system == "Linux":
            game_version = os.popen("./rust-craft-2d --version").read().splitlines()[0]
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]info Starting...game version: " + game_version + " | launcher version: " + LAUNCHER_VERSION + "\n")
            if LAUNCHER_VERSION != game_version:
                self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + "[launcher]warn: The launcher version does not match the game version! This may cause errors!\n")

            msg = "[launcher]info: running command: ./rust-craft-2d --new " + self.ui.new_game_name.text() + " --gametype " + self.new_game_type + " --seed " + str(game_seed)
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d --new " + self.ui.new_game_name.text() + 
                                " --gametype " + self.new_game_type + 
                                " --seed " + str(game_seed), 
                            0)
        else:
            msg = "[launcher]panic: unsupported platform: " + system
            self.ui.new_game_log.setText(self.ui.new_game_log.toPlainText() + msg + "\n")
    
    def update_saved_games(self):
        self.ui.open_game_name.clear()
        saved_game_path = Path("SavedGames/")
        files = list(saved_game_path.rglob(f"*game"))
        for file in files:
            self.ui.open_game_name.addItem(str(file.stem))

    def open_game(self):
        if self.ui.open_game_name.currentItem() == None:
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]panic: game name can not be empty\n")
            return
        system = platform.system()
        if system == "Windows":
            game_version = os.popen("./rust-craft-2d.exe --version").read().splitlines()[0]
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]info Starting...game version: " + game_version + " | launcher version: " + LAUNCHER_VERSION + "\n")
            if LAUNCHER_VERSION != game_version:
                self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]warn: The launcher version does not match the game version! This may cause errors!\n")

            msg = "[launcher]info: running command: ./rust-craft-2d.exe --open " + self.ui.open_game_name.currentItem().text()
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d.exe --open " + self.ui.open_game_name.currentItem().text(), 1)
        elif system == "Linux":
            game_version = os.popen("./rust-craft-2d --version").read().splitlines()[0]
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]info Starting...game version: " + game_version + " | launcher version: " + LAUNCHER_VERSION + "\n")
            if LAUNCHER_VERSION != game_version:
                self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]warn: The launcher version does not match the game version! This may cause errors!\n")

            msg = "[launcher]info: running command: ./rust-craft-2d --open " + self.ui.open_game_name.currentItem().text()
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")
            self.start_game("./rust-craft-2d --open " + self.ui.open_game_name.currentItem().text(), 1)
        else:
            msg = "[launcher]panic: unsupported platform: " + system
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + msg + "\n")

    def delete_game(self):
        if self.ui.open_game_name.currentItem() == None:
            self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]panic: game name can not be empty\n")
            return
        reply = QMessageBox.question(None, "删除存档?", "确定删除该存档?\n此操作不可逆!", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove("SavedGames/"+self.ui.open_game_name.currentItem().text()+".game")
                self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]info: Delete success.\n")
            except:
                self.ui.open_game_log.setText(self.ui.open_game_log.toPlainText() + "[launcher]panic: Cannot delete the archive! Please refresh the archive list.\n")
        self.update_saved_games()


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
