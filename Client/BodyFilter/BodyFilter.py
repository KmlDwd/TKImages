import json
import os
import cv2
import mediapipe as mp


def hand_detection(image_path: str) -> int:
    """Detect hands in image"""
    hands = mp.solutions.hands.Hands(static_image_mode=True,
                                     max_num_hands=2,
                                     model_complexity=1,
                                     min_detection_confidence=0.3,
                                     min_tracking_confidence=0.3)
    try:
        img = cv2.imread(image_path)
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    except cv2.error:
        return 0
    return int(100 * results.multi_handedness[0].classification[0].score) if results.multi_handedness is not None else 0


def face_detection(path_file: str) -> int:
    """Detect faces in image"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    try:
        img = cv2.imread(path_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, _, levels_weights = face_cascade.detectMultiScale3(gray, 1.5, 2, outputRejectLevels=True)
        if isinstance(levels_weights, tuple):
            levels_weights = 0
        else:
            levels_weights = max(abs(levels_weights))
    except cv2.error:
        levels_weights = 0
    return int(levels_weights * 15)


def run_classifier(body_type, paths):

    if "face_check" in body_type:
        paths = [x for x in paths if face_detection(x) >= int(body_type["face_check"])]

    if "hand_check" in body_type:
        paths = [x for x in paths if hand_detection(x) >= int(body_type["hand_check"])]
        
    return paths


def process_request(body):
    body = json.loads(body)
    print(body)
    
    #"params": {"detect faces": "false", "face confidence": 0, "detect hands": "false", "hands confidence": 0}}'
    params= body["params"]
    paths = body["paths"]
    face_check = params["detect faces"]
    hand_check = params["detect hands"]

    dic_setting = {}
    dic_setting["face_check"] = params["face confidence"]
    dic_setting["hand_check"] = params["hands confidence"]

    filter_paths = run_classifier(dic_setting, paths)

    return filter_paths
    