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

j = 0
for i in range(1, 1361):
    if (i - 1) % 80 < 70:
        label_dir = os.path.join(target_train, classes[j])
    else:
        label_dir = os.path.join(target_test, classes[j])

    if not os.path.isdir(label_dir):
        os.makedirs(label_dir)

    filename = "image_" + str(i).zfill(4) + ".jpg"
    image = cv2.imread(os.path.join(directory, filename))
    cv2.imwrite(os.path.join(label_dir, filename), image)

    if i % 80 == 0:
        j += 1
