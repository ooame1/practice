import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')
    cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    cv2.imshow('shibuya.jpg', np.vstack((cvtImage, image)))
    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main()

