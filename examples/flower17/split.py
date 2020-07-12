import cv2
import os

directory = "jpg"
target_train = "flower_dataset/train"
target_test = "flower_dataset/test"

if not os.path.isdir(target_train):
    os.makedirs(target_train)

if not os.path.isdir(target_test):
    os.makedirs(target_test)

classes = [
    "daffodil",
    "snowdrop",
    "lilyvalley",
    "bluebell",
    "crocus",
    "iris",
    "tigerlily",
    "tulip",
    "fritillary",
    "sunflower",
    "daisy",
    "coltsfoot",
    "dandelion",
    "cowslip",
    "buttercup",
    "windflower",
    "pansy",
]

i = 0
j = 0
for filename in sorted(os.listdir(directory)):
    if j < 70:
        label_dir = os.path.join(target_train, classes[i])
    else:
        label_dir = os.path.join(target_test, classes[i])

    if not os.path.isdir(label_dir):
        os.makedirs(label_dir)

    image = cv2.imread(os.path.join(directory, filename))

    cv2.imwrite(os.path.join(label_dir, filename), image)
    j += 1

    if j % 80 == 0:
        i += 1
        j = 0
