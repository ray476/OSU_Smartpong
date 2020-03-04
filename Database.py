import psycopg2
import pandas as pd
import _pickle as pickle


def establishConnection():
    try:
        connection = psycopg2.connect(
            host = 'osu-smartpong-db.coppbwdukw7p.us-east-2.rds.amazonaws.com',
            port = 5432,
            user = 'smartpong',
            password = 'jvg08tgCZhWBnlEa2Qj9',
            database = 'smartpong_db'
            )
    except:
        print('unable to connect')
    return connection


# given the connection and the model_name (primary key of model table), retrieve the parameters and pickle associated
# with that model, used when continuing from a checkpoint
def resumeCheckpoint(model_name, conn):
    cursor = conn.cursor()
    sql = """SELECT *
        FROM Model
        WHERE name = %s"""
    data = (model_name,)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    params = row[2:]
    cursor.close()
    return row


# takes name, params used, and the model itself and inserts them as a new row, after converting the model to a
# binary large object (bytea type in postgreSQL).  Used when a new model has been created
def insertModel(model_name, hyper_params, model, conn):
    cursor = conn.cursor()
    sql = """INSERT INTO Model
    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    blob = pickle.dumps(model)
    data = (model_name, blob, hyper_params[0], hyper_params[1], hyper_params[2], hyper_params[3], hyper_params[4])
    try:
        cursor.execute(sql, data)
    except:
        # if the insert fails, create a .p file and save
        pickle.dump(model, open(model_name, 'wb'))
        print('insert failed, pickle file of model saved locally')
    conn.commit()
    cursor.close()


