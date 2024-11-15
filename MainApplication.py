from PySide6.QtWidgets import QApplication, QMainWindow, QGroupBox, QLabel, QWidget, QLineEdit, QPushButton, QCheckBox, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QSize
from PySide6.QtGui import QPixmap, QResizeEvent
import qdarkstyle
from PIL.ImageQt import ImageQt
from PIL import Image
from ASCIIXEL import ASCIIXEL
from utils import EXTENTIONS, ASCII_CHARS_TAB, OutputType
import sys
import os

# Create the application window
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.app_ASCIIXEL = ASCIIXEL()

        # Create the Worker Thread Object
        self.instanced_thread = WorkerThread(self, self.app_ASCIIXEL)

        self.setWindowTitle("ASCIIXEL")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create all the layouts
        self.layout = QVBoxLayout()
        self.pathLayout = QHBoxLayout()
        self.settingsLayout = QGridLayout()
        self.buttonLayout = QHBoxLayout()
        self.videoLayout = QHBoxLayout()
        self.typeLayout = QVBoxLayout()
        self.asciiSetLayout = QVBoxLayout()
        self.elementSizeLayout = QVBoxLayout()
        self.colourLevelLayout = QVBoxLayout()

        # Create a group box for the settings
        self.settingsGroupBox = QGroupBox("Settings")

        # Create all the Widgets
        self.textQuery = QLabel(text="Enter the path of the video to convert: ")
        self.videoPath = QLineEdit()
        self.videoSearchButton = QPushButton(text="Open File")

        self.typeLabel = QLabel(text="Render Type")
        self.typeComboBox = QComboBox()
        for el in OutputType:
            self.typeComboBox.addItem(el.name)
        self.typeComboBox.setCurrentIndex(self.app_ASCIIXEL.output_type.value)

        self.asciiSetLabel = QLabel(text="ASCII Palette")
        self.asciiSetComboBox = QComboBox()
        for el in ASCII_CHARS_TAB:
            self.asciiSetComboBox.addItem(el)
        self.asciiSetComboBox.setCurrentIndex(self.app_ASCIIXEL.ascii_set)

        self.elementSizeLabel = QLabel(text="Element Size")
        self.elementSizeSpinBox = QSpinBox()
        self.elementSizeSpinBox.setMinimum(1)
        self.elementSizeSpinBox.setValue(self.app_ASCIIXEL.element_size)

        self.colourLevelLabel = QLabel(text="Colour Level")
        self.colourLevelSpinBox = QSpinBox()
        self.colourLevelSpinBox.setMinimum(2)
        self.colourLevelSpinBox.setValue(self.app_ASCIIXEL.colour_lvl)

        self.displayOrigCheckBox = QCheckBox(text="Display Original")
        self.displayOrigCheckBox.setChecked(self.app_ASCIIXEL.display_original)

        self.reverseColourCheckBox = QCheckBox(text="Reverse Colour")
        self.reverseColourCheckBox.setChecked(self.app_ASCIIXEL.reverse_colour)

        self.previewButton = QPushButton(text="Run Preview")
        self.recordButton = QPushButton(text="Record")
        self.cancelButton = QPushButton(text="Cancel")
        self.videoLabel = QLabel()
        self.videoOrigLabel = QLabel()

        # Add the widgets to their corresponding layouts
        self.pathLayout.addWidget(self.videoPath)
        self.pathLayout.addWidget(self.videoSearchButton)

        self.typeLayout.addWidget(self.typeLabel)
        self.typeLayout.addWidget(self.typeComboBox)
        self.settingsLayout.addLayout(self.typeLayout, 0, 0, 1, 2)

        self.asciiSetLayout.addWidget(self.asciiSetLabel)
        self.asciiSetLayout.addWidget(self.asciiSetComboBox)
        self.settingsLayout.addLayout(self.asciiSetLayout, 1, 0, 1, 2)

        self.elementSizeLayout.addWidget(self.elementSizeLabel)
        self.elementSizeLayout.addWidget(self.elementSizeSpinBox)
        self.settingsLayout.addLayout(self.elementSizeLayout, 2, 0, 1, 2)

        self.colourLevelLayout.addWidget(self.colourLevelLabel)
        self.colourLevelLayout.addWidget(self.colourLevelSpinBox)
        self.settingsLayout.addLayout(self.colourLevelLayout, 3, 0, 1, 2)

        self.settingsLayout.addWidget(self.displayOrigCheckBox, 4, 0)
        self.settingsLayout.addWidget(self.reverseColourCheckBox, 4, 1)

        self.settingsGroupBox.setLayout(self.settingsLayout)

        self.buttonLayout.addWidget(self.previewButton)
        self.buttonLayout.addWidget(self.recordButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.videoLayout.addWidget(self.videoLabel)
        self.videoLayout.addWidget(self.videoOrigLabel)

        self.layout.addWidget(self.textQuery)
        self.layout.addLayout(self.pathLayout)
        self.layout.addWidget(self.settingsGroupBox)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addLayout(self.videoLayout)

        # Set the main layout properties
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignTop)

        # Connect custom function to widget events
        self.videoSearchButton.clicked.connect(self.search)
        self.displayOrigCheckBox.stateChanged.connect(self.onStatesChanged)
        self.reverseColourCheckBox.stateChanged.connect(self.onStatesChanged)
        self.asciiSetComboBox.currentIndexChanged.connect(self.onAsciiSetIndexChanged)
        self.typeComboBox.currentIndexChanged.connect(self.onTypeIndexChanged)
        self.elementSizeSpinBox.valueChanged.connect(self.onElementSizeValueChanged)
        self.colourLevelSpinBox.valueChanged.connect(self.onColourLevelValueChanged)
        self.previewButton.clicked.connect(self.clickPreview)
        self.recordButton.clicked.connect(self.clickRecord)
        self.cancelButton.clicked.connect(self.instanced_thread.stop)

        # Set default properties of the main window
        self.central_widget.setLayout(self.layout)


    # Search video file
    def search(self) -> None:
        videoPathName = QFileDialog.getOpenFileName(caption="Open File", dir="/", filter="Video (*.mp4 *.mov *.mkv)")
        
        ext = os.path.splitext(videoPathName[0])

        if not os.path.exists(videoPathName[0]) or ext[1] not in EXTENTIONS:
            return

        self.videoPath.setText(videoPathName[0])
        self.app_ASCIIXEL.path = videoPathName[0]

    # Modify ASCIIXEL when any checkbox change
    def onStatesChanged(self) -> None:
        self.app_ASCIIXEL.display_original = self.displayOrigCheckBox.isChecked()
        if not self.app_ASCIIXEL.display_original:
            self.videoOrigLabel.clear()

        self.app_ASCIIXEL.reverse_colour = self.reverseColourCheckBox.isChecked()

    # Modify the output type
    def onTypeIndexChanged(self, index) -> None:
        self.app_ASCIIXEL.output_type = OutputType(index)

    # Modify the ascii set used
    def onAsciiSetIndexChanged(self, index) -> None:
        self.app_ASCIIXEL.ascii_set = index

    # Modify the size of the element displayed (character or pixel)
    def onElementSizeValueChanged(self, value) -> None:
        self.app_ASCIIXEL.element_size = value

    # Modify the number of colour used
    def onColourLevelValueChanged(self, value) -> None:
        self.app_ASCIIXEL.colour_lvl = value

    # Start ASCIIXEL app in a thread without saving the output
    def clickPreview(self) -> None:
        self.clickCancel()

        # Set asciixel properties and run the setup
        self.app_ASCIIXEL.reset()
        self.app_ASCIIXEL.record = False
        if not self.app_ASCIIXEL.setup(): return

        # Start a new thread
        self.instanced_thread.start()

    # Start ASCIIXEL app in a thread and save the output
    def clickRecord(self) -> None:
        self.clickCancel()

        # Set asciixel properties and run the setup
        self.app_ASCIIXEL.reset()
        self.app_ASCIIXEL.record = True
        if not self.app_ASCIIXEL.setup(): return

        # Start a new thread
        self.instanced_thread.start()
    
    # Cancel the ASCIIXEL app thread
    def clickCancel(self) -> None:
        # Kill thread if it is running
        if self.instanced_thread.isRunning():
            self.instanced_thread.stop()

    # Slot for communicating with the thread worker to get the result image
    @Slot(QPixmap)
    def updateResultImageField(self, img):
        self.videoLabel.setPixmap(img)

    # Slot for communicating with the thread worker to get the original image
    @Slot(QPixmap)
    def updateOrigImageField(self, img):
        self.videoOrigLabel.setPixmap(img)


