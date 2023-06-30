import matplotlib.pyplot as plt
import skimage.io as io
from datetime import datetime
import blur
from pano_face_detect import run
import cv2

t1=datetime.now()
result = run(source='/home/ceinfo/Downloads/SAMPLE_PANORAMA/GSAA9382.jpg', nosave=True, box=True)
t2 = datetime.now()
print("inferece time :", t2-t1)
if len(result) == 0:
    print('No Face Detected')

else:
    boxes = result
    t3=datetime.now()
    blur.test_blur('API_DATA/box_label/test.png', result)
    t4=datetime.now()
    print("blurring time :", t4-t3)
    # out = cv2.resize(out, (960, 540))
    # cv2.imshow("x",out)
    # cv2.waitKey(0)

    # closing all open windows
    # cv2.destroyAllWindows()

    # return send_file('bluroutput/image.png', mimetype='image/png')