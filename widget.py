from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt

# ===== 탭 import =====
from auth.tab_auth import AuthTab

from tabs.tab_profile import ProfileTab
from tabs.tab_books import BooksTab
from tabs.tab_rentals import RentalsTab
from tabs.tab_search import SearchTab
from tabs.tab_admin import AdminTab
from tabs.tab_users import UsersTab


class Widget(QWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # 로그인 정보
        # =========================
        self.login_user = None
        self.user_role = None

        self.setWindowTitle("도서관리 프로그램")
        self.resize(1024, 768)

        # =========================
        # 최상위 레이아웃
        # =========================
        layout = QVBoxLayout(self)

        # =========================
        # 로그인 상태 표시
        # =========================
        self.lbl_login = QLabel("로그인: -")
        self.lbl_login.setAlignment(Qt.AlignRight)
        self.lbl_login.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_login)

        # =========================
        # 탭 위젯
        # =========================
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # =========================
        # 로그인 탭 (처음엔 이것만)
        # =========================
        self.tab_auth = AuthTab(self)
        self.tabs.addTab(self.tab_auth, "로그인")

    # =========================
    # 로그인 성공 시 호출
    # =========================
    def on_login_success(self, user_id: str, role: str):
        self.login_user = user_id
        self.user_role = role.upper()

        self.lbl_login.setText(f"로그인: {user_id} ({self.user_role})")

        # 기존 탭 제거
        self.tabs.clear()

        # =========================
        # 기본 탭 생성
        # =========================
        self.tab_profile = ProfileTab(self)
        self.tab_books = BooksTab(self)
        self.tab_rentals = RentalsTab(self)
        self.tab_search = SearchTab(self)

        self.tabs.addTab(self.tab_profile, "회원정보")
        self.tabs.addTab(self.tab_books, "책 목록")
        self.tabs.addTab(self.tab_rentals, "대여 목록")
        self.tabs.addTab(self.tab_search, "도서 검색")

        # 데이터 로드
        self.tab_profile.load()
        self.tab_books.load()
        self.tab_rentals.load()

        # =========================
        # 관리자 탭
        # =========================
        if self.user_role == "ADMIN":
            self.tab_admin = AdminTab(self)
            self.tabs.addTab(self.tab_admin, "관리자")
            self.tab_admin.load()

    # =========================
    # 로그아웃
    # =========================
    def logout(self):
        self.login_user = None
        self.user_role = None

        self.lbl_login.setText("로그인: -")

        # 모든 탭 제거 후 로그인 탭만 복구
        self.tabs.clear()
        self.tabs.addTab(self.tab_auth, "로그인")

        QMessageBox.information(self, "로그아웃", "로그아웃 되었습니다.")
