import cv2
CHECKERBOARD = (6, 9)
CAMERA_INDEX = 1
OUTPUT_FILENAME = 'resource/calibration.mp4'

FOURCC_CODE = cv2.VideoWriter_fourcc(*'mp4v') 

def record_video(camera_index, output_filename, fourcc_code):
    try:

        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            return
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        out = cv2.VideoWriter(output_filename, fourcc_code, fps, (frame_width, frame_height))

        if not out.isOpened():
            cap.release()
            return
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:

                out.write(frame)
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

                if ret == True:
                    cv2.putText(frame, "OK", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow('Camera Recording - Press Q to Stop', frame)
                    cv2.waitKey(0)

                cv2.putText(frame, "RECORDING...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Camera Recording - Press Q to Stop', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

    except Exception as e:
        print(f"error: {e}")
    finally:

        if 'cap' in locals() and cap.isOpened():
            cap.release()
        if 'out' in locals() and out.isOpened():
            out.release()
        
        cv2.destroyAllWindows()
        print(f"\nfile saved: {output_filename}")
if __name__ == '__main__':
    record_video(CAMERA_INDEX, OUTPUT_FILENAME, FOURCC_CODE)
