from gpiozero import Servo
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
vs = VideoStream(src=0, resolution=(320, 240)).start()
vs.stream.set(3, 650)
vs.stream.set(4, 360)
vs.stream.get(17)
time.sleep(2.0)
SERVO_MIN = 0.000544
SERVO_MAX = 0.0024

servo_nico = Servo(18, min_pulse_width=SERVO_MIN, max_pulse_width=SERVO_MAX)
servo_finn = Servo(13, min_pulse_width=SERVO_MIN, max_pulse_width=SERVO_MAX)


current_state = ''


nico_values = {
    'upper': np.array([90, 57, 62], dtype="uint8"),
    'lower': np.array([0, 0, 0], dtype="uint8")
}
finn_values = {
    'upper': np.array([95, 125, 140], dtype="uint8"),
    'lower': np.array([32, 55, 65], dtype="uint8")
}


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", finn="asdfasdfasdf")


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


def is_cat(n, f):
    percentage = n / f
    if percentage >= 1.15 and n > 85000:
        return 'nico'
    elif percentage <= 0.85 and f > 50000:
        return 'finn'
    else:
        return 'none'


def write_text(frame, text, y):
    return cv2.putText(frame, text, (50, y),
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=3)


def update_servos():
    global current_state, servo_finn, servo_nico
    if current_state == 'nico':
        servo_nico.min()
        servo_finn.min()
    elif current_state == 'finn':
        servo_nico.max()
        servo_finn.max()
    else:
        servo_nico.max()
        servo_finn.min()
    time.sleep(1)
    servo_finn.detach()
    servo_nico.detach()


def generate():
    # grab global references to the output frame and lock variables
    global output, lock, current_state
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        frame = vs.read()
        output = frame
        nico_mask = cv2.inRange(
            frame, nico_values['lower'], nico_values['upper'])
        finn_mask = cv2.inRange(
            frame, finn_values['lower'], finn_values['upper'])
        nico_count = cv2.countNonZero(nico_mask)
        finn_count = cv2.countNonZero(finn_mask)
        height = 25
        cat = is_cat(nico_count, finn_count)
        output = write_text(output, 'nico: ' + str(nico_count), height)
        output = write_text(output, 'finn: ' + str(finn_count), height * 3)
        output = write_text(output, 'ratio: ' +
                            str(nico_count / finn_count), height * 5)
        output = write_text(output, 'is cat: ' + cat, height * 7)
        if cat != current_state:
            current_state = cat
            update_servos()
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
