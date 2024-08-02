from qfluentwidgets import MessageBoxBase, SubtitleLabel, EditableComboBox

from src.app import read_reg_value


class GamePathMessageBox(MessageBoxBase):
    """ Custom message box for selecting game path """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hideCancelButton()
        self.titleLabel = SubtitleLabel('选择游戏路径', self)
        self.pathItem = read_reg_value()
        self.pathEdit = EditableComboBox()
        self.pathEdit.addItems(self.pathItem)

        self.pathEdit.setPlaceholderText('选择或输入游戏路径')
        self.pathEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.pathEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
