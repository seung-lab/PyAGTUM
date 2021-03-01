

from ximea import xiapi

_CameraSNs=['CICAU1641091','CICAU1914024']

CameraSN = 'CICAU1641091'

# https://github.com/opencv/opencv/blob/master/samples/python/lk_track.py
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_lucas_kanade/py_lucas_kanade.html
# https://docs.opencv.org/master/dc/d6b/group__video__track.html#ga473e4b886d0bcc6b65831eb88ed93323

'''
camSN = CameraSN
CamFrameRate = 8


cam=xiapi.Camera()
cam.open_device_by_SN(camSN)
cam.set_imgdataformat('XI_RGB24')
#1028*1232*3*20*24
cam.set_limit_bandwidth(750)
cam.set_exposure(10000)
cam.set_decimation_horizontal(2)
cam.set_decimation_vertical(2)
cam.set_framerate(CamFrameRate)

cam.image=xiapi.Image()


cam.get_image(cam.image)
npimg=cam.image.get_image_data_numpy()
'''
import numpy as np
import cv2 as cv
from scipy.spatial import distance
import time

def draw_str(dst, target, s):
    # copy from cv_samples.common
    x, y = target
    cv.putText(dst, s, (x+1, y+1), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv.LINE_AA)
    cv.putText(dst, s, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv.LINE_AA)

lk_params = dict( winSize  = (10, 10),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 25,
                       qualityLevel = 0.8,
                       minDistance = 20,
                       blockSize = 20 )

class App:
    def __init__(self):
        self.track_len = 20 # max number of locations of point to remember
        self.detect_interval = 10
        self.tracks = []
        self.frame_idx = 0
        self.speed = 0
        self.time = []
        self.speed_list = []

        self.cam=xiapi.Camera()
        self.cam.open_device_by_SN('CICAU1641091')
        self.cam.set_imgdataformat('XI_RGB24')
        #1028*1232*3*20*24
        self.cam.set_limit_bandwidth(750)
        self.cam.set_exposure(10000)
        self.cam.set_decimation_horizontal(2)
        self.cam.set_decimation_vertical(2)
        self.cam.set_framerate(10)
        self.cam.image=xiapi.Image()
        self.cam.start_acquisition()

    def run(self):
        while True:
            self.cam.get_image(self.cam.image)
            frame=self.cam.image.get_image_data_numpy()
            t1 = time.time()
            frame=np.copy(frame[::2,::2,:])
            frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            vis = frame.copy()

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                   
                    new_tracks.append(tr)
                    cv.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                cv.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))
                
                
                if self.frame_idx % 20 == 0:
                    self.time.append(t1)
                    if len(self.time) > 1:
                        avg = np.mean([tr[-1][0] - tr[0][0] for tr in self.tracks if len(tr) == 20])
                        speed = np.around(avg * 0.0136/ (self.time[-1] - self.time[-2]), 3)
                        
                        self.speed_list.append(speed)
                        if len(self.speed_list) > 5:
                            self.speed = np.mean(self.speed_list)
                            self.speed_list = []
                # 0.0136mm per pixel
                draw_str(vis, (20, 40), 'speed: %3f' % self.speed)


            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv.circle(mask, (x, y), 5, 0, -1)
                p = cv.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])


            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv.imshow('lk_track', vis)

            if cv.waitKey(2) & 0xFF == ord('q'):
                self.cam.stop_acquisition()
                self.cam.close_device()
                break


def main():
    App().run()
    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()


'''
todo:
- let's measure speed first => then figure out what to do with it
1) use opencv to save an image to measure pixel size - x, y
2) implement camera stop

'''
