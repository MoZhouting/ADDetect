'''PQ系列
'''
# coding = 'utf-8'

import numpy as np
from sklearn.cluster import KMeans
import functools

class QDatabase(object):
    '''具体承载PQ功能的类
    '''
    def __init__(self, qPoints: np.ndarray, centroids: np.ndarray):
        '''通过已量化的数据和聚类中心构建QDatabase

        参数
        -----
        qPoints : 已量化的数据
        centroids : 聚类中心
        '''
        self.__qPoints = qPoints
        self.__centroids = centroids


    def find(self, points: np.ndarray, k: int) -> np.ndarray:
        '''查找K近邻

        参数
        -----
        points : 要查找的数据
        points的每一行表示1个数据点, 如：[1, 2, 3]表示1个3维点, [[1, 2, 3], [4, 5, 6]]表示2个3维点。
        特别的, [[1, 2, 3]]也可以表示1个3维点

        k : 要查找的近邻个数，即K近邻中的K

        返回值
        -----
        查找结果是一个二维矩阵, 其中每一行表示1个数据点的查找结果。
        每一行中有k个值，即k个近邻，按距离从小到大排序
        '''
        def _find(point: np.ndarray) -> np.ndarray:
            # 大致过程如下：
            # 构建查找表（查询向量到各段各个类中心的距离）
            # 查表得到查询向量到各个库向量的距离
            # 根据查得的距离值, 求距离前k小的向量索引
            lut = np.linalg.norm(point[:,None][:,None] - self.__centroids, axis=2)
            distances = np.array([np.sum(lut[np.arange(self.__centroids.shape[0]), qPoint]) for qPoint in self.__qPoints])
            candidates = np.argpartition(distances, k)[:k]
            return candidates[np.argsort(distances[candidates])]
        return np.apply_along_axis(_find, 1, points if points.ndim == 2 else points[None])


    @staticmethod
    def load(filename: str) -> 'QDatabase':
        '''从文件导入QDatabase

        参数
        -----
        filename : 要导入的文件名（必须是npy格式的）

        返回值
        -----
        ``QDatabase``对象
        '''
        with open(filename, 'rb') as f:
            return QDatabase(np.load(f), np.load(f))


    @staticmethod
    def create(points: np.ndarray, numOfSegments: int, numOfClasses: int) -> 'QDatabase':
        '''通过数据创建QDatabase

        参数
        -----
        points : 用于构建QDatabase的数据

        numOfSegments : 分段数

        numOfClasses : 每段的聚类中心数

        返回值
        -----
        ``QDatabase``对象

        '''
        # 大致过程如下：
        # 初始化KMeans对象（其数量等于分段数）
        # 对给定的数据分段执行聚类, 求出各段的各个类中心，
        # 并用这些中心来量化给定的数据，形成库向量
        # 最后保存所有的类中心
        quantizers = [KMeans(numOfClasses) for i in range(numOfSegments)]
        qPoints = np.vstack([quantizer.fit(subPoints).predict(subPoints)
                            for quantizer, subPoints in zip(quantizers, np.hsplit(points, numOfSegments))]).T
        centroids = np.vstack([quantizer.cluster_centers_[None] for quantizer in quantizers])
        return QDatabase(qPoints, centroids)
        

    def save(self, filename: str):
        '''将QDatabase保存到文件
        参数
        -----
        filename : 要保存的文件名（npy格式）

        返回值
        -----
        无
        '''
        with open(filename, 'wb') as f:
            np.save(f, self.__qPoints)
            np.save(f, self.__centroids)

_IMGE_FEATURE_DIM = 2048


if __name__ == '__main__':

    # ##################################
    # # 使用范例
    # ##################################
    #
    # # 创建4个3维点
    # data = np.array([[1.0, 1.0, 2.0],
    #                  [1.1, 3.1, 2.0],
    #                  [4.1, 0.9, 4.0],
    #                  [3.9, 2.9, 4.0]])
    #
    # # 构建QDatabase，指定分段数=3，类中心数=2
    # qdb = QDatabase.create(data, 3, 2)
    #
    # # 查找1个点的最近邻
    # # 输出[[0]]
    # print(qdb.find(np.array([1.1, 1.2, 2.0]), 1))
    #
    # # 查找1个点的最近邻（另一种方式），注意和上一种方式的区别
    # # 输出[[0]]
    # print(qdb.find(np.array([[1.1, 1.2, 2.0]]), 1))
    #
    # # 查找2个点的最近邻
    # # 输出[[0] [0]]
    # print(qdb.find(np.array([[1.1, 1.2, 2.0],
    #                          [1.1, 1.2, 2.0]]),
    #                 1))
    #
    # # 保存到文件
    # qdb.save('d:/1.npy')
    #
    # # 从文件导出
    # qdb2 = QDatabase.load('d:/1.npy')
    #
    # # 查找2个点的2-近邻
    # # 输出[[3, 2] [3, 2]]
    # print(qdb2.find(np.array([[4.2, 3.1, 4.0],
    #                           [4.2, 3.1, 4.0]]),
    #                 2))



########
    from time import clock

    start = clock()
    data = np.fromfile(r"E:\videoShotFramesDbBuild\feature\2.bin", dtype=np.float32)
    data.shape = data.size // _IMGE_FEATURE_DIM , _IMGE_FEATURE_DIM
    qdb = QDatabase.create(data, 128 , 16)
    # print(qdb.find(np.array(data),1))
    # qdb.save('d:/1.npy')
    finish=clock()
    print (finish-start)



    

    





                


