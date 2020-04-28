import psycopg2
import pandas as pd
import _pickle as pickle
import numpy as np

show_columns_model = ['name', 'node_num', 'batch_size', 'learning_rate', 'gamma', 'decay']


class Database:
    def __init__(self):
        print('\nestablishing database connection ...')
        try:
            self.connection = psycopg2.connect(
                host='osu-smartpong-db.coppbwdukw7p.us-east-2.rds.amazonaws.com',
                port=5432,
                user='smartpong',
                password='jvg08tgCZhWBnlEa2Qj9',
                database='smartpong_db'
            )
        except:
            print('unable to connect\n')
        print('connection successfully established\n')

    # given the connection and the model_name (primary key of model table), retrieve the parameters  associated
    # with that model, used when continuing from a checkpoint
    def retrieveParameters(self, model_name):
        cursor = self.connection.cursor()
        sql = """SELECT node_num, batch_size, learning_rate, gamma, decay
            FROM Model
            WHERE name = %s"""
        data = (model_name,)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close()
        return row

    def retrieveModel(self, model_name):
        cursor = self.connection.cursor()
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
    def insertModel(self, model_name, hyper_params, model):
        cursor = self.connection.cursor()
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
        self.connection.commit()
        cursor.close()

    def updateModel(self, model, model_name):
        cursor = self.connection.cursor()
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
        self.connection.commit()
        cursor.close()

    def showTables(self):
        sql = """
        SELECT "table_name","column_name", "data_type", "table_schema"
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE "table_schema" = 'public'
        ORDER BY table_name  
        """
        print(pd.read_sql(sql, con=self.connection))

    def showModels(self):
        sql2 = """
        SELECT * FROM model
        """
        print(pd.read_sql(sql2, con=self.connection, index_col=show_columns_model))

    # used for inserting files into a database
    def insertData(self, model_name, file_name):
        cursor = self.connection.cursor()
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
        self.connection.commit()
        cursor.close()

    # retrieves the last episode number of a resumed model
    def lastEpisode(self, model_name):
        cursor = self.connection.cursor()
        sql = """
        SELECT MAX(episode_num)
        FROM data
        WHERE %s"""
        data = (model_name,)
        cursor.execute(sql, data)
        result = cursor.fetchall()
        ep_num = result[0][0]
        print('resuming model {} from episode {}'.format(model_name, ep_num))
        return ep_num
