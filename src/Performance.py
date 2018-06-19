'''
'''
# coding = 'utf-8'
import sys
sys.path.append('d:/dev/unicorn/')
from src import ImageFinder
from src import FilesMaker
from src import DbBuild
from pathlib import PurePath


def fakeIlistFileEx(num,name,_):
    for i in range(num):
        yield name


class PerformanceEvaluater(object):
    '''能将图像和图像库比对，判断算法判定的和查询图像距离最小的图像是否正确，输出准确度

    输入是图像路径，由config['imagePathAlias']指定
    '''
    def __init__(self,config):
        self.__actual = None
        self.__expected = None
        self.__config = config


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
        imageFinder = ImageFinder.ImageFinder(self.__config)
        print('Retrieval Start！')
        self.__actual ={}
        with open(self.__config['imagePathAlias'], 'r') as file:
            #WARNING!!!imageFinder.find()目前只能返回1个结果
            count = 0
            for imagePath, alias in (line.strip().split(' ') for line in file):
                self.__actual[alias] = imageFinder.find(imagePath)[0]
                count += 1
                import time
                if count%100 == 0:
                    print(f'Processing Up To {count} Images', end='\r')
            print(f'Processed {count} Images Totally')

            #self.__actual = {alias:imageFinder.find(imagePath)[0] for imagePath,alias in (line.strip().split(' ') for line in file)}


    def __loadExpected(self):
        with open(self.__config['groundTruth'], 'r') as file:
            self.__expected = dict(line.strip().split(' ') for line in file)


    def __compare(self):
        print('Compute Accuracy Start!')
        if set(self.__actual.keys()) != set(self.__expected.keys()):
            return False,'keyNum is wrong!'
        # wrong = 0
        # for (k,v) in self.__actual.items():
        #     wrong += 1 if self.__expected[k] != v else 0
        # print(1-wrong/len(self.__expected))
        print('Compute Accuracy Completed ,is',len(set(self.__actual.items()) & set(self.__expected.items())) / len(self.__expected))

        return True,'OK'

from time import clock
if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # config = {
    #     #15张图
    #     'imageRoot': 'D:/dev/unicorn/test/data/__NImage/image',
    #     #10k张图
    #     #'imageRoot': 'D:/1000000/image/images0/images/0',
    #     #100k张图
    #     # 'imageRoot': 'D:/1000000/image/images0/images',
    #
    #     'targets': [('D:/dev/unicorn/test/data/__NImage/feature/imagePathLabels.txt', ['path', 'label']),
    #                 ('D:/dev/unicorn/test/data/__NImage/feature/imagePathAlias.txt', ['path', 'alias']),
    #                 ('D:/dev/unicorn/test/data/__NImage/feature/aliasLabel.txt', ['alias', 'label'])],
    #     'db': {
    #         'hashFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/1.bin',
    #         'imageFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/2.bin',
    #         'labelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/labels.txt',
    #     },
    #
    #     'imagePathLabelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/imagePathLabels.txt',
    #     'groundTruth': 'D:/dev/unicorn/test/data/__NImage/feature/aliasLabel.txt',
    #     'imagePathAlias': 'D:/dev/unicorn/test/data/__NImage/feature/imagePathAlias.txt',
    #     # 'sample': [0, 10, 20]
    #     'extracte': {
    #         'num_classes': 11,
    #         'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
    #     }
    #
    # }

    config = {
        #15张图
        'imageRoot': r'E:\videoShotFrames',
        #10k张图
        #'imageRoot': 'D:/1000000/image/images0/images/0',
        #100k张图
        # 'imageRoot': 'D:/1000000/image/images0/images',

        'targets': [('E:/videoShotFramesDbBuild/feature/imagePathLabels.txt', ['path', 'label']),
                    ('E:/videoShotFramesDbBuild/feature/imagePathAlias.txt', ['path', 'alias']),
                    ('E:/videoShotFramesDbBuild/feature/aliasLabel.txt', ['alias', 'label'])],
        'db': {
            'hashFeatureFilename': 'E:/videoShotFramesDbBuild/feature/1.bin',
            'imageFeatureFilename': 'E:/videoShotFramesDbBuild/feature/2.bin',
            'labelsFilename': 'E:/videoShotFramesDbBuild/feature/labels.txt',
        },

        'imagePathLabelsFilename': 'E:/videoShotFramesDbBuild/feature/imagePathLabels.txt',
        'groundTruth': 'E:/videoShotFramesDbBuild/feature/aliasLabel.txt',
        'imagePathAlias': 'E:/videoShotFramesDbBuild/feature/imagePathAlias.txt',
        # 'sample': [0, 10, 20]
        'extracte': {
            'num_classes': 11,
            'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
        }

    }
    # #linux
    # config = {
    #     #15张图
    #     'imageRoot': r'/home/imc/mzt/images/videoShotFrame',
    #     #10k张图
    #     #'imageRoot': 'D:/1000000/image/images0/images/0',
    #     #100k张图
    #     # 'imageRoot': 'D:/1000000/image/images0/images',
    #
    #     'targets': [('/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/imagePathLabels.txt', ['path', 'label']),
    #                 ('/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/imagePathAlias.txt', ['path', 'alias']),
    #                 ('/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/aliasLabel.txt', ['alias', 'label'])],
    #     'db': {
    #         'hashFeatureFilename': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/1.bin',
    #         'imageFeatureFilename': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/2.bin',
    #         'labelsFilename': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/labels.txt',
    #     },
    #
    #     'imagePathLabelsFilename': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/imagePathLabels.txt',
    #     'groundTruth': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/aliasLabel.txt',
    #     'imagePathAlias': '/home/imc/mzt/dev/unicorn/test/videoShotFrame/feature/imagePathAlias.txt',
    #     # 'sample': [0, 10, 20]
    #     'extracte': {
    #         'num_classes': 11,
    #         'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
    #     }
    #
    # }

    start = clock()
    # # step1
    def _resolve2(path):
        _path = PurePath(path)
        #label = '_'.join([_path.parts[-2], _path.stem])
        label = _path.parts[-2]
        imgAlias = '_'.join([label, _path.stem])
        return FilesMaker.ResolveResult(label, path, imgAlias)
    FilesMaker.makeConfigFile(config, resolver=_resolve2, openFileAfterWrite=False)
    finish=clock()
    print (finish-start)
    #
    # # WARNING!:imageFinder对象被重复构建
    # step2
    builder = DbBuild.DbBuilder(config)
    builder.build()
    finish=clock()
    print (finish-start)

    # step3

    # PE = PerformanceEvaluater(config)
    # PE.evaluate()
    # finish=clock()
    # print (f'Time Consumed {finish-start} s')