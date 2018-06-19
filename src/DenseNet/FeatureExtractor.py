# coding = 'utf-8'

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorpack.tfutils.sessinit import SaverRestoreRelaxed
from tensorpack.predict.config import PredictConfig
from tensorpack.predict.base import OfflinePredictor
import cv2
import numpy as np
from src.DenseNet.Model import Model
from src.Util import Path


class FeatureExtractor(object):
    '''基于DenseNet的特征提取器
    '''
    def __init__(self, config):
        pconfig = PredictConfig(
            model=Model(config['depth']),
            input_names=['input'],
            session_init=SaverRestoreRelaxed(config['modelPath']),
            output_names=['feature/output']
        )
        self.__predictor = OfflinePredictor(pconfig)
        self.__imageSize = config['imageSize']


    def extract(self, image):
        #image = cv2.imread(image).astype('float32')
        image = cv2.resize(image, dsize=(self.__imageSize, self.__imageSize))[None]
        return self.__predictor(image)[0]



if  __name__ == '__main__':
    # config = {
    #     'depth': 40,
    #     'modelPath': r"D:\Dev\Unicorn\model\model-37800.data-00000-of-00001",
    #     #'modelPath': r"D:\dev\Unicorn\model\model-37800.data-00000-of-00001",
    #
    #     'imageSize': 64
    # }
    # fe = FeatureExtractor(config)
    # feature = fe.extract('d:/1.jpg')
    # print('hello kitty')
    config = {
        'depth': 40,
        'modelPath': r"D:\dev\Unicorn\model\model2\model-249480.data-00000-of-00001",
        'imageSize': 64
    }
    fe = FeatureExtractor(config)
    # feature = fe.extract('d:/1.jpg')
    totalImages = 83432
    imageFeatures = np.zeros(shape=[totalImages, 2048], dtype='float32')
    count = 0
    for filename in Path.ilistFilesEx('E://videoShotFrames'):
        try:
            imageFeatures[count] = fe.extract(filename)
            count += 1
            if count % 1000 == 0:
                print(count)

        except Exception as err:
            print(f'{count}:, {err}')
    print(f'total {count} images.')
    imageFeatures.tofile('d:/83432_feature_2.bin')


