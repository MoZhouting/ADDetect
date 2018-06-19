'''
'''
# coding = 'utf-8'

import numpy as np
import os
import colorama

from src import FeatureExtract
from src.Util import Path


class DbBuilder(object):
    def __init__(self, config, featureExtracter=None):
        self.__config = config
        self.__count = 0
        self.__hashFeatures = None
        self.__imageFeatures = None
        self.__featureExtracter = featureExtracter if featureExtracter is not None else FeatureExtract.FeatureExtracter(config['extracter'])


    def __initFeatures(self, totalImages):
        self.__hashFeatures = np.zeros(shape=[totalImages, 128], dtype='float32')
        self.__imageFeatures = np.zeros(shape=[totalImages, 2048], dtype='float32')


    def __add(self, hashFeature, imageFeature):
        self.__hashFeatures[self.__count] = hashFeature
        self.__imageFeatures[self.__count] = imageFeature
        self.__count += 1


    def __save(self):

        self.__hashFeatures.tofile(self.__config['db']['hashFeatureFilename'])
        self.__imageFeatures.tofile(self.__config['db']['imageFeatureFilename'])
        np.savetxt(self.__config['db']['labelsFilename'],self.__labels,fmt='%s',newline='\n')

    def build(self):
        '''构建图像特征数据库
    '''
        self.__count = 0
        with open(self.__config['imagePathLabelsFilename'], 'r') as file:

            imagePaths = [imagePath for imagePath, label in (line.strip().split(' ') for line in file)]
            # for line in file:
            #     _line = line.strip().split(' ')
            #     try:
            #         imagePath, label = _line
            #     except Exception as err:
            #         print(_line)



        with open(self.__config['imagePathLabelsFilename'], 'r') as file:
            self.__labels = [label for imagePath, label in (line.strip().split(' ') for line in file)]
        #imagePaths = [i for i in Path.ilistFileEx(self.__config['imageRoot'])]

        self.__initFeatures(len(imagePaths))

        for index, imagePath in enumerate(imagePaths):
            hashFeature, imageFeature = self.__featureExtracter.extract(imagePath)
            self.__add(hashFeature, imageFeature)
            print(index)
        self.__save()



if __name__ == '__main__':
    # config = {
    #     #'imageRoot': 'D:/dev/unicorn/test/data/__NImage/image',
    #     'db': {
    #         'hashFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/1.bin',
    #         'imageFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/2.bin',
    #         'generatedLabelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/generatedLabels.txt',
    #     },
    #     'imagePathLabelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/imagePathLabels.txt',
    #     'extracte': {
    #         'num_classes': 11,
    #         'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
    #     }
    # }
    # builder = DbBuilder(config)
    # builder.build()
    config = {
        #'imageRoot': r'E:\videoShotFrames\AHVM1130723100003000-1',
        'db': {
            'hashFeatureFilename': 'E:/videoShotFramesDbBuild/feature/1__1.bin',
            'imageFeatureFilename': 'E:/videoShotFramesDbBuild/feature/2__1.bin',
            'labelsFilename': 'E:/videoShotFramesDbBuild/feature/x/labels.txt',
        },
        'imagePathLabelsFilename': 'E:/videoShotFramesDbBuild/feature/x/imagePathLabels.txt',
        'extracter': {
            'num_classes': 11,
            'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
        }
    }
    builder = DbBuilder(config)
    builder.build()

