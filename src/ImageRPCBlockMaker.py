# -- coding:utf-8 --


import pickle
from Util import Path
import pathlib
import os

class BlockMaker(object):

    def __init__(self, imageRoot, dbRoot, maxBlockSize=64*1024):
        self.__imageRoot = imageRoot
        self.__dbRoot = pathlib.PurePath(dbRoot)
        self.__maxBlockSize = maxBlockSize
        self.__currentBlockId = 0
        self.__currentBlockSize = 0
        self.__meta = []
        self.__blockFile = open(self.__dbRoot/f'{self.__currentBlockId}.bin', 'wb')

    def make(self):
        self.__currentBlockSize = 0
        
        for index, path in enumerate(Path.ilistFilesEx(self.__imageRoot)):
            fileSize = os.path.getsize(path)
            if fileSize > self.__maxBlockSize:
                raise ValueError(f'too large file {path} with size {fileSize}Bytes, maxBlockSize={self.__maxBlockSize}')
            self.__write(path, fileSize)


        self.__finish()

    def __write(self, path, fileSize):
        
        if self.__currentBlockSize + fileSize > self.__maxBlockSize:
            self.__blockFile.flush()
            self.__blockFile.close()
            self.__currentBlockId += 1
            self.__currentBlockSize = 0
            self.__blockFile = open(self.__dbRoot/f'{self.__currentBlockId}.bin', 'wb')

        self.__write2(path, fileSize)

    def __write2(self, path, fileSize):
        name = pathlib.PurePath(path).relative_to(self.__imageRoot)
        with open(path, 'rb') as file:
            self.__blockFile.write(file.read())
        self.__meta.append((str(name), self.__currentBlockId, self.__currentBlockSize, self.__currentBlockSize + fileSize))
        self.__currentBlockSize += fileSize


    def __finish(self):
        self.__blockFile.flush()
        self.__blockFile.close()
        with open(self.__dbRoot/'meta.bin', 'wb') as file:
            pickle.dump(self.__meta, file)

if __name__ == '__main__':
    import time
    start = time.time()
    bm = BlockMaker('g:/fdu/100m', 'e:/rpc_test_db_100m', maxBlockSize=1024*1024*1024)
    bm.make()
    print(f'{time.time()-start}')
    