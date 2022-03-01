import cv2
import os
import shutil
from tqdm import tqdm
import glob


def video2sequence(videoPath, sequencePath=None, frameInterval=1, fillCount=8):
    if sequencePath is None or not os.path.exists(sequencePath):
        fileName = os.path.splitext(os.path.basename(videoPath))[0]
        sequencePath = os.path.join(os.path.dirname(videoPath), fileName)
    if os.path.exists(sequencePath):
        shutil.rmtree(sequencePath)
    os.mkdir(sequencePath)

    vc = cv2.VideoCapture(videoPath)
    frameNums = vc.get(7)
    frameFps = vc.get(5)
    frameWidth = vc.get(3)
    frameHeight = vc.get(4)

    print(f'video_name: {os.path.basename(videoPath)}, frame count: {frameNums}, video fps: {frameFps}, '
          f'frame size: ({frameWidth}, {frameHeight})')
    ret = vc.isOpened()
    for curFrameIdx in tqdm(range(int(frameNums))):
        ret, frame = vc.read()

        if ret:
            if curFrameIdx % frameInterval == 0 and curFrameIdx > 0:
                imageName = 'img' + str(curFrameIdx).zfill(fillCount) + '.jpg'
                cv2.imwrite(os.path.join(sequencePath, imageName), frame)
                cv2.waitKey(1)
            else:
                continue
        else:
            break
    vc.release()


def sequence2video(sequenceDir, videoPath=None, fps=30, suffix='.jpg'):
    if videoPath is None or not os.path.exists(os.path.dirname(videoPath)):
        videoPath = sequenceDir + '.avi'
    assert videoPath.endswith('.avi')

    imagePaths = glob.glob(f'{sequenceDir}/*{suffix}')
    # print(imagePaths)
    frame = cv2.imread(imagePaths[0])
    h, w = frame.shape[0], frame.shape[1]
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    videoWriter = cv2.VideoWriter(videoPath, fourcc, fps, (w, h))
    videoWriter.write(frame)

    for imagePath in tqdm(imagePaths[1:]):
        frame = cv2.imread(imagePath)
        videoWriter.write(frame)
    videoWriter.release()


def convert_video_format(video_path, inFormat, outFormat='.mp4'):
    if not os.path.basename(video_path).lower().endswith(inFormat): return
    result_path = video_path.replace(inFormat, outFormat)
    os.system(f"ffmpeg -i {video_path} {result_path}")


if __name__ == '__main__':
    pass

    #############################################################################
    # 序列转视频
    # sequenceRootDir = "C:/Users/QIU/Desktop/UAV-benchmark-M/sequences"
    # for seqname in os.listdir(sequenceRootDir):
    #     sequenceDir = os.path.join(sequenceRootDir, seqname)
    #     sequence2video(sequenceDir=sequenceDir, fps=30)
    #############################################################################



    #############################################################################
    # 视频转序列
    rootDir = 'C:/Users/QIU/Desktop/xianchangbaojingshipin20220216/'
    for videoName in os.listdir(rootDir):
        videoPath = os.path.join(rootDir, videoName)
        video2sequence(videoPath, sequencePath=None, frameInterval=25, fillCount=8)
    #############################################################################



    ############################################################################
    # 视频格式转换
    # rootDir = 'C:/Users/QIU/Desktop/test/'
    # for videoName in os.listdir(rootDir):
    #     videoPath = os.path.join(rootDir, videoName)
    #     convert_video_format(videoPath, inFormat='.mp4', outFormat='.flv')
    ############################################################################


