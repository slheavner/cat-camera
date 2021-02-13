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
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

upper = np.array([100, 120, 200], dtype="uint8")
lower = np.array([30, 70, 130], dtype="uint8")
finn = {
    'lower': {
        'r': lower[2],
        'g': lower[1],
        'b': lower[0]
    }
}


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", finn=finn)


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/set_range", methods=["POST"])
def set_range():
    # return the response generated along with the specific media
    # type (mime type)
    global upper, lower
    data = request.get_json(force=True)
    min = data["min"]
    max = data["max"]
    with lock:
        upper = np.array([max["b"], max["g"], max["r"]], dtype="uint8")
        lower = np.array([min["b"], min["g"], min["r"]], dtype="uint8")
    return Response()


def generate():
    # grab global references to the output frame and lock variables
    global output, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired

        frame = vs.read()
        output = frame
        # mask = cv2.inRange(frame, lower, upper)
        # output = cv2.bitwise_and(frame, frame, mask=mask)
        # output = cv2.putText(output, str(cv2.countNonZero(
        #     mask)), (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
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
