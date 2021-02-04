#https://github.com/ysj1173886760/ScreenTranslater
from PyQt5.QtWidgets import QApplication, QMainWindow
import my_ui
import sys
import utils
from PIL import Image
import os
from PyQt5.QtCore import Qt
from screenshot_test import CaptureScreen

class GUI(QMainWindow, my_ui.Ui_MainWindow):
    
    def __init__(self):
        super(GUI, self).__init__()
        self.setupUi(self)
        # self.setWindowModality(Qt.ApplicationModal)
        self.pushButton_2.clicked.connect(self.translate_cmd)
        self.pushButton_3.clicked.connect(self.get_from_clipboard_cmd)
        self.pushButton.clicked.connect(self.capture_img)

    def capture_img(self):
        gui.hide()
        self.screenshot = CaptureScreen()
        self.screenshot.exec_()
        gui.show()
        self.set_text()

    def set_text(self):
        result = utils.baidu_ocr('tmp.png')
        if result:
            if self.checkBox.isChecked():
                result = utils.paper_format(result)
            self.textEdit.setText(result)
        os.remove('tmp.png')

    def get_from_clipboard_cmd(self):
        cb = QApplication.clipboard()
        if cb.mimeData().hasImage():
            qt_img = cb.image()
            qt_img.save('tmp.png', quality=95)
            self.set_text()

    def translate_cmd(self):
        content = self.textEdit.toPlainText()
        result = utils.baidu_translate(content)
        if result:
            self.textEdit_2.setText(result)
        else:
            self.textEdit_2.setText('Error')
    
    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_C) and (event.modifiers() == Qt.ControlModifier|Qt.AltModifier):
            self.get_from_clipboard_cmd()
        if (event.key() == Qt.Key_Z) and (event.modifiers() == Qt.ControlModifier|Qt.AltModifier):
            self.translate_cmd()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    gui.setWindowTitle('ScreenTranslator')
    gui.show()
    sys.exit(app.exec_())