# -- coding:utf-8 --

import xmlrpc.client
import collections

class ImageRPCProvider(object):

    def __init__(self, url, bufferSize=1024*1024):
        self.__proxy = xmlrpc.client.ServerProxy(url)
        self.__index = 0
        self.__eos = False
        self.__buffer = collections.deque()
        self.__maxSizePerFetch = bufferSize

    def __iter__(self):
        return self

    def __next__(self):
        if self.__eos:
            raise StopIteration

        if not self.__buffer:
            print('Buffer空了')

        if self.__buffer or self.__fetchImagesFromServer():
            item = self.__buffer[0]
            self.__buffer.popleft()
            return item

        self.__eos = True
        raise StopIteration


    def close(self):
        self.__proxy('close')()

    
    def __fetchImagesFromServer(self):
        print('开始请求远端服务器上的数据')
        msg, result = self.__proxy.fetch(self.__index, self.__maxSizePerFetch)
        if msg != 'OK':
            print(f'远端服务器数据取光了，当然也有可能是出错了')
            return False
        
        print(f'这次拿到了{len(result)}张图')
        self.__index += len(result)
        self.__buffer = collections.deque(result)
        return True



if __name__ == '__main__':
    provider = ImageRPCProvider('http://localhost:8080', bufferSize=1024*1024)
    for index, result in enumerate(provider):
        # print(f'输出{index}号图')
        with open(f'd:/rpc_test_receive_yrs/{index}.jpg', 'wb') as file:
            file.write(result[1].data)
    provider.close()

