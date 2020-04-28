import psycopg2
import pandas as pd
import _pickle as pickle
import numpy as np

show_columns_model = ['name', 'node_num', 'batch_size', 'learning_rate', 'gamma', 'decay']

def establishConnection():
    print('\nestablishing database connection ...')
    try:
        connection = psycopg2.connect(
            host = 'osu-smartpong-db.coppbwdukw7p.us-east-2.rds.amazonaws.com',
            port = 5432,
            user = 'smartpong',
            password = 'jvg08tgCZhWBnlEa2Qj9',
            database = 'smartpong_db'
            )
    except:
        print('unable to connect\n')
    print('connection successfully established\n')
    return connection


# given the connection and the model_name (primary key of model table), retrieve the parameters  associated
# with that model, used when continuing from a checkpoint
def retrieveParameters(model_name, conn):
    cursor = conn.cursor()
    sql = """SELECT node_num, batch_size, learning_rate, gamma, decay
        FROM Model
        WHERE name = %s"""
    data = (model_name,)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close()
    return row


def retrieveModel(model_name, conn):
    cursor = conn.cursor()
    sql = """SELECT pickle
         FROM Model
         WHERE name = %s"""
    data = (model_name,)
    cursor.execute(sql, data)
    row = cursor.fetchall()
    for each in row:
        ## The result is also in a tuple
        for pickledStoredModel in each:
            ## Unpickle the stored string
            unpickledModel = pickle.loads(pickledStoredModel)
            ## compare with original
    cursor.close()
    print('model loaded from database successfully')
    return unpickledModel


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


def updateModel(model, model_name, conn):
    cursor = conn.cursor()
    blob = pickle.dumps(model)
    sql = """UPDATE Model
        SET pickle = %s
        WHERE name = %s"""
    data = (blob, model_name)
    # cursor.execute(sql, data)
    try:
        cursor.execute(sql, data)
    except:
        model_name = model_name + '.p'
        pickle.dump(model, open(model_name, 'wb'))
        print('update failed, pickle file of model saved locally')
    conn.commit()
    cursor.close()


def showTables(conn):
    sql = """
    SELECT "table_name","column_name", "data_type", "table_schema"
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE "table_schema" = 'public'
    ORDER BY table_name  
    """
    print(pd.read_sql(sql, con=conn))


def showModels(conn):
    sql2 = """
    SELECT * FROM model
    """
    print(pd.read_sql(sql2, con=conn, index_col=show_columns_model))


# used for inserting files into a database without the file name in the file
def insertData(conn, model_name, file_name):
    cursor = conn.cursor()
    file = open(file_name, 'r')
    file_arr = np.loadtxt(file)
    for i in range(file_arr.shape[0]):
        sql = """
            INSERT INTO Data
            VALUES (%s, %s, %s)"""
        ep = int(file_arr[i][0])
        reward = int(file_arr[i][1])
        data = (model_name, ep, reward)
        cursor.execute(sql, data)
    conn.commit()
    cursor.close()