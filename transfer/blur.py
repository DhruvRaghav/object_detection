import cv2
from numba import jit, cuda


def rectblur(imgage, boxes):
    img=cv2.imread(imgage)

    if len(boxes) > 0:


        # img = (img.copy())
        height, width = img.shape[0], img.shape[1]


        for row in boxes:

            row2 = [int(j) for j in row]
            row1 = [row2[0], row2[1], row2[2], row2[3]]

            # print('row1', row1)
            box = [0, 0, 0, 0]
            box[0] = row1[0]
            box[1] = row1[1]
            box[2] = row1[2]
            box[3] = row1[3]
            if box[0]>=0 and box[1]>=0 and box[2] <= width and box[3] <= height:

                cv2.rectangle(img, (box[0], box[1]), (box[2]-1, box[3]-1),(0,0,0),1)

                ROI=img[box[1]:box[3], box[0]:box[2]]

                blur=cv2.GaussianBlur(ROI, (23,23),5)
                # print(type(blur))
                # blur=np.array(blur)

                img[box[1]:box[1]+blur.shape[0],box[0]:box[0]+blur.shape[1]]=blur

                cv2.imwrite('bluroutput/image.png', img)

                # Image.fromarray(img).save('bluroutput/image.jpg')
            else:
                return 'Invalid parameter'

        # return img

@jit
def test_blur(imgage, boxes):
    img = cv2.imread(imgage)

    if len(boxes) > 0:

        # img = (img.copy())
        height, width = img.shape[0], img.shape[1]

        for row in boxes:

            row2 = [int(j) for j in row]
            row1 = [row2[0], row2[1], row2[2], row2[3]]

            # print('row1', row1)
            box = [0, 0, 0, 0]
            box[0] = row1[0]
            box[1] = row1[1]
            box[2] = row1[2]
            box[3] = row1[3]
            if box[0] >= 0 and box[1] >= 0 and box[2] <= width and box[3] <= height:

                cv2.rectangle(img, (box[0], box[1]), (box[2] - 1, box[3] - 1), (0, 0, 0), 1)

                ROI = img[box[1]:box[3], box[0]:box[2]]

                blur = cv2.GaussianBlur(ROI, (23, 23), 5)
                # print(type(blur))
                # blur=np.array(blur)

                img[box[1]:box[1] + blur.shape[0], box[0]:box[0] + blur.shape[1]] = blur

                cv2.imwrite('bluroutput/Image.png', img)
                # return img

                # Image.fromarray(img).save('bluroutput/image.jpg')
            else:
                return 'Invalid parameter'

        # return img