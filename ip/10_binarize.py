import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'


image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')
img_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def on_trackbar(threshold_value):
    if img_grayscale is None:
        return

    threshold_value = max(1, threshold_value)

    ret, binary_image = cv2.threshold(
        img_grayscale, 
        threshold_value, 
        255,
        cv2.THRESH_BINARY
    )
    cv2.imshow("Binarized Image", binary_image)

def main():
    initial_threshold = 127
    cv2.namedWindow("Binarized Image", cv2.WINDOW_NORMAL)
    cv2.createTrackbar(
        "Threshold",
        "Binarized Image",
        initial_threshold,
        250,
        on_trackbar
    )

    on_trackbar(initial_threshold)

    while True:
        if cv2.waitKey(1) & 0xFF== ord('q'):
            break
    cv2.destroyAllWindows()
    return 0

if __name__ == "__main__":
    main()

