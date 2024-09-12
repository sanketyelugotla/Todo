# install cmake, face_recognition, opencv-python, numpy

import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime


def face_recog():

    video_capture = cv2.VideoCapture(0)

    # Load known faces
    myPic = face_recognition.load_image_file("static/faces/sanket.jpg")
    myPic_encoding = face_recognition.face_encodings(myPic)[0]

    yagneshPic = face_recognition.load_image_file("static/faces/yagnesh.jpg")
    yagneshPic_encoding = face_recognition.face_encodings(yagneshPic)[0]

    known_face_encodings = [myPic_encoding, yagneshPic_encoding]
    known_face_names = ["sanket", "yagnesh"]

    # list of expected students
    students = known_face_names.copy()
    face_locations = []
    face_encodings = []

    # Get the current date and time
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    f = open(f"{current_date}.csv", "w+", newline="")
    lnwriter = csv.writer(f)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Recognise faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # Add the text if a person is present
                if name in known_face_names:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOfText = (10, 100)
                    fontScale = 1.5
                    fontColor = (255, 0, 0)
                    thickness = 3
                    lineType = 2
                    cv2.putText(frame, name + " Present", bottomLeftCornerOfText,
                                font, fontScale, fontColor, thickness, lineType)

                    if name in students:
                        students.remove(name)
                        current_time = now.strftime("%H-%M%S")
                        lnwriter.writerow([name, current_time])

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    f.close()
