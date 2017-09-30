import face_recognition
import time
import os
import json
from pathlib import Path
import numpy as np
import sys

current_milli_time = lambda: int(round(time.time() * 1000)) # Function to calculate the time
start = current_milli_time()

known_face_dictionary = {}
cache = Path("cache.txt")  # Load from cache if it's there
if cache.exists():
    with open('cache.txt') as file:
        data = json.load(file)
        known_face_dictionary = dict(map(lambda item: (item[0], np.array(item[1])), data.items()))
        print("Loaded from cache")
        sys.stdout.flush()



known_pictures_dir = "known_pictures"
if not known_face_dictionary: # if empty
    for filename in os.listdir(os.path.join(os.path.dirname(__file__),known_pictures_dir)):
        print(os.path.join(os.path.dirname(__file__),known_pictures_dir) + "/" + filename)
        sys.stdout.flush()
        if filename[:1] == "." :  # For .DS_Store
            continue
        face_name = filename.replace(".jpg", "")
        face_image = face_recognition.load_image_file(os.path.join(os.path.dirname(__file__),known_pictures_dir) + "/" + filename)
        known_face_dictionary[face_name] = face_recognition.face_encodings(face_image)[0] # Only get the first face


unknown_pictures_dir = "unknown_pictures"
unknown_face_dictionary = {}
for filename in os.listdir(os.path.join(os.path.dirname(__file__),unknown_pictures_dir)):
    unknown_face_name = filename.replace(".jpg", "")
    unknown_face_image = face_recognition.load_image_file(os.path.join(os.path.dirname(__file__),unknown_pictures_dir) + "/" + filename)
    unknown_face_dictionary[unknown_face_name] = face_recognition.face_encodings(unknown_face_image)[0]


load = current_milli_time()
print("Load took", load - start)
sys.stdout.flush()


#Check unknown faces
known_face_encodings = list(known_face_dictionary.values())
known_face_names = list(known_face_dictionary.keys())

for unknown_face in unknown_face_dictionary.keys():
    unknown_face_encoding = unknown_face_dictionary[unknown_face]
    results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
    indicies_results = [k for k,v in enumerate(results) if v == True]
    for index in indicies_results:
        print("Picture " + unknown_face + " is of " + known_face_names[index])
        sys.stdout.flush()

compare = current_milli_time()
print("compare took", compare - load)
sys.stdout.flush()

# Write to cache
with open('cache.txt', 'w') as file:
    file.write(json.dumps(dict(map(lambda item: (item[0], item[1].tolist()), known_face_dictionary.items()))))