'''
'''
# coding = 'utf-8'

import cv2
import colorama

from src.Util.Path import ilistFilesEx

colorama.init(autoreset=True)
import contextlib
from collections import deque, defaultdict
from typing import List, Tuple, Union, Sequence
import itertools
from collections import defaultdict



class ImageExtracter(object):
    '''
    '''

    def __init__(self, filename):
        self.__captor = cv2.VideoCapture(filename)

        if not self.__captor.isOpened():
            raise ValueError(f'{colorama.Fore.RED}cannot open video {filename}')
        self.__currentFrameIndex = -1
        self.__eof = False


    def __iter__(self):
        return self


    def __next__(self):
        if self.__eof:
            raise StopIteration
        
        #while True:
        ret, frame = self.__captor.read()
        if not ret:
            self.__eof = True
            raise StopIteration

        self.__currentFrameIndex += 1
        return { 'index': self.__currentFrameIndex, 'frame': frame }
            

    def release(self):
        self.__captor.release()




class ImageFilter(object):

    def __init__(self, extracter):
        self.__extracter = extracter


    def __iter__(self):
        filteredResult = (self._filter(result) for result in self.__extracter)
#
        #yield from (fr for fr in filteredResult if fr is not None)
        return (fr for fr in filteredResult if fr is not None)

    
    def _filter(self, param):
        # 子类重写此函数
        # 默认什么都不做, 直接返回内层Filter或Extracter传递的param
        return param


    def release(self):
        self.__extracter.release()
        self._release()


    def _release(self):
        # 子类重写此函数
        # 默认什么都不做
        pass

    @property
    def extracter(self):
        return self.__extracter


class FrameIndexFilter(ImageFilter):
    ''' 间隔采样过滤器
    '''
    def __init__(self, extracter, interval):
        super(FrameIndexFilter, self).__init__(extracter)
        self.__interval = interval


    def _filter(self, param):
        return param if not (param['index'] % self.__interval) else None



class ShotFrameFilter(ImageFilter):
    '''镜头帧过滤器
    '''
    def __init__(self, extractor, minInterval=25, minSimilarity=0.85):
        super(ShotFrameFilter, self).__init__(extractor)
        self.__minInterval = minInterval
        self.__prevFrame = None
        self.__currentFrame = None
        self.__totalShots = 0
        self.__interval = minInterval - 1
        self.__minSimilarity = minSimilarity
    

    def _filter(self, param):
        self.__currentFrame = param['frame']

        self.__interval += 1
        if self.__interval < self.__minInterval:
            return None

        if not self._reachShotFrame():
            self.__prevFrame = self.__currentFrame
            return None

        self.__prevFrame = self.__currentFrame
        param['shotIndex'] = self.__totalShots
        self.__totalShots += 1
        self.__interval = 0
        return param


    def _reachShotFrame(self):
        '''判断是否到达镜头帧
        '''
        return self.__prevFrame is None\
                or not ShotFrameFilter._areImagesSimilar(self.__prevFrame, self.__currentFrame, self.__minSimilarity)


    @staticmethod
    def _areImagesSimilar(image0, image1, threshold):
        '''判断两幅图像是否相似

        参数:
        image0: 第一幅图像(BGR格式)
        image1: 第二幅图像(BGR格式)
        threshold: 相似度阈值
        '''
        hsv0 = cv2.cvtColor(image0, cv2.COLOR_BGR2HSV)
        hsv1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
        hist0 = ShotFrameFilter._calHSVHist(hsv0)
        hist1 = ShotFrameFilter._calHSVHist(hsv1)
        return cv2.compareHist(hist0, hist1, cv2.HISTCMP_CORREL) >= threshold


    @staticmethod
    def _calHSVHist(hsv):
        '''计算HSV图像的直方图
            
        三通道bin数分别为[8, 4, 4]

        参数:
        hsv: hsv格式图像
        '''
        return cv2.calcHist([hsv], [0, 1, 2], None, [8, 4, 4], [0, 181, 0, 256, 0, 256])


class ShotFrameMarker(ShotFrameFilter):

    def __init__(self, extractor, minInterval=25, minSimilarity=0.85):
        super(ShotFrameMarker, self).__init__(extractor, minInterval, minSimilarity)

    def __iter__(self):
        for param in self.extracter:
            fr = self._filter(param)
            param['isShotFrame'] = (fr is not None)
            yield param



