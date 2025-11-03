import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')

    M = cv2.getRotationMatrix2D((image.shape[1]//2, image.shape[0]//2), 45, 1.0)
    rotated = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

    cv2.imshow('shibuya.jpg', np.vstack((rotated, image)))
    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main()

