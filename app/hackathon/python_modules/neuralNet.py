import face_recognition
import time
import os
import json
from pathlib import Path
import numpy as np
import math


def recipSum(scores):
    return sum(list(map(lambda val: math.exp(1.0/val), scores)))

def softmax(score, denom):
    return math.exp(1.0/score)/denom

# current_milli_time = lambda: int(round(time.time() * 1000)) # Function to calculate the time
# start = current_milli_time()

known_face_dictionary = {}
cacheFile = os.path.join(os.path.dirname(__file__), "cache.txt")
cache = Path(cacheFile)  # Load from cache if it's there
if cache.exists():
    with open(cacheFile) as file:
        data = json.load(file)
        known_face_dictionary = dict(map(lambda item: (item[0], np.array(item[1])), data.items()))
        # print("Loaded from cache")

badPics = open('badPics.txt', 'w+')

known_pictures_dir = os.path.join(os.path.dirname(__file__), "known_pictures")
if not known_face_dictionary: # if empty
    for filename in os.listdir(known_pictures_dir):
        # print(known_pictures_dir + "/" + filename)
        if filename[:1] == "." :  # For .DS_Store
            continue
        face_name = filename.replace(".jpg", "")
        face_image = face_recognition.load_image_file(known_pictures_dir + "/" + filename)
        try:
            known_face_dictionary[face_name] = face_recognition.face_encodings(face_image)[0] # Only get the first face
        except Exception as e:
            print (e)
            badPics.write(face_name + "\n")
            badPics.flush()

unknown_pictures_dir = os.path.join(os.path.dirname(__file__), "unknown_pictures")
unknown_face_dictionary = {}
for filename in os.listdir(unknown_pictures_dir):
    if filename[:1] == "." :  # For .DS_Store
        continue
    unknown_face_name = filename.replace(".jpg", "")
    unknown_face_image = face_recognition.load_image_file(unknown_pictures_dir + "/" + filename)
    try:
        unknown_face_dictionary[unknown_face_name] = face_recognition.face_encodings(unknown_face_image)[0]
    except Exception as e:
        print (e)
        badPics.write(unknown_face_name + "\n")
        badPics.flush()
    os.remove(os.path.join(os.path.dirname(__file__), "unknown_pictures") + "/" + filename)


#Check unknown faces
known_face_encodings = list(known_face_dictionary.values())
known_face_names = list(known_face_dictionary.keys())
threshold = .65
for unknown_face in unknown_face_dictionary.keys():
    unknown_face_encoding = unknown_face_dictionary[unknown_face]
    # results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
    result_distances = face_recognition.face_distance(known_face_encodings, unknown_face_encoding)
    positive_result_indicies = [k for k,v in enumerate(result_distances) if v < threshold]
    recip_sum = recipSum([result_distances[index] for index in positive_result_indicies])
    normed_res = {}
    for index in positive_result_indicies:
        normed_res[known_face_names[index]]=softmax(result_distances[index], recip_sum)

    if normed_res:
        print(json.dumps(normed_res))


# Write to cache
with open(cacheFile, 'w') as file:
    file.write(json.dumps(dict(map(lambda item: (item[0], item[1].tolist()), known_face_dictionary.items()))))
