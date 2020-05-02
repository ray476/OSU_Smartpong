import psycopg2
import pandas as pd
import _pickle as pickle
import Database

# to drop test tables, add the real tables and add some data
# establish connection create cursor
connection = Database.establishConnection()
cursor = connection.cursor()
Database.showTables(connection)
# drop tables
# cursor.execute("""DROP TABLE data""")
# cursor.execute("""DROP TABLE testpickle""")
# cursor.execute("""DROP TABLE testtable""")
# connection.commit()
# check results
# print('drops done')
# Database.showTables(connection)

# cursor.execute("""CREATE TABLE Models(
#     name varchar(32) PRIMARY KEY,
#     pickle bytea,
#     node_num int,
#     batch_size int,
#     learning_rate real,
#     gamma real,
#      decay real)""")
# cursor.execute("""CREATE TABLE data(
#     model_name varchar(32)  REFERENCES models(name),
#     episode_num int,
#     reward int)""")
# connection.commit()
# again check result
# print('tables created')
# Database.showTables(connection)
# create values to pass to insert model
H = 300  # number of hidden layer neurons
batch_size = 7  # every how many episodes to do a param update?
learning_rate = 5e-4
gamma = 0.99  # discount factor for reward
decay_rate = 0.99  # decay factor for RMSProp leaky sum of grad^2
hyper_params = [H, batch_size, learning_rate, gamma, decay_rate]
model = pickle.load(open('./first_model/save1.p', 'rb'))
name = 'first_model'
# Database.insertModel(name, hyper_params, model, connection)
connection.commit()

# add data to table
# with open('./first_model./new_results_copy.txt', 'r') as row:
#     cursor.copy_from(row, 'save1_data', sep=' ')
# with open('./better_batch_testing/20-batch.txt', 'r') as row:
#     cursor.copy_from(row, 'data', sep=' ')

# read data
# sql2 = """
# SELECT * FROM data
# """
# print(pd.read_sql(sql2, con=connection))

Database.showModels(connection)
connection.commit()
connection.close()
cursor.close()

