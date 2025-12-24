from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel,
    QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
import requests

from tabs.tab_users import UsersTab


class AdminTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        main_layout = QVBoxLayout(self)

        # =========================
        # 관리자 제목
        # =========================
        title = QLabel("관리자 전용 기능")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        main_layout.addWidget(title)

        # =========================
        # 관리자 내부 탭
        # =========================
        self.admin_tabs = QTabWidget()
        main_layout.addWidget(self.admin_tabs)

        # =========================
        # [1] 회원 관리
        # =========================
        self.tab_users = UsersTab(self.parent)
        self.admin_tabs.addTab(self.tab_users, "회원 관리")

        # =========================
        # [2] 도서 관리
        # =========================
        self.tab_books = QWidget()
        self._setup_book_admin_ui()
        self.admin_tabs.addTab(self.tab_books, "도서 관리")

    # =========================
    # 도서 관리 UI
    # =========================
    def _setup_book_admin_ui(self):
        layout = QVBoxLayout(self.tab_books)

        # -------- 등록 영역 --------
        info = QLabel("도서 등록 (관리자)")
        info.setStyleSheet("font-weight: bold;")
        layout.addWidget(info)

        form = QFormLayout()

        self.input_title = QLineEdit()
        self.input_author = QLineEdit()
        self.input_publisher = QLineEdit()

        form.addRow("도서명", self.input_title)
        form.addRow("저자", self.input_author)
        form.addRow("출판사", self.input_publisher)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("도서 등록")
        self.btn_clear = QPushButton("입력 초기화")

        self.btn_add.clicked.connect(self.add_book)
        self.btn_clear.clicked.connect(self.clear_form)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        # -------- 도서 목록 --------
        list_label = QLabel("등록된 도서 목록")
        list_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(list_label)

        self.book_table = QTableWidget()
        self.book_table.setColumnCount(4)
        self.book_table.setHorizontalHeaderLabels(
            ["ID", "도서명", "저자", "출판사"]
        )
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.book_table)

        # -------- 삭제 버튼 --------
        self.btn_delete = QPushButton("선택 도서 삭제")
        self.btn_delete.clicked.connect(self.delete_book)
        layout.addWidget(self.btn_delete)

    # =========================
    # 도서 등록
    # =========================
    def add_book(self):
        title = self.input_title.text().strip()
        author = self.input_author.text().strip()
        publisher = self.input_publisher.text().strip()

        if not title or not author:
            QMessageBox.warning(self, "입력 오류", "도서명과 저자는 필수입니다.")
            return

        res = requests.post(
            "http://127.0.0.1:5000/books",
            json={
                "user_id": self.parent.login_user,
                "title": title,
                "author": author,
                "publisher": publisher
            }
        )

        if res.status_code == 200:
            QMessageBox.information(self, "성공", "도서가 등록되었습니다.")
            self.clear_form()
            self.load_books()                 # 관리자 목록 갱신
            self.parent.tab_books.load()      # 사용자 목록 갱신

        elif res.status_code == 409:
            QMessageBox.warning(self, "중복", "이미 등록된 도서입니다.")
        else:
            QMessageBox.warning(self, "실패", "도서 등록 실패")

    # =========================
    # 관리자 도서 목록 불러오기
    # =========================
    def load_books(self):
        res = requests.get("http://127.0.0.1:5000/books")
        data = res.json()

        books = data.get("books", [])
        self.book_table.setRowCount(len(books))

        for row, b in enumerate(books):
            self.book_table.setItem(row, 0, QTableWidgetItem(str(b["id"])))
            self.book_table.setItem(row, 1, QTableWidgetItem(b["title"]))
            self.book_table.setItem(row, 2, QTableWidgetItem(b["author"]))
            self.book_table.setItem(
                row, 3, QTableWidgetItem(b.get("publisher") or "")
            )

    # =========================
    # 도서 삭제
    # =========================
    def delete_book(self):
        row = self.book_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 오류", "삭제할 도서를 선택하세요.")
            return

        book_id = self.book_table.item(row, 0).text()

        res = requests.delete(
            f"http://127.0.0.1:5000/books/{book_id}",
            json={"user_id": self.parent.login_user}
        )

        if res.status_code == 200:
            QMessageBox.information(self, "삭제 완료", "도서가 삭제되었습니다.")
            self.load_books()
            self.parent.tab_books.load()
        else:
            QMessageBox.warning(self, "실패", "도서 삭제 실패")

    # =========================
    # 입력 초기화
    # =========================
    def clear_form(self):
        self.input_title.clear()
        self.input_author.clear()
        self.input_publisher.clear()

    # =========================
    # 관리자 탭 로드
    # =========================
    def load(self):
        self.tab_users.load()
        self.load_books()
