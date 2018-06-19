'''
'''
# coding = 'utf-8'
from colorama import init, Fore, Style
init(autoreset=True, strip=False)

from src.imageproc import ImageExtractor
import cv2
import os
import pathlib
from src.Util import Path


class VideoShotFrameExtrator(object):
    def __init__(self):
        pass

    # def writeFrames(self, src, dst):
    #     videonames = self.__getVideonames(src)
    #     for videoname in videonames:
    #         ImageExtractor.getImageExtracter

    def writeFrames(self, videoDir, frameDirRoot):
        videoFilenames = self.__getVideonames(videoDir)
        #videoFilenames =[r'E:\test\AHVM1130723100003000-1.ts']
        count = 0
        for videoFilename in videoFilenames:
            try:
                framesDir = self.__getTargetDir(videoFilename, frameDirRoot)
                self.__writeFrames(videoFilename, framesDir)
                count += 1
                if count % 10 == 0:
                    print(f'已经处理了 {Fore.GREEN}{count}{Style.BRIGHT}{Fore.WHITE} 个文件了')
            except Exception as err:
                print(err)
                print(videoFilename)

    def __getTargetDir(self, videoFilename, frameDirRoot):
        #输入视频文件名和镜头帧输出文件夹，输出镜头帧文件夹
        targetDir = frameDirRoot+'/'+pathlib.PurePath(videoFilename).stem
        os.mkdir(targetDir)
        return targetDir

    def __getVideonames(self,src):
        #输入视频文件夹，输出视频绝对路径
        return  Path.ilistFilesEx(src)


    def __writeFrames(self, videoFilename, framesDir):
        #输入为视频文件名，在镜头帧输出文件夹内写入镜头帧
        with ImageExtractor.getImageExtractor(videoFilename, shotFrameOnly='yes') as extractor:
            for param in extractor:
                #print(f'{param["shotIndex"]}_{param["index"]}')
                #print(param['frame'].shape)
                #return
                cv2.imwrite(f'{framesDir}/{param["shotIndex"]}_{param["index"]}.jpg',param['frame'])




if __name__ == '__main__':
    #src = r'E:\ADVT'
    src =r'C:\Users\Mozhouting\Desktop\testVideo\test'

    dst = r'C:\Users\Mozhouting\Desktop\testVideo\shotFrames'

    vsfe = VideoShotFrameExtrator()
    vsfe.writeFrames(src, dst)