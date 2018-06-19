'''从视频中获取图像
'''
# coding = 'utf-8'

import cv2
import colorama
colorama.init(autoreset=True)

class ImageExtracter(object):
    '''图像提取器
    '''

    def __init__(self, filename, interval=0):
        self.__captor = cv2.VideoCapture(filename)
        if not self.__captor.isOpened():
            raise ValueError(f'{colorama.Fore.RED}cannot open video {filename}')
        self.__eof = False
        self.__currentFrameIndex = -1
        self.__interval = interval

    def __iter__(self):
        return self


    def __next__(self):
        if self.__eof:
            raise StopIteration
        
        ret, frame = self.__captor.read()
        if not ret:
            self.__eof = True
            raise StopIteration
        else:
            self.__currentFrameIndex += 1
            return frame


if __name__ == '__main__':
    
    ie = ImageExtracter('d:/qqq.mp4')