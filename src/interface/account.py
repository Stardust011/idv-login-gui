from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QHeaderView, \
    QWidget
from qfluentwidgets import PrimaryPushButton, FluentIcon, InfoBar, \
    InfoBarPosition, LineEdit, PushButton, TableWidget, GroupHeaderCardWidget

from src.accountManage import AccountManage, CheckLoginFinishThread


class AccountInterface(QFrame):
    # 初始化Widget类，继承自QFrame
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)  # 调用父类的构造函数

        self.check_login_thread = CheckLoginFinishThread()

        # 给子界面设置全局唯一的对象名
        self.setObjectName('AccountInterface')

        self.table = TableWidget(parent=self)
        # 设置表格大小
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(5, 2, 5, 2)
        # self.table.setSpacing(5)
        self.table.setContentsMargins(5, 2, 5, 2)
        self.vBoxLayout.addWidget(self.table)
        # width = self.parent().width()
        # height = self.parent().height()
        # self.table.setGeometry(0, 0, width+200, height)

        # 启用边框并设置圆角
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)

        self.table.setWordWrap(False)
        self.table.setRowCount(5)
        self.table.setColumnCount(5)

        self.account_manage = AccountManage()
        for i, account in enumerate(self.account_manage.accounts):
            self.table.setItem(i, 0, QTableWidgetItem(account['uuid']))
            self.table.setItem(i, 1, QTableWidgetItem(account['name']))
            self.table.setItem(i, 2, QTableWidgetItem(account['create_time']))
            self.table.setItem(i, 3, QTableWidgetItem(account['last_login_time']))
            self.table.setCellWidget(i, 4, self.button_for_row(id=i))

        header_labels = ['账号UUID', '别名', '创建时间', '最后登录时间', '操作']
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.verticalHeader().hide()

        # 设置QHeaderView::ResizeToContents
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.account_add_card = AccountAddCard(parent=self)
        self.vBoxLayout.addWidget(self.account_add_card)

    def button_for_row(self, id):
        widget = QWidget()
        login_button = PushButton(FluentIcon.CHEVRON_RIGHT_MED, '登录', self)
        login_button.clicked.connect(lambda: self.login_account(id))
        more_button = PushButton(FluentIcon.MORE, '更多', self)
        more_button.clicked.connect(lambda: self.show_more(id))

        hLayout = QHBoxLayout()
        hLayout.addWidget(login_button)
        hLayout.addWidget(more_button)
        hLayout.setContentsMargins(5, 0, 5, 0)
        # hLayout.setSpacing(0)
        widget.setLayout(hLayout)
        return widget

    def login_account(self, id: int):
        InfoBar.info(
            title='',
            content="正在登录账号...",
            orient=Qt.Horizontal,
            # isClosable=True,
            position=InfoBarPosition.BOTTOM,
            parent=self
        )
        # 禁用全部登录按钮
        for i in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(i, 4)
            if cell_widget is not None:
                cell_widget.layout().itemAt(0).widget().setEnabled(False)
        self.account_manage.login_account(id)
        self.check_login_thread.start()
        self.check_login_thread.check_login_finish_signal.connect(self.check_login_finish)

    def show_more(self, id: int):
        pass

    def check_login_finish(self, status):
        if status == 0:
            InfoBar.success(
                title='',
                content="登录成功",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
        elif status == 1:
            InfoBar.error(
                title='',
                content="登录失败",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
        elif status == -1:
            InfoBar.warning(
                title='',
                content="请先启动代理",
                orient=Qt.Horizontal,
                # isClosable=True,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
        # 启用全部登录按钮
        for i in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(i, 4)
            if cell_widget is not None:
                cell_widget.layout().itemAt(0).widget().setEnabled(True)


class AccountAddCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("添加账号")
        self.setBorderRadius(8)

        self.lineEdit = LineEdit()
        self.lineEdit.setPlaceholderText("请输入账号UUID")
        self.addButton = PrimaryPushButton(FluentIcon.ADD, "添加")
        self.addButton.clicked.connect(self.add_account)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.addWidget(self.addButton)
        self.hBoxLayout.setContentsMargins(5, 5, 5, 5)
        self.hBoxLayout.setSpacing(5)

        self.vBoxLayout.addLayout(self.hBoxLayout)

    def add_account(self):
        pass