class SpecIndexFilter(ImageFilter):
    '''过滤出指定帧索引的过滤器
    '''
    def __init__(self, extractor: Union[ImageExtracter, ImageFilter], specIndices: List[Tuple[int, int]]):
        '''
        '''
        super(SpecIndexFilter, self).__init__(extractor)
        try:
            self.__specIndices = SpecIndexFilter.__prepareSpecIndices(specIndices)
        except Exception as err:
            raise ValueError(f'Invalid specIndices: {specIndices} with error: {err}')

        self.__currentRange = self.__specIndices.popleft() if self.__specIndices else None


    def __iter__(self):
        return self


    def __next__(self):
        if self.__currentRange is None:
            raise StopIteration

        for param in self.extracter:
            index = param['index']
            if self.__currentRange[0] <= index < self.__currentRange[1]:
                return param
            elif index == self.__currentRange[1]:
                if not self.__specIndices:
                    break
                else:
                    self.__currentRange = self.__specIndices.popleft()
                    if self.__currentRange[0] == index:
                        return param
                
        self.__currentRange = None
        raise StopIteration


    @staticmethod
    def __prepareSpecIndices(specIndices: List[Tuple[int, int]]):
        for _range in specIndices:
            if not (isinstance(_range[0], int)
                and isinstance(_range[1], int)
                and (0 <= _range[0] < _range[1])):
                raise ValueError(f'invalid range detected on {_range}')

        if len(specIndices) < 2:
            return deque(specIndices)

        _specIndices = sorted(specIndices, key=lambda tp: tp[0])
        for range0, range1 in zip(_specIndices[:-1], _specIndices[1:]):
            if range0[1] > range1[0]:
                raise ValueError(f'ranges overlapped between {range0} and {range1}')
        
        return deque(_specIndices)


class addSpecIndexFilter(ImageFilter):
    def __init__(self, extractor, addframe):
        super(addSpecIndexFilter, self).__init__(extractor)
        self.__frame, self.__repeatTimes = addframe


    def __iter__(self):
        extraFrames = itertools.repeat(self.__frame, self.__repeatTimes)
        videoFrames = (param['frame'] for param in self.extracter)
        frames = itertools.chain(extraFrames, videoFrames)
        return ({'index': index, 'frame': frame} for index, frame in enumerate(frames))



class _FrameObserver(object):

    def __init__(self, start, end, observee):
        if start < end:
            self.__start, self.__end, self.__isPostive = start, end, True
        else:
            self.__start, self.__end, self.__isPostive = end + 1, start + 1, False
        self.__images = []
        self.__observee = observee

    def handle(self, index, frame):
        if self.start <= index < self.end:
            self.__images.append(frame)
        elif index == self.end:
            self.__observee.unregister(self)
             

    @property
    def start(self):
        return self.__start


    @property
    def images(self):
        return self.__images if self.__isPostive else self.__images[::-1]
    
#此类是observee
class _FancyImageExtractor(object):
    def __init__(self, videoFilename, indices):
        self.__frameObservers = [_FrameObserver(*tp, self) for tp in indices]#全队列
        self.__activeObservers = []#工作队列
        self.__unregisterObservers = []#反注册队列

        #defaultdict

        # d = defaultdict(lambda: len(d))
        # for i in l:
        #     if i not in d.keys():
        #         print(d[i])
        # print(d)
       
        _dict = defaultdict(list)
        for fo in self.__frameObservers:
            _dict[fo.start].append(fo)
        #deque构建队列
        self.__candidates = deque(sorted(_dict.items(), key=lambda tp:tp[0]))
        self.__nextCandidate = self.__candidates.popleft() if self.__candidates else None
        self.__videoFilename = videoFilename

    def extract(self):
        if self.__nextCandidate is None:
            return

        ie = ImageExtracter(self.__videoFilename)
        for param in ie:
            index = param['index']
            if self.__nextCandidate and self.__nextCandidate[0] == index:
                self.__activeObservers.extend(self.__nextCandidate[1])
                self.__nextCandidate = self.__candidates.popleft() if self.__candidates else None

        
            for fo in self.__activeObservers:
                fo.handle(index, param['frame'])

            if self.__unregisterObservers:
                for fo in self.__unregisterObservers:
                    self.__activeObservers.remove(fo)
                self.__unregisterObservers = []
                
            if not (self.__activeObservers or self.__nextCandidate):
                break

        ie.release()
        return [fo.images for fo in self.__frameObservers]


    def unregister(self, observer):
        self.__unregisterObservers.append(observer)


def fancyExtractImage(videoFilename, indices):
    return _FancyImageExtractor(videoFilename, indices).extract()


