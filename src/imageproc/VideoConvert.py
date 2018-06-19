# coding = 'utf-8'

import os
import pathlib
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


def tsToMp4(src, dst, ffmpegPath=None):
    _src = _addDoubleQuoteToStringContainsSpace(src)
    _dst = _addDoubleQuoteToStringContainsSpace(dst)
    if ffmpegPath:
        _fullFfmpegPath = pathlib.Path(_removeDoubleQuoteFromString(ffmpegPath)) / 'ffmpeg.exe'
        _ffmpegPath = _addDoubleQuoteToStringContainsSpace(str(_fullFfmpegPath))
    else:
        _ffmpegPath = 'ffmpeg.exe'

    cmd = f'{_ffmpegPath} -i {_src} -c:v libx264 -c:a copy {_dst} -loglevel error'
    os.system(cmd)

if __name__ == '__main__':
    pass