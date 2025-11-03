import cv2

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/'

def main():
    video = cv2.VideoCapture(RESOURCE_DIR + 'big_buck_bunny.mp4')
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        cv2.imshow('Video Frame', frame)
        if cv2.waitKey(30) == ord('q'):
            break
    video.release()
    return 0

if __name__ == "__main__":
    main()
