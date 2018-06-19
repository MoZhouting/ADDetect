# -- coding:utf-8 --

from xmlrpc.server import SimpleXMLRPCServer
import pickle
import pathlib

class ImageRPCServer(object):

    _META_FILENAME = 'meta.bin'


    def __init__(self, root):

        self.__root = pathlib.PurePath(root)
        with open(self.__root/ImageRPCServer._META_FILENAME, 'rb') as file:
            self.__info = pickle.load(file)

        self.__currentBlockIndex = -1
        

    def fetch(self, index, maxSize):
        try:
            if index >= len(self.__info):
                return 'Failed', ''

            totalSize = 0
            fetchItems = []
            for item in self.__info[index:]:
                totalSize += item[3] - item[2]
                if totalSize > maxSize:
                    break

                fetchItems.append(item)
                
            if not fetchItems:
                return 'Failed', ''

            data = []
            for item in fetchItems:
                imageName = item[0]
                blockIndex = item[1]
                if blockIndex != self.__currentBlockIndex:
                    self.__prepareCache(blockIndex)
                start = item[2]
                end = item[3]
                data.append((imageName, self.__cache[start:end]))
            return 'OK', data
        except Exception as err:
            return 'Failed', ''
        

    def __prepareCache(self, blockIndex):
        with open(self.__root/f'{blockIndex}.bin', 'rb') as file:
            self.__cache = bytearray(file.read())


if __name__ == '__main__':
    server = SimpleXMLRPCServer(('0.0.0.0', 8080))
    imageServer = ImageRPCServer('d:/rpc_test_db_yrs/')
    server.register_instance(imageServer)
    server.serve_forever()
