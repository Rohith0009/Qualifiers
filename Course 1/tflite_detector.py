import threading
import time
import numpy as np
import signal
import cv2
import sys
import pyhula
import ctypes
from collections import deque
from tflite_runtime.interpreter import Interpreter
import os

class tflite_detector:
    def __init__(self,model="model.tflite",label="label.txt",vid_width=1280,vid_height=720):
        self.confidence_level = 0.5
        self.detected_object = []
        self.tf_model = model
        self.tf_label = label
        self.model_loaded = False
        self.vid_width = vid_width
        self.vid_height = vid_height
        print("1111111")

        if os.path.isfile(self.tf_model) and os.path.isfile(self.tf_label):
            print("22222")
            with open(self.tf_label, "r") as f:
                self.labels = [line.strip() for line in f.readlines()]
                f.close()

            print(len(self.labels))

            self.interpreter = Interpreter(model_path=self.tf_model)
            self.interpreter.allocate_tensors()
            self.input_details, self.output_details = self.interpreter.get_input_details(), self.interpreter.get_output_details()
            self.tf_input_width = self.input_details[0]['shape'][2]
            self.tf_input_height = self.input_details[0]['shape'][1]
            self.floating_model = self.input_details[0]['dtype'] == np.float32
            self.model_loaded = True

            print("33333")
        else:
            print("Loading model failed: model file or label file not found")
    
    def get_detected_obj(self):
        return self.detected_object

    def detect(self,frame=None):
        frame_cv2 = frame
        frame_rgb = cv2.cvtColor(frame_cv2, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.tf_input_width, self.tf_input_height))
        input_data = np.expand_dims(frame_resized, axis=0)
        self.detected_object = []
        highest_score_obj = None
        highest_score = -1
         # set frame as input tensors
        if self.floating_model:
            input_data = (np.float32(input_data) - 127.5) / 127.5
#            print('fola')
#        self.interpreter.set_tensor(self.input_details[0]['index'], [input_data])
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # perform inference
        self.interpreter.invoke()

        # Get output tensor need to modify this part for dfferent type of model
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
#        boxes = self.interpreter.get_tensor(self.output_details[0]['index']).squeeze()
#        classes = self.interpreter.get_tensor(self.output_details[1]['index']).squeeze()
#        scores = self.interpreter.get_tensor(self.output_details[2]['index']).squeeze()

        if len(scores) > 0:
            for i in range(len(scores)):
                if ((scores[i] > self.confidence_level) and (scores[i] <= 1.0)):
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                    ymin = int(max(1, (boxes[i][0] * self.vid_height)))
                    xmin = int(max(1, (boxes[i][1] * self.vid_width)))
                    ymax = int(min(self.vid_height, (boxes[i][2] * self.vid_height)))
                    xmax = int(min(self.vid_width, (boxes[i][3] * self.vid_width)))
                    cv2.rectangle(frame, (xmin, ymin),(xmax, ymax), (10, 255, 0), 4)
                    center_x = (xmin + xmax) // 2
                    center_y = (ymin + ymax) // 2
                    object_name = self.labels[int(classes[i])]
                    label = '%s: %d%%' % (object_name, int(scores[i]*100))
                    current_score = int(scores[i]*100)
                    current_detected_object = {'label':object_name,'score':scores[i]*100,'x':center_x,'y':center_y}
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                # Make sure not to draw label too close to top of window
                    label_ymin = max(ymin, labelSize[1] + 10)
                    cv2.rectangle(frame_cv2, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
                    cv2.putText(frame_cv2, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    self.detected_object.append(current_detected_object)
                    if current_score > highest_score:
                        highest_score = current_score
                        highest_score_obj = current_detected_object
        else:
            cv2.putText(frame_cv2, "Detecting with tflite", (self.vid_width -200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0) , 1)
        return highest_score_obj, frame_cv2
