# coding:utf-8
import ctypes
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentTranslator
from qfluentwidgets import NavigationItemPosition, FluentWindow

from src.app import stop_proxy
from src.dirPrefix import dirPrefix
from src.interface.account import AccountInterface
from src.interface.home import HomeInterface
from src.interface.settings import SettingsInterface
from src.runtimeLog import runtime_log


def is_admin():
    """检查当前进程是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """尝试以管理员权限重新运行当前脚本"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


# class Widget(QFrame):
#     """初始化Widget类，继承自QFrame"""
#     def __init__(self, text: str, parent=None):
#         super().__init__(parent=parent)  # 调用父类的构造函数
#         self.label = SubtitleLabel(text, self)  # 创建一个子标题标签，文本为传入的text
#         self.hBoxLayout = QHBoxLayout(self)  # 创建一个水平布局
#
#         setFont(self.label, 24)  # 设置标签的字体大小为24
#         self.label.setAlignment(Qt.AlignCenter)  # 设置标签的文本对齐方式为居中
#         self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)  # 将标签添加到水平布局中，并设置对齐方式为居中
#
#         # 给子界面设置全局唯一的对象名，对象名由传入的text转换而来，空格替换为'-'
#         self.setObjectName(text.replace(' ', '-'))


class Main(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = HomeInterface('Home Interface', parent=self)
        self.accountInterface = AccountInterface('Account Interface', parent=self)
        # self.videoInterface = Widget('Video Interface', self)
        self.settingInterface = SettingsInterface('Setting Interface', parent=self)

        self.init_navigation()
        self.init_window()

    def init_navigation(self):
        """添加子界面到导航栏"""
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.accountInterface, FIF.FINGERPRINT, '渠道服账号管理')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.resize(700, 600)
        self.setWindowTitle('IDV登录器')
        self.setWindowIcon(QIcon(dirPrefix('assets/icon.webp')))


if __name__ == '__main__':
    if not is_admin():
        print("Script is not running as admin, attempting to elevate privileges...")
        run_as_admin()
    else:
        app = QApplication(sys.argv)
        # 创建翻译器实例，生命周期必须和 app 相同
        translator = FluentTranslator()
        app.installTranslator(translator)
        # 创建主界面实例
        runtime_log.info('主页面启动')
        _ = Main()
        try:
            _.show()
            app.exec()
        except Exception as e:
            runtime_log.exception(f"程序异常退出: {e}")
        runtime_log.info('程序退出')
        stop_proxy()
