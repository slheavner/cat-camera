from matplotlib import pyplot as plt
import numpy as np
from cv2 import cv2
upper = np.array([100, 120, 200], dtype="uint8")
lower = np.array([30, 70, 130], dtype="uint8")
cam = cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    if ret:
        mask = cv2.inRange(frame, lower, upper)
        print(cv2.countNonZero(mask))
        output = cv2.bitwise_and(frame, frame, mask=mask)
        output = cv2.putText(output, str(cv2.countNonZero(
            mask)), (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
        cv2.imshow("frame",  np.hstack([frame, output]))
    if cv2.waitKey(delay=20) & 0xFF == ord('q'):
        break
s, image = cam.read()
cam.release()

print(s)
# image = cv2.imread('/Users/samuel.heavner/Downloads/finn-and-nico.jpeg')
# image = cv2.resize(image, (720, 1280))
# image = cv2.blur(image, (10, 10))
# print(image) # reads the image
# image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # convert to HSV
figure_size = 9  # the dimension of the x and y axis of the kernal.
mask = cv2.inRange(image, lower, upper)
output = cv2.bitwise_and(image, image, mask=mask)
cv2.imshow("images", np.hstack([image, output]))
cv2.waitKey(0)
# plt.figure(figsize=(11,6))
# plt.subplot(121), plt.imshow(cv2.cvtColor(image, cv2.COLOR_HSV2RGB)),plt.title('Original')
# plt.xticks([]), plt.yticks([])
# plt.subplot(122), plt.imshow(cv2.cvtColor(output, cv2.COLOR_HSV2RGB)),plt.title('Median Filter')
# plt.xticks([]), plt.yticks([])
# plt.show()
