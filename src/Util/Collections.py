# -- coding:utf-8 --


def tryAdd(setObject, element):
    '''尝试向set添加元素

	参数
	setObject: 要添加元素的目标set
    element: 元素

    返回值
    当set中无该元素时，返回True(并将该元素添加到set)，反之返回False
	'''
    if element in setObject:
        return False

    setObject.add(element)
    return True


if __name__ == '__main__':
    pass