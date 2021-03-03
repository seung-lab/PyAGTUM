
# 210301 save an image from ximea camera
from ximea import xiapi
import cv2 as cv
import numpy as np

cam=xiapi.Camera()
cam.open_device_by_SN('CICAU1641091')
cam.set_imgdataformat('XI_RGB24')
        #1028*1232*3*20*24
cam.set_limit_bandwidth(750)
cam.set_exposure(10000)
cam.set_decimation_horizontal(2)
cam.set_decimation_vertical(2)
cam.set_framerate(8)
cam.image=xiapi.Image()
cam.start_acquisition()

cam.get_image(cam.image)
frame=cam.image.get_image_data_numpy()
frame=np.copy(frame[::2,::2,:])

cam.stop_acquisition()
cam.close_device()
# cv.imwrite("210301-cam_slot_shot.tif", frame)
# 0.0136mm per pixel


#--------------------------------------------------------------------

from ximea import xiapi
import cv2 as cv
import numpy as np

def draw_str(dst, target, s):
    # copy from cv_samples.common
    x, y = target
    cv.putText(dst, s, (x+1, y+1), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv.LINE_AA)
    cv.putText(dst, s, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv.LINE_AA)

lk_params = dict( winSize  = (10, 10),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 25,
                       qualityLevel = 0.6,
                       minDistance = 20,
                       blockSize = 20 )

from ximea import xiapi
import cv2 as cv
import numpy as np

cam=xiapi.Camera()
cam.open_device_by_SN('CICAU1641091')
cam.set_imgdataformat('XI_RGB24')
        #1028*1232*3*20*24
cam.set_limit_bandwidth(750)
cam.set_exposure(10000)
cam.set_decimation_horizontal(2)
cam.set_decimation_vertical(2)
cam.set_framerate(8)
cam.image=xiapi.Image()
cam.start_acquisition()

cam.get_image(cam.image)
frame=cam.image.get_image_data_numpy()
frame=np.copy(frame[::2,::2,:])
prev_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)


cam.get_image(cam.image)
frame=cam.image.get_image_data_numpy()
frame=np.copy(frame[::2,::2,:])
frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
vis = frame.copy()

tracks = []
mask = np.zeros_like(frame_gray)
mask[:] = 255
for x, y in [np.int32(tr[-1]) for tr in tracks]:
    cv.circle(mask, (x, y), 5, 0, -1)
p = cv.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
if p is not None:
    for x, y in np.float32(p).reshape(-1, 2):
        tracks.append([(x, y)])




img0, img1 = prev_gray, frame_gray
p0 = np.float32([tr[-1] for tr in tracks]).reshape(-1, 1, 2)
p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
d = abs(p0-p0r).reshape(-1, 2).max(-1)
good = d < 1
new_tracks = []
for tr, (x, y), good_flag in zip(tracks, p1.reshape(-1, 2), good):
    if not good_flag:
        continue
    tr.append((x, y))
    if len(tr) > 10:
        del tr[0]
    print(len(tr))
    new_tracks.append(tr)
    cv.circle(vis, (x, y), 2, (0, 255, 0), -1)
tracks = new_tracks


cv.polylines(vis, [np.int32(tr) for tr in tracks], False, (0, 255, 0))
draw_str(vis, (20, 20), 'track count: %d' % len(tracks))


            if self.frame_idx % 10 == 0 and len(self.tracks)>0:
                # try to remove abs
                speed = np.around(np.mean([abs(tr[0][0] - tr[-1][0]) for tr in self.tracks if len(tr) == 10]) * 0.0136, 4)
                # 0.0136mm per pixel
                draw_str(vis, (40, 40), 'speed: %f' % speed)


            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv.circle(mask, (x, y), 5, 0, -1)
                p = cv.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        tracks.append([(x, y)])


            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv.imshow('lk_track', vis)


















cam.stop_acquisition()
cam.close_device()