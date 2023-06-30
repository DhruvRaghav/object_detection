import json

from flask import Flask, request, Response, jsonify
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import requests
from flask import send_file
import skimage.io as io

from solar_detect import run
# from geojson_convt import tif_maker, geojson5
import base64

import os

if not (os.path.exists('Logs')):
    os.makedirs('Logs/', exist_ok=False)
log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
handler = TimedRotatingFileHandler('Logs/' + log_filename, when='MIDNIGHT', backupCount=7)

formatter = Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')

logger = logging.getLogger('gunicorn.error')

handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

logger.setLevel(logger.level)
logger.addHandler(handler)

logger.propagate = False

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/solar_detection_mGIS_aiml', methods=['POST', 'GET'])  # Single Api
def label():
    resp = Response(status=200, content_type='application/json')

    try:

        if request.content_type is not None:
            if request.content_type.startswith('multipart/form-data'):
                if 'file' in request.files.keys():

                    if (request.files['file'].filename.endswith('.jpg')) or (
                            request.files['file'].filename.endswith('.png')) or (
                            request.files['file'].filename.endswith('.jpeg') or
                            request.files['file'].filename.endswith('.bmp')):
                        image = request.files['file']
                        print(request.files)
                        bounds = request.form['bounds']
                        print("bounds  ", bounds)
                        img = io.imread(image)
                        io.imsave('/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.png',
                                  img)
                        result = run(
                            source='/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.png',
                            nosave=True, box=True)

                        """ Calling GDAL Library API """
                        url = "http://10.10.21.228:5099/gdal_utils"
                        headers = {}
                        files = []
                        # bounds = '{"_southWest": {"lat": 28.574572543440226, "lng": 77.22573280334474},"_northEast": {"lat": 28.603512986817798, "lng": 77.26242542266847}}'

                        # file_path = '/home/ceinfo/Downloads/ortho/10m_1.png'
                        file_path = '/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.png'

                        # coords = '[[1044, 126, 1075, 148], [961, 202, 991, 224], [682, 243, 776, 308], [1052, 143, 1085, 166],[1031, 88, 1063, 112]]'
                        coords = str(result)
                        print("bounds in solar ", bounds)
                        payload = {'bounds': bounds, 'file_path': file_path, 'coords': coords}
                        response = requests.post(url, headers=headers, data=payload, files=files)
                        print(response.text)
                        return response.text
                        # return result

                    else:
                        resp.status_code = 400
                        resp.response = json.dumps(
                            {"code": "400", "error": "Invalid Image file."})
                        return resp

                else:
                    resp.status_code = 400
                    resp.response = json.dumps({"code": "400", "error": "file parameter missing"})
                    return resp

            else:
                resp.status_code = 400
                return resp

        else:
            resp.status_code = 400
            resp.response = json.dumps({"code": "400", "error": "file Parameter not available"})
            return resp

    except Exception as e:
        logger.error(msg=str(e), status_code=500)
        resp.status_code = 500
        return resp


@app.route('/solar_detection_tiff', methods=['POST', 'GET'])  # Single Api
def tiff():
    resp = Response(status=200, content_type='application/json')

    try:

        if request.content_type is not None:
            if request.content_type.startswith('multipart/form-data'):
                if 'file' in request.files.keys():

                    if request.files['file'].filename.endswith('.tif') or request.files['file'].filename.endswith(
                            '.tiff'):
                        image = request.files['file']
                        # bounds = request.form['bounds']
                        # print("bounds  ",bounds)
                        image.save('/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.jpeg')
                        result = run(
                            source='/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.jpeg',
                            nosave=True, box=True)

                        """ Calling GDAL Library API """
                        url = "http://10.10.21.228:5099/gdal_utils_tiff"
                        headers = {}
                        files = []
                        # bounds = '{"_southWest": {"lat": 28.574572543440226, "lng": 77.22573280334474},"_northEast": {"lat": 28.603512986817798, "lng": 77.26242542266847}}'

                        # file_path = '/home/ceinfo/Downloads/ortho/10m_1.png'
                        file_path = '/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.jpeg'

                        # coords = '[[1044, 126, 1075, 148], [961, 202, 991, 224], [682, 243, 776, 308], [1052, 143, 1085, 166],[1031, 88, 1063, 112]]'
                        coords = str(result)
                        # print("bounds in solar ",bounds)
                        payload = {'file_path': file_path, 'coords': coords}
                        response = requests.post(url, headers=headers, data=payload, files=files)
                        print(response.text)
                        return response.text
                        # return result

                    else:
                        resp.status_code = 400
                        resp.response = json.dumps(
                            {"code": "400", "error": "Invalid Image file."})
                        return resp

                else:
                    resp.status_code = 400
                    resp.response = json.dumps({"code": "400", "error": "file parameter missing"})
                    return resp

            else:
                resp.status_code = 400
                return resp

        else:
            resp.status_code = 400
            resp.response = json.dumps({"code": "400", "error": "file Parameter not available"})
            return resp

    except Exception as e:
        logger.error(msg=str(e), status_code=500)
        resp.status_code = 500
        return resp


