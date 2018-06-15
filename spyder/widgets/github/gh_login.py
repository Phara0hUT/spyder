# -*- coding: utf-8 -*-
# Copyright © QCrash - Colin Duquesnoy
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Login dialog to authenticate on Github.

Taken from the QCrash Project:
https://github.com/ColinDuquesnoy/QCrash
"""

import sys

from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import (QDialog, QFormLayout, QLabel, QLineEdit,
                            QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
                            QVBoxLayout, QWidget)

from spyder.config.base import _
from spyder.config.base import get_image_path
from spyder.py3compat import to_text_string


GH_MARK_NORMAL = get_image_path('GitHub-Mark.png')
GH_MARK_LIGHT = get_image_path('GitHub-Mark-Light.png')
TOKEN_URL = "https://github.com/settings/tokens/new?scopes=public_repo"


class DlgGitHubLogin(QDialog):
    """Dialog to submit error reports to Github."""

    def __init__(self, parent, username):
        super(DlgGitHubLogin, self).__init__(parent)

        title = _("Sign in to Github")
        self.resize(400, 340)
        self.setWindowTitle(title)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Header
        html = ('<html><head/><body><p align="center"><img src="{mark}"/></p>'
                '<p align="center">{title}</p></body></html>')
        mark = GH_MARK_NORMAL
        if self.palette().base().color().lightness() < 128:
            mark = GH_MARK_LIGHT
        lbl_html = QLabel(html.format(mark=mark, title=title))

        # Tabs
        tabs = QTabWidget()

        # Basic form layout
        basic_form_layout = QFormLayout()
        basic_form_layout.setContentsMargins(-1, 0, -1, -1)

        basic_lbl_msg = QLabel(_("For regular users, i.e. users <b>without</b> "
                                 "two-factor authentication enabled"))
        basic_lbl_msg.setWordWrap(True)
        basic_lbl_msg.setAlignment(Qt.AlignJustify)

        lbl_user = QLabel(_("Username:"))
        basic_form_layout.setWidget(0, QFormLayout.LabelRole, lbl_user)
        self.le_user = QLineEdit()
        self.le_user.textChanged.connect(self.update_btn_state)
        basic_form_layout.setWidget(0, QFormLayout.FieldRole, self.le_user)
        basic_form_layout.addRow("", QWidget())

        lbl_password = QLabel(_("Password: "))
        basic_form_layout.setWidget(2, QFormLayout.LabelRole, lbl_password)
        self.le_password = QLineEdit()
        self.le_password.setEchoMode(QLineEdit.Password)
        self.le_password.textChanged.connect(self.update_btn_state)
        basic_form_layout.setWidget(2, QFormLayout.FieldRole, self.le_password)

        # Basic auth tab
        basic_auth = QWidget()
        basic_layout = QVBoxLayout()
        basic_layout.addSpacerItem(QSpacerItem(QSpacerItem(0, 8)))
        basic_layout.addWidget(basic_lbl_msg)
        basic_layout.addSpacerItem(
            QSpacerItem(QSpacerItem(0, 1000, vPolicy=QSizePolicy.Expanding)))
        basic_layout.addLayout(basic_form_layout)
        basic_layout.addSpacerItem(
            QSpacerItem(QSpacerItem(0, 1000, vPolicy=QSizePolicy.Expanding)))
        basic_auth.setLayout(basic_layout)
        tabs.addTab(basic_auth, _("Password Only"))

        # Token form layout
        token_form_layout = QFormLayout()
        token_form_layout.setContentsMargins(-1, 0, -1, -1)

        token_lbl_msg = QLabel(_("For users <b>with</b> two-factor "
                                 "authentication enabled, or who prefer a "
                                 "per-app token authentication.<br><br>"
                                 "You can go <b><a href=\"{}\">here</a></b> "
                                 "and click \"Generate token\" at the bottom "
                                 "to create a new token to use for this, with "
                                 "the appropriate permissions.").format(TOKEN_URL))
        token_lbl_msg.setOpenExternalLinks(True)
        token_lbl_msg.setWordWrap(True)
        token_lbl_msg.setAlignment(Qt.AlignJustify)

        lbl_token = QLabel("Token: ")
        token_form_layout.setWidget(1, QFormLayout.LabelRole, lbl_token)
        self.le_token = QLineEdit()
        self.le_token.setEchoMode(QLineEdit.Password)
        self.le_token.textChanged.connect(self.update_btn_state)
        token_form_layout.setWidget(1, QFormLayout.FieldRole, self.le_token)

        # Token auth tab
        token_auth = QWidget()
        token_layout = QVBoxLayout()
        token_layout.addSpacerItem(QSpacerItem(QSpacerItem(0, 8)))
        token_layout.addWidget(token_lbl_msg)
        token_layout.addSpacerItem(
            QSpacerItem(QSpacerItem(0, 1000, vPolicy=QSizePolicy.Expanding)))
        token_layout.addLayout(token_form_layout)
        token_layout.addSpacerItem(
            QSpacerItem(QSpacerItem(0, 1000, vPolicy=QSizePolicy.Expanding)))
        token_auth.setLayout(token_layout)
        tabs.addTab(token_auth, _("Access Token"))

        # Sign in button
        self.bt_sign_in = QPushButton(_("Sign in"))
        self.bt_sign_in.clicked.connect(self.accept)
        self.bt_sign_in.setDisabled(True)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(lbl_html)
        layout.addWidget(tabs)
        layout.addWidget(self.bt_sign_in)
        self.setLayout(layout)

        # Final adjustments
        if username:
            self.le_user.setText(username)
            self.le_password.setFocus()
        else:
            self.le_user.setFocus()

        self.setFixedSize(self.width(), self.height())
        self.le_password.installEventFilter(self)
        self.le_user.installEventFilter(self)

    def eventFilter(self, obj, event):
        interesting_objects = [self.le_password, self.le_user]
        if obj in interesting_objects and event.type() == QEvent.KeyPress:
            if (event.key() == Qt.Key_Return and
                    event.modifiers() & Qt.ControlModifier and
                    self.bt_sign_in.isEnabled()):
                self.accept()
                return True
        return False

    def update_btn_state(self):
        user = to_text_string(self.le_user.text()).strip() != ''
        password = to_text_string(self.le_password.text()).strip() != ''
        token = to_text_string(self.le_token.text()).strip() != ''
        enable = (user and password) or token
        self.bt_sign_in.setEnabled(enable)

    @classmethod
    def login(cls, parent, username):
        dlg = DlgGitHubLogin(parent, username)
        if dlg.exec_() == dlg.Accepted:
            user = dlg.le_user.text()
            password = dlg.le_password.text()
            token = dlg.le_token.text()
            if token != '':
                return (token,)
            else:
                return user, password
        return None, None


def test():
    from spyder.utils.qthelpers import qapplication
    app = qapplication()
    dlg = DlgGitHubLogin(None, None)
    dlg.show()
    sys.exit(dlg.exec_())


if __name__ == "__main__":
    test()
