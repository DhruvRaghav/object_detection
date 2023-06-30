import torch

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5m')  # or yolov5n - yolov5x6, custom

# Images
img = '/home/ceinfo/Downloads/For Vision Processing-20220927T041310Z-001/For Vision Processing/3c0335f4-4ca1-41ee-b578-9d716029a4d4.mp4'  # or file, Path, PIL, OpenCV, numpy, list

# Inference
results = model(img)

# Results
results.print()  # or .show(), .save(), .crop(), .pandas(), etc.