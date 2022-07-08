import cv2
import os
import shutil
import xml.etree.ElementTree as ET

from .track_tools import get_anno_dict, get_color


class CommonCfg:
    prefix = ''
    suffix = '.jpg'
    zfill = 1
    fps = 30
    startIdx = 1
    endIdx = -1
    interval = 1
    lineWidth = 1


def video2sequence(videoPath, sequenceDir=None, cfg:CommonCfg=None) -> int:
    if sequenceDir is None or not os.path.exists(sequenceDir):
        fileName = os.path.splitext(os.path.basename(videoPath))[0]
        sequenceDir = os.path.join(os.path.dirname(videoPath), fileName)
    if os.path.exists(sequenceDir):
        shutil.rmtree(sequenceDir)
    os.mkdir(sequenceDir)

    vc = cv2.VideoCapture(videoPath)
    frameNums = int(vc.get(7))
    
    startIdx = max(0, cfg.startIdx)
    endIdx = min(cfg.endIdx, frameNums)
    if endIdx==-1: endIdx = frameNums

    ret = vc.isOpened()
    for curFrameIdx in range(1, frameNums+1):
        ret, frame = vc.read()
        if ret:
            if startIdx <= curFrameIdx <= endIdx and (curFrameIdx - cfg.startIdx) % cfg.interval == 0:
                imageName = cfg.prefix + str(curFrameIdx).zfill(cfg.zfill) + cfg.suffix
                cv2.imwrite(os.path.join(sequenceDir, imageName), frame)
                cv2.waitKey(1)
            else:
                continue
        else:
            break
    vc.release()
    return 0


def sequence2video(imageDir, videoPath=None, cfg:CommonCfg=None) -> int:
    if videoPath is None or not os.path.exists(os.path.dirname(videoPath)):
        videoPath = imageDir + '.avi'
    if not videoPath.endswith('.avi'): return -1

    imageNums = len(os.listdir(imageDir))

    startIdx = max(0, cfg.startIdx)
    endIdx = min(cfg.endIdx, imageNums)
    if endIdx==-1:endIdx=imageNums
    
    if not (startIdx < endIdx <=  imageNums): return -1

    frame = cv2.imread(os.path.join(imageDir, f'{cfg.prefix}{str(startIdx).zfill(cfg.zfill)}{cfg.suffix}'))
    h, w = frame.shape[0], frame.shape[1]
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    videoWriter = cv2.VideoWriter(videoPath, fourcc, cfg.fps, (w, h))
    videoWriter.write(frame)
    for idx in range(startIdx+cfg.interval, endIdx, cfg.interval):
        imagePath = os.path.join(imageDir, f'{cfg.prefix}{str(idx).zfill(cfg.zfill)}{cfg.suffix}')
        if not os.path.exists(imagePath):
            return -1
        frame = cv2.imread(imagePath)
        videoWriter.write(frame)
    videoWriter.release()
    return 0


def detections2vides(imageDir, xmlDir, videoPath=None, cfg:CommonCfg=None) -> int:

    cateDict = {}
    if videoPath is None or not os.path.exists(os.path.dirname(videoPath)):
        videoPath = imageDir + '.avi'
    if not videoPath.endswith('.avi'): return -1

    imageNums = len(os.listdir(imageDir))

    startIdx = max(0, cfg.startIdx)
    endIdx = min(cfg.endIdx, imageNums)
    if endIdx==-1:endIdx=imageNums
    
    if not (startIdx < endIdx <=  imageNums): return -1

    frame = cv2.imread(os.path.join(imageDir, f'{cfg.prefix}{str(startIdx).zfill(cfg.zfill)}{cfg.suffix}'))
    targets = get_targets_from_xml(os.path.join(xmlDir, f'{cfg.prefix}{str(startIdx).zfill(cfg.zfill)}.xml'), cateDict)
    
    h, w = frame.shape[0], frame.shape[1]
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    videoWriter = cv2.VideoWriter(videoPath, fourcc, cfg.fps, (w, h))
    videoWriter.write(draw_detections(frame, targets, cfg.lineWidth))
    for idx in range(startIdx+cfg.interval, endIdx, cfg.interval):
        imagePath = os.path.join(imageDir, f'{cfg.prefix}{str(idx).zfill(cfg.zfill)}{cfg.suffix}')
        if not os.path.exists(imagePath):
            return -1
        frame = cv2.imread(imagePath)
        targets = get_targets_from_xml(os.path.join(xmlDir, f'{cfg.prefix}{str(idx).zfill(cfg.zfill)}.xml'), cateDict)
        videoWriter.write(draw_detections(frame, targets, cfg.lineWidth))
    videoWriter.release()
    return 0

