from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
# file stuff
import os
import pdfplumber
from docx import Document

# Database

from database.database import Database

class UploadPage(QWidget):
    send_text = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)

        self.test_button = QPushButton("Upload text")
        self.test_button.clicked.connect(self.open_dialog)
        self.main_layout.addWidget(self.test_button)

    def open_dialog(self):
        
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",
            "Text Files (*.txt);;PDF Files (*.pdf);;Word Files (*.docx);;All Files (*)"
        )
        
        file_name = os.path.basename(file_path)

        if file_path:
            match selected_filter:
                case "PDF Files (*.pdf)": 
                    with pdfplumber.open(file_path) as pdf:
                        pages = []
                        for page in pdf.pages:
                            pages.append(page.extract_text())
                        pages = " ".join(pages)
                        print(pages)
                        Database.add_text(file_name, pages)
                        self.send_text.emit([pages, file_name])
                        
                        return
                case "Word Files (*.docx)":
                    document = Document(file_path)
                    fullText = []

                    # Iterate through all paragraphs and append their text to a list
                    for para in document.paragraphs:
                        fullText.append(para.text)

                    # Join the list of strings with newline characters
                    print('\n'.join(fullText))
                    Database.add_text(file_name, '\n'.join(fullText))
                    self.send_text.emit(['\n'.join(fullText), file_name])
                    
                    return
                case _:
                    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
                        try:
                            with open(file_path, "r", encoding=encoding) as f:
                                text = f.read()
                                print(text)
                                Database.add_text(file_name, text)
                                self.send_text.emit([text, file_name])
                                
                                return
                        except UnicodeDecodeError:
                            continue

                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        text = f.read()
                        print(text)
                        Database.add_text(file_name, text)
                        self.send_text.emit([text, file_name])
                        
                        return
                    
            print(selected_filter)
        else:
            QMessageBox.warning(self, "file not found", "Could not find file or Error loading file")
