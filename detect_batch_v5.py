"""
This script is run as a child process to avoid request time-outs using celery.
A different instance of the model is loaded for every child.
Celery might have an issue with deallocation of GPU memory used by tensorflow. Might also be an issue from TF itself.
Replace this architecture with tensorflow serving instance instead, if possible.
"""
import os
import time
import gc
import psycopg2
import sys
# import populate_v3
import numpy as np
import pandas as pd
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
from datetime import datetime
# import models
# from utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
""""detect_batch_v5.py is implementing two models at the same time
    To revert to single model process use detect_batch_v4.py """
os.makedirs('./Logs/Detect_Batch/', exist_ok=True)
handler = TimedRotatingFileHandler('Logs/Detect_Batch/log-detect_batch', when='MIDNIGHT', backupCount=7)
formatter = Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')
logger = logging.getLogger('__name__')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

def detect_batch(image_path, data_table):

    """
    Function to detect objects in a complete path and add the objects to DB
    :param self: self instance. Needed to create child process
    :param need: Type of object to detect
    :param image_path: Path of images
    :param table_name: Table name corresponding to path
    :param skip: Index of image till which to skip
    :return:
    JSON with  {'current': i, 'total': total, 'status': status } format

    """
    batch_connect2 = "dbname='AI_ML_HUB' user='postgres' host='10.10.21.84' " + "password='postgres'"
    try:
        import keras
        import tensorflow as tf

    except ImportError:
        raise ImportError

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    sess_batch = tf.Session(config=config)
    sess_batch.run(tf.global_variables_initializer())
    keras.backend.tensorflow_backend.set_session(sess_batch)
    total=0
    # Load model based on object type required
    try:
        conn = psycopg2.connect(batch_connect2)
        cursor = conn.cursor()

        model_path_1 = 'model1/final_model_95.h5'
        df_class_1 = pd.read_csv('model1/classes.csv')


        model_path = 'model2/TSDR_resnet50_csv_42.h5'
        df_class = pd.read_csv('model2/classes.csv')


        # load retinanet model for prediction using CPU/GPU
        global model_batch
        model_batch = models.load_model(model_path, backbone_name='resnet50')

        global model_batch_1
        model_batch_1 = models.load_model(model_path_1, backbone_name='resnet50')

        global graph_batch
        graph_batch = tf.get_default_graph()

        global graph_batch_1
        graph_batch_1 = tf.get_default_graph()
        # graph_batch.finalize()

        global labels_to_names
        # load label to names mapping for visualization purposes
        labels_to_names = dict(zip(list(df_class.No), list(df_class.Label)))

        global labels_to_names_1
        # load label to names mapping for visualization purposes
        labels_to_names_1 = dict(zip(list(df_class_1.No), list(df_class_1.Label)))
        print(image_path)
        total = len(os.listdir(image_path))

        image_list=os.listdir(image_path)
        image_list.sort()
        # print("skip",skip)
        df=pd.DataFrame(columns=['file_name', 'label'])
        print('models loaded')
        for i, image_name in enumerate(image_list):
            print(image_name)
            try:
                image = read_image_bgr(os.path.join(image_path, image_name))
                image = preprocess_image(image)
                image, scale = resize_image(image)

                with graph_batch.as_default():
                    boxes, scores, labels = model_batch.predict_on_batch(np.expand_dims(image, axis=0))
                    # print(boxes,scores,labels)
                with graph_batch_1.as_default():
                    boxes_1, scores_1, labels_1 = model_batch_1.predict_on_batch(np.expand_dims(image, axis=0))
                    # print(boxes,scores,labels)

                # correct for image scale
                boxes /= scale
                boxes_1 /=scale
                object_boxes = []
                labels_to_names[-1] = 'background'
                labels_to_names_1[-1] = 'background'
                lat, long, heading,timing = 0, 0, 0,''
                for box, score, label in zip(boxes[0], scores[0], labels[0]):
                    if score > 0.5:
                        # convert boc co-ordinates to int
                        b = box.astype(int).tolist()
                        desc = ''
                        sign = 0
                        label1 = labels_to_names[label]
                        cursor.execute("select Description from catalog.traffic_sign_description where Annotation_label='{label}'".
                            format(label=label1))
                        desc_data = cursor.fetchone()
                        if (desc_data == None):
                            desc = label1
                            # sign = 0

                        else:
                            if (desc_data[0] != None):
                                desc = desc_data[0]
                                # sign = desc_data[1]
                            else:
                                desc = label1
                                # sign = 0
                        if (desc != 'NA'):
                            df.loc[len(df.index)] = [image_name, label1]
                            pass
                            cursor.execute('''INSERT INTO data.{table_name} (image_name, model,bbox1, obj_class) VALUES('{image_name}','TSDR', '{b}',
                                            '{label}')'''.format(table_name=data_table, label=desc,b=b,image_name=image_name))
                        else:
                            logger.error(
                                msg='Data not available for image'+image_name )

                for box_x, score_x, label_x in zip(boxes_1[0], scores_1[0], labels_1[0]):
                    if score_x > 0.6:
                        # convert boc co-ordinates to int
                        b = box_x.astype(int).tolist()
                        desc = ''
                        sign = 0
                        label2 = labels_to_names_1[label_x]
                        if label2 in ["speed_limit_2", "speed_limit_3", "speed_limit_1", "towing_zone",
                                    "toilet_ahead", "road_closed"]:
                            print(image_name, label2)

                            cursor.execute(
                                "select Description, Sign_type from catalog.traffic_sign_description where Annotation_label='{label}'".
                                format(label=label2))
                            desc_data = cursor.fetchone()
                            if (desc_data == None):
                                desc = label2
                                sign = 0

                            else:
                                if (desc_data[0] != None):
                                    desc = desc_data[0]
                                    # sign = desc_data[1]
                                else:
                                    desc = label2
                                    sign = 0
                            if (desc != 'NA'):
                                # print('insert NA')
                                df.loc[len(df.index)] = [image_name, label2]
                                pass
                                cursor.execute('''INSERT INTO data.{table_name} (image_name, model,bbox1, obj_class) VALUES('{image_name}','TSDR', '{b}',
                                            '{label}')'''.format(table_name=data_table,label=desc, b=b, image_name=image_name))
                            else:
                                logger.error(
                                    msg='Data not available for image'+image_name )

                    cursor.execute(
                        "UPDATE catalog.ai_process_log SET processed_image={i} WHERE data_table='{table_name}'".format(
                            i=i + 1, table_name=data_table))
                    conn.commit()
            except Exception as e:
                logger.error(
                    msg='Exception occurred\t' + str(e) + '\tTraceback\t' + '~'.join(
                        str(traceback.format_exc()).split('\n')))
    except Exception as e:
        logger.error(
            msg='Exception occurred\t' + str(e) + '\tTraceback\t' + '~'.join(str(traceback.format_exc()).split('\n')))

        raise e

    finally:
        # Clear session
        keras.backend.tensorflow_backend.clear_session()
        if(model_batch!=None):
            del model_batch
            gc.collect()
            conn.close()
        else:
            print('interrupt')
            # When path is interrupted
            conn.commit()
            conn.close()

if __name__ == '__main__':
    detect_batch('/mnt/vol1/City_images_Execution/image_data', 'acs_delhi_industrial_area_22102021')


