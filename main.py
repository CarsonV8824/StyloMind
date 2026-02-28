import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import Qt, QIcon

from ui.main_window import MainWindow

from database.database import Database

from pathlib import Path
import sys, os, json

def get_resource_path(relative_path):
    """Get the absolute path to a resource, compatible with PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def load_stylesheet(app: QApplication) -> None:
    style_path = Path(get_resource_path("assets/styles.css"))
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))

def main():
    
    app = QApplication(sys.argv)
    load_stylesheet(app)
    app.setWindowIcon(QIcon(str(Path("assets/logo.png"))))

    window = MainWindow()
    window.setWindowIcon(QIcon(str(Path("assets/logo.png"))))
    
    window.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()