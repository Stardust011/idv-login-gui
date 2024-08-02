import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QApplication
from qfluentwidgets import PrimaryPushButton, FluentIcon, InfoBar, \
    InfoBarPosition, PushButton, ElevatedCardWidget, ImageLabel, \
    LargeTitleLabel

from src.app import start_app_with_explorer, create_shortcut, stop_proxy, StartProxyThread
from src.component.gamePathMessageBox import GamePathMessageBox
from src.config import cfg
from src.dirPrefix import dirPrefix
from src.runtimeLog import runtime_log


class HomeInterface(QFrame):
    # 初始化Widget类，继承自QFrame
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)  # 调用父类的构造函数
        # 防止卡顿无响应，将耗时操作放到子线程中
        self.start_proxy_thread = StartProxyThread()
        self.auto_start = False
        # 给子界面设置全局唯一的对象名
        self.setObjectName('HomeInterface')

        self.vBoxLayout = QVBoxLayout(self)
        # self.hBoxLayout = QHBoxLayout(self)  # 创建一个水平布局
        # self.top_info_bar_manager = TopInfoBarManager()

        # self.label = SubtitleLabel('快捷启动', self)  # 创建一个子标题标签，文本为传入的text
        # 创建按钮
        self.once_start_button = PrimaryPushButton(FluentIcon.PLAY, '   一键启动', self)
        self.once_start_button.setFixedSize(600, 50)
        self.once_start_button.setToolTip("一键启动代理并启动游戏")
        self.once_start_button.setIconSize(QSize(26, 26))
        # self.once_start_button.setFont(fontSize=26)
        self.once_start_button.clicked.connect(self.once_start)

        self.start_proxy_button = PrimaryPushButton(FluentIcon.SEND, '   启动代理', self)
        self.start_proxy_button.setFixedSize(600, 50)
        self.start_proxy_button.setIconSize(QSize(26, 26))
        self.start_proxy_button.clicked.connect(self.start_proxy)

        self.start_game_button = PrimaryPushButton(FluentIcon.GAME, '   启动游戏', self)
        self.start_game_button.setFixedSize(600, 50)
        self.start_game_button.setIconSize(QSize(26, 26))
        self.start_game_button.clicked.connect(self.start_game)

        self.close_proxy_button = PushButton(FluentIcon.CLOSE, '   关闭代理', self)
        self.close_proxy_button.setFixedSize(600, 50)
        self.close_proxy_button.setIconSize(QSize(26, 26))
        self.close_proxy_button.clicked.connect(self.close_proxy)

        # setFont(self.label, 24)  # 设置标签的字体大小为24
        # self.label.setAlignment(Qt.AlignLeft)  # 设置标签的文本对齐方式为

        # 添加至布局
        # self.vBoxLayout.addWidget(self.label, 1, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.once_start_button, 1, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.start_proxy_button, 1, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.start_game_button, 1, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.close_proxy_button, 1, Qt.AlignCenter)
        # 创建一个分割线
        self.vBoxLayout.addSpacing(50)

        # self.once_start_card = EmojiCard('NotoHuggingFace.svg', '一键启动')
        # self.once_start_card.clicked.connect(self.once_start)
        # self.vBoxLayout.addWidget(self.once_start_card, 1, Qt.AlignCenter)
        # self.start_proxy_card = EmojiCard('NotoGrinningFaceWithSweat.svg', '启动代理')
        # self.start_proxy_card.clicked.connect(self.start_proxy)
        # self.vBoxLayout.addWidget(self.start_proxy_card, 1, Qt.AlignCenter)
        # self.start_game_card = EmojiCard('NotoFoldedHands.svg', '启动游戏')
        # self.start_game_card.clicked.connect(self.start_game)
        # self.vBoxLayout.addWidget(self.start_game_card, 1, Qt.AlignCenter)
        # self.close_proxy_card = EmojiCard('NotoSmilingFaceWithHearts.svg', '关闭代理')
        # self.close_proxy_card.clicked.connect(self.close_proxy)
        # self.vBoxLayout.addWidget(self.close_proxy_card, 1, Qt.AlignCenter)

    def once_start(self):
        self.auto_start = True
        # 检测是否存在游戏路径
        self.check_game_path()
        # 启动代理
        self.start_proxy()

    def check_game_path(self):
        # 检测是否存在游戏路径
        # ink_path = r'C:\ProgramData\idv-login\dwrg.lnk'
        ink_path = os.path.join(cfg.get(cfg.workDir), 'dwrg.lnk')
        if not os.path.exists(ink_path):
            runtime_log.info(f"游戏路径不存在，正在创建快捷方式")
            # 弹出对话框
            msg_box = GamePathMessageBox(parent=self)
            if msg_box.exec():
                runtime_log.info(f"选择了游戏路径: {msg_box.pathEdit.currentText()}")
                # 创建快捷方式
                create_shortcut(target_path=msg_box.pathEdit.currentText())

            InfoBar.success(
                title='',
                content="设置已更新",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )

    def start_proxy(self):
        # 禁用按钮
        self.once_start_button.setEnabled(False)
        self.start_proxy_button.setEnabled(False)
        QApplication.processEvents()
        # 启动代理
        self.start_proxy_thread.start()
        # 连接信号
        self.start_proxy_thread.start_proxy_signal.connect(self.start_proxy_callback)

    def start_proxy_callback(self, status):
        if status:
            # 启动成功
            InfoBar.success(
                title='',
                content="代理已启动",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
        else:
            # 启动失败
            InfoBar.error(
                title='',
                content="代理启动失败, 请尝试重启电脑",
                orient=Qt.Horizontal,
                # isClosable=True,
                duration=-1,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
        if self.auto_start:
            # 启动游戏
            self.start_game()
            self.auto_start = False
            # 启动成功
            InfoBar.success(
                title='',
                content="游戏已启动",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )

    def start_game(self):
        self.check_game_path()
        start_app_with_explorer()

    def close_proxy(self):
        stop_proxy()
        # 关闭成功
        InfoBar.success(
            title='',
            content="代理已关闭",
            orient=Qt.Horizontal,
            # isClosable=True,
            position=InfoBarPosition.BOTTOM,
            parent=self
        )
        self.once_start_button.setEnabled(True)
        self.start_proxy_button.setEnabled(True)


class EmojiCard(ElevatedCardWidget):

    def __init__(self, iconName: str, name: str, parent=None):
        super().__init__(parent)
        iconPath = dirPrefix(f'assets/icon/{iconName}')
        self.iconWidget = ImageLabel(iconPath, self)
        self.label = LargeTitleLabel(name, self)

        self.iconWidget.scaledToHeight(70)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setAlignment(Qt.AlignCenter)
        # self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        # self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignCenter)

        self.setFixedSize(700, 100)
