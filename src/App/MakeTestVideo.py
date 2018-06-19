import sys
sys.path.append('../../')

from colorama import init, Fore, Style
init(autoreset=True, strip=False)
from typing import List, Tuple
import pathlib
import shutil
import time
import os
import cv2
from src.Util import Time
from src.Util.Path import ilistFilesEx
import random
import itertools
from enum import Enum

def _pairwise(iterable):
    # [1, 2, 3, 4, 5] -> [(1, 2), (2, 3), (3, 4), (4, 5)]
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _getVideoDuration(videoRoot: str) -> List[Tuple[str, int]]:
    # 获取视频时长
    return [(path, int(cv2.VideoCapture(path).get(cv2.CAP_PROP_FRAME_COUNT)))
                for path in ilistFilesEx(videoRoot)]


def _prepareTempDir():
    # 准备好临时目录
    tempDir = pathlib.Path('./temp')
    if tempDir.is_dir():
        shutil.rmtree(tempDir)
        time.sleep(1)
        print(f'[准备操作]  临时目录 {tempDir.absolute()} 已经存在, 执行删除')
    tempDir.mkdir()
    print(f'[准备操作]  创建临时目录 {Fore.GREEN}{tempDir.absolute()}')


def _makeComponentTypes(adParts: int, startsWithAd: bool, endsWithAd: bool):
    # adParts: 广告段数
    # startsWithAd: 以广告开始
    # endsWithAd: 以广告结束
    if adParts == 0:
        return [False]

    # 素材类型列表True表示是广告段， False表示是非广告段
    componentTypes = [startsWithAd]
    if startsWithAd:
        adParts -= 1
    if endsWithAd:
        pair = [False, True]
    else:
        componentTypes.append(False)
        pair = [True, False]

    componentTypes.extend(pair * adParts)
    return componentTypes


def _makeAdComponent(adVideoDuration: List[Tuple[str, int]], maxAdSegmentSize: int):
    numOfAd = random.randint(1, min(len(adVideoDuration), maxAdSegmentSize))
    _components = [random.choice(adVideoDuration) for i in range(numOfAd)]
    component = [(_component[0], None) for _component in _components]
    duration = sum([_component[1] for _component in _components])
    return component, duration


