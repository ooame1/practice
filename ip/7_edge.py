import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')
    cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    median_val = np.median(cvtImage) 

    auto_threshold1 = int(max(0, 0.66 * median_val))
    auto_threshold2 = int(min(255, 1.33 * median_val))
    edge_canny = cv2.Canny(cvtImage, auto_threshold1, auto_threshold2)
    edge_sobel_x = cv2.Sobel(cvtImage, cv2.CV_16S, 1, 0)
    edge_sobel_y = cv2.Sobel(cvtImage, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(edge_sobel_x)
    absY = cv2.convertScaleAbs(edge_sobel_y)
    edge_sobel = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    edge_lap = cv2.Laplacian(cvtImage, cv2.CV_16S)
    edge_lap = cv2.convertScaleAbs(edge_lap)

    cv2.imshow("Sobel", edge_sobel)
    cv2.imshow('Laplacian', edge_lap)
    cv2.imshow('Canny', edge_canny)
    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main()

