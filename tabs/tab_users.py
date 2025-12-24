from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
import requests

BASE_URL = "http://127.0.0.1:5000"


class UsersTab(QWidget):
    """
    관리자 전용 회원 관리 탭
    - 회원 목록 조회
    - 회원 삭제
    """
    def __init__(self, parent):
        super().__init__(parent)

        # 🔹 부모(widget.py) 참조
        self.parent = parent

        # ===== 레이아웃 =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # ===== 제목 =====
        title = QLabel("회원 관리 (관리자 전용)")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        # ===== 회원 테이블 =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["아이디", "권한", "가입일"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        layout.addWidget(self.table)

        # ===== 삭제 버튼 =====
        btn_delete = QPushButton("선택 회원 삭제")
        btn_delete.setFixedWidth(160)
        btn_delete.clicked.connect(self.delete_user)

        layout.addWidget(btn_delete)

    # =========================
    # 회원 목록 로드
    # =========================
    def load(self):
        """
        widget.py 에서
        - 로그인 후
        - 관리자 탭 열릴 때 호출
        """
        try:
            r = requests.get(f"{BASE_URL}/users", timeout=4)
            if r.status_code != 200:
                raise Exception("서버 응답 오류")
            data = r.json()
            users = data.get("users", [])
        except Exception as e:
            QMessageBox.critical(self, "오류", f"회원 목록 조회 실패\n\n{e}")
            return

        self.table.setRowCount(len(users))
        for row, u in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(u.get("user_id", "")))
            self.table.setItem(row, 1, QTableWidgetItem(u.get("role", "")))
            self.table.setItem(row, 2, QTableWidgetItem(u.get("created_at", "")))

    # =========================
    # 회원 삭제
    # =========================
    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "오류", "삭제할 회원을 선택하세요.")
            return

        user_id = self.table.item(row, 0).text()

        if user_id.lower() == "admin":
            QMessageBox.warning(self, "불가", "관리자 계정은 삭제할 수 없습니다.")
            return

        confirm = QMessageBox.question(
            self,
            "회원 삭제",
            f"'{user_id}' 회원을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            r = requests.delete(f"{BASE_URL}/users/{user_id}", timeout=4)
            if r.status_code != 200:
                raise Exception("삭제 실패")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"회원 삭제 실패\n\n{e}")
            return

        QMessageBox.information(self, "완료", "회원 삭제 완료")
        self.load()
