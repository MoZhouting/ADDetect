# -- coding:utf-8 --

import os
import platform
import pathlib
import shutil
from src.Util import Collections

__IS_WINDOWS = platform.system() == 'Windows'

if __IS_WINDOWS:
    # pip install pypiwin32
    import pythoncom
    from win32com.shell import shell


def _getShorcutRealPath(path):
    if not __IS_WINDOWS:
        return path

    try:
        pythoncom.CoInitialize()
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink)
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(path)
        realPath = shortcut.GetPath(shell.SLGP_SHORTPATH)[0]
        return realPath
    except Exception as err:
        return path


def ilistFilesEx(path, recursive=True):
    '''获取目录下所有文件列表(generator)

    参数
    path: 目录名或指向目录的快捷方式
    recursive: 是否递归(必须为True, 当前不支持非递归模式)
    '''
    if not recursive:
        raise NotImplementedError('Listing files in non-recursive mode is not supported now :(')

    if os.path.isdir(path):
        yield from _ilistFilesEx(path, {pathlib.PurePath(path)})
        return

    if pathlib.PurePath(path).suffix.lower() != '.lnk':
        return

    realName = _getShorcutRealPath(path)
    if os.path.isdir(realName):
        yield from(_ilistFilesEx(realName, {pathlib.PurePath(realName)}))


def _ilistFilesEx(path, visitedPaths):
    for root, dirs, files in os.walk(path):
        for file in files:
            # 不是.lnk文件，返回文件名
            if os.path.splitext(file)[1].lower() != '.lnk':
                _path = pathlib.PurePath(os.path.join(root, file))
                if Collections.tryAdd(visitedPaths, _path):
                    yield str(_path)
                continue

            # 是.lnk文件，但不是快捷方式，返回文件名
            filename = os.path.join(root, file)
            realName = _getShorcutRealPath(filename)
            if not realName:
                _path = pathlib.PurePath(filename)
                if Collections.tryAdd(visitedPaths, _path):
                    yield str(_path)
                continue

            # 快捷方式指向文件，返回真实文件名
            if os.path.isfile(realName):
                _path = pathlib.PurePath(realName)
                if Collections.tryAdd(visitedPaths, _path):
                    yield str(_path)
                continue

            # 快捷方式指向目录，则遍历该目录
            _path = pathlib.PurePath(realName)
            if Collections.tryAdd(visitedPaths, _path):
                yield from _ilistFilesEx(_path, visitedPaths)

        for _dir in dirs:
            _path = pathlib.PurePath(_dir)
            if Collections.tryAdd(visitedPaths, _path):
                yield from _ilistFilesEx(_path, visitedPaths)


def ilistFiles(dir):
    '''获取目录下的所有文件列表(generator)

        参数
        dir : 目录名
        '''
    _, _, files = next(os.walk(dir))
    return (os.path.join(dir, file) for file in files)


def listFiles(dir):
    '''获取目录下的所有文件列表(list)

        参数
        dir : 目录名
        '''
    _, _, files = next(os.walk(dir))
    return [os.path.join(dir, file) for file in files]


def clearDir(dirName):
    '''删除目录下所有文件及子目录, 注意可能有权限问题

    参数
    dirName: 目录名
    '''
    if not os.path.isdir(dirName):
        raise NotADirectoryError(dirName)

    shutil.rmtree(dirName)
    os.mkdir(dirName)


if __name__ == '__main__':
    pass
