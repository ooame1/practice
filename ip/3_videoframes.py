import cv2

RESOURCE_DIR = './resource/'
OUTPUT_DIR = './output/frames/'

def main():
    if not cv2.os.path.exists(OUTPUT_DIR):
        cv2.os.makedirs(OUTPUT_DIR)

    video = cv2.VideoCapture(RESOURCE_DIR + 'big_buck_bunny.mp4')
    count = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        if count % 30 == 0:
            cv2.imwrite(OUTPUT_DIR + 'frame_{:.0f}.jpg'.format(video.get(cv2.CAP_PROP_POS_FRAMES)), frame)
        count += 1
    video.release()
    return 0

if __name__ == "__main__":
    main()