# Create signal type
class ImgSignals(QObject):
    signal_img = Signal(QPixmap)
    signal_img_orig = Signal(QPixmap)

# Create the Worker Thread
class WorkerThread(QThread):
    def __init__(self, parent=None, app_ASCIIXEL=None) -> None:
        QThread.__init__(self, parent)

        self.app_ASCIIXEL = app_ASCIIXEL

        self.exit = False

        # Instantiate signals and connect signals to slots
        self.signals = ImgSignals()
        self.signals.signal_img.connect(parent.updateResultImageField)
        self.signals.signal_img_orig.connect(parent.updateOrigImageField)
    
    def run(self) -> None:
        if self.app_ASCIIXEL == None: return

        while not self.app_ASCIIXEL.finish:
            if self.exit:
                self.exit = False
                return

            self.app_ASCIIXEL.runStep()
            img = QPixmap.fromImage(ImageQt(self.app_ASCIIXEL.out_image))
            self.signals.signal_img.emit(img)

            if self.app_ASCIIXEL.display_original:
                pil_img_orig = Image.fromarray(self.app_ASCIIXEL.cv2_image).convert('RGB')
                img_orig = QPixmap.fromImage(ImageQt(pil_img_orig))
                self.signals.signal_img_orig.emit(img_orig)

        self.app_ASCIIXEL.record_video()
    
    @Slot()
    def stop(self) -> None:
        self.exit = True


if __name__ == '__main__':
#     app = ASCIIXEL(path='videos/Touhou-Bad_Apple!!.mp4', ascii_set=2, display_original=False, reverse_colour=False, output_type=OutputType.PIXEL_ART, record=True)
#     app.run()

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec())