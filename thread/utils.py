import os


def rename_folder(folderDir, originIndexSort, cfg):
    if not originIndexSort:
        filenames = os.listdir(folderDir)
        for idx in range(len(filenames)):
            suffix = filenames[idx].split('.')[-1]
            dstName = f'{cfg.prefix}{str(idx+1).zfill(cfg.zfill)}.{suffix}'
            os.rename(os.path.join(folderDir, filenames[idx]), os.path.join(folderDir, dstName))
    else:
        for idx in range(cfg.startIdx, cfg.startIdx+len(os.listdir(folderDir))):
            srcName = f'{cfg.prefix}{idx}{cfg.suffix}'
            srcPath = os.path.join(folderDir, srcName)
            if os.path.exists(srcPath):
                dstName = f'{cfg.prefix}{str(idx).zfill(cfg.zfill)}{cfg.suffix}'
                os.rename(srcPath, os.path.join(folderDir, dstName))
    return 0
