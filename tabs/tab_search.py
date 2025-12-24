from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
import requests

BASE_URL = "http://127.0.0.1:5000"


class SearchTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ===== 검색 영역 =====
        row = QHBoxLayout()
        self.input_keyword = QLineEdit()
        self.input_keyword.setPlaceholderText("도서 제목 / 키워드 입력")

        btn_search = QPushButton("검색")
        btn_search.clicked.connect(self.search)

        btn_new = QPushButton("신작 도서 조회")
        btn_new.clicked.connect(self.load_new)

        row.addWidget(self.input_keyword)
        row.addWidget(btn_search)
        row.addWidget(btn_new)

        # ===== 결과 테이블 =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["제목", "저자", "출판사"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addLayout(row)
        layout.addWidget(self.table)

    def _json(self, resp):
        try:
            return resp.json()
        except Exception:
            return {}

    def search(self):
        keyword = self.input_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "오류", "검색어를 입력하세요.")
            return

        try:
            r = requests.get(f"{BASE_URL}/book-search", params={"q": keyword}, timeout=6)
            data = self._json(r)
            books = data.get("books", [])
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "오류", f"도서 검색 실패\n\n{e}")
            return

        self.table.setRowCount(len(books))
        for i, b in enumerate(books):
            self.table.setItem(i, 0, QTableWidgetItem(b.get("title", "")))
            self.table.setItem(i, 1, QTableWidgetItem(b.get("author", "")))
            self.table.setItem(i, 2, QTableWidgetItem(b.get("publisher", "")))

    def load_new(self):
        try:
            r = requests.get(f"{BASE_URL}/book-new", timeout=6)
            data = self._json(r)
            books = data.get("books", [])
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "오류", f"신작 도서 조회 실패\n\n{e}")
            return

        self.table.setRowCount(len(books))
        for i, b in enumerate(books):
            self.table.setItem(i, 0, QTableWidgetItem(b.get("title", "")))
            self.table.setItem(i, 1, QTableWidgetItem(b.get("author", "")))
            self.table.setItem(i, 2, QTableWidgetItem(b.get("publisher", "")))
