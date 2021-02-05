# 마스크 착용여부 (동영상)
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np
import cv2

# 딥러닝 모델 불러오기
facenet = cv2.dnn.readNet('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')
model = load_model('models/mask_detector.model')

Message_Mask = "Mask: "
Message_Yes = "Yes"
Message_No = "No"

cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()

    if ret == False:
        break
    

    h, w, c = img.shape
    # 이미지 전처리하기
    blob = cv2.dnn.blobFromImage(img, size=(300, 300), mean=(104., 177., 123.)) # 300 300


    # 얼굴 영역 탐지 모델로 추론하기
    facenet.setInput(blob)
    dets = facenet.forward()

    # 각 얼굴에 대해서 반복문 돌기
    for i in range(dets.shape[2]):
        confidence = dets[0, 0, i, 2]

        if confidence < 0.5:
            continue

        # 사각형 꼭지점 찾기
        x1 = int(dets[0, 0, i, 3] * w)
        y1 = int(dets[0, 0, i, 4] * h)
        x2 = int(dets[0, 0, i, 5] * w)
        y2 = int(dets[0, 0, i, 6] * h)

        # 얼굴 잘라내기
        face = img[y1:y2, x1:x2]

        face_input = cv2.resize(face, dsize=(224, 224)) #224 224
        face_input = cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB) # 전처리 할때 색 바꿔주기
        face_input = preprocess_input(face_input) # 전처리 함수 .shape:(224,244,3)
        face_input = np.expand_dims(face_input, axis=0) # 차원 변형 .shape:(1,224,224,3)

        mask, nomask = model.predict(face_input).squeeze() #openCV의 forward()와 역할이 같다.

        if mask > nomask: # 마스크 착용 시
            color = (0,255,0)
            cv2.putText(img, '%s %s' % (Message_Mask, Message_Yes), org=(x1, y1), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=color, thickness=2)
        else:
            color = (0,0,255)
            cv2.putText(img, '%s %s' % (Message_Mask, Message_No), org=(x1, y1), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=color, thickness=2)

        # 사각형 그리기
        cv2.rectangle(img, pt1=(x1, y1), pt2=(x2, y2), thickness=2, color=color)

    cv2.imshow('result', img)
    print(face.shape)
    if cv2.waitKey(1) == ord('q'):
        break