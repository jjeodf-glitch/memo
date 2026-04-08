#!/usr/bin/env python3
"""모던 메모장 앱 - 진입점"""
import sys
import os

# ensure src/ is in path whether run as `python app.py` or `python -m src.app`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
except ImportError:
    print("=" * 60)
    print("오류: customtkinter 패키지가 설치되지 않았습니다.")
    print("다음 명령어로 설치하세요:")
    print("  pip install customtkinter pillow")
    print("=" * 60)
    sys.exit(1)

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
