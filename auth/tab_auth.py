from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
import requests

BASE_URL = "http://127.0.0.1:5000"


class AuthTab(QWidget):
    """
    로그인/회원가입 화면
    로그인 성공하면 parent(Widget)의 on_login_success(user_id, role) 호출
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        root = QVBoxLayout(self)
        root.setContentsMargins(220, 120, 220, 120)
        root.setSpacing(12)

        title = QLabel("도서관리 프로그램")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        root.addWidget(title)

        self.auth_tabs = QTabWidget()
        self.auth_tabs.setStyleSheet("QTabBar::tab { height: 30px; width: 120px; }")
        root.addWidget(self.auth_tabs)

        # =========================
        # 로그인 탭
        # =========================
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(10)

        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("아이디")

        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("비밀번호")
        self.input_pw.setEchoMode(QLineEdit.Password)

        btn_login = QPushButton("로그인")
        btn_login.setFixedHeight(40)
        btn_login.clicked.connect(self.login)

        login_layout.addWidget(QLabel("아이디"))
        login_layout.addWidget(self.input_id)
        login_layout.addWidget(QLabel("비밀번호"))
        login_layout.addWidget(self.input_pw)
        login_layout.addSpacing(8)
        login_layout.addWidget(btn_login)

        # =========================
        # 회원가입 탭
        # =========================
        signup_tab = QWidget()
        signup_layout = QVBoxLayout(signup_tab)
        signup_layout.setSpacing(10)

        self.signup_id = QLineEdit()
        self.signup_id.setPlaceholderText("아이디")

        self.signup_pw = QLineEdit()
        self.signup_pw.setPlaceholderText("비밀번호")
        self.signup_pw.setEchoMode(QLineEdit.Password)

        self.signup_pw2 = QLineEdit()
        self.signup_pw2.setPlaceholderText("비밀번호 확인")
        self.signup_pw2.setEchoMode(QLineEdit.Password)

        btn_signup = QPushButton("회원가입")
        btn_signup.setFixedHeight(40)
        btn_signup.clicked.connect(self.signup)

        signup_layout.addWidget(QLabel("아이디"))
        signup_layout.addWidget(self.signup_id)
        signup_layout.addWidget(QLabel("비밀번호"))
        signup_layout.addWidget(self.signup_pw)
        signup_layout.addWidget(QLabel("비밀번호 확인"))
        signup_layout.addWidget(self.signup_pw2)
        signup_layout.addSpacing(8)
        signup_layout.addWidget(btn_signup)

        self.auth_tabs.addTab(login_tab, "로그인")
        self.auth_tabs.addTab(signup_tab, "회원가입")

        # 스타일(선택)
        self.setStyleSheet("""
            QWidget { font-family: 'Malgun Gothic'; font-size: 13px; }
            QLineEdit {
                height: 36px; padding: 6px 10px;
                border: 1px solid #ccc; border-radius: 6px;
            }
            QPushButton {
                height: 36px; border-radius: 6px;
                background-color: #4f46e5; color: white; font-weight: bold;
            }
            QPushButton:hover { background-color: #4338ca; }
        """)

    def _json(self, resp):
        try:
            return resp.json()
        except Exception:
            return {}

    # =========================
    # 회원가입
    # =========================
    def signup(self):
        user_id = self.signup_id.text().strip()
        pw = self.signup_pw.text().strip()
        pw2 = self.signup_pw2.text().strip()

        if not user_id or not pw:
            QMessageBox.warning(self, "오류", "아이디/비밀번호를 입력하세요.")
            return
        if pw != pw2:
            QMessageBox.warning(self, "오류", "비밀번호 확인이 일치하지 않습니다.")
            return

        try:
            r = requests.post(f"{BASE_URL}/signup", json={"id": user_id, "password": pw}, timeout=4)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "오류", f"회원가입 요청 실패\n\n{e}")
            return

        if r.status_code == 200:
            QMessageBox.information(self, "성공", "회원가입 완료! 로그인 탭으로 이동합니다.")
            self.signup_id.clear()
            self.signup_pw.clear()
            self.signup_pw2.clear()
            self.auth_tabs.setCurrentIndex(0)
        elif r.status_code == 409:
            QMessageBox.warning(self, "실패", "중복 ID입니다.")
        else:
            QMessageBox.warning(self, "실패", "회원가입 실패")

    # =========================
    # 로그인
    # =========================
    def login(self):
        user_id = self.input_id.text().strip()
        pw = self.input_pw.text().strip()

        if not user_id or not pw:
            QMessageBox.warning(self, "오류", "아이디/비밀번호를 입력하세요.")
            return

        try:
            r = requests.post(f"{BASE_URL}/login", json={"id": user_id, "password": pw}, timeout=4)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "오류", f"서버 연결 실패\n\n{e}")
            return

        if r.status_code != 200:
            QMessageBox.warning(self, "실패", "로그인 실패")
            return

        data = self._json(r)
        login_user = data.get("user_id")
        role = (data.get("role") or "USER").strip()

        # ✅ Widget에 로그인 성공 전달
        self.parent.on_login_success(login_user, role)

        # 입력창 정리
        self.input_pw.clear()
