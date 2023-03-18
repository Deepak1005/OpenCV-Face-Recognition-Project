import face_recognition as fr
from threading import Thread
import numpy as np
import time
import os
import cv2
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

exclude_names = ['Unknown', 'HOD', 'Principal']

class VideoStream:
    def __init__(self, stream):
        self.video = cv2.VideoCapture(stream)
        self.video.set(cv2.CAP_PROP_FPS, 60)

        if self.video.isOpened() is False:
            print("Can't accessing the webcam stream.")
            exit(0)

        self.grabbed , self.frame = self.video.read()

        self.stopped = True
        
        self.thread = Thread(target=self.update)
        self.thread.daemon = True
    
    def start(self):
        self.stopped = False
        self.thread.start()

    def update(self):
        while True :
            if self.stopped is True :
                break
            self.grabbed , self.frame = self.video.read()

        self.video.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

        
def encode_faces():
    encoded_data = {}

    for dirpath, dnames, fnames in os.walk("./Images"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg"):
                face = fr.load_image_file("Images/" + f)
                encoding = fr.face_encodings(face)[0]
                encoded_data[f.split(".")[0]] = encoding
    return encoded_data

def Attendance(name):
    today = time.strftime('%d_%m_%Y')
    f = open(f'Records/Record_{today}.csv', 'a')
    f.close()

    
    with open(f'Records/Record_{today}.csv', 'r') as f:
        data = f.readlines()
        names = []
        for line in data:
            entry = line.split(',')
            names.append(entry[0])

    
    with open(f'Records/Record_{today}.csv', 'a') as fs:
        if name not in names:
            current_time = time.strftime('%H:%M:%S')
            if name not in exclude_names:
                fs.write(f"\n{name}, {current_time}")


if __name__ == "__main__":
    faces = encode_faces()
    encoded_faces = list(faces.values())
    faces_name = list(faces.keys())
    video_frame = True

    
    video_stream = VideoStream(stream=0)
    video_stream.start()

    while True:
        if video_stream.stopped is True:
            break
        else :
            frame = video_stream.read()

            if video_frame:
                face_locations = fr.face_locations(frame)
                unknown_face_encodings = fr.face_encodings(frame, \
                face_locations)

                face_names = []
                for face_encoding in unknown_face_encodings:
                    matches = fr.compare_faces(encoded_faces, \
                    face_encoding)
                    name = "Unknown"

                    face_distances = fr.face_distance(encoded_faces,\
                    face_encoding)
                    try:

                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = faces_name[best_match_index]

                        face_names.append(name)
                    except:
                        pass

            video_frame = not video_frame

            for (top, right, bottom, left), name in zip(face_locations,\
            face_names):
                cv2.rectangle(frame, (left-20, top-20), (right+20, \
                bottom+20), (0, 255, 0), 2)
                
                cv2.rectangle(frame, (left-20, bottom -15), \
                (right+20, bottom+20), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
               
                cv2.putText(frame, name, (left -20, bottom + 15), \
                font, 0.85, (255, 255, 255), 2)
                
                
                Attendance(name)

         
        delay = 0.04
        time.sleep(delay)

        cv2.imshow('frame' , frame)
        key = cv2.waitKey(1)
    
        if key == ord('q'):
            break

    video_stream.stop()
    email_sender="bellamkondadeepak1@gmail.com"
    password="punelppttrhtjxsu"
    subject="Automate Attendence "
    with open('D:\Mini_Project\MINE\projectfol\completeData\Mail\mail.csv','r') as csvfile:
        reader=csv.reader(csvfile)
        for line in reader:
            text="helo "+line[1]+" you got "+line[2]+" attendece"
            print(text)
            email_send=line[2]
            msg=MIMEMultipart()
            msg['From']=email_sender
            msg["To"]=email_send
            msg.attach(MIMEText(text,"plain"))
            part=MIMEBase('application',"octect-stream")
            today = time.strftime('%d_%m_%Y')
            part.set_payload(open(f"D:\Mini_Project\MINE\projectfol\completeData\Records\Record_{today}.csv","rb").read())
            encoders.encode_base64(part)
            
            part.add_header('content-Disposition','attachment ; filename="D:\Mini_Project\MINE\projectfol\completeData\Records\Record_{today}.csv"')
            msg.attach(part)
            text=msg.as_string()
            server=smtplib.SMTP_SSL("smtp.gmail.com",465)
            server.login(email_sender,password)
            server.sendmail(email_sender,email_send,text)
            server.quit()
            


    cv2.destroyAllWindows()

