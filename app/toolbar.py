from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QToolBar, QToolButton

__tool_button_style__ = Qt.ToolButtonStyle.ToolButtonTextUnderIcon


class ToolBar(QToolBar):
    toolbar_actions = (
        'open_dir',
        'next_image',
        'prev_image'
    )

    def __init__(self, actions):
        super().__init__()

        for action_name in self.toolbar_actions:
            action = actions[action_name]

            button = ToolButton()
            button.setDefaultAction(action)
            button.setToolButtonStyle(__tool_button_style__)

            self.addWidget(button)


class ToolButton(QToolButton):
    def minimumSizeHint(self):
        return QSize(70, 60)