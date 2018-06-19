'''
'''
# coding = 'utf-8'

from  src import ImageDb
#from  src import FeatureExtract
from src.DenseNet import FeatureExtractor
import numpy as np

from functools import singledispatch, update_wrapper

def methdispatch(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

class ImageFinder(object):
    def __init__(self,config):
        self.__imageDb = ImageDb.ImageDb(config['db'])
        self.__featureExtracter = FeatureExtractor.FeatureExtractor(config)


    # def find(self, imagePath):
    #     '''查找图像的Label
    #
    #     参数
    #     imagePath: 图像文件路径
    #     '''
    #     hashFeature, imageFeature = self.__featureExtracter.extract(imagePath)
    #     # hashFeature = np.zeros(shape=[1, 128], dtype='float32')
    #     # imageFeature = np.zeros(shape=[1, 2048], dtype='float32')
    #     return self.__imageDb.find(hashFeature, imageFeature)

    @methdispatch
    def find(self, arg , output='l'):
        pass


    @find.register(str)
    def _(self, imagePath, output):


        hashFeature, imageFeature = self.__featureExtracter.extract(imagePath)
        return hashFeature
        #_find()

        # hashFeature = np.zeros(shape=[1, 128], dtype='float32')
        # imageFeature = np.zeros(shape=[1, 2048], dtype='float32')

        return self.__imageDb.find(hashFeature, imageFeature, output)


    @find.register(np.ndarray)
    def _(self, frame, output):

        # hashFeature, imageFeature = self.__featureExtracter.extract(frame)
        imageFeature = self.__featureExtracter.extract(frame)

        #_find()

        # hashFeature = np.zeros(shape=[1, 128], dtype='float32')
        # imageFeature = np.zeros(shape=[1, 2048], dtype='float32')
        return self.__imageDb.find(None, imageFeature, output)


if __name__ == '__main__':

    config = {
        'db': {
            'hashFeatureFilename': 'E:/videoShotFramesDbBuild/feature/1.bin',
            'imageFeatureFilename': 'E:/videoShotFramesDbBuild/feature/2.bin',
            'labelsFilename': 'E:/videoShotFramesDbBuild/feature/labels.txt',
        },
        'extracter': {
            'num_classes': 11,
            'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
        }
    }

    hashFeature = np.fromfile(config['db']['hashFeatureFilename'], dtype=np.float32)
    hashFeature.shape = 83432, 128

    imageFinder = ImageFinder(config)
    imagePath = r"E:\videoShotFrames\AHVM1130823100003000-3\2_78.jpg"
    imagePath2 = r"E:\videoShotFrames\AHVM1130723100003000-1\2_78.jpg"
    imagePath3 = r"D:\img1\2_78.jpg"
    h0 = imageFinder.find(imagePath, 'l')
    print(type(h0))
    h2 = imageFinder.find(imagePath2, 'l')
    h3 = imageFinder.find(imagePath3, 'l')
    import numpy as np
    # print(np.linalg.norm(h0 - h1))
    # print(np.linalg.norm(h2 - h1))
    # print(np.linalg.norm(h2 - h0))
    print(np.linalg.norm(h2 - hashFeature[71]))




