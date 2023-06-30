import json

from flask import Flask, request, Response, jsonify
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

from flask import send_file
import skimage.io as io

from detect_template import run

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

# try:
#
#     weights= '/home/ce00145322/Downloads/yolov5/runs/train/exp7/weights/best.pt'
# except Exception as e:
#     logger.error(msg="model is not loaded")


@app.route('/box', methods=['POST', 'GET'])  # Single Api
def box():
    resp = Response(status=200, content_type='application/json')

    # image = request.files['file']

    try:

        if request.content_type != None:
            if request.content_type.startswith('multipart/form-data'):
                if 'file' in request.files.keys():
                    if (request.files['file'].filename.endswith('.jpg')) or (request.files['file'].filename.endswith('.png')) or (request.files['file'].filename.endswith('.jpeg')):
                        image = request.files['file']
                        img = io.imread(image)
                        io.imsave('API_DATA/box/test.png', img)

                        result= run(source='API_DATA/box', nosave=True, box=True)
                        # if len(result)>0:

                        if len(result) == 0:
                            print(len(result))
                            resp.status_code = 400
                            resp.response = json.dumps(
                                {"code": "400", "error": "No Face Detected"})
                            return resp
                        else:
                            # return jsonify(result)
                            resp = json.dumps(result)
                            return resp



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




@app.route('/label-box', methods=['POST', 'GET'])  # Single Api
def label():

    resp = Response(status=200, content_type='application/json')

    # image = request.files['file']

    try:

        if request.content_type != None:
            if request.content_type.startswith('multipart/form-data'):
                if 'file' in request.files.keys():

                    if (request.files['file'].filename.endswith('.jpg')) or (request.files['file'].filename.endswith('.png')) or (request.files['file'].filename.endswith('.jpeg')):
                        image = request.files['file']
                        img = io.imread(image)
                        io.imsave('API_DATA/box_label/test.png', img)

                        result= run(source='API_DATA/box_label', nosave=True, label_1=True)
                        # if len(result)>0:

                        if len(result) == 0:
                            # print(len(result))
                            resp.status_code = 400
                            resp.response = json.dumps(
                                {"code": "400", "error": "No Face Detected"})
                            return resp
                        else:
                            # return jsonify(result)
                            resp = json.dumps(result)
                            return resp



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


    #


@app.route('/img-box', methods=['POST', 'GET'])  # Single Api
def box_img():

    resp = Response(status=200, content_type='application/json')

    image = request.files['file']

    try:

        if request.content_type != None:
            if request.content_type.startswith('multipart/form-data'):
                if 'file' in request.files.keys():

                    if (request.files['file'].filename.endswith('.jpg')) or (
                    request.files['file'].filename.endswith('.png')) or (
                    request.files['file'].filename.endswith('.jpeg')):
                        image = request.files['file']
                        img = io.imread(image)
                        io.imsave('API_DATA/box_img/test.png', img)

                        result = run(source='API_DATA/box_img', nosave=True, img=True)
                        # if len(result)>0:

                        # if len(result) == 0:
                        #     print(len(result))
                        #     resp.status_code = 400
                        #     resp.response = json.dumps(
                        #         {"code": "400", "error": "No Face Detected"})
                        #     return resp
                        # else:
                            # return jsonify(result)
                        return send_file(result, mimetype='image/png')



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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)