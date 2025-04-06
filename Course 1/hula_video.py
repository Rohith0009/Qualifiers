import threading
import time
import numpy as np
import signal
import cv2
import sys
import pyhula
import ctypes
from collections import deque
import os

class hula_video:
    def __init__(self,hula_api,hula_ip="0.0.0.0",display=False):
        '''
        Initialize the hula_video with the pyhula object.
        display parameter: Tell the hula_video to display video stream or not. 
        Example:
            video = hula_video(hula_api=uapi,display=False)

        '''
        self.uapi = hula_api
        self.hula_ip = hula_ip
        self.video_port = 9000 + (self.uapi.get_plane_id() * 2)
        self.live = display
        self.display = display
        self.video_queue = deque()

        self.videothread = threading.Thread(target=self._receive_video_data)
        self.lib = ctypes.cdll.LoadLibrary('ffmpeg-lib.dll')
        self.lib.init_video.argtypes = [ctypes.c_wchar_p,ctypes.c_int]
        self.lib.init_video.restype = ctypes.c_int
        self.lib.get_rgb_datas_length.argtypes = None
        self.lib.get_rgb_datas_length.restype = ctypes.c_int

        self.lib.get_width.argtypes = None
        self.lib.get_width.restype = ctypes.c_int
        self.lib.get_height.argtypes = None
        self.lib.get_height.restype = ctypes.c_int

        self.lib.get_rgb_datas.argtypes = [ctypes.POINTER(ctypes.c_uint8),ctypes.c_int]
        self.lib.get_rgb_datas.restype = None
        self.lib.get_rgb_ptr.argtypes = None
        self.lib.get_rgb_ptr.restype = ctypes.POINTER(ctypes.c_uint8)
        self.lib.should_update_frame.argtypes = None
        self.lib.should_update_frame.restype = ctypes.c_bool
        self.lib.has_updated_frame.argtypes = None
        self.lib.has_updated_frame.restype = None
        self.stopApp = False
        self.record = False
        self.photo_filename = "photo"
        self.photo_index= 0
        self.detect = False
        self.confidence_level = 0.5
        self.detected_object = []
        self.detected_object_score = []
        self.detecting = False
        self.buffer_size = 25
        self.savepath = os.path.join(os.getcwd(),'photo')
        if not os.path.exists(self.savepath):
            print("creating save directory")
            os.makedirs(self.savepath)

    def __del__(self):
        self.close()

    def close(self):
        '''
        Close the video stream. 
        '''
        self.stopApp = True
    
    def readframe(self):
        if self.video_queue.empty == False:
            return self.video_queue.pop()
                        
    def video_mode_on(self):
        '''
        Call this function to turn on the video stream from the drone. This must be called after initializing a hula_video object.
        '''
        self.stopApp = False
        self.uapi.Plane_cmd_swith_rtp(0)
        print('Starting video stream. Please wait.')
        time.sleep(1)
        ret = self.lib.init_video(self.hula_ip,self.video_port)
        while self.lib.get_rgb_datas_length() <= 0:
            pass
        print('Stream started.')
        self.videothread.start()

    def startrecording(self,filename="photo"):
        '''
        Call this function to tell hula_video to store the video received from the drone into individual files.
        parameter:
        filename - defines what the photo files are prepended.
        '''
        self.record = True
        self.photo_filename = filename
        self.photo_index = 0
    
    def stoprecording(self):
        '''
        Call this function to tell hula_video to stop recording.
        '''
        self.record = False        

    def get_image_size(self):
        '''
        Call this function to find out what is the resolution of the video.
        Returns a tuple of height and width of video resolution.
        '''
        return (self.lib.get_height(),self.lib.get_width())

    def stop_live(self):
        '''
        Call this function to stop the live display.
        '''
        self.live = False
        self.video_queue = deque()

    def get_video(self,get_latest=True,keep_getting=True):
        '''
        Call this function to get a frame of the video. It returns the latest frame in the form of numpy array.
        '''
        while len(self.video_queue) == 0 and keep_getting and self.stopApp == False:
            time.sleep(0.1)
        frame = None
        if self.stopApp == False:
            if get_latest:
                frame = self.video_queue.pop()
            else:
                frame = self.video_queue.popleft()            
        return frame


    def _receive_video_data(self):
        print('Started Video Receiver for Drone %d' % self.video_port)
        length = self.lib.get_rgb_datas_length()
        self.vid_width = self.lib.get_width()
        self.vid_height = self.lib.get_height()
        if self.display:
            cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

        while self.stopApp == False:
            sh = self.lib.should_update_frame()
            if(sh):
                data_ptr = self.lib.get_rgb_ptr()
                data = np.ctypeslib.as_array(data_ptr, shape=(length,))[:length]
                image_array = np.frombuffer(data, dtype=np.uint8).reshape((self.vid_height, self.vid_width, 3))
                frame_cv2 = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

                if len(self.video_queue) + 1 >= self.buffer_size:
                   throw = self.video_queue.popleft()
                self.video_queue.append(frame_cv2)

                if self.record:
                    #cv2.imwrite(self.photo_filename + str(self.photo_index) + '.jpg', frame_cv2)
                    cv2.imwrite(os.path.join(self.savepath , self.photo_filename + str(self.photo_index) + '.jpg'), frame_cv2)
                    self.photo_index +=1
                if self.display:
                    cv2.imshow('Video', frame_cv2)
                    cv2.waitKey(1)


        if self.display:
            cv2.destroyWindow('Video')
        self.uapi.Plane_cmd_swith_rtp(1)
        print('Video stream closed')
    