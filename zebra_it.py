import numpy as np
import torch
from tqdm import tqdm
import cv2
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, plot_one_box, \
	strip_optimizer
from utils.torch_utils import select_device, load_classifier, time_synchronized


def detect(source, box=False, img_n=False):
	with torch.no_grad():
		weights = '/home/ce00145322/PycharmProjects/Zebra_CDnet_online/runs/exp3/weights/best.pt'
		imgsz = 640
		# print(source)

		# Initialize
		device = select_device(device="0")

		half = device.type != 'cpu'

		# Load model
		model = attempt_load(weights, map_location=device)  # load FP32 model

		imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size 如果不是32的倍数，就向上取整调整至32的倍数并答应warning

		if half:
			model.half()  # to FP16

		# Second-stage classifier
		classify = False
		if classify:
			modelc = load_classifier(name='resnet101', n=2)  # initialize
			modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model'])  # load weights
			modelc.to(device).eval()

		# Set Dataloader

		roi_in_pixels = None

		# Get names and colors
		names = model.module.names if hasattr(model, 'module') else model.names  # 解决GPU保存的模型多了module属性的问题

		if 'item' in names:
			names = ['crosswalk']

		model.eval()

		img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
		_ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once 空跑一次，释放！！牛逼

		# detected_img_id = 0
		dataset = LoadImages(source, img_size=imgsz, roi=roi_in_pixels)
		# print(dataset)

		bar = tqdm(dataset)

		bound = []

		for iii, (path, img, im0s, vid_cap, recover) in enumerate(bar):
			# print('number', iii)
			# print('path', path)
			# print('image', img)
			# print('image zero',im0s)
			# print('vidio', vid_cap)
			# print('recover',recover)

			img = torch.from_numpy(img).to(device)
			img = img.half() if half else img.float()  # uint8 to fp16/32
			img /= 255.0  # 0 - 255 to 0.0 - 1.0
			if img.ndimension() == 3:
				img = img.unsqueeze(0)  # 从[3, h, w]转换为[batch_size, 3, h, w]的形式

			pred = model(img, augment='store_true')[0]

			# Apply NMS
			pred = non_max_suppression(pred, 0.1, 0.1, classes=0, agnostic='store_true')

			# Apply Classifier
			if classify:
				pred = apply_classifier(pred, modelc, img, im0s)

			# Process detections
			for i, det in enumerate(pred):  # detections per image
				if not 'store_true' and det is not None:
					small_img_shape = torch.from_numpy(np.array([recover[1], recover[0]]).astype(np.float))
					det[:, 0], det[:, 2] = det[:, 0] + recover[2], det[:, 2] + recover[2]
					det[:, 1], det[:, 3] = det[:, 1] + recover[3], det[:, 3] + recover[3]
				else:
					small_img_shape = img.shape[2::]

				p, s, im0 = path, '', im0s  # im0s是原图

				s += '%gx%g ' % img.shape[2:]  # print string, 640x640

				if det is not None and len(det):
					# Rescale boxes from img_size to im0 size
					det[:, :4] = scale_coords(small_img_shape, det[:, :4], im0.shape).round()  # 转换成原图的x1 y1 x2 y1，像素值
					# Print results
					for c in det[:, -1].unique():
						n = (det[:, -1] == c).sum()  # detections per class
						s += '%g %ss, ' % (n, names[int(c)])  # add to string # i.e. 1 crosswalk

					for *xyxy, conf, cls in det:

						if names[int(cls)] in ['crosswalk']:
							x1 = int(xyxy[0])
							# print(x1)
							y1 = int(xyxy[1])
							# print(y1)
							x2 = int(xyxy[2])
							# print(x2)
							y2 = int(xyxy[3])

							bounding_box = [x1, y1, x2, y2]
							bound.append(bounding_box)

		if box == True:
			return bound
		if img_n == True:
			cv2.rectangle(im0, (x1, y1), (x2, y2), (255, 255, 255), 2)
			output_path='outputs/test.png'
			cv2.imwrite(output_path, im0)
			return output_path