@app.route('/solar_panel_detection', methods=['POST', 'GET'])  # Single Api
def solar():
    resp = Response(status=200, content_type='application/json')

    try:

        if request.content_type is not None:
            print(request.content_type)

            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application'
                                                                                                         '/x-www-form'
                                                                                                         '-urlencoded'):
                if 'file' in request.files.keys():

                    file = request.files['file']

                    if (request.files['file'].filename.endswith('.jpg')) or (
                            request.files['file'].filename.endswith('.png')) or (
                            request.files['file'].filename.endswith('.jpeg') or
                            request.files['file'].filename.endswith('.bmp')):
                        image = request.files['file']
                        # bounds = request.form['bounds']
                        # print("bounds  ",bounds)
                        img = io.imread(image)
                        io.imsave('/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.png',
                                  img)
                        result = run(
                            source='/mnt/vol1/Deployment_Project/Yolo_Projects/yolov_apis/API_DATA/box_label/test.png',
                            nosave=True, box=True)

                        """ Calling GDAL Library API """
                        url = "http://10.10.21.228:5099/pixel_utils"
                        headers = {}
                        files = []

                        coords = str(result)

                        payload = {'coords': coords}
                        response = requests.post(url, headers=headers, data=payload, files=files)
                        print(response.text)
                        return response.text

                    else:
                        resp.status_code = 400
                        resp.response = json.dumps(
                            {"code": "400", "error": "Invalid Image file."})
                        return resp

                else:
                    resp.status_code = 400
                    resp.response = json.dumps({"code": "400", "error": "file parameter missing"})
                    return resp

            else:
                resp.status_code = 400
                return resp

        else:
            resp.status_code = 400
            resp.response = json.dumps({"code": "400", "error": "file Parameter not available"})
            return resp

    except Exception as e:
        logger.error(msg=str(e), status_code=500)
        resp.status_code = 500
        return resp


# @app.route('/solar_draw', methods=['POST', 'GET'])  # Single Api
# def box_img():
#     resp = Response(status=200, content_type='application/json')
#
#     try:
#
#         if request.content_type is not None:
#             if request.content_type.startswith('multipart/form-data'):
#                 if 'file' in request.files.keys():
#
#                     if (request.files['file'].filename.endswith('.jpg')) or (
#                             request.files['file'].filename.endswith('.png')) or (
#                             request.files['file'].filename.endswith('.jpeg')):
#                         image = request.files['file']
#                         print(image)
#                         img = io.imread(image)
#                         io.imsave('API_DATA/box_img/test.png', img)
#
#                         result = run(source='API_DATA/box_img', nosave=True, img=True)
#
#                         # return send_file(result, mimetype='image/png')
#                         with open(result, "rb") as image2string:
#                             converted_string = base64.b64encode(image2string.read())
#                         # print(len(converted_string))
#                         return converted_string
#
#                     else:
#                         resp.status_code = 400
#                         resp.response = json.dumps(
#                             {"code": "400", "error": "Invalid Image file."})
#                         return resp
#
#                 else:
#                     resp.status_code = 400
#                     resp.response = json.dumps({"code": "400", "error": "file parameter missing"})
#                     return resp
#
#             else:
#                 resp.status_code = 400
#                 return resp
#
#         else:
#             resp.status_code = 400
#             resp.response = json.dumps({"code": "400", "error": "file Parameter not available"})
#             return resp
#
#     except Exception as e:
#         logger.error(msg=str(e), status_code=500)
#         resp.status_code = 500
#         return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=False)
