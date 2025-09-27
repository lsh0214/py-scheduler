# py-scheduler
파이썬으로만 제작한 개발자 지망생이 쓰기 좋은 스케줄러 프로그램입니다.

파이썬으로만 제작을 하였기에 개발자를 지망하는 이들에게는 쉽게 소스코드를 바꾸며 자유롭게 사용 가능한 툴을 목적으로 하는 작품입니다.

사용 방법:
해당 코드를 vs코드에 입력 및 사용하는 이미지 파일또한 같은 폴더 넣어두기 이후 필요한 라이브러리 다운을 위하여 터미널창에
pip install pyat5
입력
이후 
pyinstaller --onefile --windowed --icon="py.ico" --add-data="py.ico;." 파일명
입력 dist폴더에 exe형태로 실행파일이 있는 것이 확인 가능합니다.

💻 기술 스택 (Technology Stack)
이 프로그램은 다음의 기술들을 기반으로 만들어졌습니다.

GUI 프레임워크: PyQt5

파이썬에서 데스크톱 애플리케이션을 만들기 위한 가장 대표적인 라이브러리입니다.

QtWidgets: 버튼, 라벨, 캘린더, 레이아웃 등 화면을 구성하는 모든 시각적 요소(위젯)를 담당합니다.

QtCore: QDate (날짜 처리), Qt (시그널-슬롯) 등 프로그램의 핵심 기능을 담당합니다.

QtGui: QIcon (아이콘), QColor (색상) 등 그래픽 관련 요소를 담당합니다.

데이터 저장 및 관리: JSON

사용자의 스케줄 데이터를 schedules.json 파일에 저장하고 불러오는 역할을 합니다. 사람이 읽기 쉬운 텍스트 기반 형식이라 데이터 확인 및 수정이 용이하며, 파이썬의 딕셔너리 및 리스트와 구조가 거의 동일해 다루기 쉽습니다.

표준 라이브러리

sys: 시스템 관련 기능을 다룹니다. 특히 sys._MEIPASS를 확인하는 부분은 PyInstaller로 배포할 것을 염두에 둔 것입니다.

os: 운영체제와 상호작용하며, 파일 경로를 조합(os.path.join)하거나 절대 경로를 얻는(os.path.abspath) 등 파일 시스템 접근에 사용됩니다.

배포 도구 (코드 내 암시): PyInstaller

resource_path 함수와 그 안의 sys._MEIPASS 로직은 이 코드를 .exe 실행 파일로 변환하기 위해 PyInstaller를 사용할 것을 명확하게 보여줍니다.

🏛️ 프로그램 접근법 및 구조
이 프로그램은 현대적인 GUI 애플리케이션의 표준적인 설계 방식을 따르고 있습니다.

객체 지향 프로그래밍 (OOP) 기반 설계

PySchedulerApp (메인 윈도우), ScheduleDialog (입력 다이얼로그) 등 기능별로 클래스를 명확하게 분리하여 코드의 재사용성과 유지보수성을 높였습니다.

특히 WeeklyTitleLabel, ScheduleTextLabel처럼 기존 Qt 위젯(QLabel)을 **상속(subclassing)**하여 스타일과 기능을 커스터마이징한 것은 좋은 OOP 설계 방식입니다.

이벤트 기반(Event-Driven) 아키텍처

프로그램이 정해진 순서대로 실행되는 것이 아니라, 사용자의 행동(버튼 클릭, 날짜 선택 등)을 **이벤트(Event)**로 받아 처리합니다.

PyQt의 핵심 메커니즘인 시그널-슬롯(Signal-Slot) 모델을 적극적으로 사용합니다. 예를 들어, self.add_btn.clicked.connect(self.add_schedule) 코드는 '버튼이 클릭되면(Signal)', 'add_schedule 메서드를 실행하라(Slot)'는 의미입니다.

UI/데이터 분리 접근

