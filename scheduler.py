schedule#버전 2 수정버전
import sys
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QCalendarWidget, QStackedWidget, QDialog, QHBoxLayout,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCharFormat, QColor

class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("스케줄 추가/수정")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("스케줄 제목")
        self.layout.addWidget(QLabel("제목:"))
        self.layout.addWidget(self.title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("상세 내용")
        self.layout.addWidget(QLabel("상세 내용:"))
        self.layout.addWidget(self.desc_input)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("URL 링크 (선택 사항)")
        self.layout.addWidget(QLabel("링크:"))
        self.layout.addWidget(self.link_input)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_schedule_data(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()
        link = self.link_input.text()
        return {"title": title, "desc": desc, "link": link}

class PySchedulerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.schedules = {}  # {'YYYY-MM-DD': [{'title': '', 'desc': '', 'link': ''}, ...]}
        self.initUI()
        self.selected_date = QDate.currentDate()

    def initUI(self):
        self.setWindowTitle("Py스케줄러")
        self.setWindowIcon(QIcon('py.png'))
        self.setGeometry(100, 100, 800, 600)

        self.main_stack = QStackedWidget(self)
        self.setCentralWidget(self.main_stack)

        self.create_main_menu()
        self.create_scheduler_page()
        
        self.load_schedules() # 프로그램 시작 시 자동 불러오기

    def create_main_menu(self):
        main_menu_widget = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("파이썬으로만 제작한 스케줄러")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        scheduler_btn = QPushButton("사용자 지정 스케줄")
        scheduler_btn.setFixedSize(200, 50)
        scheduler_btn.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))
        layout.addWidget(scheduler_btn, alignment=Qt.AlignCenter)

        main_menu_widget.setLayout(layout)
        self.main_stack.addWidget(main_menu_widget)

    def create_scheduler_page(self):
        scheduler_widget = QWidget()
        layout = QVBoxLayout()
        
        # 상단 버튼 레이아웃
        top_btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("뒤로가기")
        self.save_file_btn = QPushButton("스케줄 저장")
        self.load_file_btn = QPushButton("스케줄 불러오기")
        top_btn_layout.addWidget(self.back_btn)
        top_btn_layout.addStretch()
        top_btn_layout.addWidget(self.save_file_btn)
        top_btn_layout.addWidget(self.load_file_btn)
        layout.addLayout(top_btn_layout)
        
        # 달력 및 스케줄 리스트
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.show_date_schedules)
        layout.addWidget(self.calendar)
        
        self.schedule_list = QListWidget()
        self.schedule_list.itemDoubleClicked.connect(self.open_link_or_edit)
        layout.addWidget(self.schedule_list)
        saturday_format = QTextCharFormat()
        saturday_format.setForeground(QColor('blue'))
        self.calendar.setWeekdayTextFormat(Qt.Saturday, saturday_format)


        
        # 하단 버튼 레이아웃
        bottom_btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("스케줄 추가")
        self.delete_btn = QPushButton("스케줄 삭제")
        bottom_btn_layout.addWidget(self.add_btn)
        bottom_btn_layout.addWidget(self.delete_btn)
        layout.addLayout(bottom_btn_layout)
        
        # 연결
        self.add_btn.clicked.connect(self.add_schedule)
        self.delete_btn.clicked.connect(self.delete_schedule)
        self.back_btn.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        self.save_file_btn.clicked.connect(self.save_schedules_to_file)
        self.load_file_btn.clicked.connect(self.load_schedules_from_file)

        scheduler_widget.setLayout(layout)
        self.main_stack.addWidget(scheduler_widget)
        
    def show_date_schedules(self, date):
        self.selected_date = date
        self.schedule_list.clear()
        date_str = date.toString("yyyy-MM-dd")
        
        if date_str in self.schedules:
            for schedule in self.schedules[date_str]:
                item_text = f"제목: {schedule['title']}"
                if schedule['link']:
                    item_text += " [🔗]"
                item = QListWidgetItem(item_text)
                self.schedule_list.addItem(item)
    
    def add_schedule(self):
        dialog = ScheduleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_schedule_data()
            if not data['title']:
                QMessageBox.warning(self, "경고", "스케줄 제목을 입력해주세요.")
                return

            date_str = self.selected_date.toString("yyyy-MM-dd")
            if date_str not in self.schedules:
                self.schedules[date_str] = []
            self.schedules[date_str].append(data)
            self.show_date_schedules(self.selected_date)
            QMessageBox.information(self, "성공", "스케줄이 추가되었습니다.")

    def delete_schedule(self):
        selected_item = self.schedule_list.currentItem()
        if selected_item:
            row = self.schedule_list.row(selected_item)
            date_str = self.selected_date.toString("yyyy-MM-dd")
            
            if QMessageBox.question(self, "스케줄 삭제", "정말 삭제하시겠습니까?", 
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                del self.schedules[date_str][row]
                self.show_date_schedules(self.selected_date)
                QMessageBox.information(self, "성공", "스케줄이 삭제되었습니다.")
    
    def open_link_or_edit(self, item):
        row = self.schedule_list.row(item)
        date_str = self.selected_date.toString("yyyy-MM-dd")
        schedule_data = self.schedules[date_str][row]
        
        if schedule_data['link']:
            webbrowser.open_new(schedule_data['link'])
        else:
            QMessageBox.information(self, "상세 보기", 
                                    f"제목: {schedule_data['title']}\n"
                                    f"내용: {schedule_data['desc']}")

    def save_schedules_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "스케줄 저장", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "저장 완료", f"{file_path}에 스케줄이 성공적으로 저장되었습니다.")

    def load_schedules_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "스케줄 불러오기", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.schedules = json.load(f)
                self.show_date_schedules(self.selected_date)
                QMessageBox.information(self, "불러오기 완료", f"{file_path}에서 스케줄을 성공적으로 불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일 불러오기 중 오류 발생: {e}")
                
    def load_schedules(self):
        # 기본적으로 'schedules.json' 파일을 찾아 자동으로 불러옵니다.
        try:
            with open('schedules.json', 'r', encoding='utf-8') as f:
                self.schedules = json.load(f)
        except FileNotFoundError:
            self.schedules = {}
        except Exception as e:
            QMessageBox.critical(self, "오류", f"자동 불러오기 중 오류 발생: {e}")
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '종료', '종료하기 전에 스케줄을 저장하시겠습니까?', 
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            self.save_schedules_to_file()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PySchedulerApp()
    ex.show()
    sys.exit(app.exec_())