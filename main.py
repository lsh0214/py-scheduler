import sys
import os  # <<< 추가
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QCalendarWidget, QStackedWidget, QDialog, QHBoxLayout,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGridLayout, QCheckBox, QFrame
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon, QTextCharFormat, QColor

# ===================================================================
# ===== 리소스 경로를 찾는 헬퍼 함수 (추가) =========================
# ===================================================================
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller는 임시 폴더를 생성하고 그 경로를 _MEIPASS에 저장합니다.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ===================================================================


# 이번 주 일정 제목 라벨 (클릭 기능 없음)
class WeeklyTitleLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__("이번 주 일정", parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                font-size: 18px; 
                font-weight: bold; 
                color: white;
                background-color: #3498db;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                margin: 5px;
            }
        """)

class ScheduleTextLabel(QLabel):
    def __init__(self, schedule, parent=None):
        super().__init__(schedule.get('title', ''), parent)
        self.schedule_data = schedule
        self.setCursor(Qt.PointingHandCursor)
        self.setWordWrap(True)
        self.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                font-weight: 500;
                font-family: "맑은 고딕", "Segoe UI", Arial, sans-serif;
                padding: 2px 4px;
                margin: 1px 0;
                border: none;
                min-height: 16px;
                max-height: 20px;
            }
            QLabel:hover {
                color: #2980b9;
                font-weight: 600;
                text-decoration: underline;
            }
        """)

    def mousePressEvent(self, event):
        title = self.schedule_data.get('title', 'N/A')
        desc = self.schedule_data.get('desc', '없음')
        link = self.schedule_data.get('link', '')
        completed = self.schedule_data.get('completed', False)

        dialog = QDialog(self)
        dialog.setWindowTitle("스케줄 상세 정보")
        dialog.setFixedSize(320, 200)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(f"<b>제목:</b> {title}")
        title_label.setStyleSheet("font-size: 13px; color: #2c3e50;")
        layout.addWidget(title_label)

        desc_label = QLabel(f"<b>내용:</b> {desc}")
        desc_label.setStyleSheet("font-size: 12px; color: #34495e;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        if link:
            url_label = QLabel(f"<b>URL:</b> <a href='{link}'>{link}</a>")
            url_label.setOpenExternalLinks(True)
            url_label.setStyleSheet("font-size: 12px; color: #2980b9;")
        else:
            url_label = QLabel("<b>URL:</b> 없음")
            url_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(url_label)

        checkbox = QCheckBox("완료됨")
        checkbox.setChecked(completed)
        checkbox.setStyleSheet("margin-top: 10px;")
        layout.addWidget(checkbox)

        def update_schedule_status():
            self.schedule_data['completed'] = checkbox.isChecked()
            # 메인 윈도우 인스턴스를 찾아서 데이터 업데이트
            main_window = self.window()
            if isinstance(main_window, PySchedulerApp):
                main_window.save_schedules()
                main_window.update_weekly_schedule_list()
                main_window.show_date_schedules(main_window.selected_date)

        checkbox.stateChanged.connect(update_schedule_status)

        ok_button = QPushButton("확인")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignRight)

        dialog.exec_()

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule_data=None):
        super().__init__(parent)
        self.setWindowTitle("스케줄 추가/수정")
        self.setFixedSize(400, 350)

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

        self.completed_checkbox = QCheckBox("완료됨")
        self.layout.addWidget(self.completed_checkbox)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

        if schedule_data:
            self.title_input.setText(schedule_data.get('title', ''))
            self.desc_input.setPlainText(schedule_data.get('desc', ''))
            self.link_input.setText(schedule_data.get('link', ''))
            self.completed_checkbox.setChecked(schedule_data.get('completed', False))

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_schedule_data(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()
        link = self.link_input.text()
        completed = self.completed_checkbox.isChecked()
        return {"title": title, "desc": desc, "link": link, "completed": completed}

class DateShiftDialog(QDialog):
    """스케줄 불러오기 시 날짜 조정을 위한 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("시작 날짜 조정")
        self.setFixedSize(350, 300)
        
        layout = QVBoxLayout(self)
        
        self.checkbox = QCheckBox("새 시작 날짜 지정")
        layout.addWidget(self.checkbox)
        
        self.calendar = QCalendarWidget()
        self.calendar.setEnabled(False) # 처음에는 비활성화
        layout.addWidget(self.calendar)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("확인")
        self.cancel_button = QPushButton("취소")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.checkbox.stateChanged.connect(self.toggle_calendar)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def toggle_calendar(self, state):
        self.calendar.setEnabled(state == Qt.Checked)

    def get_selection(self):
        """사용자의 선택 결과를 반환합니다."""
        return self.checkbox.isChecked(), self.calendar.selectedDate()

class PySchedulerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.schedules = {}
        self.initUI()
        self.selected_date = QDate.currentDate()

    def initUI(self):
        self.setWindowTitle("Py스케줄러")
        # --- 수정된 부분 ---
        self.setWindowIcon(QIcon(resource_path('py.ico')))
        # -------------------
        self.setGeometry(100, 100, 1040, 600)

        self.main_stack = QStackedWidget(self)
        self.setCentralWidget(self.main_stack)

        self.create_main_menu()
        self.create_scheduler_page()

        self.load_schedules()

    def create_main_menu(self):
        main_menu_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 15, 20, 15)

        title_label = QLabel("파이썬으로 만든 스케줄러")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; margin: 10px;")
        main_layout.addWidget(title_label)
        
        self.week_title = WeeklyTitleLabel(self)
        main_layout.addWidget(self.week_title)

        day_labels_layout = QHBoxLayout()
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        for day_name in day_names:
            day_label = QLabel(day_name)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setFixedSize(140, 30)
            day_label.setStyleSheet("""
                font-size: 16px; 
                font-weight: bold; 
                color: #000000;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin: 1px;
            """)
            day_labels_layout.addWidget(day_label)
        main_layout.addLayout(day_labels_layout)

        self.weekly_grid_layout = QHBoxLayout()
        self.weekly_grid_layout.setSpacing(6)
        self.weekly_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.weekly_day_widgets = []
        
        for i in range(7):
            day_container = QFrame()
            day_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #333333;
                    border-radius: 5px;
                    min-height: 220px;
                    max-height: 220px;
                    min-width: 140px;
                    max-width: 140px;
                }
            """)
            
            day_layout = QVBoxLayout(day_container)
            day_layout.setContentsMargins(6, 6, 6, 6)
            day_layout.setSpacing(2)
            day_layout.addStretch()

            self.weekly_day_widgets.append(day_layout)
            self.weekly_grid_layout.addWidget(day_container)

        main_layout.addLayout(self.weekly_grid_layout)

        scheduler_btn = QPushButton("사용자 지정 스케줄")
        scheduler_btn.setFixedSize(250, 60)
        scheduler_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        scheduler_btn.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))
        main_layout.addWidget(scheduler_btn, alignment=Qt.AlignCenter)

        main_menu_widget.setLayout(main_layout)
        self.main_stack.addWidget(main_menu_widget)

    def create_scheduler_page(self):
        scheduler_widget = QWidget()
        layout = QVBoxLayout()

        top_btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("뒤로가기")
        self.save_file_btn = QPushButton("스케줄 저장")
        self.load_file_btn = QPushButton("스케줄 불러오기")
        
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d; color: white; padding: 8px 16px;
                border-radius: 6px; font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.save_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745; color: white; padding: 8px 16px;
                border-radius: 6px; font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.load_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; color: white; padding: 8px 16px;
                border-radius: 6px; font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #138496; }
        """)
        
        top_btn_layout.addWidget(self.back_btn)
        top_btn_layout.addStretch()
        top_btn_layout.addWidget(self.save_file_btn)
        top_btn_layout.addWidget(self.load_file_btn)
        layout.addLayout(top_btn_layout)

        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.show_date_schedules)
        layout.addWidget(self.calendar)

        saturday_format = QTextCharFormat()
        saturday_format.setForeground(QColor('blue'))
        self.calendar.setWeekdayTextFormat(Qt.Saturday, saturday_format)

        sunday_format = QTextCharFormat()
        sunday_format.setForeground(QColor('red'))
        self.calendar.setWeekdayTextFormat(Qt.Sunday, sunday_format)

        self.schedule_list = QListWidget()
        self.schedule_list.itemDoubleClicked.connect(self.edit_schedule)
        layout.addWidget(self.schedule_list)

        bottom_btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("스케줄 추가")
        self.delete_btn = QPushButton("스케줄 삭제")
        
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff; color: white; padding: 8px 16px;
                border-radius: 6px; font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545; color: white; padding: 8px 16px;
                border-radius: 6px; font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        
        bottom_btn_layout.addWidget(self.add_btn)
        bottom_btn_layout.addWidget(self.delete_btn)
        layout.addLayout(bottom_btn_layout)

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
            for i, schedule in enumerate(self.schedules[date_str]):
                title = schedule.get('title', '제목 없음') 
                item_text = f"{'✓' if schedule.get('completed', False) else '○'} {title}"
                
                if schedule.get('link'):
                    item_text += " [🔗]"
                
                item = QListWidgetItem(item_text)
                if schedule.get('completed', False):
                    item.setForeground(QColor('#888'))
                
                item.setData(Qt.UserRole, i)
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
            self.update_weekly_schedule_list()
            self.save_schedules() # 추가 시 자동 저장
            QMessageBox.information(self, "성공", "스케줄이 추가되었습니다.")

    def edit_schedule(self, item):
        row = item.data(Qt.UserRole)
        date_str = self.selected_date.toString("yyyy-MM-dd")
        schedule_data = self.schedules[date_str][row]

        dialog = ScheduleDialog(self, schedule_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_schedule_data()
            if not updated_data['title']:
                QMessageBox.warning(self, "경고", "스케줄 제목을 입력해주세요.")
                return
            
            self.schedules[date_str][row] = updated_data
            self.show_date_schedules(self.selected_date)
            self.update_weekly_schedule_list()
            self.save_schedules() # 수정 시 자동 저장
            QMessageBox.information(self, "성공", "스케줄이 수정되었습니다.")

    def delete_schedule(self):
        selected_item = self.schedule_list.currentItem()
        if selected_item:
            row = selected_item.data(Qt.UserRole)
            date_str = self.selected_date.toString("yyyy-MM-dd")

            if QMessageBox.question(self, "스케줄 삭제", "정말 삭제하시겠습니까?",
                                      QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                del self.schedules[date_str][row]
                if not self.schedules[date_str]:
                    del self.schedules[date_str]
                self.show_date_schedules(self.selected_date)
                self.update_weekly_schedule_list()
                self.save_schedules() # 삭제 시 자동 저장
                QMessageBox.information(self, "성공", "스케줄이 삭제되었습니다.")

    def save_schedules(self):
        try:
            with open('schedules.json', 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"자동 저장 오류: {e}")

    def update_weekly_schedule_list(self):
        for day_layout in self.weekly_day_widgets:
            while day_layout.count() > 1: # stretch를 제외하고 모두 제거
                child = day_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        today = QDate.currentDate()
        start_of_week = today.addDays(1 - today.dayOfWeek())

        for i in range(7):
            date = start_of_week.addDays(i)
            date_str = date.toString("yyyy-MM-dd")

            if date_str in self.schedules and self.schedules[date_str]:
                for schedule in self.schedules[date_str]:
                    schedule_text = ScheduleTextLabel(schedule, self)
                    schedule_text.setMaximumWidth(120)
                    schedule_text.setAlignment(Qt.AlignLeft)
                    self.weekly_day_widgets[i].insertWidget(self.weekly_day_widgets[i].count() - 1, schedule_text)
        self.update()
        QApplication.processEvents()
        
    def save_schedules_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "스케줄 저장", "schedules.json", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "저장 완료", f"{file_path}에 저장되었습니다.")

    def load_schedules_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "스케줄 불러오기", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_schedules = json.load(f)
            
            if not loaded_schedules:
                QMessageBox.information(self, "알림", "불러온 파일에 스케줄이 없습니다.")
                return

            dialog = DateShiftDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                adjust_date, new_start_date = dialog.get_selection()

                if adjust_date:
                    original_dates = [QDate.fromString(d, "yyyy-MM-dd") for d in loaded_schedules.keys()]
                    original_start_date = min(original_dates)
                    offset_days = original_start_date.daysTo(new_start_date)
                    
                    new_schedules = {}
                    for date_str, schedules_on_day in loaded_schedules.items():
                        original_date = QDate.fromString(date_str, "yyyy-MM-dd")
                        new_date = original_date.addDays(offset_days)
                        new_date_str = new_date.toString("yyyy-MM-dd")
                        new_schedules[new_date_str] = schedules_on_day
                    
                    self.schedules = new_schedules
                else:
                    self.schedules = loaded_schedules
            else:
                return

            for date_schedules in self.schedules.values():
                for schedule in date_schedules:
                    if 'completed' not in schedule:
                        schedule['completed'] = False
            
            self.show_date_schedules(self.selected_date)
            self.update_weekly_schedule_list()
            self.save_schedules()
            QMessageBox.information(self, "불러오기 완료", f"{file_path}에서 불러왔습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 불러오기 중 오류 발생: {e}")

    def load_schedules(self):
        try:
            with open('schedules.json', 'r', encoding='utf-8') as f:
                loaded_schedules = json.load(f)
            
            for date_schedules in loaded_schedules.values():
                for schedule in date_schedules:
                    if 'completed' not in schedule:
                        schedule['completed'] = False
            
            self.schedules = loaded_schedules
            self.update_weekly_schedule_list()
        except FileNotFoundError:
            self.schedules = {}
        except Exception as e:
            QMessageBox.critical(self, "오류", f"자동 불러오기 중 오류 발생: {e}")

    def closeEvent(self, event):
        self.save_schedules()
        
        reply = QMessageBox.question(self, '종료', '프로그램을 종료하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PySchedulerApp()
    ex.show()
    sys.exit(app.exec_())
