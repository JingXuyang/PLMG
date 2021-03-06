#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2019.2
# Email : muyanru345@163.com
###################################################################
import dayu_widgets.utils as utils
from dayu_widgets import dayu_theme
from dayu_widgets.mixin import property_mixin, cursor_mixin, focus_shadow_mixin
from dayu_widgets.qt import *


@property_mixin
@cursor_mixin
@focus_shadow_mixin
class MComboBox(QComboBox):
    Separator = '/'
    sig_value_changed = Signal(list)

    def __init__(self, parent=None):
        super(MComboBox, self).__init__(parent)
        self._root_menu = None
        self._display_formatter = utils.display_formatter
        self.setEditable(True)
        line_edit = self.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setTextMargins(4, 0, 4, 0)
        line_edit.setStyleSheet('background-color:transparent')
        # line_edit.setCursor(Qt.PointingHandCursor)
        line_edit.installEventFilter(self)
        self._has_custom_view = False
        self.set_value('')
        self.set_placeholder(self.tr('Please Select'))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._dayu_size = dayu_theme.default_size

    def get_dayu_size(self):
        """
        Get the push button height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value):
        """
        Set the avatar size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.lineEdit().setProperty('dayu_size', value)
        self.style().polish(self)

    dayu_size = Property(int, get_dayu_size, set_dayu_size)

    def set_formatter(self, func):
        self._display_formatter = func

    def set_placeholder(self, text):
        self.lineEdit().setPlaceholderText(text)

    def set_value(self, value):
        self.setProperty('value', value)

    def _set_value(self, value):
        self.lineEdit().setProperty('text', self._display_formatter(value))
        if self._root_menu:
            self._root_menu.set_value(value)

    def set_menu(self, menu):
        self._root_menu = menu
        self._root_menu.sig_value_changed.connect(self.sig_value_changed)
        self._root_menu.sig_value_changed.connect(self.set_value)

    def setView(self, *args, **kwargs):
        self._has_custom_view = True
        super(MComboBox, self).setView(*args, **kwargs)

    def showPopup(self):
        if self._has_custom_view:
            super(MComboBox, self).showPopup()
        else:
            QComboBox.hidePopup(self)
            self._root_menu.popup(self.mapToGlobal(QPoint(0, self.height())))

    def setCurrentIndex(self, index):
        raise NotImplementedError

    def eventFilter(self, widget, event):
        if widget is self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                self.showPopup()
        return super(MComboBox, self).eventFilter(widget, event)

    def huge(self):
        """Set MComboBox to huge size"""
        self.set_dayu_size(dayu_theme.huge)
        return self

    def large(self):
        """Set MComboBox to large size"""
        self.set_dayu_size(dayu_theme.large)
        return self

    def medium(self):
        """Set MComboBox to  medium"""
        self.set_dayu_size(dayu_theme.medium)
        return self

    def small(self):
        """Set MComboBox to small size"""
        self.set_dayu_size(dayu_theme.small)
        return self

    def tiny(self):
        """Set MComboBox to tiny size"""
        self.set_dayu_size(dayu_theme.tiny)
        return self
