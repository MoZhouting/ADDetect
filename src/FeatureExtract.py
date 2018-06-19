'''
'''
# coding = 'utf-8'

import tensorflow as tf
import numpy as np
from src.inception import inception_module
import cv2
from src.imageproc import ImageExtractor

from functools import singledispatch, update_wrapper

def methdispatch(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

class FeatureExtracter():

    def __init__(self,config):
        self.__config=config
        self.x_image = None
        self.__image_buffer = None
        self.logits = None
        self.highfeatures = None
        self.ssss = None
        self.__output = None
        self.saver = None
        self.__sess = None
        self.__sess = None
        self.__buildNet()
        self.__loadModel()

    def __loadModel(self):
        self.saver.restore(self.__sess, self.__config['checkpoint_path'])

    def __buildInputImagePlaceholder(self):
        self.__image_buffer = tf.placeholder("string")
        image = tf.image.decode_jpeg(self.__image_buffer, channels=3)
        image = tf.image.convert_image_dtype(image, dtype=tf.float32)
        image = tf.image.central_crop(image, central_fraction=0.875)
        # Resize the image to the original height and width.
        image = tf.expand_dims(image, 0)
        image = tf.image.resize_bilinear(image, [299, 299], align_corners=False)
        image_tensor = tf.squeeze(image, [0])
        self.x_image = tf.reshape(image_tensor, [-1, 299, 299, 3])

    def __buildNet(self):
        #graph = tf.Graph().as_default()
        # Number of classes in the dataset label set plus 1.
        # Label 0 is reserved for an (unused) background class.
        num_classes = self.__config['num_classes']+1
        # setup an input image placeholder to feed image buffer
        self.__buildInputImagePlaceholder()
        # Build a Graph that computes the logits predictions from the inference model.
        # WARNING!!!
        self.logits,self.highfeatures, self.ssss = inception_module.inference(self.x_image, num_classes)
        # result is the output of the softmax unit
        self.__output = tf.nn.softmax(self.ssss, name="result")
        # Restore the moving average version of the learned variables for eval.
        variable_averages = tf.train.ExponentialMovingAverage(
            inception_module.MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_averages.variables_to_restore()
        self.saver = tf.train.Saver(variables_to_restore)
        self.__sess = tf.Session()

    @methdispatch
    def extract(self, arg):
        pass

    @extract.register(str)
    def _(self, image_path):
        '''提取图像特征

        参数
        image_path: 图像检索路径
        '''
        image_data = tf.gfile.FastGFile(image_path, 'rb').read()
        # print(image_data)

        output, hashFeature, imageFeature = self.__sess.run([self.__output, self.logits, self.highfeatures],
                                                  feed_dict={self.__image_buffer: image_data})
        hashFeature = np.squeeze(hashFeature)
        imageFeature = np.squeeze(imageFeature[0])
        imageFeature = np.array([imageFeature])
        hashFeature = np.array([hashFeature])
        for i in range(len(hashFeature[0])):
            if hashFeature[0][i] > 0.5:
                hashFeature[0][i] = 1
            else:
                hashFeature[0][i] = 0
        return hashFeature, imageFeature


    @extract.register(np.ndarray)
    def _(self, frame):
        '''提取视频帧特征
        参数
        frame: ImageExtractor提取的视频帧
        '''

        image_data = cv2.imencode('.jpg', frame)[1].tostring()
        #print(image_data)

        output, hashFeature, imageFeature = self.__sess.run([self.__output, self.logits, self.highfeatures],
                                                  feed_dict={self.__image_buffer: image_data})
        hashFeature = np.squeeze(hashFeature)
        imageFeature = np.squeeze(imageFeature[0])
        imageFeature = np.array([imageFeature])
        hashFeature = np.array([hashFeature])
        for i in range(len(hashFeature[0])):
            if hashFeature[0][i] > 0.5:
                hashFeature[0][i] = 1
            else:
                hashFeature[0][i] = 0

        return hashFeature, imageFeature

    def cmp(self, feature1, feature2):
        dist = np.linalg.norm(feature1 - feature2)
        return dist



if __name__ == '__main__':
    # config = {
    #
    #         'num_classes': 11,
    #         'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
    # }
    # fe = FeatureExtracter(config)
    #
    # frames = []
    # with ImageExtractor.getImageExtracter(r"E:\test\zzAHVM1130823100003000-13.ts",  shotFrameOnly='yes') as extractor:
    #
    #     for param in extractor:
    #         #print(param.keys())
    #         frames.append(param["frame"])
    #
    #         print(f'{param["shotIndex"]}_{param["index"]}')
    # #！！！frames[1]的1对应1_53.jpg中的1，frames[0]的1和0_0.jpg中的1一致
    # #行末的[1]代表imageFeature，[0]代表hashFeature
    # f1 = fe.extract(r"E:\test\zzAHVM1130823100003000-13\3_204.jpg")[1]
    # f2 = fe.extract(frames[3])[1]
    # print(fe.cmp(f1,f2))
    pass
