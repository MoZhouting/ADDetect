'''
'''
# coding = 'utf-8'

import sys
import operator
sys.path.append('d:/dev/unicorn/')
from src import ImageFinder
from src import FilesMaker
from src import DbBuild
from src import FeatureExtract
from pathlib import PurePath
from src.imageproc import ImageExtractor
from functools import reduce

class AccuracyItem(object):
    '''
    '''
    def __init__(self, correct: int, total: int):
        self.__correct = correct
        self.__total = total


    def __add__(self, other: 'AccuracyItem') -> 'AccuracyItem':
        return AccuracyItem(self.correct + another.correct, self.total + another.total)


    def __iadd__(self, other: 'AccuracyItem') -> 'AccuracyItem':
        self.__correct += another.correct
        self.__total += another.total
        return self


    def __str__(self) -> str:
        return f'total: {self.total}, correct: {self.correct}, wrong: {self.wrong}, accuracy: {self.accuracy:.{4}}'


    @property
    def correct(self) -> int:
        return self.__correct


    @property
    def total(self) -> int:
        return self.__total


    @property
    def wrong(self) -> int:
        return self.__total - self.__correct


    @property
    def accuracy(self) -> float:
        return self.__correct / self.__total if self.__total else float('nan')



class VideoPerformanceEvaluater(object):
    '''能将视频的镜头帧和镜头帧库比对，判断算法判定的镜头帧所属视频是否正确，输出准确度

    输入是config['imagePathAlias']指示的文件中的镜头帧路径
    '''
    def __init__(self,config):
        self.__actual = {}
        self.__expected = None
        self.__config = config
        self.__imageFinder = ImageFinder.ImageFinder(self.__config)
        self.__accuracyItems = []


    def evaluate(self):
        '''执行评估过程，输出性能数据

        :return:
        无
        '''
        self.__getActual()
        self.__loadExpected()
        isOK, reason = self.__compare()
        print(reason if not isOK else 'ok')


    def __getActual(self):

        #先处理一个视频
        #videoFilenames = [r"E:\ADVT\SV3M\2SV3M1130906080003120-2.ts"]
        # videoFilenames = []
        #
        # self.__actual = {'AHVM1130723100003000-1.ts': ['AHVM1130723100003000-1','AHVM1130723100003000-1','AHVM1130723100003000-1'],
        #                  'AHVM1130723100003000-2.ts': ['AHVM1130723100003000-2','AHVM1130723100003000-3','AHVM1130723100003000-3']}
        #for filename in videoFilenames:
        #config中['imagePathAlias']未修改，因为生成的文件名也要改，以免出错
        with open(self.__config['imagePathAlias'], 'r') as file:
            #WARNING!!!imageFinder.find()目前只能返回1个结果
            count = 0
            for videoPath, alias in (line.strip().split(' ') for line in file):
                try:
                    #label = 'zZJVM1130911340003420-11'
                    label = self.__getLabel(videoPath)

                except Exception as err:
                    print(err)
                    continue
                    #return
                count += 1
                self.__actual[alias] = label
                print(label)
                if count % 5 == 0:
                    print(f'Processing Up To {count} Videos')
            print(f'Processed {count} Videos Totally')


    def __getLabel(self, filename):
        framesOfOneVideo = []
        label = []
        with ImageExtractor.getImageExtracter(filename, shotFrameOnly='yes') as extractor:
            #return label
            for param in extractor:
                label.append(self.__imageFinder.find(param["frame"])[0])
                #print("Hello,World!")

            return  label
     #           print(f'{param["shotIndex"]}_{param["index"]}')


    def __loadExpected(self):
        with open(self.__config['groundTruth'], 'r') as file:
            self.__expected = dict((line.strip().split(' ') for line in file))


    def __compare(self):
        print('Compute Accuracy Start!')
        isOK, reason = self.__prepareList()
        if not isOK:
            return False, reason

        result = reduce(operator.add, self.__accuracyItems)
        print(result.accuracy)
        return True,'OK'


    def __prepareList(self):
        self.__accuracyItems = []
        if len(self.__expected) == 0:
            return False, 'expected is empty!'
        if set(self.__actual.keys()) != set(self.__expected.keys()):
            return False, 'keyNum is wrong!'
        for video, labels in self.__actual.items():
            self.__accuracyItems.append(AccuracyItem(labels.count(self.__expected[video]), len(labels)))

        return True,'OK'


from time import clock
if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    config = {
        #为避免修改DbBuild，仍使用imageRoot，但指示的是视频文件所在的文件夹
        'imageRoot': r'E:\ADVT',
        'targets': [('E:/videoShotFramesDbBuild/feature/video/videoPathLabels.txt', ['path', 'label']),
                    ('E:/videoShotFramesDbBuild/feature/video/videoPathAlias.txt', ['path', 'alias']),
                    ('E:/videoShotFramesDbBuild/feature/video/aliasLabel.txt', ['alias', 'label'])],
        'db': {
            'hashFeatureFilename': 'E:/videoShotFramesDbBuild/feature/1.bin',
            'imageFeatureFilename': 'E:/videoShotFramesDbBuild/feature/2.bin',
            'labelsFilename': 'E:/videoShotFramesDbBuild/feature/labels.txt',
        },

        'imagePathLabelsFilename': r'E:/videoShotFramesDbBuild/feature/video/videoPathLabels.txt',
        'groundTruth': 'E:/videoShotFramesDbBuild/feature/video/aliasLabel.txt',
        'imagePathAlias': 'E:/videoShotFramesDbBuild/feature/video/videoPathAlias.txt',

        # 'sample': [0, 10, 20]
        'extracter': {
            'num_classes': 11,
            'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
        }

    }


    start = clock()
    # # # step1
    # def _resolve2(path):
    #     _path = PurePath(path)
    #     #label = '_'.join([_path.parts[-2], _path.stem])
    #     label = _path.stem
    #     imgAlias = '_'.join([_path.parts[-2], label])
    #     return FilesMaker.ResolveResult(label, path, imgAlias)
    # FilesMaker.makeConfigFile(config, resolver=_resolve2, openFileAfterWrite=False)
    # finish=clock()
    # print (finish-start)
    # #
    # # # WARNING!:imageFinder对象被重复构建
    # # step2
    # # builder = DbBuild.DbBuilder(config)
    # # builder.build()
    # # finish=clock()
    # print (finish-start)
    #
    # # step3
    #
    # # PE = PerformanceEvaluater(config)
    # # PE.evaluate()
    # # finish=clock()
    # # print (f'Time Consumed {finish-start} s')
    #
    # new step3
    vpe = VideoPerformanceEvaluater(config)
    vpe.evaluate()
    finish=clock()
    print (f'Time Consumed {finish-start} s')

    # with open(config['groundTruth'], 'r') as file:
    #     # WARNING!!!imageFinder.find()目前只能返回1个结果
    #
    #
    #     for i, line in enumerate(file):
    #         try:
    #             videoPath, alias = line.strip().split(' ')
    #         except:
    #             print(i)
    #         # try:
    #         #     label = self.__getLabel(videoPath)
    #         # except Exception as err:
    #         #     print(err)
    #         #     # continue
    #         #     retur





