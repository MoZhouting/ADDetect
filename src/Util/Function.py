# coding = 'utf-8'

from functools import singledispatch, update_wrapper, partial

def nthDispatch(func, n):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kwargs):
        return dispatcher.dispatch(args[n].__class__)(*args, **kwargs)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

    
'''用于实例方法的 SingleDispatch
'''
# 出处: https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
instanceMethodDispatch = partial(nthDispatch, n=1)

''' 用法举例
class AAA(object):

    @instanceMethodDispatch
    def foo(self, n):
        pass

    @foo.register(int)
    def _(self, n):
        print('a')

    @foo.register(str)
    def _(self, n):
        print('b')

AAA().foo(1)        # 输出a
AAA().foo('1')      # 输出b
'''


if __name__ == '__main__':
    pass