스케줄 데이터는 self.schedules라는 딕셔너리 변수에 모두 저장하고, UI는 이 데이터를 기반으로 화면을 그려주는 역할을 합니다. 데이터가 변경되면 show_date_schedules, update_weekly_schedule_list 같은 메서드를 호출하여 화면을 새로고침하는 방식으로 데이터와 화면 표시를 분리했습니다.

중앙 집중식 데이터 관리

모든 스케줄 데이터(self.schedules)는 메인 클래스인 PySchedulerApp가 소유하고 관리합니다. 스케줄을 추가하거나 수정하는 ScheduleDialog는 단지 데이터를 입력받는 역할만 하고, 실제 데이터 변경 및 저장은 PySchedulerApp이 담당하여 데이터의 일관성을 유지합니다.

🧠 주요 알고리즘 및 로직
코드에 포함된 핵심적인 로직과 문제 해결 방식은 다음과 같습니다.

1. 리소스 경로 결정 알고리즘 (resource_path 함수)

문제: 개발 환경(스크립트 실행)과 배포 환경(.exe 실행)에서 아이콘 같은 외부 파일의 경로가 달라지는 문제를 해결해야 합니다.

알고리즘:

try-except 구문을 사용해 sys._MEIPASS라는 변수가 있는지 확인합니다. 이 변수는 PyInstaller가 만든 .exe 파일이 실행될 때만 존재합니다.

성공 시 (try): .exe 환경이므로, 파일이 임시로 풀린 _MEIPASS 폴더를 기준 경로(base_path)로 설정합니다.

실패 시 (except): 일반 스크립트 실행 환경이므로, 현재 작업 폴더를 기준 경로로 설정합니다.

결정된 기준 경로와 파일 이름을 조합하여 최종 경로를 반환합니다.

2. 주간 스케줄 표시 알고리즘 (update_weekly_schedule_list 메서드)

문제: 오늘을 기준으로 이번 주(월~일)의 스케줄을 메인 화면에 표시해야 합니다.

알고리즘:

QDate.currentDate()로 오늘 날짜를 가져옵니다.

today.dayOfWeek() (월요일=1, ..., 일요일=7)를 이용해 이번 주 월요일의 날짜를 계산합니다. (today.addDays(1 - today.dayOfWeek()))

for 루프를 0부터 6까지 반복하면서 월요일 날짜에 루프 변수 i를 더해 해당 요일의 날짜를 계산합니다.

계산된 날짜를 "yyyy-MM-dd" 형식의 문자열로 변환합니다.

이 문자열을 key로 사용하여 self.schedules 딕셔너리에서 해당 날짜의 스케줄 목록을 조회합니다.

스케줄이 존재하면, 각 스케줄에 대해 ScheduleTextLabel 위젯을 생성하여 화면의 해당 요일 칸에 추가합니다.

3. 스케줄 날짜 일괄 이동(Shift) 알고리즘 (load_schedules_from_file 메서드)

문제: 외부 스케줄 파일을 불러올 때, 기존 날짜들을 사용자가 선택한 새 시작 날짜에 맞춰 전체적으로 이동시켜야 합니다.

알고리즘:

불러온 스케줄 데이터에서 모든 날짜를 추출하여 그중 가장 오래된 날짜(original_start_date)를 찾습니다.

사용자에게 DateShiftDialog를 통해 새로운 시작 날짜(new_start_date)를 입력받습니다.

기존 시작일과 새 시작일 사이의 날짜 차이(offset_days)를 계산합니다.

새로운 딕셔너리(new_schedules)를 준비합니다.

불러온 기존 스케줄의 모든 날짜에 대해 반복문을 실행합니다.

각 날짜에 offset_days만큼 더하여 새로운 날짜를 계산합니다.

새로운 날짜를 key로, 기존 스케줄 내용을 value로 하여 new_schedules 딕셔너리에 저장합니다.

모든 작업이 끝나면, 프로그램의 메인 스케줄 데이터(self.schedules)를 이 new_schedules로 교체합니다.
