from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
import requests

BASE_URL = "http://127.0.0.1:5000"


class BooksTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # 🔹 widget.py 참조
        self.parent = parent

        # ===== 레이아웃 =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ===== 테이블 =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "제목", "저자", "출판사", "대여상태", "등록일"]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        layout.addWidget(self.table)

        # ===== 버튼 영역 =====
        btn_row = QHBoxLayout()

        self.btn_rent = QPushButton("대여하기")
        self.btn_rent.setFixedWidth(120)
        self.btn_rent.clicked.connect(self.rent_book)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_rent)

        layout.addLayout(btn_row)

    # =========================
    # 로그인 후 호출
    # =========================
    def load(self):
        """
        widget.py 에서 로그인 성공 후 호출됨
        """
        try:
            r = requests.get(f"{BASE_URL}/books", timeout=4)
            data = r.json()
            books = data.get("books", [])
        except Exception as e:
            QMessageBox.critical(self, "오류", f"책 목록 불러오기 실패\n\n{e}")
            return

        self.table.setRowCount(len(books))

        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(str(book.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(book.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(book.get("author", "")))
            self.table.setItem(row, 3, QTableWidgetItem(book.get("publisher", "")))

            rented = "대여중" if book.get("is_rented") else "대여가능"
            self.table.setItem(row, 4, QTableWidgetItem(rented))

            self.table.setItem(row, 5, QTableWidgetItem(str(book.get("created_at", ""))))

        self.table.resizeColumnsToContents()

    # =========================
    # 대여 처리
    # =========================
    def rent_book(self):
        if not self.parent.login_user:
            QMessageBox.warning(self, "오류", "로그인이 필요합니다.")
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "오류", "대여할 책을 선택하세요.")
            return

        book_id_item = self.table.item(row, 0)
        status_item = self.table.item(row, 4)

        if status_item.text() == "대여중":
            QMessageBox.warning(self, "불가", "이미 대여중인 책입니다.")
            return

        book_id = int(book_id_item.text())

        try:
            r = requests.post(
                f"{BASE_URL}/rent",
                json={
                    "user_id": self.parent.login_user,
                    "book_id": book_id
                },
                timeout=4
            )
        except Exception as e:
            QMessageBox.critical(self, "오류", f"대여 요청 실패\n\n{e}")
            return

        if r.status_code == 200:
            QMessageBox.information(self, "완료", "대여되었습니다.")
            self.load()                       # 책 목록 갱신
            self.parent.tab_rentals.load()    # 대여 목록 갱신
        elif r.status_code == 409:
            QMessageBox.warning(self, "실패", "이미 대여중인 책입니다.")
        else:
            QMessageBox.warning(self, "실패", "대여 실패")
