from imutils.video import VideoStream
from flask import Response
from flask import request
from flask import Flask
from flask import render_template
import numpy as np
import threading
import argparse
import datetime
import imutils
import time
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
# vs = VideoStream(src=0,resolution=(320, 240)).start()
time.sleep(2.0)

nico_values = {
    'upper': np.array([90, 57, 62], dtype="uint8"),
    'lower': np.array([0, 0, 0], dtype="uint8")
}
finn_values = {
    'upper': np.array([95, 125, 140], dtype="uint8"),
    'lower': np.array([32, 55, 65], dtype="uint8")
}

finn = 'asdf'
@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", finn=finn)


@app.route("/video_feed_nico")
def video_feed_nico():
    return Response(generate('nico.png'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_nico2")
def video_feed_nico2():
    return Response(generate('nico2.png'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_finn")
def video_feed_finn():
    return Response(generate('finn.png'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_finn2")
def video_feed_finn2():
    return Response(generate('finn2.png'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_none")
def video_feed_none():
    return Response(generate('none.png'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/set_range", methods=["POST"])
def set_range():
    # return the response generated along with the specific media
    # type (mime type)
    global upper, lower
    data = request.get_json(force=True)
    with lock:
        upper = np.array([data[0], data[1], data[2]], dtype="uint8")
        lower = np.array([data[3], data[4], data[5]], dtype="uint8")
    return Response()


def is_cat(n, f):
    percentage = n / f
    if percentage >= 1.15 and n > 200000:
        return 'nico'
    elif percentage <= 0.85 and f > 200000:
        return 'finn'
    else:
        return 'none'


def generate(path):
    # grab global references to the output frame and lock variables
    global output, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired

        frame = cv2.imread(path, 1)
        output = frame
        nico_mask = cv2.inRange(frame, nico_values['lower'], nico_values['upper'])
        finn_mask = cv2.inRange(frame, finn_values['lower'], finn_values['upper'])
        nico_count = cv2.countNonZero(nico_mask)
        finn_count = cv2.countNonZero(finn_mask)
        output = cv2.putText(output, "Nico: " + str(nico_count), (50, 50), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), thickness=10)
        output = cv2.putText(output, "Finn: " + str(finn_count), (50, 150), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), thickness=10)
        output = cv2.putText(output, "Percentage: " + str(nico_count / finn_count), (50, 250), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), thickness=10)
        output = cv2.putText(output, "Is Cat: " + is_cat(nico_count, finn_count), (50, 350), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), thickness=10)
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
# release the video stream pointer
vs.stop()
