# coding = 'utf-8'
import sys
sys.path.append('../../')

from colorama import init, Fore, Style
init(autoreset=True, strip=False)

import argparse
import src.imageproc.VideoShotFrameExtractor as vsfe


def extractShotFrame(src, dst):
    vsfe.VideoShotFrameExtrator().writeFrames(src, dst)
    print('处理完成')


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True)
    parser.add_argument('--dst', required=True)
    args = vars(parser.parse_args(sys.argv[1:]))
    extractShotFrame(args['src'], args['dst'])

