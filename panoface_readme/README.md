[<img align = 'right' src="https://about.mappls.com/images/mappls-b-logo.svg" height="60" /> ](https://www.mapmyindia.com/api)

<br>


# <div align = "center"> Panaroma - Face Detection & Blurring 

## Introduction
Automated Face Detection and Blurring in Panorama street view images. 

## Installation 

It is recommended to create a virtual environment first using  Anaconda package manager.
```sh
conda create -n face python=3.7
```
### Installing Dependencies using PIP 

```sh
pip install -r requirements.txt
```

## Inference
For custom inference on a local folder tune input parameteres in inference.py acccordingly.

```sh
python inference.py --source ./images-folder-path
```

## API Deployment ##

To Run the API locally

```sh
python pano_face_api.py
```

**Input Type :**  Image (.jpg/.png) - API needs a single input as an Image

**For Bounding Boxes output :**

```curl
     curl --location --request POST 'http://10.10.21.111:5004/face_pano_box' \
     --form 'file=@"/home/ceinfo/Downloads/SAMPLE_PANORAMA/GSAA9382.jpg"' 
```

**Output :**

     [[668, 1781, 1066, 2098], [2132, 1073, 2156, 1102], [662, 1786, 1068, 2097], [3787, 1103, 3817, 1133], [3698, 1068,
     3732, 1105], [3220, 887, 3247, 918], [1502, 1450, 1772, 1741], [2645, 972, 2739, 1067]]
<br>


**For Image with Face detected :**

```curl
     curl --location --request POST 'http://10.10.21.111:5004/face_pano_draw' \
     --form 'file=@"/home/ceinfo/Downloads/SAMPLE_PANORAMA/GSAA9382.jpg"'
```

**Output :**

![Bounding boxes drawn on faces](face_detect.png "Face Detections")



**For Image with Face Blurred :**

```curl
     curl --location --request POST 'http://10.10.21.111:5004/face_pano_blur' \
     --form 'file=@"/home/ceinfo/Downloads/SAMPLE_PANORAMA/GSAA9382.jpg"'
```
**Output :**

![](faceblur.png)
