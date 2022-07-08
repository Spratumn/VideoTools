import os
import cv2


def view_tracks(imageDir, txtPath, prefix='', suffix='.jpg', zfill=1, startIdx=1, endIdx=-1, lineThickness=1):

    annoDict = get_anno_dict(txtPath)
    imageNums = len(os.listdir(imageDir))
    if not imageNums >= len(annoDict.keys()): return -1

    startIdx = max(0, startIdx)
    if endIdx==-1:endIdx=imageNums
    endIdx = min(endIdx, imageNums)
    if not (startIdx < endIdx <=  imageNums): return -1

    idx = startIdx
    while True:
        filename = f'{prefix}{str(idx).zfill(zfill)}{suffix}'
        imagePath = os.path.join(imageDir, filename)
        if not os.path.exists(imagePath):
            continue
        if idx not in annoDict:continue

        image = cv2.imread(imagePath)
        targets = annoDict[idx]

        for targetId, x, y, w, h in targets:
            color = get_color(targetId)
            cv2.rectangle(image, (x, y), (x+w, y+h), color, lineThickness)
            cv2.putText(image, str(targetId), (x, y-2), cv2.FONT_HERSHEY_SIMPLEX, 1, color, lineThickness)
        cv2.putText(image, f'({startIdx}-{endIdx}):{idx}, press ESC to exit.', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), lineThickness)
        
        cv2.namedWindow('tracks', 0)
        cv2.imshow('tracks', image)
        key = cv2.waitKey(0)
        
        if key == 27:break
        if key == 100:
            idx += 1
            idx = min(endIdx, idx)
        if key == 97:
            idx -= 1
            idx = max(startIdx, idx)
    return 0


def get_color(targetId):
    colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 0)]
    if targetId <= 3:
        return colors[targetId]
    idx = targetId * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)
    return color


def get_anno_dict(txtPath):
    """
    frameId, targetId, x, y, w, h, score, cateId, ...
    """
    with open(txtPath, 'r') as f:
        lines = f.readlines()
    annoDict = {}
    for line in lines:
        frameId, targetId, x, y, w, h =  [int(float(v)) for v in line.rstrip().split(',')[:6]]
        if frameId not in annoDict:
            annoDict[frameId] = [[targetId, x, y, w, h]]
        else:
            annoDict[frameId].append([targetId, x, y, w, h])

    return annoDict


if __name__ == '__main__':
    view_tracks(imageDir='C:/Users/QIU/Desktop/uav0000268_05773_v',
                txtPath='C:/Users/QIU/Desktop/radar/uav0000268_05773_v.txt',
                prefix='',
                suffix='.jpg',
                zfill=7,
                startIdx=1,
                endIdx=-1,
                lineThickness=3)