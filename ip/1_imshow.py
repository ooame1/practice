import cv2

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    image = cv2.imread(RESOURCE_DIR + 'shibuya.jpg')

    cv2.imshow('shibuya.jpg', image)
    cv2.waitKey(0)
    return 0

if __name__ == "__main__":
    main()

