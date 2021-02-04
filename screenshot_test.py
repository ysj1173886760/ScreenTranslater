import sys
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, qApp
from PyQt5.QtCore import Qt, qAbs, QRect
from PyQt5.QtGui import QPen, QPainter, QColor, QGuiApplication

class CaptureScreen(QDialog):
    # 初始化变量
    beginPosition = None
    endPosition = None
    fullScreenImage = None
    captureImage = None
    isMousePressLeft = None
    painter = QPainter()

    def __init__(self):
        super(QWidget, self).__init__()
        self.initWindow()   # 初始化窗口
        self.captureFullScreen()    # 获取全屏

    def initWindow(self):
        self.setWindowModality(Qt.ApplicationModal) # 设置模态属性
        self.setMouseTracking(True)     # 鼠标追踪
        self.setCursor(Qt.CrossCursor)  # 设置光标
        self.setWindowFlag(Qt.FramelessWindowHint)  # 窗口无边框
        self.setWindowState(Qt.WindowFullScreen)    # 窗口全屏

    def captureFullScreen(self):
        self.fullScreenImage = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        # screenGeometry = qApp.primaryScreen().virtualGeometry()
        # screenPixmap = qApp.primaryScreen().grabWindow(qApp.desktop().winId(), screenGeometry.x(), screenGeometry.y(),
        #                                                                     screenGeometry.width(), screenGeometry.height())
        # # print(screenGeometry.width(), screenGeometry.height(), screenGeometry.x(), screenGeometry.y())
        # self.fullScreenImage = screenPixmap
        # screen_count = QApplication.desktop().screenCount()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.beginPosition = event.pos()
            self.isMousePressLeft = True
        if event.button() == Qt.RightButton:
            # 如果选取了图片,则按一次右键开始重新截图
            if self.captureImage is not None:
                self.captureImage = None
                self.paintBackgroundImage()
                self.update()
            else:
                self.close()

    def mouseMoveEvent(self, event):
        if self.isMousePressLeft is True:
            self.endPosition = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.endPosition = event.pos()
        self.isMousePressLeft = False

    def mouseDoubleClickEvent(self, event):
        if self.captureImage is not None:
            self.saveImage()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.captureImage is not None:
                self.saveImage()
                self.close()

    def paintBackgroundImage(self):
        shadowColor = QColor(0, 0, 0, 100)  # 黑色半透明
        self.painter.drawPixmap(0, 0, self.fullScreenImage)
        self.painter.fillRect(self.fullScreenImage.rect(), shadowColor)     # 填充矩形阴影

    def paintEvent(self, event):
        self.painter.begin(self)    # 开始重绘
        self.paintBackgroundImage()
        penColor = QColor(30, 144, 245)     # 画笔颜色
        self.painter.setPen(QPen(penColor, 1, Qt.SolidLine, Qt.RoundCap))    # 设置画笔,蓝色,1px大小,实线,圆形笔帽
        if self.isMousePressLeft is True:
            pickRect = self.getRectangle(self.beginPosition, self.endPosition)   # 获得要截图的矩形框
            self.captureImage = self.fullScreenImage.copy(pickRect)         # 捕获截图矩形框内的图片
            self.painter.drawPixmap(pickRect.topLeft(), self.captureImage)  # 填充截图的图片
            self.painter.drawRect(pickRect)     # 画矩形边框
        self.painter.end()  # 结束重绘

    def getRectangle(self, beginPoint, endPoint):
        pickRectWidth = int(qAbs(beginPoint.x() - endPoint.x()))
        pickRectHeight = int(qAbs(beginPoint.y() - endPoint.y()))
        pickRectTop = beginPoint.x() if beginPoint.x() < endPoint.x() else endPoint.x()
        pickRectLeft = beginPoint.y() if beginPoint.y() < endPoint.y() else endPoint.y()
        pickRect = QRect(pickRectTop, pickRectLeft, pickRectWidth, pickRectHeight)
        # 避免高度宽度为0时候报错
        if pickRectWidth == 0:
            pickRect.setWidth(2)
        if pickRectHeight == 0:
            pickRect.setHeight(2)

        return pickRect

    def saveImage(self):
        self.captureImage.save('tmp.png', quality=95)   # 保存图片到当前文件夹中
        self.close()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    windows = CaptureScreen()
    windows.show()
    sys.exit(app.exec_())