'''
'''
#coding = 'utf-8'


# import cv2
#
# videoCapture = cv2.VideoCapture(r"C:\Users\Mozhouting\Desktop\testVideo\test3\素材\CV1M1130723300001800-1.ts")
# #fps = videoCapture.get(cv2.CV_CAP_PROP_FPS)
# fps = 25
# size = (576, 720)
# print(size)
# cv2.VideoWriter(r'C:\Users\Mozhouting\Desktop\testVideo\test3', cv2.VideoWriter_fourcc(*'XVID'), 25, size, False)

# print(fps, size, 'v->', v)

# success, frame = videoCapture.read()
#
# while success:
#     cv2.imshow('MyWindow', frame)
#     cv2.waitKey(1000 / int(fps))
#     v.write(frame)
#     success, frame = videoCapture.read()

import os
os.chdir(r"C:\Users\Mozhouting\Desktop\testVideo\test3\素材")
os.system('ffmpeg -i CV1M1130723300001800-1.ts -ab 128 -acodec libmp3lame -ac 1 -ar 22050 -r 29.97 -b 512 -y CV1M1130723300001800-1.mp4')
os.system('ffmpeg -ss 00:00:00 -t 00:00:05 -i CV1M1130723300001800-1.ts -vcodec copy -acodec copy split9.mp4')
os.system('ffmpeg -ss 00:00:00 -t 00:01:00 -i CV1M1130723300001800-2.ts -vcodec copy -acodec copy split1.mp4')
os.system('ffmpeg -f concat -i list.txt -c copy concat.mp4')