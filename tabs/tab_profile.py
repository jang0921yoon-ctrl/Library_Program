from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox
)
from PySide6.QtCore import Qt


class ProfileTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # 🔹 부모(widget.py) 참조
        self.parent = parent

        # ===== 레이아웃 =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # ===== 제목 =====
        title = QLabel("회원 정보")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        # ===== 정보 라벨 =====
        self.lbl_user_id = QLabel("아이디: -")
        self.lbl_role = QLabel("권한: -")
        self.lbl_created = QLabel("가입일: -")

        layout.addWidget(self.lbl_user_id)
        layout.addWidget(self.lbl_role)
        layout.addWidget(self.lbl_created)

        layout.addStretch()

        # ===== 로그아웃 버튼 =====
        btn_logout = QPushButton("로그아웃")
        btn_logout.setFixedWidth(120)
        btn_logout.clicked.connect(self.logout_clicked)

        layout.addWidget(btn_logout, alignment=Qt.AlignLeft)

    # =========================
    # 로그인 후 호출되는 함수
    # =========================
    def load(self):
        """
        widget.py 에서 로그인 성공 후 호출됨
        """
        user_id = self.parent.login_user
        role = self.parent.user_role

        self.lbl_user_id.setText(f"아이디: {user_id}")
        self.lbl_role.setText(f"권한: {role}")
        self.lbl_created.setText("가입일: -")  # 나중에 서버 연동

    # =========================
    # 로그아웃 버튼
    # =========================
    def logout_clicked(self):
        confirm = QMessageBox.question(
            self,
            "로그아웃",
            "로그아웃 하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.parent.logout()
