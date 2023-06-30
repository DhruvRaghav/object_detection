from detect_template import run
import sys
from pathlib import Path
import os
from PIL import Image
import psycopg2

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

image1, boxes = run(source='/home/ceinfo/Downloads/auto.jpg', project=ROOT, both=True)
print(image1, boxes)

image = Image.open(image1)

# Create a bounding box
bbox = boxes[3]['person']
print(bbox)

# Crop the image
cropped_image = image.crop(bbox)

# Save the cropped image
cropped_image.save('cropped_image.jpg')


def detect(img_path, data_table):

    batch_connect2 = "dbname='AI_ML_HUB' user='postgres' host='10.10.21.84' " + "password='postgres'"
    conn = psycopg2.connect(batch_connect2)
    cursor = conn.cursor()

    image1, boxes = run(source='/home/ceinfo/Downloads/auto.jpg', project=ROOT, both=True)

    cursor.execute('''INSERT INTO data.{table_name} (image_name, model,bbox1, obj_class) VALUES('{image_name}','TSDR', '{b}',
                                                '{label}')'''.format(table_name=data_table, label=desc, b=b,
                                                                     image_name=image_name))
    cursor.execute(
        "UPDATE catalog.ai_process_log SET processed_image={i} WHERE data_table='{table_name}'".format(
            i=i + 1, table_name=data_table))
