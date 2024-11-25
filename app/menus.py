from typing import Callable, TYPE_CHECKING

from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QMenu,
    QHBoxLayout,
    QWidgetAction,
    QWidget,
    QCheckBox,
    QLabel
)

from app.objects import Annotation
from app.styles.style_sheets import (
    CheckBoxStyleSheet,
    LabelStyleSheet,
    WidgetStyleSheet
)
from app.utils import text_to_color, pretty_text

if TYPE_CHECKING:
    from app.canvas import Canvas


class ContextMenu(QMenu):
    background_color = '#2a2b2f'
    hover_color = '#46464a'
    margins = 0, 0, 0, 0

    def __init__(self, parent: 'Canvas') -> None:
        super().__init__(parent)

    def add_menu_item(self, item: QWidget, binding: Callable) -> None:
        widget_action = QWidgetAction(self)

        widget = QWidget()
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        widget.setStyleSheet(str(WidgetStyleSheet(self.background_color)))

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(*self.margins)
        layout.addWidget(item)

        widget_action.setDefaultWidget(widget)
        widget_action.triggered.connect(binding)

        self.addAction(widget_action)

    def add_action(self,
                   label_text: str,
                   binding: Callable,
                   risky: bool
                   ) -> None:
        label = QLabel(label_text)
        label.setStyleSheet(str(LabelStyleSheet(risky)))

        self.add_menu_item(label, binding)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        event_type = event.type()

        if event_type in (QEvent.Type.HoverEnter, QEvent.Type.HoverMove):
            obj.setStyleSheet(f'background-color: {self.hover_color};')
        elif event_type == QEvent.Type.HoverLeave:
            obj.setStyleSheet(f'background-color: {self.background_color};')

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (Qt.MouseButton.RightButton & event.buttons()
                and self.rect().contains(event.pos())):
            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (Qt.MouseButton.RightButton == event.button()
                and self.rect().contains(event.pos())):
            return

        super().mouseReleaseEvent(event)


class CanvasContextMenu(ContextMenu):
    margins = 10, 7, 0, 7

    def __init__(self, parent: 'Canvas') -> None:
        super().__init__(parent)

        hidden_annos = parent.get_hidden_annotations()
        text, should_hide = ('Show All', False) \
            if hidden_annos else ('Hide All', True)

        def set_hidden_all() -> None:
            for anno in parent.annotations:
                anno.hidden = should_hide

            parent.update()

        self.add_action(text, set_hidden_all, False)
        self.addSeparator()

        for annotation in parent.annotations[::-1]:  # Prioritize newer annos
            self.add_anno_checkbox(parent, annotation)

    def add_anno_checkbox(self,
                          parent: 'Canvas',
                          annotation: Annotation
                          ) -> None:
        def flip_hidden(annotation: Annotation) -> None:
            if not annotation:
                return

            annotation.hidden = not annotation.hidden
            parent.update()

        checkbox = QCheckBox()
        checkbox.setChecked(not annotation.hidden)
        checkbox.stateChanged.connect(lambda: flip_hidden(annotation))

        label = pretty_text(annotation.label_name)
        padded_length = len(label) + 15

        checkbox.setText(label.ljust(padded_length))
        checkbox_color = text_to_color(annotation.label_name)

        checkbox.setStyleSheet(str(CheckBoxStyleSheet(
            checkbox_color, self.background_color)))

        self.add_menu_item(checkbox, flip_hidden)


class AnnotationContextMenu(ContextMenu):
    margins = 10, 6, 0, 6

    def __init__(self, parent: 'Canvas') -> None:
        super().__init__(parent)

        self.add_action('Rename', parent.rename_annotation, False)
        self.add_action('Hide', parent.hide_annotation, False)

        self.addSeparator()

        self.add_action('Delete', parent.delete_annotation, True)
