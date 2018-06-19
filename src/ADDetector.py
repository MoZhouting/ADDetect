'''
'''
# coding = 'utf-8'

#import Type.List
#from  src import ImageFinder
import operator
import numpy as np
from src import ImageFinder
from src.imageproc import ImageExtractor

import  functools
from typing import List,Tuple



class ADDetector(object):
    def __init__(self, config):

        self.__df = DistFinder(config)
        self.__da = DiscriminateAlgorithm(config)



    def run(self, videoFilename: str, resultFilename: str):
        '''检测视频中广告的首尾帧号

        对视频文件进行广告检测，并将检测结果输出到文件
        输出文件中可能有0行或者1行，0行表示视频中没有广告，1行表示视频中所有广告的首尾帧号。
        数据格式示例如下：
        0,513,1024,2049,4096,8193
        它表示视频中包含3段广告，
        第一段广告的首尾帧号分别是0和513，
        第二段广告的首尾帧号分别是1024和2049，
        第三段广告的首尾帧号分别是是4096和8193
        注意：首尾帧号表示了一个左闭右开的帧区间，
        也就是，如果尾帧号513表示最后一个广告帧的帧号是512

        参数
        -----
        videoFilename: 待检测的视频文件的路径
        resultFilename: 结果输出文件。

        '''

        distances = []
        i = 0
        with ImageExtractor.getImageExtractor(videoFilename, shotFrameOnly='yes') as sfe:

            for param in sfe:
                # distances:List[Tuple(float, int)] = self.__df.find(param['frame'])
                dist,label = self.__df.find(param['frame'])
                index = param['index']
                distances.append((dist, index,label[0],i))
                i = i+1
        print(distances)

        #:List[Tuple[int, int]]
        result= self.__da.discriminate(distances)
        self.__writeResult(result, resultFilename)

    def __writeResult(self, result, resultFilename):
        print(result)

class ShotFrameExtractor(object):
    def __init__(self):
        pass


class DistFinder(object):
    def __init__(self, config):
        self.f = ImageFinder.ImageFinder(config)

    def find(self, frame: np.ndarray) -> float:
        '''得到查询图像和图像库中所有图像的最小距离

        :param frame:
        查询图像

        :return:
        查询图像和图像库中最相似的图像的距离
        '''

        return self.f.find(frame, output = 'd')


class DiscriminateAlgorithm(object):
    def __init__(self, config):
        self.__threshold = config['threshold']

    def discriminate(self, dist: List[Tuple[float, int]]) -> List[Tuple[int, int]]:
        '''

        :param dist:
        是一个距离-帧号对组成的列表
        距离是图像和图像库中所有图像的最小距离

        :return:
        判别结果是一个list，list中每一项是一个tuple,一个tuple中存放一个广告的首尾帧号。
        数据格式示例如下：
        [(0,513),(1024,2049),(4096,8193)]
        它表示视频中包含3段广告，
        第一段广告的首尾帧号分别是0和513，
        第二段广告的首尾帧号分别是1024和2049，
        第三段广告的首尾帧号分别是是4096和8193
        注意：首尾帧号表示了一个左闭右开的帧区间，
        也就是，如果尾帧号513表示最后一个广告帧的帧号是512
        '''

        # a = [0, 1, 0, 0, 1]
        #
        # def fn(l, tp):
        #     if operator.xor(tp[1], len(l) % 2) == 1:
        #         l.append(tp[0])
        #
        #     elif tp[1] == 0 and len(l) % 2 == 1:
        #         l.append(tp[0])
        #     return l
        #
        # # def fn(l,tp):
        # #     # if tp[1] != len(l)%2:
        # #     #     return l + [tp[0]]
        # #     # else:
        # #     #     return l
        # #
        # #     return l + [tp[0]] if tp[1] != len(l)%2 else l
        # print(functools.reduce(fn, enumerate(a), []))
        for i in range(1,36):
            print(i)''
            #result = functools.reduce(lambda l, tp: l + [tp[1]] if (tp[0] < self.__threshold)^(len(l) % 2) else l, dist, [])
            result = functools.reduce(lambda l, tp: l + [tp[1]] if (tp[0] < i) ^ (len(l) % 2) else l,
                                      dist, [])
            result = list(zip(result[0::2], result[1::2]))
            print(f'{result}')
        #  result = [(0, 289),(314, 364), (462, 1442)]
        #  # def fn(l, tp):
        #  #     #l = [(0, 289)]
        #  #     # if tp[0] - l[-1][1] < 75:
        #  #     #     l = l[:-1]+[(l[-1][0],tp[1])]
        #  #     # else:
        #  #     #     l= l+[tp]
        #  #
        #  #     return l[:-1]+[(l[-1][0],tp[1])] if tp[0] - l[-1][1] < 75 else l+[tp]
        # # print(functools.reduce(fn,result,[(0, 289)]))
        #  print(functools.reduce(lambda l,tp:l[:-1]+[(l[-1][0],tp[1])] if tp[0] - l[-1][1] < 75 else l+[tp], result[1:], result[:1]))-
            print(functools.reduce(lambda l, tp: l[:-1] + [(l[-1][0], tp[1])] if tp[0] - l[-1][1] < 75 else l + [tp],
                           result[1:], result[:1]))
        return ''
        #return list(zip(result[0::2], result[1::2]))

if __name__ == '__main__':
    config = {
        'depth': 40,
        'modelPath': r"D:\dev\Unicorn\model\model2\model-249480.data-00000-of-00001",
        'imageSize': 64,

        'db': {
             'hashFeatureFilename': r"E:\videoShotFramesDbBuild\denseNeFeature\83432_feature_2.bin",
            # 'imageFeatureFilename': r"E:\videoShotFramesDbBuild\feature\2.bin",
            'imageFeatureFilename': r"E:\videoShotFramesDbBuild\denseNeFeature\83432_feature_2.bin",
            'labelsFilename': r"E:\videoShotFramesDbBuild\feature\labels.txt"
        },
        'extracter': {
            'num_classes': 11,
            'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
            },
        'threshold': 10

    }
    ADD = ADDetector(config)
    ADD.run(r"C:\Users\Mozhouting\Desktop\testVideo\0315.mp4", None)





