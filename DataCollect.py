from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
import os
from sys import platform
import argparse
import time
from Utils import PoseUtils
import numpy as np
import csv
from collections import deque
import pandas as pd

# Import Openpose (Windows/Ubuntu/OSX)
sys.path.append('/usr/local/python');


try:
    from openpose import pyopenpose as op
except:
    raise Exception('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')


params = dict()
params["logging_level"] = 3
params["output_resolution"] = "-1x-1"
params["net_resolution"] = "-1x416"
params["model_pose"] = "BODY_25"
params["alpha_pose"] = 0.5
params["scale_gap"] = 0.25
params["scale_number"] = 1
params["render_threshold"] = 0.7
params["disable_blending"] = False
params["model_folder"] = "/home/prince/openpose/models/"

opWrapper = op.WrapperPython()
opWrapper.configure(params)


class  MainWIndow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWIndow, self).__init__(parent)
        self.timer_camera = QtCore.QTimer()
        self.width = 720
        self.height = 480
        self.set_ui();
        self.slot_init();
        # openpose params
        

        print(params)
        # Starting OpenPose
        self.opWrapper = opWrapper
        self.opWrapper.start()

        # Process Image
        self.datum = op.Datum()

        self.SEQ_LEN = 10
        self.isStarted = False
        self.UserFrames = {}

        self.make_pause = False
        self.saved_count = 0
        self.backgorund_image = {}
        self.users_complete = {}
        self.currentExamination = 0

        # initiate the video
        self.cap = cv2.VideoCapture("/home/prince/Desktop/destination.mp4")

    def set_ui(self):
        self.__layout_main = QtWidgets.QHBoxLayout()
        self.__layout_fun_button = QtWidgets.QVBoxLayout()
        self.__layout_data_show = QtWidgets.QVBoxLayout()

        self.button_open_camera = QtWidgets.QPushButton(u'OFF')
        # self.action_list = {0: "Picking_up_left", 1: "Picking_up_right", 2: "Putting_back_left", 3: "Putting_back_right", 4: "No_action", 5: "Grabbing_left", 6: "Grabbing_right", 7: "Grabbing_both"}


        self.button_action_1 = QtWidgets.QPushButton(u'Picking_up_right')
        self.button_action_2 = QtWidgets.QPushButton(u'Picking_up_left')
        self.button_action_3 = QtWidgets.QPushButton(u'Putting_back_left')
        self.button_action_4 = QtWidgets.QPushButton(u'Putting_back_right')
        self.button_action_5 = QtWidgets.QPushButton(u'No_action')
        self.button_action_6 = QtWidgets.QPushButton(u'Grabbing_left')
        self.button_action_7 = QtWidgets.QPushButton(u'Grabbing_right')
        self.button_action_8 = QtWidgets.QPushButton(u'Grabbing_both')

        self.button_close = QtWidgets.QPushButton(u'Fermer')


        self.button_continue = QtWidgets.QPushButton(u'Continuer')




        self.button_open_camera.setMinimumHeight(50)
        self.button_action_1.setMinimumHeight(50)
        self.button_action_2.setMinimumHeight(50)
        self.button_action_3.setMinimumHeight(50)
        self.button_action_4.setMinimumHeight(50)
        self.button_action_5.setMinimumHeight(50)
        self.button_action_6.setMinimumHeight(50)
        self.button_action_7.setMinimumHeight(50)
        self.button_action_8.setMinimumHeight(50)
        self.button_continue.setMinimumHeight(50)

        self.button_close.setMinimumHeight(50)

        self.button_close.move(10, 100)

        self.infoBox = QtWidgets.QTextBrowser(self)
        self.infoBox.setGeometry(QtCore.QRect(10, 400, 300, 180))

        #
        self.label_show_camera = QtWidgets.QLabel()
        self.label_move = QtWidgets.QLabel()
        self.label_move.setFixedSize(200, 200)

        self.label_show_camera.setFixedSize(self.width + 1, self.height + 1)
        self.label_show_camera.setAutoFillBackground(True)

        self.__layout_fun_button.addWidget(self.button_open_camera)

        self.__layout_fun_button.addWidget(self.button_action_1)
        self.__layout_fun_button.addWidget(self.button_action_2)
        self.__layout_fun_button.addWidget(self.button_action_3)
        self.__layout_fun_button.addWidget(self.button_action_4)
        self.__layout_fun_button.addWidget(self.button_action_5)
        self.__layout_fun_button.addWidget(self.button_action_6)
        self.__layout_fun_button.addWidget(self.button_action_7)
        self.__layout_fun_button.addWidget(self.button_action_8)

        self.__layout_fun_button.addWidget(self.button_close)
        self.__layout_fun_button.addWidget(self.label_move)
        self.__layout_fun_button.addWidget(self.button_continue)

        self.__layout_main.addLayout(self.__layout_fun_button)
        self.__layout_main.addWidget(self.label_show_camera)

        self.setLayout(self.__layout_main)
        self.label_move.raise_()
        self.setWindowTitle(u'Action Collection')

    def slot_init(self):
        self.button_open_camera.clicked.connect(self.button_event)
        self.timer_camera.timeout.connect(self.show_camera)

        self.button_action_1.clicked.connect(self.button_event)
        self.button_action_2.clicked.connect(self.button_event)
        self.button_action_3.clicked.connect(self.button_event)
        self.button_action_4.clicked.connect(self.button_event)
        self.button_action_5.clicked.connect(self.button_event)
        self.button_action_6.clicked.connect(self.button_event)
        self.button_action_7.clicked.connect(self.button_event)
        self.button_action_8.clicked.connect(self.button_event)
        self.button_close.clicked.connect(self.close)
        self.button_continue.clicked.connect(self.Continue_without_saving)

    def button_event(self):
        # self.action_list = {0: "Picking_up_left", 1: "Picking_up_right", 2: "Putting_back_left", 3: "Putting_back_right", 4: "No_action", 5: "Grabbing_left", 6: "Grabbing_right", 7: "Grabbing_both"
        sender = self.sender()
        self.label_csv = open('labels.csv', 'a')
        if sender == self.button_action_1:
            self.save_Frames()
            self.label_csv.write("Picking_up_left" + "\n")
            self.timer_camera.start(1)
        if sender ==  self.button_action_2:
            self.save_Frames()
            self.label_csv.write("Picking_up_right" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_3:
            self.save_Frames()
            self.label_csv.write("Putting_back_left" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_4:
            self.save_Frames()
            self.label_csv.write("Putting_back_right" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_5:
            self.save_Frames()
            self.label_csv.write("No_action" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_6:
            self.save_Frames()
            self.label_csv.write("Grabbing_left" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_7:
            self.save_Frames()
            self.label_csv.write("Grabbing_right" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_action_8:
            self.save_Frames()
            self.label_csv.write("Grabbing_both" + "\n")
            self.timer_camera.start(1)
        if sender == self.button_open_camera:
            if self.isStarted == False:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.isStarted = True
                self.timer_camera.start(1)
                self.button_open_camera.setText(u'ON')
                self.infoBox.setText(u'blabla 1')
            else:
                self.isStarted = False
                self.timer_camera.stop()
                self.cap.release()
                self.label_show_camera.clear()
                self.button_open_camera.setText(u'OFF')
                self.infoBox.setText(u'blabla')
        self.label_csv.close()


    def returnPropre(self, i):
        return i[:-1]

    def save_Frames(self):
        self.action_csv = open("data.csv", 'a')
        for item in self.UserFrames["customer"]:
            wr = csv.writer(self.action_csv, delimiter=',', lineterminator='\n')
            wr.writerows([item])

        if not os.path.exists("hands_left/" + str(self.saved_count)): os.makedirs("hands_left/" + str(self.saved_count))
        if not os.path.exists("hands_right/" + str(self.saved_count)): os.makedirs("hands_right/" + str(self.saved_count))

        for index, backG in enumerate(self.backgorund_image["hands_left"]):
            cv2.imwrite("hands_left/" + str(self.saved_count) + "/" + str(index) + ".jpg", backG)
        for index, full_user in enumerate(self.users_complete["hands_right"]):
            cv2.imwrite("hands_right/" + str(self.saved_count) + "/" + str(index) + ".jpg", full_user)

        self.UserFrames["customer"].clear()
        self.backgorund_image["hands_left"].clear()
        self.users_complete["hands_right"].clear()
        self.action_csv.close()
        self.saved_count = self.saved_count + 1

    def Rewind_sequence(self):
        sequences_nums = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.previous_sequence_starting = int(sequences_nums) - self.SEQ_LEN
        self.cap.set(1, self.previous_sequence_starting)
        print(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def Continue_without_saving(self):
        self.UserFrames["customer"].clear()
        self.backgorund_image["hands_left"].clear()
        self.users_complete["hands_right"].clear()
        self.timer_camera.start(1)
        self.Rewind_sequence()


    def show_camera(self):
        start = time.time()
        ret, frame = self.cap.read()
        frame  = cv2.resize(frame, (720, 480))
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if frame is None:
            pass

        if ret == True:
            self.datum.cvInputData = frame
            self.opWrapper.emplaceAndPop([self.datum])
            keypoints = self.datum.poseKeypoints.tolist()
            frame_keypoints = self.datum.cvOutputData

            peoples = []
            peoples_keypoints = []


            if isinstance(keypoints, float):
                pass
            else:
                for person in keypoints:
                    left_hand = PoseUtils.getHandFromPoseIndexes(person, 7, 6, 5, 0.1)
                    right_hand = PoseUtils.getHandFromPoseIndexes(person, 4, 3, 2, 0.1)

                    left_hand_picture = frame[left_hand[1]: left_hand[3], left_hand[0]: left_hand[2]]
                    right_hand_picture = frame[right_hand[1]: right_hand[3], right_hand[0]: right_hand[2]]

                    if left_hand_picture is None:
                        left_hand_picture = np.zeros([500, 500, 3], dtype=np.uint8)



                    if right_hand_picture is None:
                        right_hand_picture = np.zeros([500, 500, 3], dtype=np.uint8)


                    fullbody = PoseUtils.getFullHumanBoudingBox(person, left_hand, right_hand, 0.1)
                    full_person_image = frame[fullbody[1]: fullbody[3], fullbody[0]: fullbody[2]]

                    peoples.append(fullbody)
                    person = [self.returnPropre(i) for i in person]
                    peoples_keypoints.append(person)



                    if full_person_image is None:
                        print("nope")
                    else:
                        if full_person_image.shape[0] < 80:
                            print('lol')
                        else:
                            self.UserFrames.setdefault("customer", deque(maxlen=self.SEQ_LEN)).append(person)
                            self.backgorund_image.setdefault("hands_left", deque(maxlen=self.SEQ_LEN)).append(left_hand_picture)
                            self.users_complete.setdefault("hands_right", deque(maxlen=self.SEQ_LEN)).append(right_hand_picture)

                    if len(self.UserFrames["customer"]) is self.SEQ_LEN:
                        self.timer_camera.stop()


                if len(peoples) > 0:
                    result = np.array(peoples)
                    total_peoples = len(result)
                    det = result[:, 0:5]

                    self.trackers = self.tracker.update(det)

                    for user in self.trackers:
                        x1, y1, x2, y2, id = user
                        # save he left hand of the user
                        # save the right hand of the user
                        self.UserFrames.setdefault(str(user[4:]), deque(maxlen=self.SEQ_LEN)).append(user[:4])


                        print(user)
                        #cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)


                    #j = np.argmin(np.array([print(i) for i in person]))
                    #print(j)
                    #cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)


            end = time.time()
            self.fps = 1. / (end - start)
            cv2.putText(frame, 'FPS: %.2f' % self.fps, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            showImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))



    def close(self):
        self.timer_camera.start(1)


if __name__ == '__main__':
    print("The system starts ro run.")
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWIndow()
    ui.show()
    sys.exit(app.exec_())