def tracking2vides(imageDir, txtPath, videoPath=None, cfg:CommonCfg=None) -> int:
    if videoPath is None or not os.path.exists(os.path.dirname(videoPath)):
        videoPath = imageDir + '.avi'
    if not videoPath.endswith('.avi'): return -1

    imageNums = len(os.listdir(imageDir))

    startIdx = max(0, cfg.startIdx)
    endIdx = min(cfg.endIdx, imageNums)
    if endIdx==-1:endIdx=imageNums
    
    if not (startIdx < endIdx <=  imageNums): return -1

    annoDict = get_anno_dict(txtPath)

    frame = cv2.imread(os.path.join(imageDir, f'{cfg.prefix}{str(startIdx).zfill(cfg.zfill)}{cfg.suffix}'))
    h, w = frame.shape[0], frame.shape[1]
    if startIdx in annoDict: 
        targets = annoDict[startIdx]
        frame = draw_tracks(frame, targets, cfg.lineWidth)
    
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    videoWriter = cv2.VideoWriter(videoPath, fourcc, cfg.fps, (w, h))

    videoWriter.write(frame)
    for idx in range(startIdx+cfg.interval, endIdx, cfg.interval):
        imagePath = os.path.join(imageDir, f'{cfg.prefix}{str(idx).zfill(cfg.zfill)}{cfg.suffix}')
        if not os.path.exists(imagePath):
            return -1
        frame = cv2.imread(imagePath)
        if idx in annoDict: 
            targets = annoDict[idx]
            frame = draw_tracks(frame, targets, cfg.lineWidth)
        videoWriter.write(frame)
    videoWriter.release()
    return 0


def draw_tracks(image, targets, lineWidth=1):
    for targetId, x, y, w, h in targets:
        color = get_color(targetId)
        cv2.rectangle(image, (x, y), (x+w, y+h), color, lineWidth)
        cv2.putText(image, str(targetId), (x, y-2), cv2.FONT_HERSHEY_SIMPLEX, 1, color, lineWidth)
    return image

def draw_detections(image, targets, lineWidth=1):
    for x1, y1, x2, y2, catename, cateId in targets:
        color = get_color(cateId)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, lineWidth)
        cv2.putText(image, catename, (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX, 1, color, lineWidth)
    return image

def convert_video_format(video_path, inFormat, outFormat='.mp4'):
    if not os.path.basename(video_path).lower().endswith(inFormat): return
    result_path = video_path.replace(inFormat, outFormat)
    os.system(f"ffmpeg -i {video_path} {result_path}")


def get_targets_from_xml(xmlPath, cateDict:dict):
    targets = []
    xmlRoot = ET.parse(xmlPath)
    objectElements = xmlRoot.findall("object")
    for objectNode in objectElements:
        catename = objectNode.find('name').text.capitalize()
        if catename not in cateDict:
            cateId = len(cateDict.keys())
            cateDict[catename] = cateId
        bbox = objectNode.find('bndbox')
        x1 = int(float(bbox.find('xmin').text))
        y1 = int(float(bbox.find('ymin').text))
        x2 = int(float(bbox.find('xmax').text))
        y2 = int(float(bbox.find('ymax').text))
        targets.append([x1, y1, x2, y2, catename, cateDict[catename]])
    
    return targets


if __name__ == '__main__':
    pass

    #############################################################################
    # 序列转视频
    # sequenceRootDir = "C:/Users/QIU/Desktop/01_20220704080522-20220704080822_1"
    # for seqname in os.listdir(sequenceRootDir):
    #     sequenceDir = os.path.join(sequenceRootDir, seqname)
    #     sequence2video(sequenceDir=sequenceDir, fps=25)
    #############################################################################



    #############################################################################
    # 视频转序列
    # rootDir = 'C:/Users/QIU/Desktop/Videos/'
    # for videoName in os.listdir(rootDir):
    #     videoPath = os.path.join(rootDir, videoName)
    #     video2sequence(videoPath, sequencePath=None, frameInterval=1, fillCount=8)
    #############################################################################



    ############################################################################
    # 视频格式转换
    # rootDir = 'C:/Users/QIU/Desktop/test/'
    # for videoName in os.listdir(rootDir):
    #     videoPath = os.path.join(rootDir, videoName)
    #     convert_video_format(videoPath, inFormat='.wmv', outFormat='.mp4')
    ############################################################################
    xmlPath = 'C:/Users/QIU/Desktop/Videos/labels/0001572.xml'
    cateDict = {}
    get_targets_from_xml(xmlPath, cateDict)
    print(cateDict)


