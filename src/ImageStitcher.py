'''
'''
# coding = 'utf-8'



# filename0 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
# filename1 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
# filename2 = r"C:\Users\Mozhouting\Desktop\testVideo\0210广告节目.avi"
#
# specIndices0 = [(2, 4), (100, 101)]
# specIndices1 = [(0, 1), (100, 101)]
# specIndices2 = [(0, 1), (100, 101)]
# import numpy as np
#
# with getImageExtractor(filename0, specIndices=specIndices0) as extractor0, \
#         getImageExtractor(filename1, specIndices=specIndices1) as extractor1, \
#         getImageExtractor(filename2, specIndices=specIndices2) as extractor2:
#     for index, params in enumerate(zip(extractor0, extractor1, extractor2)):
#         cv2.imwrite(f'd:/{index}.jpg', np.vstack((params[0]['frame'], params[1]['frame'], params[2]['frame'])))




import functools

from src.imageproc import ImageExtractor
import numpy as np
import cv2

class ImagesStitcher(object):
    def __init__(self,config):
        self.__config = config

    def __index2Img(self, index, videoname):
        with ImageExtractor.getImageExtracter(videoname, shotFrameOnly='no') as extractor:
            def a(n):
                for param in extractor:
                    if n == param['index']:
                        return param['frame']

            def fn(l, n):
                return l + [a(n)]
            return functools.reduce(fn, index, [])



    def __findFrames(self):

        frame0 = self.__index2Img(self.__config['index'][0], self.__config['video'][0])
        frame1 = self.__index2Img(self.__config['index'][1], self.__config['video'][1])
        frame2 = self.__index2Img(self.__config['index'][2], self.__config['video'][2])
        return frame0, frame1, frame2


    def stitchFrames(self):
        '''拼接三张图片，将拼接后的图片输出
        用于对照三张图片，查看检索效果

        :return:
        '''
        frame0, frame1, frame2 = self.__findFrames()
        for flag,frames in enumerate(zip(frame0, frame1, frame2)):
            stitchedFrames = np.concatenate(frames, axis=0)
            print(stitchedFrames)
            cv2.imwrite(f'C://Users\Mozhouting\Desktop\ImagesStitcher\{flag}.jpg', stitchedFrames)


if __name__ == '__main__':
    config = {
        'video': [r"C:\Users\Mozhouting\Desktop\ImagesStitcher\1.ts",
                  r"C:\Users\Mozhouting\Desktop\ImagesStitcher\2.ts",
                  r"C:\Users\Mozhouting\Desktop\ImagesStitcher\3.ts"],
        'index': [ [0,100], [0,100], [0,100]]
    }
    iser = ImagesStitcher(config)
    iser.stitchFrames()
    print(config)
    # stitchedFrames = np.concatenate(frames, axis=0)
