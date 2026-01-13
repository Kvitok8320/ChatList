import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Минимальная программа PyQt")
        self.setGeometry(100, 100, 400, 200)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Создаем метку
        self.label = QLabel("Нажмите кнопку!")
        layout.addWidget(self.label)
        
        # Создаем кнопку
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)
    
    def on_button_clicked(self):
        self.label.setText("Кнопка была нажата!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

