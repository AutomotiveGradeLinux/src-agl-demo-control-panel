# Copyright (C) 2024 Suchinton Chakravarty
#
# SPDX-License-Identifier: Apache-2.0

import sys
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QBrush
from PyQt6.QtCore import pyqtProperty, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtWidgets import QApplication, QCheckBox


class AnimatedToggle(QCheckBox):
    """
    A custom toggle switch widget with animation effects.

    Inherits QCheckBox class from PyQt6.QtWidgets module.
    """

    bg_color = pyqtProperty(
        QColor, lambda self: self._bg_color,
        lambda self, col: setattr(self, '_bg_color', col))
    circle_color = pyqtProperty(
        QColor, lambda self: self._circle_color,
        lambda self, col: setattr(self, '_circle_color', col))
    active_color = pyqtProperty(
        QColor, lambda self: self._active_color,
        lambda self, col: setattr(self, '_active_color', col))
    disabled_color = pyqtProperty(
        QColor, lambda self: self._disabled_color,
        lambda self, col: setattr(self, '_disabled_color', col))
    circle_pos = pyqtProperty(
        float, lambda self: self._circle_pos,
        lambda self, pos: (setattr(self, '_circle_pos', pos), self.update()))
    intermediate_bg_color = pyqtProperty(
        QColor, lambda self: self._intermediate_bg_color,
        lambda self, col: setattr(self, '_intermediate_bg_color', col))

    def __init__(self, parent=None):
        """
        Constructs an AnimatedToggle object.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the toggle switch (default is None).

        """
        super().__init__(parent)
        self._bg_color = QColor("#965D62")
        self._circle_color = QColor("#DDD")
        self._active_color = QColor('#4BD7D6')
        self._disabled_color = QColor('#965D62')
        self._circle_pos = None
        self._intermediate_bg_color = None
        self._animation_duration = 500  # milliseconds
        self._user_checked = False

        self.setFixedHeight(28)
        self.stateChanged.connect(self.start_transition)

    def setDuration(self, duration: int):
        """
        Sets the duration of the animation.

        Parameters
        ----------
        duration : int
            The duration of the animation in milliseconds.

        """
        self._animation_duration = duration

    def update_pos_color(self, checked=None):
        self._circle_pos = self.height() * (1.1 if checked else 0.1)
        if self.isChecked():
            self._intermediate_bg_color = self._active_color
        else:
            self._intermediate_bg_color = self._bg_color

    def start_transition(self, state):
        if not self._user_checked:
            self.update_pos_color(state)
            return
        for anim in [self.create_animation, self.create_bg_color_animation]:
            animation = anim(state)
            animation.start()
        self._user_checked = False

    def mousePressEvent(self, event):
        self._user_checked = True
        super().mousePressEvent(event)

    def create_animation(self, state):
        return self._create_common_animation(state, b'circle_pos', self.height() * 0.1, self.height() * 1.1)

    def create_bg_color_animation(self, state):
        return self._create_common_animation(state, b'intermediate_bg_color', self._bg_color, self._active_color)

    def _create_common_animation(self, state, prop, start_val, end_val):
        animation = QPropertyAnimation(self, prop, self)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        animation.setDuration(self._animation_duration)
        animation.setStartValue(start_val if state else end_val)
        animation.setEndValue(end_val if state else start_val)
        return animation

    def showEvent(self, event):
        super().showEvent(event)
        self.update_pos_color(self.isChecked())

    def resizeEvent(self, event):
        self.update_pos_color(self.isChecked())

    def sizeHint(self):
        size = super().sizeHint()
        size.setWidth(self.height() * 2)
        return size

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        """
        Handles the paint event of the toggle switch.

        Parameters
        ----------
        event : QPaintEvent
            The paint event.

        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        circle_color = QColor(
            self.disabled_color if not self.isEnabled() else self.circle_color)
        bg_color = QColor(self.disabled_color if not self.isEnabled() else self.intermediate_bg_color) \
            if self.intermediate_bg_color is not None else QColor("transparent")

        border_radius = self.height() / 2
        toggle_width = self.height() * 2
        toggle_margin = self.height() * 0.3
        circle_size = self.height() * 0.8

        if self.circle_pos is None:
            self.update_pos_color(self.isChecked())

        bg_path = QPainterPath()
        bg_path.addRoundedRect(
            0, 0, toggle_width, self.height(), border_radius, border_radius)
        painter.fillPath(bg_path, QBrush(bg_color))

        circle = QPainterPath()
        circle.addEllipse(self.circle_pos, self.height()
                          * 0.1, circle_size, circle_size)
        painter.fillPath(circle, QBrush(circle_color))

        self.setStyleSheet(f"background-color: {bg_color.name()};")

        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimatedToggle()
    window.show()
    sys.exit(app.exec())
