from PySide2.QtCore import QThread, Signal
from .video_tools import sequence2video, video2sequence, tracking2vides, detections2vides, CommonCfg
from .track_tools import view_tracks
from .utils import rename_folder

class Sequence2VideoThread(QThread):
    trigger = Signal(str)
    """
    """
    def __init__(self, sequenceDir, commonCfg:CommonCfg, xmlDir=None, txtPath=None):
        super(Sequence2VideoThread, self).__init__()
        self.sequenceDir = sequenceDir
        self.xmlDir = xmlDir
        self.txtPath = txtPath
        self.commonCfg = commonCfg

    def run(self):
        if self.xmlDir is None and self.txtPath is None:
            ret = sequence2video(self.sequenceDir, cfg=self.commonCfg)
        elif self.xmlDir is not None:
            ret = detections2vides(self.sequenceDir, xmlDir=self.xmlDir, cfg=self.commonCfg)
        else:
            ret = tracking2vides(self.sequenceDir, self.txtPath, cfg=self.commonCfg)
        self.trigger.emit(f'{ret},finish')


class Video2SequenceThread(QThread):
    trigger = Signal(str)
    """
    """
    def __init__(self, videoPath, commonCfg:CommonCfg):
        super(Video2SequenceThread, self).__init__()
        self.videoPath = videoPath
        self.commonCfg = commonCfg

    def run(self):
        ret = video2sequence(self.videoPath, cfg=self.commonCfg)
        self.trigger.emit(f'{ret},finish')
        

class ViewTracksThread(QThread):
    trigger = Signal(str)
    """
    """
    def __init__(self, sequenceDir, commonCfg:CommonCfg, txtPath):
        super(ViewTracksThread, self).__init__()
        self.sequenceDir = sequenceDir
        self.commonCfg = commonCfg
        self.txtPath = txtPath

    def run(self):
        prefix = self.commonCfg.prefix
        suffix = self.commonCfg.suffix
        zfill = self.commonCfg.zfill
        startIdx = self.commonCfg.startIdx
        endIdx = self.commonCfg.endIdx
        lineThickness = self.commonCfg.lineWidth
        ret = view_tracks(self.sequenceDir, self.txtPath, prefix, suffix, zfill, startIdx, endIdx, lineThickness)
        self.trigger.emit(f'{ret},finish')


class RenameFolderThread(QThread):
    trigger = Signal(str)
    """
    """
    def __init__(self, folderDir, originIndexSort, commonCfg):
        super(RenameFolderThread, self).__init__()
        self.folderDir = folderDir
        self.originIndexSort = originIndexSort
        self.commonCfg = commonCfg

    def run(self):
        ret = rename_folder(self.folderDir, self.originIndexSort, self.commonCfg)
        self.trigger.emit(f'{ret},finish')

