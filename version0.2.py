from PyQt5.QtWidgets import QApplication, QMainWindow
import my_ui
import sys
import utils
from PIL import Image
import os

class GUI(QMainWindow, my_ui.Ui_MainWindow):
    
    def __init__(self):
        super(GUI, self).__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.translate_cmd)
        self.pushButton_3.clicked.connect(self.get_from_clipboard_cmd)

    def get_from_clipboard_cmd(self):
        cb = QApplication.clipboard()
        if cb.mimeData().hasImage():
            qt_img = cb.image()
            pil_img = Image.fromqimage(qt_img)
            pil_img.save('tmp.png')
            result = utils.baidu_ocr('tmp.png')
            if result:
                self.textEdit.setText(result)
            os.remove('tmp.png')

    def translate_cmd(self):
        content = self.textEdit.toPlainText()
        result = utils.baidu_translate(content)
        if result:
            self.textEdit_2.setText(result)
        else:
            self.textEdit_2.setText('Error')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())