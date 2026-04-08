# 메모장 (Memo)

모던하고 세련된 데스크톱 메모 앱입니다.  
Python + CustomTkinter 기반의 상업용 수준 UI로, 단일 portable exe 파일로 배포됩니다.

---

## 주요 기능

### UI/UX
- **모던 디자인** – CustomTkinter 기반의 세련된 UI
- **다크/라이트 모드** – 시스템 설정 연동 및 수동 토글
- **사이드바** – 메모 목록, 카테고리 트리, 실시간 검색

### 메모 관리
- **카테고리 관리** – 폴더별 메모 분류 (사용자 정의 카테고리)
- **메모 고정(Pin)** – 중요 메모를 상단에 고정
- **태그 시스템** – 컬러 태그 추가 및 태그별 필터링
- **휴지통** – 삭제된 메모 복구 가능
- **메모 정렬** – 이름순, 생성일순, 수정일순

### 에디터
- **탭 기능** – 여러 메모를 탭으로 동시에 열기
- **자동 저장** – 타이핑 후 2초 이내 자동 저장 (JSON 기반 내부 저장소)
- **줄 번호** – 에디터 좌측 줄 번호 표시 (토글 가능)
- **실행취소 / 다시실행** – 무제한 히스토리
- **찾기 / 바꾸기** – 인라인 검색 바
- **폰트 크기 조절** – Ctrl+마우스 휠 또는 Ctrl++/-
- **글자 수 / 단어 수** – 실시간 표시

### 파일
- **파일 열기 / 저장 / 다른 이름으로 저장** – `.txt` 파일 import/export
- **드래그 앤 드롭** – 텍스트 파일 드롭으로 열기

---

## 프로젝트 구조

```
src/
  app.py              # 앱 진입점
  ui/
    main_window.py    # 메인 윈도우 (사이드바 + 에디터)
    sidebar.py        # 사이드바 (검색, 카테고리, 메모 목록)
    editor.py         # 텍스트 에디터 (줄 번호, 찾기/바꾸기)
    toolbar.py        # 상단 툴바
    statusbar.py      # 하단 상태 바
    dialogs.py        # 다이얼로그 (태그, 설정, 카테고리)
  models/
    note.py           # 메모 데이터 모델
    category.py       # 카테고리 데이터 모델
  storage/
    store.py          # JSON 저장/로드 로직
  utils/
    theme.py          # 테마/색상 관리
    config.py         # 앱 설정
```

---

## 설치 및 사용 방법

### exe 다운로드 (권장)

1. [Releases](../../releases) 페이지로 이동
2. 최신 버전의 `Memo.exe` 다운로드
3. 그대로 실행 (설치 불필요, portable)

### Python으로 직접 실행

```bash
# Python 3.10 이상 필요
pip install -r requirements.txt
python src/app.py
```

---

## 키보드 단축키

| 단축키 | 기능 |
|---|---|
| `Ctrl+N` | 새 메모 |
| `Ctrl+O` | 파일 열기 |
| `Ctrl+S` | 파일로 저장 |
| `Ctrl+Shift+S` | 다른 이름으로 저장 |
| `Ctrl+W` | 현재 탭 닫기 |
| `Ctrl+F` | 찾기 |
| `Ctrl+H` | 찾기/바꾸기 |
| `Ctrl+Z` | 실행취소 |
| `Ctrl+Y` | 다시실행 |
| `Ctrl+B` | 볼드 |
| `Ctrl+I` | 이탤릭 |
| `Ctrl+L` | 줄 번호 토글 |
| `Ctrl++` / `Ctrl+-` | 폰트 크기 조절 |
| `Ctrl+마우스 휠` | 폰트 크기 조절 |

---

## 데이터 저장 위치

메모 데이터는 `~/.memo_app/` 디렉토리에 JSON 형식으로 저장됩니다.

---

## 빌드 방법

```bash
pip install -r requirements.txt
pyinstaller --onefile --windowed --name Memo src/app.py
# dist/Memo.exe 생성
```

GitHub에 `v*` 태그를 push하면 GitHub Actions가 자동으로 빌드하여 Release에 업로드합니다.

```bash
git tag v2.0.0
git push origin v2.0.0
```

---

## 라이선스

[MIT License](LICENSE)