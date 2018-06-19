# coding = 'utf-8'
import sys
sys.path.append('../../')

from colorama import init, Fore, Style
init(autoreset=True, strip=False)

from src.imageproc import VideoConvert
from src.Util import Path
import pathlib
import argparse


def _showConfig(srcRootPath, dstRootPath, ffmpegPath, verbose, convertFile):
    if convertFile:
        print(f'源文件: {Fore.GREEN}{srcRootPath}')
        print(f'目标文件: {Fore.GREEN}{dstRootPath}')
        print(f'ffmpeg目录: {Fore.GREEN}{ffmpegPath}' if ffmpegPath else f'ffmpeg目录: {Fore.GREEN}未指定')
    else:
        print(f'源目录: {Fore.GREEN}{srcRootPath}')
        print(f'目标目录: {Fore.GREEN}{dstRootPath}')
        print(f'ffmpeg目录: {Fore.GREEN}{ffmpegPath}' if ffmpegPath else f'ffmpeg目录: {Fore.GREEN}未指定')
        print('进度信息: ' + f'{Fore.GREEN}开启' if verbose else f'{Fore.GREEN}关闭')


def _tsToMp4File(srcPath, dstPath, ffmpegPath):
    _showConfig(srcPath, dstPath, ffmpegPath, None, True)
    dstDir = dstPath.parent
    dstDir.mkdir(parents=True, exist_ok=True)
    VideoConvert.tsToMp4(str(srcPath), str(dstPath), ffmpegPath)
    print('处理完成')
    return


def _makeMp4Path(srcPath, srcRootPath, dstRootPath):
    dstPath = dstRootPath / pathlib.Path(srcPath).relative_to(srcRootPath)
    return dstPath.parent / f'{dstPath.stem}.mp4'


def _tsToMp4Dir(srcRootPath, dstRootPath, ffmpegPath, verbose):
    _showConfig(srcRootPath, dstRootPath, ffmpegPath, verbose, False)
    dstRootPath.mkdir(parents=True, exist_ok=True)
    allFilenames = [filename for filename in Path.ilistFilesEx(str(srcRootPath)) if pathlib.Path(filename).suffix.lower() == '.ts']
    totalFiles = len(allFilenames)
    print(f'文件总数: {Fore.GREEN}{totalFiles}')

    count = 0
    for srcPath in allFilenames:
        dstPath = _makeMp4Path(srcPath, srcRootPath, dstRootPath)
        dstPath.parent.mkdir(parents=True, exist_ok=True)
        VideoConvert.tsToMp4(str(srcPath), str(dstPath), ffmpegPath)
        count += 1
        if verbose and count % 10 == 0:
            print(f'已经处理了 {Fore.GREEN}{count}{Style.BRIGHT}{Fore.WHITE}/ {Fore.YELLOW}{totalFiles} {Style.RESET_ALL}个文件了')
    print('处理完成')


def tsToMp4(srcRoot, dstRoot, ffmpegPath=None, verbose=True):
    if ffmpegPath and ' ' in ffmpegPath:
        print('ffmpeg路径不能带空格！')
        return

    srcRootPath = pathlib.Path(srcRoot)
    dstRootPath = pathlib.Path(dstRoot)

    if srcRootPath.is_file():
        _tsToMp4File(srcRootPath, dstRootPath, ffmpegPath)
    else:
        _tsToMp4Dir(srcRootPath, dstRootPath, ffmpegPath, verbose)



if __name__ == '__main__':

    ###############################################################################################
    # 使用方法如下
    # 1. 转换一个ts文件，并输出到一个mp4文件
    # 用法: python TSToMp4.py --src 待转换视频文件名 --dst 转换后文件名
    # 举例: python TSToMp4.py --src d:/video_ts/1.ts --dst d:/video_mp4/1.mp4
    #
    # 2. 转换一个目录中的所有ts视频文件, 并输出到另一个目录
    # 用法: python TSToMp4.py --src 待转换视频文件根目录 --dst 转换后文件的根目录
    # 举例: python TSToMp4.py --src d:/video_ts --dst d:/video_mp4
    #
    # 3. 指定ffmpeg.exe所在目录（可选项）
    # 用法: python TSToMp4.py --src 待转换视频文件根目录 --dst 转换后文件的根目录 --ffmpeg ffmpeg所在目录
    # 举例: python TSToMp4.py --src d:/video_ts --dst d:/video_mp4 --ffmpeg d:/dev/unicorn/bin
    #
    # 4. 输出进度信息（可选项，默认是False，当src和dst为文件时无进度信息）
    # 用法: python TSToMp4.py --src 待转换视频文件根目录 --dst 转换后文件的根目录 --ffmpeg ffmpeg所在目录 -v
    # 举例: python TSToMp4.py --src d:/video_ts --dst d:/video_mp4 --ffmpeg d:/dev/unicorn/bin -v
    ###############################################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True)
    parser.add_argument('--dst', required=True)
    parser.add_argument('--ffmpeg')
    parser.add_argument('-v', action='store_true')
    args = vars(parser.parse_args(sys.argv[1:]))
    tsToMp4(args['src'], args['dst'], args['ffmpeg'], args['v'])