def _makeNadComponent(nadVideoDuration, nadSegmentDuration: Tuple[int, int]):
    nadPath, nadDuration = random.choice(nadVideoDuration)
    duration = random.randrange(*nadSegmentDuration)
    start = random.randint(0, nadDuration // 25 - duration)
    return [(nadPath, (Time.secondToHSM(start), Time.secondToHSM(duration)))], duration * 25


def _makeComponents(adVideoDuration: List[Tuple[str, int]],
                    nadVideoDuration: List[Tuple[str, int]],
                    componentTypes: List[bool],
                    maxAdSegmentSize: int,
                    nadSegmentDuration: Tuple[int, int]):
    # adPaths: 所有广告视频路径
    # nadPaths: 所有非广告视频路径
    # nadVideoDuration: 所有非广告视频时长
    # componentTypes: component类型
    # adSegmentSize: 广告段的广告数量上限
    # nadSegmentDuration: 非广告段的时长上下限, 以秒为单位, 左闭右开
    components = []
    durations = [0]
    for componentType in componentTypes:
        if componentType:
            component, duration = _makeAdComponent(adVideoDuration, maxAdSegmentSize)
        else:
            component, duration = _makeNadComponent(nadVideoDuration, nadSegmentDuration)
        components.extend(component)
        durations.append(duration)

    groundTruth = list(_pairwise(list(itertools.accumulate(durations))))[::2]
    return components, groundTruth


def _makeVideoComponents(adVideoDir: str, nadVideoDir: str, config: dict) -> Tuple[List[Tuple[str, Tuple[str, str]]],
                                                                                   List[Tuple[int, int]]]:
    # 随机获取视频拼接列表
    # 拼接列表的组成形式:
    # [(视频名, (起始时间，持续秒数))]
    # 元组为None表示整个视频都要, 仅用于广告视频

    # 获取视频时长
    adVideoDuration = _getVideoDuration(adVideoDir)
    nadVideoDuration = _getVideoDuration(nadVideoDir)

    # 素材类型列表，其中True表示是广告段， False表示是非广告段
    componentTypes = _makeComponentTypes(config['adParts'], config['startsWithAd'], config['endsWithAd'])

    # 根据素材类型列表，构造素材视频清单并得到广告检测的GroundTruth
    components, groundTruth = _makeComponents(adVideoDuration,
                                              nadVideoDuration,
                                              componentTypes,
                                              config['maxAdSegmentSize'],
                                              config['nadSegmentDuration'])

    # components长这种样子
    # components = [('e:/make_test_video_exp/material/material_0_3314_0_intra_0.mp4', ('00:00:00', '00:00:10')),
    #               ('e:/AHVM/AHVM1130723100003000-1.mp4', None),
    #               ('e:/make_test_video_exp/material/material_0_3314_0_intra_0.mp4', ('00:01:00', '00:00:15'))]

    # groundTruth长这样子
    # groundTruth = [(0, 100), (1024, 2048)]

    return components, groundTruth


def _addDoubleQuoteToStringContainsSpace(text):
    if ' ' in text\
        and not text.startswith('"'):
            return f'"{text}"'
    else:
        return text


def _removeDoubleQuoteFromString(text):
    if text.startswith('"'):
        return text[1:-1]
    else:
        return text


def _makeVideo(components: List[Tuple[str, Tuple[str, str]]], resultPath: pathlib.Path, ffmpegDir: str):
    # 准备临时目录
    _prepareTempDir()
    tempDir = pathlib.Path('./temp')
    fullFfmpegPath = pathlib.Path(ffmpegDir) / 'ffmpeg.exe'

    allFiles = []
    # 制作素材（非广告）视频和视频拼接列表
    for index, component in enumerate(components):
        materialVideoPath = component[0]
        # 如果是非广告视频则执行裁剪, 并将裁剪结果输出到临时目录
        if component[1] is not None:
            start, duration = component[1]
            clipPath = tempDir / f'material_{index}.mp4'
            cmd = (f'{fullFfmpegPath}'
                   f' -ss {start} -t {duration} -i {pathlib.Path(materialVideoPath).absolute()}'
                   f' -q:v 0 -q:a 0 {clipPath.absolute()}'
                   f' -loglevel error')
            os.system(cmd)
            allFiles.append(clipPath.name)
            print(f'[裁剪素材]  File: {materialVideoPath} Start: {start} Duration: {duration}'
                  f' --> {Fore.GREEN}{clipPath.absolute()}')
        else:
            targetPath = tempDir / f'material_{index}.mp4'
            if not targetPath.exists():
                shutil.copyfile(materialVideoPath, targetPath)
                allFiles.append(targetPath.name)
                print(f'[复制广告]  {materialVideoPath} --> {Fore.GREEN}{targetPath.absolute()}')

    # 输出视频拼接列表文件
    _concatListPath = tempDir / 'list.txt'
    with open(_concatListPath, 'w') as f:
        for filename in allFiles:
            f.write(f'file ./{filename}' + '\n')
    concatListPath = str(_concatListPath.absolute()).replace('\\', '/')

    # 构造命令行
    cmd = f'{fullFfmpegPath} -f concat -safe 0 -i {concatListPath} -c copy {resultPath.absolute()} -loglevel error'
    # print(cmd)
    os.system(cmd)
    print(f'[制作视频]  测试视频 {Fore.GREEN}{resultPath.absolute()}{Style.RESET_ALL} 制作完成')


def _DetectAd(testVideoPath) -> List[Tuple[int, int]]:
    return []


def _calcOverlapRate(seg0, seg1):
    # 求时间段seg0时间段seg1的重叠率
    start = max(seg0[0], seg1[0])
    end = min(seg0[1], seg1[1])
    return max(0.0, (end - start) / (seg1[1] - seg1[0]))


def _evaluate(actual, expected):
    if not expected:
        return (1.0, 0.0) if not actual else (0.0, 0.0)

    if not actual:
        return 0.0, 0.0

    # 匹配的时间段数
    matches = 0
    # 边界误差
    borderError = 0
    for seg0 in actual:
        for seg1 in expected:
            # 重叠率大于0.8的两段才认为是有效匹配
            # 这里有点效率问题, 已经被匹配上的不应该再参与匹配
            # 不过道理上，出错是不会的
            if _calcOverlapRate(seg0, seg1) > 0.8:
                matches += 1
                borderError += abs(seg0[0] - seg1[0]) + abs(seg0[1] - seg1[1])
                break

    # 准确率 = 总匹配数 / 总时间段数
    precision = matches / len(actual)
    return precision, borderError


def _doTest(testVideoPath, groundTruth, config) -> bool:
    # testVideoPath: 测试视频路径
    # maxBorderError: 最大边界误差
    result = _DetectAd(testVideoPath)
    # precision, borderError = _evaluate(result, groundTruth)
    precision, borderError = 1.0, 0.0
    return precision >= config['minPrecision'] and borderError <= config['maxBorderDist']


def makeTestVideo(config):
    ffmpegDir = _removeDoubleQuoteFromString(config['path']['ffmpeg'])
    if ' ' in ffmpegDir:
        raise ValueError('ffmpeg目录中不能带空格')

    adVideoDir = _addDoubleQuoteToStringContainsSpace(config['path']['adRoot'])
    nadVideoDir = _addDoubleQuoteToStringContainsSpace(config['path']['nadRoot'])
    targetDir = _addDoubleQuoteToStringContainsSpace(config['path']['targetRoot'])

    # 制作成功的视频数量
    resultVideoCount = 0
    # 总尝试次数
    totalTryCount = 0
    for i in range(config['num']):
        tryCount = 0
        print(f'[制作视频]  开始制作第 {Fore.GREEN}{i + 1}{Style.RESET_ALL}/ {config["num"]} 个视频')
        # 制作一个视频
        while tryCount < config['maxTry']:
            print(f'[制作视频]  开始第 {Fore.GREEN}{tryCount + 1}{Style.RESET_ALL}/ 100 次尝试')
            # 获取随机视频制作列表和广告检测GroundTruth
            components, groundTruth = _makeVideoComponents(adVideoDir, nadVideoDir, config['component'])

            # 制作视频
            videoPath = pathlib.Path(targetDir) / f'test_video_{i}.mp4'
            _makeVideo(components, videoPath, ffmpegDir)

            # 计算准确率
            tryCount += 1
            if _doTest(str(videoPath), groundTruth, config['performance']):
                print(f'[测试视频]  {Fore.GREEN}{videoPath} {Style.RESET_ALL}通过测试， 保留')
                break
            else:
                print(f'[测试视频]  {Fore.GREEN}{videoPath} {Style.RESET_ALL}未通过测试， 删除')
                time.sleep(1)
                os.remove(str(videoPath))

        totalTryCount += tryCount
        if tryCount < 100:
            print(f'[制作视频]  制作第 {Fore.GREEN}{i + 1}{Style.RESET_ALL}/ {config["num"]} 个视频成功')
            resultVideoCount += 1
        else:
            print(f'[制作视频]  制作第 {Fore.GREEN}{i + 1}{Style.RESET_ALL}/ {config["num"]} 个视频失败，达到最大尝试次数')


    # 删除临时目录
    # tempDir = pathlib.Path('./temp')
    # shutil.rmtree(tempDir)
    # time.sleep(1)
    # print(f'[清理操作]  删除临时目录 {Fore.GREEN}{tempDir.absolute()}')
    print(f'[处理完成]  共制作了 {Fore.GREEN}{resultVideoCount} {Style.RESET_ALL}/ {config["num"]} 个测试视频， '
          f'总尝试次数 {Fore.GREEN}{totalTryCount}')



if __name__ == '__main__':


    config = {
        'path':{
            'adRoot': 'e:/make_test_video_exp/ad',          # 广告视频目录
            'nadRoot': 'e:/make_test_video_exp/nad',        # 非广告视频目录
            'targetRoot': 'e:/make_test_video_exp/result',  # 输出视频目录
            'ffmpeg': 'd:/dev/unicorn/bin'                  # ffmpeg所在目录
        },
        'num': 1,                               # 要制作的测试视频数量
        'maxTry': 100,                          # 制作视频的最多尝试次数
        'component': {
            'adParts': 2,                       # 广告段数
            'startsWithAd': True,               # 以广告开始
            'endsWithAd': False,                # 以广告结束
            'maxAdSegmentSize': 3,              # 一个广告段最多包含的广告数量
            'nadSegmentDuration': (10, 61)      # 非广告段的时长范围，左闭右开
        },
        'performance': {
            'minPrecision': 0.9,            # 准确率阈值
            'maxBorderDist': 15             # 最大边界误差
        }
    }

    makeTestVideo(config)

