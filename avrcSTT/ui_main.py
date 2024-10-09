import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QStyle, QPushButton, QFrame, QTextBrowser, QComboBox, QSizePolicy
from PyQt6.QtGui import QGuiApplication

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Set parent widget
        self.parent = parent
        self.setAutoFillBackground(True)
        self.initial_pos = None
        self.is_window_maximized = False  # Track window state

        # Set layout for custom title bar
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(2)

        # Create title label
        self.title_label = QLabel("avrcSTT")
        self.title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: 2px solid black; border-radius: 12px; margin: 2px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title_label.setText(title)
        layout.addWidget(self.title_label)
        
        # Min button
        min_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton)
        self.minimize_button = QPushButton(self)
        self.minimize_button.setFixedSize(25, 25)
        self.minimize_button.setStyleSheet("background-color: black; color: white;")
        self.minimize_button.setIcon(min_icon)
        self.minimize_button.clicked.connect(self.minimize_window)

        # Max button
        max_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        self.maximize_button = QPushButton(self)
        self.maximize_button.setFixedSize(25, 25)
        self.maximize_button.setStyleSheet("background-color: black; color: white;")
        self.maximize_button.setIcon(max_icon)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)

        # Close button
        close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.close_button = QPushButton(self)
        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("background-color: black; color: white;")
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.close_window)

        buttons = [
            self.minimize_button,
            self.maximize_button,
            self.close_button
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(28, 28)
            button.setStyleSheet("background-color: black; color: white;")
            layout.addWidget(button)

        # Set layout and background color
        self.setLayout(layout)
        self.setStyleSheet("background-color: black; height: 20px;")
    
    # Function for Maximize/Normal Button
    def toggle_maximize_restore(self):
                normal_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
                max_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
                if self.is_window_maximized:
                        self.parent.showNormal()  # Restore to normal size
                        self.is_window_maximized = False
                        self.maximize_button.setIcon(max_icon)  # Change button to maximize icon
                else:
                        self.parent.showMaximized()  # Maximize window
                        self.is_window_maximized = True
                        self.maximize_button.setIcon(normal_icon)  # Change button to restore icon

    # Function for Minimize Button
    def minimize_window(self):
        self.parent.showMinimized()

    # Function for Close Button
    def close_window(self):
        self.parent.close()

    # Allow dragging the custom title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class CustomWindow(QWidget):
        def __init__(self):
                super().__init__()

                # Remove the default title bar
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
                self.resize(927, 678)
                self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                self.title_bar = CustomTitleBar(self)

                # Add content (for demonstration)
                self.setStyleSheet("background-color: #2C2C2C; border-radius: 12px;")  # Set the background color of the main content

                # centralwidget
                self.centralwidget = QWidget(parent=self)
                self.centralwidget.setObjectName("centralwidget")
                self.centralwidget.resize(927,678)

                # centralwidget_layout 
                self.centralwidget_layout = QVBoxLayout(self.centralwidget)
                self.centralwidget_layout.setContentsMargins(2, 2, 2, 2)
                self.centralwidget_layout.setSpacing(0)
                self.centralwidget_layout.setObjectName("centralwidget_layout")

                # create main content bar
                self.content = QFrame()
                self.content.setStyleSheet("background-color: none")
                self.content.setContentsMargins(2, 2, 2, 2)
                self.content.setFrameShape(QFrame.Shape.StyledPanel)
                self.content.setFrameShadow(QFrame.Shadow.Raised)
                self.content.setObjectName("content")
                
                # create textBrowser
                self.textBrowser = QTextBrowser(parent=self.content)
                self.textBrowser.setObjectName("textBrowser")
                self.content_bar_layout = QHBoxLayout(self.content)  
                self.content_bar_layout.setContentsMargins(9, 9, 9, 9) 
                self.content_bar_layout.setSpacing(0)
                self.content_bar_layout.addWidget(self.textBrowser)
                self.textBrowser.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
                
                # model_selection_bar
                self.model_selection_bar = QFrame()
                self.model_selection_bar.setStyleSheet("background-color: none")
                self.model_selection_bar.setFrameShape(QFrame.Shape.StyledPanel)
                self.model_selection_bar.setFrameShadow(QFrame.Shadow.Raised)
                self.model_selection_bar.setObjectName("model_selection_bar")

                # create model_selection_bar_layout (horizontalLayout_3)
                self.model_selection_bar_layout = QHBoxLayout(self.model_selection_bar)
                self.model_selection_bar_layout.setObjectName("model_selection_bar_layout")
                self.model_selection_bar_label = QLabel(parent=self.model_selection_bar)
                self.model_selection_bar_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; font-family: 'Roboto Black'")
                #self.model_selection_bar_label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
                self.model_selection_bar_label.setObjectName("model_selection_bar_label")       
                self.model_selection_bar_label.setText("Select Transcribe Model:")

                # create comboBox to model_selection_bar
                self.comboBox = QComboBox(parent=self.model_selection_bar)
                self.comboBox.setObjectName("comboBox")
                # create pushButton to model_selection_bar
                self.pushButton = QPushButton(parent=self.model_selection_bar)
                self.pushButton.setObjectName("pushButton")
                # create pushButton_2 to model_selection_bar
                self.pushButton_2 = QPushButton(parent=self.model_selection_bar)
                self.pushButton_2.setObjectName("pushButton_2")
                
                # add widgets to selection bar layout
                self.model_selection_bar_layout.addWidget(self.model_selection_bar_label)
                self.model_selection_bar_layout.addWidget(self.comboBox)
                self.model_selection_bar_layout.addWidget(self.pushButton)
                self.model_selection_bar_layout.addWidget(self.pushButton_2)
                
                # add widgets
                self.centralwidget_layout.addWidget(self.title_bar)
                self.centralwidget_layout.addWidget(self.content)
                self.centralwidget_layout.addWidget(self.model_selection_bar)

        def showMaximized(self):
                screen = QGuiApplication.primaryScreen()
                available_geometry = screen.availableGeometry()
                self.setGeometry(available_geometry)
                self.centralwidget.setGeometry(available_geometry)
                self.update()
                self.centralwidget.update() 
        
        def showNormal(self):   
                self.resize(927, 678)
                self.centralwidget.resize(927, 678)
                self.update()
                self.centralwidget.update() 
             

def main():
    app = QApplication(sys.argv)

    # Create an instance of the custom window
    window = CustomWindow()
    window.setGeometry(100, 100, 927, 678)  # Set window size
    window.show()

    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
        main()
