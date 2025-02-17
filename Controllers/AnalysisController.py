from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QSizePolicy, QHBoxLayout, QVBoxLayout

from Models.ProcessedImage import ProcessedImage
from Models.Parameters import Parameters
from Models.Analysis import Analysis
from Services.Threads.AnalysisThread import AnalysisThread
from Services.Threads.PostAnalysisThread import PostAnalysisThread
from Components.Widgets.StylizedButton import StylizedButton
from Components.Widgets.PageTitle import PageTitle
from Components.Analysis.StatComponent import StatComponent
from Components.Analysis.ImageComponent import ImageComponent
from Components.Analysis.ProgressComponent import ProgressComponent
from Controllers.BaseController import BaseController
from Controllers.MessageBox.CancelMessageBox import CancelMessageBox

class AnalysisController(BaseController):

    def __init__(self):
        super().__init__()

        self._analysis = None
        self._cancel_message_box = None

        self._title = PageTitle("Initialisation de l'analyse", False, self)

        self._stat_component = StatComponent()
        self._image_component = ImageComponent()
        self._progress_component = ProgressComponent()

        components_layout = QGridLayout()
        components_layout.setHorizontalSpacing(20)
        components_layout.setColumnStretch(0, 6)
        components_layout.setColumnStretch(1, 5)

        components_layout.addWidget(self._stat_component, 0, 0)
        components_layout.addWidget(self._image_component, 0, 1)
        components_layout.addWidget(self._progress_component, 1, 0, 1, 2)

        self._return_button = StylizedButton("Annuler", "yellow")
        self._return_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        button_layout.setSpacing(35)
        button_layout.addWidget(self._return_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._title)
        main_layout.addLayout(components_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self._return_button.clicked.connect(self._returnClick)

        self._analysis_thread = AnalysisThread()
        self._analysis_thread.initialized.connect(self._neuralNetworkInitialized)
        self._analysis_thread.imageProcessed.connect(self._imageProcessed)
        self._analysis_thread.completed.connect(self._analysisFinished)

        self._post_analysis_thread = PostAnalysisThread()
        self._post_analysis_thread.completed.connect(self._postAnalysisFinished)

    def start(self, parameters: Parameters, images: list):
        self._analysis = Analysis(parameters, images)

        self._title.setText("Initialisation de l'analyse")

        self._stat_component.reset(parameters)
        self._image_component.reset(parameters)
        self._progress_component.reset(self._analysis.imagesCount())

        self._return_button.setText("Annuler")
        self._return_button.setObjectName("yellow")
        self.style().unpolish(self._return_button)
        self.style().polish(self._return_button)

        self._analysis_thread.start(parameters, images)

    def stop(self):
        self._progress_component.stop()

    def askExit(self) -> bool:
        if self._analysis.isFinished():
            return True

        return CancelMessageBox(self).exec_()

    @Slot(ProcessedImage)
    def _imageProcessed(self, processed_image: ProcessedImage):
        self._analysis.addProcessedImage(processed_image)

        next_image = self._analysis.nextImageName()
        if next_image is None:
            next_image = "Pas de prochaine image"

        self._image_component.update(processed_image)
        self._stat_component.update(self._analysis)
        self._progress_component.update(next_image, self._analysis.currentImageIndex(), self._analysis.estimateTimeLeft())

    @Slot()
    def _returnClick(self):
        if self._analysis.isFinished():
            self.changeWidget.emit("/history", self._analysis)
        else:
            self._cancel_message_box = CancelMessageBox(self)

            if self._cancel_message_box.exec_():
                self._analysis_thread.stop()
                self.changeWidget.emit("/menu", None)

            self._cancel_message_box = None

    @Slot()
    def _neuralNetworkInitialized(self):
        self._title.setText("Analyse en cours")
        self._analysis.start()

    @Slot()
    def _analysisFinished(self):
        self._analysis.finish()

        self._title.setText("Post analyse en cours")
        self._post_analysis_thread.start(self._analysis)

    @Slot()
    def _postAnalysisFinished(self):
        if self._cancel_message_box:
            self._cancel_message_box.close()

        self._title.setText("Analyse terminée")
        self._return_button.setText("Continuer")
        self._return_button.setObjectName("blue")
        self.style().unpolish(self._return_button)
        self.style().polish(self._return_button)
