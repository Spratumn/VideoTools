from ui.ui_mainwindow import Ui_MainWindow

import sys
import os
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from thread import *


# mainwindow
class PyTools(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('PyTools')

        self.lineEditAnnotationPath.setEnabled(False)
        self.pButAnnotationPath.setEnabled(False)
        self.pButViewTracks.setEnabled(False)

        # slot-signal
        self.pButSequenceImageDir.clicked.connect(self.select_sequence_image_dir)
        self.pButAnnotationPath.clicked.connect(self.select_sequence_annotation_path)
        self.pButVideoPath.clicked.connect(self.select_video_path)
        self.pButRenameFolderDir.clicked.connect(self.select_rename_folder_dir)

        self.comboBoxAnnotation.currentIndexChanged.connect(self.annotation_option_edit)

        self.pButSeq2Video.clicked.connect(self.sequence_to_video)
        self.pButViewTracks.clicked.connect(self.view_sequence_tracks)
        self.pButVideo2Sequence.clicked.connect(self.video_to_sequence)
        self.pButRenameFolder.clicked.connect(self.rename_folder)
        

    def sequence_to_video(self):
        if not self.check_op(message='Are you sure to make video form the selected sequence?'):return
        
        annotationType = self.comboBoxAnnotation.currentText()
        xmlDir = None
        txtPath = None
        if annotationType == 'Detection':
            xmlDir = self.lineEditAnnotationPath.text()
            if not os.path.exists(xmlDir) or len(os.listdir(xmlDir)) == 0:
                QMessageBox.warning(self, "Warning", "xml dir not exist or empty!", QMessageBox.Ok)
                return
        if annotationType == 'Tracking':
            txtPath = self.lineEditAnnotationPath.text()
            if not os.path.exists(txtPath):
                QMessageBox.warning(self, "Warning", "txt path not exist!", QMessageBox.Ok)
                return

        sequenceDir = self.lineEditSequenceImageDir.text()
        if not os.path.exists(sequenceDir) or len(os.listdir(sequenceDir)) == 0:
            QMessageBox.warning(self, "Warning", "sequence not exist or empty!", QMessageBox.Ok)
            return
        
        commonCfg = self.get_common_configs()
        self.seq2videoThread = Sequence2VideoThread(sequenceDir=sequenceDir,
                                                    commonCfg=commonCfg,
                                                    xmlDir=xmlDir, txtPath=txtPath)
        self.seq2videoThread.start()
        self.seq2videoThread.trigger.connect(self.sequence_to_video_log)
        self.pButSeq2Video.setEnabled(False)
        self.pButSeq2Video.setText('Making')
        self.pButSequenceImageDir.setEnabled(False)
        self.lineEditAnnotationPath.setEnabled(False)
        self.pButAnnotationPath.setEnabled(False)
        self.comboBoxAnnotation.setEnabled(False)
        self.lineEditSequenceImageDir.setEnabled(False)


    def sequence_to_video_log(self, strMessage):
        ret, message = strMessage.split(',')
        if message=='finish':
            self.pButSeq2Video.setEnabled(True)
            self.pButSeq2Video.setText('Make Video')
            self.pButSequenceImageDir.setEnabled(True)
            self.lineEditAnnotationPath.setEnabled(True)
            self.pButAnnotationPath.setEnabled(True)
            self.comboBoxAnnotation.setEnabled(True)
            self.lineEditSequenceImageDir.setEnabled(True)
        if ret!='0':
            QMessageBox.warning(self, "Warning", "Make video failed, check configs!", QMessageBox.Ok)
    
    def view_sequence_tracks(self):
        if not self.check_op(message='Are you sure to view the tracks of the selected sequence?'):return
        
        sequenceDir = self.lineEditSequenceImageDir.text()
        if not os.path.exists(sequenceDir) or len(os.listdir(sequenceDir)) == 0:
            QMessageBox.warning(self, "Warning", "sequence not exist or empty!", QMessageBox.Ok)
            return
        txtPath = self.lineEditAnnotationPath.text()
        if not os.path.exists(txtPath):
            QMessageBox.warning(self, "Warning", "txt path not exist!", QMessageBox.Ok)
            return
        
        commonConfig = self.get_common_configs()
        
        self.viewTracksThread = ViewTracksThread(sequenceDir=sequenceDir,
                                                commonCfg=commonConfig,
                                                txtPath=txtPath)
        self.viewTracksThread.start()
        self.viewTracksThread.trigger.connect(self.view_sequence_tracks_log)
        self.pButViewTracks.setEnabled(False)
        self.pButViewTracks.setText('Viewing')

    def view_sequence_tracks_log(self, strMessage):
        ret, message = strMessage.split(',')
        if message=='finish':
            self.pButViewTracks.setEnabled(True)
            self.pButViewTracks.setText('View Tracks')
        if ret!='0':
            QMessageBox.warning(self, "Warning", "View tracks failed, check configs!", QMessageBox.Ok)
            

    def video_to_sequence(self):
        if not self.check_op(message='Are you sure to extract frames form the selected video?'):return
        
        videoPath = self.lineEditVideoPath.text()
        if not os.path.exists(videoPath):
            QMessageBox.warning(self, "Warning", "video not exist!", QMessageBox.Ok)
            return
        
        commonCfg = self.get_common_configs()
        
        self.video2seqThread = Video2SequenceThread(videoPath=videoPath,
                                                    commonCfg=commonCfg)
        self.video2seqThread.start()
        self.video2seqThread.trigger.connect(self.video_to_sequence_log)
        self.pButVideo2Sequence.setEnabled(False)
        self.pButVideo2Sequence.setText('Extracting')
        self.pButVideoPath.setEnabled(False)
        self.lineEditVideoPath.setEnabled(False)


    def video_to_sequence_log(self, strMessage):
        ret, message = strMessage.split(',')
        if message=='finish':
            self.pButVideo2Sequence.setEnabled(True)
            self.pButVideo2Sequence.setText('Extract Frames')
            self.pButVideoPath.setEnabled(True)
            self.lineEditVideoPath.setEnabled(True)
        if ret!='0':
            QMessageBox.warning(self, "Warning", "Extract frames failed, check configs!", QMessageBox.Ok)


    def rename_folder(self):
        if not self.check_op(message='Are you sure to rename the selected video?'):return
        
        folderDir = self.lineEditRenameFolderDir.text()
        if not os.path.exists(folderDir):
            QMessageBox.warning(self, "Warning", "folder not exist!", QMessageBox.Ok)
            return
        originIndexSort = self.checkBoxOriginIndexSort.isChecked()
        commonCfg = self.get_common_configs()
        
        self.renameFolderThread = RenameFolderThread(folderDir=folderDir,
                                                    originIndexSort=originIndexSort,
                                                    commonCfg=commonCfg)
        self.renameFolderThread.start()
        self.renameFolderThread.trigger.connect(self.rename_folder_log)
        self.pButRenameFolder.setEnabled(False)
        self.pButRenameFolder.setText('Renaming')
        self.pButRenameFolderDir.setEnabled(False)
        self.lineEditRenameFolderDir.setEnabled(False)


    def rename_folder_log(self, strMessage):
        ret, message = strMessage.split(',')
        if message=='finish':
            self.pButRenameFolder.setEnabled(True)
            self.pButRenameFolder.setText('Rename')
            self.pButRenameFolderDir.setEnabled(True)
            self.lineEditRenameFolderDir.setEnabled(True)
        if ret!='0':
            QMessageBox.warning(self, "Warning", "Rename folder failed, check configs!", QMessageBox.Ok)


    def select_sequence_image_dir(self):
        imageDir = QFileDialog.getExistingDirectory(self, 'Select Sequence Image Dir')
        if os.path.exists(imageDir):
            self.lineEditSequenceImageDir.setText(imageDir)

    def select_sequence_annotation_path(self):
        if self.comboBoxAnnotation.currentText() == 'Detection':
            annotationPath = QFileDialog.getExistingDirectory(self, 'Select Sequence Xml Dir', './')
        elif self.comboBoxAnnotation.currentText() == 'Tracking':
            annotationPath, _ = QFileDialog.getOpenFileName(self, 'Select Sequence Annotations Path', './', 'txt file (*.txt)')
        else: annotationPath = ''
        if os.path.exists(annotationPath):
            self.lineEditAnnotationPath.setText(annotationPath)

    def select_video_path(self):
        videoPath, _ = QFileDialog.getOpenFileName(self, 'Select Video Path', './', "video file (*.mp4 *.avi)")
        if os.path.exists(videoPath):
            self.lineEditVideoPath.setText(videoPath)

    def select_rename_folder_dir(self):
        folderDir = QFileDialog.getExistingDirectory(self, 'Select Rename folder Dir')
        if os.path.exists(folderDir):
            self.lineEditRenameFolderDir.setText(folderDir)

    def annotation_option_edit(self):
        annotationType = self.comboBoxAnnotation.currentText()
        if annotationType == 'None':
            self.lineEditAnnotationPath.setEnabled(False)
            self.pButAnnotationPath.setEnabled(False)
            self.pButViewTracks.setEnabled(False)
        else:
            self.lineEditAnnotationPath.setEnabled(True)
            self.pButAnnotationPath.setEnabled(True)
            if annotationType == 'Tracking':
                self.pButViewTracks.setEnabled(True)
            else:
                self.pButViewTracks.setEnabled(False)

    def check_op(self, message):
        reply = QMessageBox.question(self, 'Message', message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def get_common_configs(self):
        commonCfg = CommonCfg()
        commonCfg.prefix = self.lineEditPrefix.text()
        commonCfg.suffix = self.comboBoxSuffix.currentText()
        commonCfg.startIdx = self.spinBoxStartIdx.value()
        commonCfg.endIdx = self.spinBoxEndIdx.value()
        commonCfg.interval = self.spinBoxInterval.value()
        commonCfg.zfill = self.spinBoxZfill.value()
        commonCfg.fps = self.spinBoxFPS.value()
        commonCfg.lineWidth = self.spinBoxLineWidth.value()
        return commonCfg


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = PyTools()
    w.show()
    sys.exit(app.exec_())
