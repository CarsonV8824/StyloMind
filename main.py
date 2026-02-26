import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import Qt

from ui.main_window import MainWindow

def main():
    # 1. Create the application instance
    app = QApplication(sys.argv)

    # 2. Create the main window instance
    window = MainWindow()
    
    # 3. Show the window
    window.show()

    # 4. Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()