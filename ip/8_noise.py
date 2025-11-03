import cv2
import numpy as np

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def add_gaussian_noise(image, mean=0, sigma=20):
    noisy_image = image.astype(np.float32)
    row, col = image.shape

    gauss = np.random.normal(mean, sigma, (row, col))

    noisy_image = noisy_image + gauss

    noisy_image = np.clip(noisy_image, 0, 255)
    return noisy_image.astype(np.uint8)

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')
    cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    noisy_image = add_gaussian_noise(cvtImage)
    cv2.imshow('Noisy Image', np.vstack((noisy_image, cvtImage)))
    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main()

