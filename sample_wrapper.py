from datetime import datetime
import time
# from detect_template import run
# from detect_batch_v5 import detect_batch
from detect_batch_yolo import run
import psycopg2
import os

batch_connect2 = "dbname='AI_ML_HUB' user='postgres' host='10.10.21.84' " + "password='postgres'"

# class SBDR_Wrapper:
timing=10
Model_name='general_objects'


def TSDR_Wrapper():
    try:
        conn = psycopg2.connect(batch_connect2)
        cursor = conn.cursor()
        print(conn)
        while True:
            # print("check", datetime.now().strftime("%H:%M:%S"))
            print("select folder_path,description from catalog.ai_process_queue where model_name='{model}' and remarks='' order by req_date limit 1".format(model=Model_name))
            #
            # print("select folder_path,description from catalog.ai_process_queue where model_name='{model}' order by req_date limit 1".format(model=Model_name))
            cursor.execute("select folder_path,description from catalog.ai_process_queue where model_name='{model}' and remarks='' order by req_date limit 1".format(model=Model_name))
            q_data = cursor.fetchone()
            if (q_data != None):
                print("process found", q_data)
                folder_path = q_data[0]
                description = q_data[1]
                if not os.path.exists(folder_path):
                    print("update catalog.ai_process_queue set remarks='Folder path does not exists' where folder_path='{folder_path}' and model_name='{model}'  ".format(
                            model=Model_name, folder_path=folder_path,description=description))
                    cursor.execute(
                        "update catalog.ai_process_queue set remarks='Folder path does not exists' where folder_path='{folder_path}' and model_name='{model}' ".format(
                            model=Model_name, folder_path=folder_path))

                # Check if path exists in DB
                else:
                    data_list=os.listdir(folder_path)
                    if(len(data_list)==0):
                        cursor.execute(
                            "update catalog.ai_process_queue set remarks='Folder path is empty' where folder_path='{folder_path}' and model_name='{model}' ".format(
                                model=Model_name, folder_path=folder_path))
                    else:
                        print("select * from catalog.ai_process_log where model_name='{Model_name}' and  data_table='{data_table}'".format(Model_name=Model_name, data_table=description))
                        cursor.execute("select * from catalog.ai_process_log where model_name='{Model_name}' and  data_table='{data_table}'".format(Model_name=Model_name, data_table=description))
                        flag2=cursor.fetchall()
                        print(flag2)
                        if(len(flag2)==0):
                            print("insert into catalog.ai_process_log (folder_path, model_name,process_date,start_time,total_images,processed_image,description,data_table) values('{folder_path}','{model_name}','{t_date}','{s_time}',{total_images},0,'{desc}','{data_table}') ".format( \
                                            model_name=Model_name,t_date=datetime.now().date(),s_time=datetime.now().time(),total_images=len(data_list),desc=description,data_table=description,folder_path=folder_path))
                            cursor.execute("insert into catalog.ai_process_log (folder_path,model_name,process_date,start_time,total_images,processed_image,description,data_table) values('{folder_path}','{model_name}','{t_date}','{s_time}',{total_images},0,'{desc}','{data_table}') ".format( \
                                            model_name=Model_name,t_date=datetime.now().date(),s_time=datetime.now().time(),total_images=len(data_list),desc=description,data_table=description,folder_path=folder_path))
                            print("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'data' AND table_name ='{data_table}')".format(data_table=description))
                            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'data' AND table_name ='{data_table}')".format(data_table=description))
                            flag = cursor.fetchone()
                            print(flag[0])
                            if(flag[0]==False):
                                print("create table data.{data_table} (Image_name varchar,model varchar, obj_class varchar, bbox1 varchar,bbox2 varchar, text_data varchar, latitude float, longitude float, eloc int)".format(data_table=description))
                                cursor.execute("create table data.{data_table} (Image_name varchar,model varchar, obj_class varchar, bbox1 varchar,bbox2 varchar, text_data varchar, latitude float, longitude float, eloc int)".format(data_table=description))
                        # except Exception as e:
                            else:
                                print('already exists')
                            cursor.execute("delete from catalog.ai_process_queue where folder_path='{folder_path}' and model_name='{model}' ".format(model=Model_name, folder_path=folder_path))
                            # print('call the detection')
                            conn.commit()
                            conn.close()
                            # detect_batch(folder_path, description)
                            # print("oooooooooo",folder_path, description)
                            run(source=folder_path, data_table=description)
                            conn = psycopg2.connect(batch_connect2)
                            cursor = conn.cursor()
                            cursor.execute(
                                "update catalog.ai_process_log set end_time='{end_time}' where folder_path='{folder_path}' and model_name='{model}' ".format(
                                    model=Model_name, folder_path=folder_path,end_time=datetime.now().time()))

                        else:
                            cursor.execute("update catalog.ai_process_queue set remarks='Already Executed' where folder_path='{folder_path}' and model_name='{model}' ".format(
                                model=Model_name, folder_path=folder_path))
                            conn.commit()
                            conn.close()
            else:
                print("checked", datetime.now())
            # conn.commit()
            time.sleep(timing)
    except Exception as e:
        print(e)
        conn.close()



if __name__ == '__main__':
    TSDR_Wrapper()