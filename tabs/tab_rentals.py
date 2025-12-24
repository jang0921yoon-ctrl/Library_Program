from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
import requests

BASE_URL = "http://127.0.0.1:5000"


class RentalsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # 🔹 widget.py 참조
        self.parent = parent

        # ===== 레이아웃 =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ===== 테이블 =====
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["대여ID", "책 제목", "저자", "대여일"]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        layout.addWidget(self.table)

        # ===== 버튼 영역 =====
        btn_row = QHBoxLayout()

        self.btn_return = QPushButton("반납하기")
        self.btn_return.setFixedWidth(120)
        self.btn_return.clicked.connect(self.return_book)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_return)

        layout.addLayout(btn_row)

    # =========================
    # 로그인 후 호출
    # =========================
    def load(self):
        """
        widget.py 로그인 성공 후 호출됨
        """
        if not self.parent.login_user:
            return

        try:
            r = requests.post(
                f"{BASE_URL}/my-rentals",
                json={"user_id": self.parent.login_user},
                timeout=4
            )
            data = r.json()
            rentals = data.get("rentals", [])
        except Exception as e:
            QMessageBox.critical(self, "오류", f"대여 목록 불러오기 실패\n\n{e}")
            return

        self.table.setRowCount(len(rentals))

        for row, r in enumerate(rentals):
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("author", "")))
            self.table.setItem(row, 3, QTableWidgetItem(r.get("rented_at", "")))

        self.table.resizeColumnsToContents()

    # =========================
    # 반납 처리
    # =========================
    def return_book(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "오류", "반납할 대여를 선택하세요.")
            return

        rental_id_item = self.table.item(row, 0)
        rental_id = int(rental_id_item.text())

        confirm = QMessageBox.question(
            self,
            "확인",
            "선택한 책을 반납하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            r = requests.post(
                f"{BASE_URL}/return",
                json={"rental_id": rental_id},
                timeout=4
            )
        except Exception as e:
            QMessageBox.critical(self, "오류", f"반납 요청 실패\n\n{e}")
            return

        if r.status_code == 200:
            QMessageBox.information(self, "완료", "반납되었습니다.")
            self.load()                      # 내 대여 목록 갱신
            self.parent.tab_books.load()    # 책 목록 갱신
        else:
            QMessageBox.warning(self, "실패", "반납 실패")
