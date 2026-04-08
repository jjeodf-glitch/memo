# 메모장 (Memo)

가볍고 편하게 쓸 수 있는 메모장 데스크톱 앱입니다.  
Python + tkinter 기반으로 외부 의존성 없이 동작하며, 단일 portable exe 파일로 배포됩니다.

---

## 주요 기능

- **탭 기능** – 여러 메모를 탭으로 동시에 관리
- **파일 열기 / 저장 / 다른 이름으로 저장** – `.txt` 파일 지원
- **자동 저장** – 30초 간격으로 임시 파일에 자동 저장
- **실행취소 / 다시실행** – 무제한 히스토리
- **찾기 / 바꾸기** – 대소문자 구분 옵션 포함
- **다크 모드** – 기본 다크 테마, 라이트 모드 토글 가능
- **폰트 크기 조절** – Ctrl+마우스 휠 또는 Ctrl++/- 로 조절
- **상태 바** – 현재 줄·열, 총 줄 수, 글자 수, 폰트 크기 표시

---

## 설치 및 사용 방법

### exe 다운로드 (권장)

1. [Releases](../../releases) 페이지로 이동
2. 최신 버전의 `Memo.exe` 다운로드
3. 그대로 실행 (설치 불필요, portable)

### Python으로 직접 실행

```bash
# Python 3.10 이상 필요 (tkinter 포함)
python src/memo.py
```

---

## 키보드 단축키

| 단축키 | 기능 |
|---|---|
| `Ctrl+N` | 새 탭 |
| `Ctrl+O` | 파일 열기 |
| `Ctrl+S` | 저장 |
| `Ctrl+Shift+S` | 다른 이름으로 저장 |
| `Ctrl+W` | 현재 탭 닫기 |
| `Ctrl+F` | 찾기 |
| `Ctrl+H` | 바꾸기 |
| `Ctrl+Z` | 실행취소 |
| `Ctrl+Y` | 다시실행 |
| `Ctrl++` / `Ctrl+-` | 폰트 크기 조절 |
| `Ctrl+마우스 휠` | 폰트 크기 조절 |

---

## 빌드 방법

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Memo src/memo.py
# dist/Memo.exe 생성
```

GitHub에 `v*` 태그를 push하면 GitHub Actions가 자동으로 빌드하여 Release에 업로드합니다.

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 라이선스

[MIT License](LICENSE)