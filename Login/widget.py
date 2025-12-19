from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem
)


import requests



class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.login_user = None
        self.setWindowTitle("도서관리 프로그램")

        self.setMinimumSize(1024, 768)

        # =========================
        # 바깥 탭 위젯 (회원가입/로그인/메인)
        # =========================
        self.tab_widget = QTabWidget()

        # =========================
        # 로그인 탭
        # =========================
        tab_login = QWidget()
        login_layout = QVBoxLayout()

        self.line_id = QLineEdit()
        self.line_id.setPlaceholderText("아이디")

        self.line_pw = QLineEdit()
        self.line_pw.setPlaceholderText("비밀번호")
        self.line_pw.setEchoMode(QLineEdit.Password)

        btn_login = QPushButton("로그인")
        btn_login.clicked.connect(self.login_clicked)

        login_layout.addWidget(QLabel("로그인"))
        login_layout.addWidget(self.line_id)
        login_layout.addWidget(self.line_pw)
        login_layout.addWidget(btn_login)
        tab_login.setLayout(login_layout)

        # =========================
        # 회원가입 탭
        # =========================
        tab_signup = QWidget()
        signup_layout = QVBoxLayout()

        signup_layout.addWidget(QLabel("ID, Password 설정"))

        self.signup_id = QLineEdit()
        self.signup_id.setPlaceholderText("아이디")

        self.signup_pw = QLineEdit()
        self.signup_pw.setPlaceholderText("비밀번호")
        self.signup_pw.setEchoMode(QLineEdit.Password)

        btn_signup = QPushButton("회원가입")
        btn_signup.clicked.connect(self.signup_clicked)

        signup_layout.addWidget(self.signup_id)
        signup_layout.addWidget(self.signup_pw)
        signup_layout.addWidget(btn_signup)

        tab_signup.setLayout(signup_layout)

        # =========================
        # 메인 탭 (안쪽에 기능 탭 3개)
        # =========================
        tab_main = QWidget()
        main_layout = QVBoxLayout()

        self.main_tabs = QTabWidget()  # 메인 내부 탭

        # --- 회원정보 탭 ---
        tab_users = QWidget()
        users_layout = QVBoxLayout()

        self.lbl_user_id = QLabel("아이디: ")
        self.lbl_role = QLabel("권한: ")
        self.lbl_created = QLabel("가입일: ")

        self.new_pw = QLineEdit()
        self.new_pw.setPlaceholderText("새 비밀번호")
        self.new_pw.setEchoMode(QLineEdit.Password)

        btn_change_pw = QPushButton("비밀번호 변경")
        btn_change_pw.clicked.connect(self.change_password)

        users_layout.addWidget(self.lbl_user_id)
        users_layout.addWidget(self.lbl_role)
        users_layout.addWidget(self.lbl_created)
        users_layout.addWidget(self.new_pw)
        users_layout.addWidget(btn_change_pw)

        tab_users.setLayout(users_layout)

        # --- 책정보 탭 ---
        tab_books = QWidget()
        books_layout = QVBoxLayout()

        self.books_table = QTableWidget()
        self.books_table.setColumnCount(6)
        self.books_table.setHorizontalHeaderLabels(
            ["ID", "제목", "저자", "출판사", "대여상태", "등록일"]
        )
        self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.setSelectionMode(QTableWidget.SingleSelection)

        books_layout.addWidget(self.books_table)

        btn_rent = QPushButton("대여하기")
        btn_rent.clicked.connect(self.rent_selected_book)

        books_layout.addWidget(btn_rent)


        tab_books.setLayout(books_layout)

        # --- 대여 탭 ---
        tab_rentals = QWidget()
        rentals_layout = QVBoxLayout()

        self.rentals_table = QTableWidget()
        self.rentals_table.setColumnCount(5)
        self.rentals_table.setHorizontalHeaderLabels(
            ["대여ID", "책 제목", "저자", "대여일", "반납일"]
        )
        self.rentals_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rentals_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rentals_table.setSelectionMode(QTableWidget.SingleSelection)

        btn_return = QPushButton("반납하기")
        btn_return.clicked.connect(self.return_selected_rental)

        rentals_layout.addWidget(self.rentals_table)
        tab_rentals.setLayout(rentals_layout)

        self.main_tabs.addTab(tab_users, "회원정보")
        self.main_tabs.addTab(tab_books, "책정보")
        self.main_tabs.addTab(tab_rentals, "대여")

        main_layout.addWidget(self.main_tabs)
        rentals_layout.addWidget(btn_return)
        tab_main.setLayout(main_layout)

        # =========================
        # 탭 추가 (회원가입/로그인/메인)
        # =========================
        self.tab_widget.addTab(tab_signup, "회원가입")
        self.tab_widget.addTab(tab_login, "로그인")
        self.tab_widget.addTab(tab_main, "메인")

        # 로그인 전에는 메인 탭 잠금
        self.tab_widget.setTabEnabled(2, False)

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def login_clicked(self):
        user_id = self.line_id.text().strip()
        user_pw = self.line_pw.text().strip()

        if not user_id or not user_pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 입력하세요.")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/login",
                json={
                    "id": user_id,
                    "password": user_pw
                },
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()

                if data["result"] == "success":
                    self.login_user = data["user_id"]

                    QMessageBox.information(self, "성공", "로그인 성공!")

                    # 메인 탭 활성화
                    self.tab_widget.setTabEnabled(2, True)
                    self.tab_widget.setCurrentIndex(2)

                    # 로그인 성공 후 로그인/회원가입 탭 비활성화
                    self.tab_widget.setTabEnabled(0, False)  # 회원가입
                    self.tab_widget.setTabEnabled(1, False)  # 로그인

                    self.load_my_info()
                    self.load_books()


                else:
                    QMessageBox.warning(self, "실패", "로그인 실패")
            else:
                QMessageBox.warning(self, "실패", "로그인 실패")

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def signup_clicked(self):
        user_id = self.signup_id.text().strip()
        user_pw = self.signup_pw.text().strip()

        if not user_id or not user_pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 입력하세요.")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/signup",
                json={
                    "id": user_id,
                    "password": user_pw
                },
                timeout=3
            )

            if response.status_code == 200:
                QMessageBox.information(self, "성공", "회원가입 성공! 로그인 해주세요.")

                # 입력창 초기화
                self.signup_id.clear()
                self.signup_pw.clear()

                # 로그인 탭으로 이동
                self.tab_widget.setCurrentIndex(1)

            elif response.status_code == 409:
                QMessageBox.warning(self, "실패", "이미 존재하는 아이디입니다.")
            else:
                QMessageBox.warning(self, "실패", "회원가입 실패")

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def load_my_info(self):
        try:
            r = requests.post(
                "http://127.0.0.1:5000/me",
                json={"id": self.login_user},
                timeout=3
            )
            data = r.json()

            if data["result"] == "success":
                u = data["user"]
                self.lbl_user_id.setText(f"아이디: {u['user_id']}")
                self.lbl_role.setText(f"권한: {u['role']}")

                created = u.get("created_at")

                if not created:
                    created_date = "-"
                else:
                    # datetime이면 strftime 가능, 문자열이면 앞 10글자 사용
                    if hasattr(created, "strftime"):
                        created_date = created.strftime("%Y-%m-%d")
                    else:
                        created_date = str(created)[:10]

                self.lbl_created.setText(f"가입일: {created_date}")


            else:
                QMessageBox.warning(self, "오류", "회원정보를 불러오지 못했습니다.")

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def change_password(self):
        pw = self.new_pw.text().strip()
        if not pw:
            QMessageBox.warning(self, "오류", "새 비밀번호를 입력하세요.")
            return

        try:
            r = requests.post(
                "http://127.0.0.1:5000/change-password",
                json={"id": self.login_user, "password": pw},
                timeout=3
            )

            if r.status_code == 200:
                QMessageBox.information(self, "성공", "비밀번호가 변경되었습니다.")
                self.new_pw.clear()
            else:
                QMessageBox.warning(self, "실패", "비밀번호 변경 실패")

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def load_books(self):
        try:
            r = requests.get("http://127.0.0.1:5000/books", timeout=3)
            data = r.json()

            if data.get("result") != "success":
                QMessageBox.warning(self, "오류", "책 목록을 불러오지 못했습니다.")
                return

            books = data.get("books", [])
            self.books_table.setRowCount(len(books))

            for row, b in enumerate(books):
                self.books_table.setItem(row, 0, QTableWidgetItem(str(b["id"])))
                self.books_table.setItem(row, 1, QTableWidgetItem(b["title"]))
                self.books_table.setItem(row, 2, QTableWidgetItem(b["author"]))
                self.books_table.setItem(row, 3, QTableWidgetItem(b.get("publisher") or ""))

                status = "대여중" if b["is_rented"] else "대여가능"
                self.books_table.setItem(row, 4, QTableWidgetItem(status))

                self.books_table.setItem(row, 5, QTableWidgetItem(str(b["created_at"])))

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def _get_selected_book_id(self):
        row = self.books_table.currentRow()
        if row < 0:
            return None
        item = self.books_table.item(row, 0)  # 0번 컬럼이 ID
        return int(item.text()) if item else None

    def rent_selected_book(self):
        book_id = self._get_selected_book_id()
        if not book_id:
            QMessageBox.warning(self, "오류", "책을 먼저 선택하세요.")
            return

        try:
            r = requests.post("http://127.0.0.1:5000/rent", json={"book_id": book_id, "user_id": self.login_user}, timeout=3)
            if r.status_code == 200:
                QMessageBox.information(self, "성공", "대여 완료!")
                self.load_books()
                self.load_my_rentals()
            elif r.status_code == 409:
                QMessageBox.warning(self, "실패", "이미 대여중인 책입니다.")
            else:
                QMessageBox.warning(self, "실패", "대여 실패")
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def return_selected_book(self):
        book_id = self._get_selected_book_id()
        if not book_id:
            QMessageBox.warning(self, "오류", "책을 먼저 선택하세요.")
            return

        try:
            r = requests.post("http://127.0.0.1:5000/return", json={"book_id": book_id}, timeout=3)
            if r.status_code == 200:
                QMessageBox.information(self, "성공", "반납 완료!")
                self.load_books()
                self.load_my_rentals()
            else:
                QMessageBox.warning(self, "실패", "반납 실패")
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def load_my_rentals(self):
        try:
            r = requests.post(
                "http://127.0.0.1:5000/my-rentals",
                json={"user_id": self.login_user},
                timeout=3
            )
            data = r.json()

            if data.get("result") != "success":
                QMessageBox.warning(self, "오류", "대여 목록을 불러오지 못했습니다.")
                return

            rows = data.get("rentals", [])
            self.rentals_table.setRowCount(len(rows))

            for row, r in enumerate(rows):
                self.rentals_table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.rentals_table.setItem(row, 1, QTableWidgetItem(r["title"]))
                self.rentals_table.setItem(row, 2, QTableWidgetItem(r["author"]))
                self.rentals_table.setItem(row, 3, QTableWidgetItem(r["rented_at"]))
                self.rentals_table.setItem(
                    row, 4, QTableWidgetItem(r["returned_at"] or "-")
                )

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

    def _get_selected_rental_id(self):
        row = self.rentals_table.currentRow()
        if row < 0:
            return None
        return int(self.rentals_table.item(row, 0).text())

    def return_selected_rental(self):
        rental_id = self._get_selected_rental_id()
        if not rental_id:
            QMessageBox.warning(self, "오류", "반납할 대여를 선택하세요.")
            return

        try:
            r = requests.post(
                "http://127.0.0.1:5000/return",
                json={"rental_id": rental_id},
                timeout=3
            )

            if r.status_code == 200:
                QMessageBox.information(self, "성공", "반납 완료")
                self.load_books()
                self.load_my_rentals()
            else:
                QMessageBox.warning(self, "실패", "반납 실패")

        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "서버 오류", "서버에 연결할 수 없습니다.")

