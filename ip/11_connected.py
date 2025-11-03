import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')
    cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, binary_im = cv2.threshold(cvtImage, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    bin_clo = cv2.dilate(binary_im, kernel, iterations=2)
    cv2.imshow('bin_clo', np.vstack((bin_clo, binary_im)))
    cv2.waitKey(0)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_im, connectivity=8)

    print('num_labels = ',num_labels)
    print('stats = ',stats)
    print('centroids = ',centroids)
    print('labels = ',labels)

    return 0

if __name__ == "__main__":
    main()