@contextlib.contextmanager
def getImageExtractor(filename, interval=0, shotFrameOnly='no', specIndices=[]):
    '''
    '''
    imageExtractor = None
    try:
        imageExtractor = ImageExtracter(filename)

        if interval != 0:
            imageExtractor = FrameIndexFilter(imageExtractor, interval)

        if shotFrameOnly == 'yes':
            imageExtractor = ShotFrameFilter(imageExtractor)

        if specIndices:
            imageExtractor = SpecIndexFilter(imageExtractor, specIndices)


        yield imageExtractor

    finally:
        if imageExtractor is not None:
            imageExtractor.release()


@contextlib.contextmanager
def getImageExtractor(filename, interval=0, shotFrameOnly='no', specIndices=[], addImage = None):
    '''
    '''
    imageExtractor = None
    try:
        imageExtractor = ImageExtracter(filename)

        if interval != 0:
            imageExtractor = FrameIndexFilter(imageExtractor, interval)

        if shotFrameOnly == 'yes':
            imageExtractor = ShotFrameFilter(imageExtractor)

        if specIndices:
            imageExtractor = SpecIndexFilter(imageExtractor, specIndices)

        if addImage:
            imageExtractor = addSpecIndexFilter(imageExtractor, addImage)


        yield imageExtractor

    finally:
        if imageExtractor is not None:
            imageExtractor.release()


# filename0 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
#
# specIndices0 = [(0, 1), (10, 11)]
# import numpy as np
#
# frame = cv2.imread(r"C:\Users\Mozhouting\Desktop\ImagesStitcher\0.jpg")
# import itertools
#
# with getImageExtractor(filename0, specIndices=specIndices0) as extractor0:
#     stitchedFrames = list(itertools.chain(itertools.repeat(frame, 3), [param['frame'] for param in extractor0]))
#     for flag, stitchedFrame in enumerate(stitchedFrames):
#         cv2.imwrite(f'C://Users\Mozhouting\Desktop\ImagesStitcher\{flag}.jpg', stitchedFrame)



if __name__ == '__main__':
    # l = {'letter':['A','B', 'C', 'D', 'E', ['F', 'G']],'num':[1,2,3]}
    # c = 'Q'
    # # ['Q', 'Q', 'Q', 'A', 'B', 'C', 'D', 'E']
    # import itertools
    # print(list(itertools.chain(itertools.repeat(c, 3) ,gen1(l['letter']))))
    # print(list(itertools.chain.from_iterable(l)))


    # filename0 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
    # filename1 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
    # filename2 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
    #
    # specIndices0 = [(2, 4), (100,101)]
    # specIndices1 = [(0, 1), (100, 101)]
    # specIndices2 = [(0, 1), (100, 101)]
    # import numpy as np
    # with getImageExtractor(filename0, specIndices=specIndices0) as extractor0, \
    #     getImageExtractor(filename1, specIndices=specIndices1) as extractor1, \
    #     getImageExtractor(filename2, specIndices=specIndices2) as extractor2:
    #
    #     for index, params in enumerate(zip(extractor0, extractor1, extractor2)):
    #         cv2.imwrite(f'd:/{index}.jpg', np.vstack((params[0]['frame'], params[1]['frame'],params[2]['frame'])))


    # from time import clock
    # start = clock()
    # import os
    #
    # count = -1
    # for path in ilistFilesEx('E:\ADVT'):
    #     path = r"C:\Users\Mozhouting\Desktop\AHVM1130723100003000-1.ts"
    #     ie = ImageExtracter(path)
    #     sfm = ShotFrameMarker(ie)
    #     for param in sfm:
    #         # cv2.imwrite(f'd:/1/{param["index"]}_{param["shotIndex"]}_{param["isShotFrame"]}.jpg',param['frame']
    #         print(param.keys())
            #cv2.imwrite(f'd:/1/{param["index"]}_{param["isShotFrame"]}.jpg', param['frame'])
    #
    #     for param in sfm:
    #         if param['isShotFrame']:
    #             if count == 999:
    #                 break
    #             count += 1
    #             print(param['index'])
    #             os.mkdir(f'E:/videoAllFrames/{count}')
    #
    #         cv2.imwrite(f'E:/videoAllFrames/{count}/{param["index"]}.jpg', param['frame'])
    #     if count == 999:
    #         break
    # finish=clock()
    # print (finish-start)
    path = r"C:\Users\Mozhouting\Desktop\testVideo\test3\素材\concat3.mp4"
    # ie = ImageExtracter(path)
    # sfm = ShotFrameMarker(ie)
    with getImageExtractor(path,interval=0, shotFrameOnly='no', specIndices=[]) as extractor0:

        for param in extractor0:
            # cv2.imwrite(f'd:/2/{param["index"]}_{param["shotIndex"]}}.jpg',param['frame'])
            print(param["index"])










