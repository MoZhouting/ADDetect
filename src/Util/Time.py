# -- coding:utf-8 --

import time
import datetime
import typing

def convertDateTimeFormat(datetime:str, srcFormat:str, destFormat:str):
	'''转换日期时间字符串格式

	参数
	datetime : 原字符串（待转换的日期时间）
	srcFormat : 原字符串的日期时间格式
	destFormat : 转换后字符串的日期时间格式
	'''

	try:
		_datetime = time.strptime(datetime, srcFormat)
	except ValueError:
		raise ValueError('Invalid datetime string {} with format {}'.format(datetime, srcFormat))
	
	return time.strftime(destFormat, _datetime) if destFormat != srcFormat else datetime


def strToTimeStampInt(datetime:str, format:str):
	'''日期时间字符串 -> 整数时间戳

	参数
	datetime : 原字符串（待转换的日期时间）
	format : 原字符串的日期时间格式
	'''

	try:
		_datetime = time.strptime(datetime, format)
	except ValueError:
		raise ValueError('Invalid datetime string {} with format {}'.format(datetime, format))

	return int(time.mktime(_datetime))


_CLOSE_TYPES = \
	{
		# 模式 : (begin端是闭的， end端是闭的)
		'[]' : (True, True), 
		'()' : (False, False), 
		'[)' : (True, False), 
		'(]' : (False, True)
	}


def dateSequence(begin:str, end:str, format='%Y-%m-%d', mode='[)'):
	'''生成日期序列

	参数
	begin: 起始日期
	end: 结束日期
	format: begin和end的日期格式
	mode: 序列头尾开闭模式, 可以是'[]', '()', '[)', '(]'四者之一
	'''

	try:
		beginDate = datetime.datetime.strptime(begin, format)
		endDate = datetime.datetime.strptime(end, format)
	except ValueError:
		raise ValueError('Invalid date string {} or {} with format {}'.format(begin, end, format))

	try:
		beginClosed, endClosed = _CLOSE_TYPES[mode]
	except KeyError:
		raise ValueError('Invalid value of closeType: {}, using "[]", "()", "(]", "[)" instead.'.format(mode))

	if not beginClosed:
		beginDate = beginDate + datetime.timedelta(days=1)
	if not endClosed:
		endDate = endDate + datetime.timedelta(days=-1)

	duration = (endDate - beginDate).days
	return [beginDate + datetime.timedelta(days=i) for i in range(duration + 1)] if duration >= 0 else []
	

def dateStrSequence(begin:str, end:str, srcFormat='%Y-%m-%d', destFormat=None, mode='[)'):
	'''生成日期序列

	参数
	begin: 起始日期
	end: 结束日期
	srcFormat: 输入(begin和end）日期的格式
	destFormat: 输出日期的格式, 如果为None, 则和srcFormat采用相同格式
	mode: 序列头尾开闭模式, 可以是'[]', '()', '[)', '(]'四者之一
	'''

	destFormat = srcFormat if destFormat is None else destFormat
	return [date.strftime(destFormat) for date in dateSequence(begin, end, format=srcFormat, mode=mode)]


def secondToHSM(seconds: int) -> str:
	if not isinstance(seconds, int):
		raise TypeError(f'Invalid type of arg "seconds", int expected, {type(seconds)} given')
	if seconds < 0 or seconds > 86399:
		raise ValueError(f'Invalid value of arg "seconds, [0, 86400) expected, {seconds} given')

	h, m = divmod(seconds, 60 * 60)
	m, s = divmod(m, 60)
	return f'{h:0{2}}:{m:0{2}}:{s:0{2}}'



if __name__ == '__main__':
	pass