'''
'''
# coding = 'utf-8'
import sys
sys.path.append('d:/dev/unicorn/')
import tensorflow as tf
import numpy as np
from src.imageproc import ImageExtractor
import cv2
from src.Util import Path
from src.imageproc import ImageExtractor
import functools
import operator
from  src import ImageDb
from  src import FeatureExtract

# from functools import singledispatch, update_wrapper
#
# def methdispatch(func):
#     dispatcher = singledispatch(func)
#     def wrapper(*args, **kw):
#         return dispatcher.dispatch(args[1].__class__)(*args, **kw)
#     wrapper.register = dispatcher.register
#     update_wrapper(wrapper, func)
#     return wrapper
#
# class ImageFinder(object):
#     def __init__(self, config):
#         self.__imageDb = ImageDb.ImageDb(config['db'])
#         self.__featureExtracter = FeatureExtract.FeatureExtracter(config['extracter'])
#
#     @methdispatch
#     def find(self, arg):
#         pass
#
#
#     @find.register(str)
#     def _(self, imagePath):
#
#
#         hashFeature, imageFeature = self.__featureExtracter.extract(imagePath)
#         #_find()
#
#         # hashFeature = np.zeros(shape=[1, 128], dtype='float32')
#         # imageFeature = np.zeros(shape=[1, 2048], dtype='float32')
#         return self.__imageDb.find(hashFeature, imageFeature)
#
#
#     @find.register(np.ndarray)
#     def _(self, frame):
#
#         hashFeature, imageFeature = self.__featureExtracter.extract(frame)
#         #_find()
#
#         # hashFeature = np.zeros(shape=[1, 128], dtype='float32')
#         # imageFeature = np.zeros(shape=[1, 2048], dtype='float32')
#         return self.__imageDb.find(hashFeature, imageFeature)

if __name__ == '__main__':
    src = r'E:\video'

    # def __getVideonames(self,src):
        #输入视频文件夹，输出视频文件名


    # iF = ImageFinder()
    # iF.find('lalla')


    # for i in Path.ilistFilesEx(src):
    #
    #     print(i)
    #     for index, frame in ImageExtractor.ImageExtracter(i):
    #
    #
    #
    # image_raw = tf.gfile.FastGFile(r'C:\Users\Mozhouting\Desktop\0_0.jpg', 'rb').read()
    cvread = cv2.imread(r'C:\Users\Mozhouting\Desktop\0_0.jpg')
    #cv2.imencode(np.fromstring(cvread,np.uint8),cv2.IMREAD_COLOR)



    encode = cv2.imencode('.jpg', cvread)
    print(type(encode[1]))


    #img = tf.image.decode_jpeg(encode[1].tostring())


    # with tf.gfile.GFile(r'C:\Users\Mozhouting\Desktop\2.jpg','wb') as f:
    #     f.write(encode[1].tostring()) # ndarray


    #
    # index, frame = ImageExtractor.ImageExtracter(r'C:\Users\Mozhouting\Desktop\0.jpg')
    # print(frame)


