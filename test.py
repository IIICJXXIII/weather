import pandas as pd
# import pymysql
from sqlalchemy import create_engine,text

# connect=pymysql.connect(host='localhost',user='root',password='123',database='china_all',port=3306)
# cursor=connect.cursor()
# sql='select * from china_map'
# cursor.execute(sql)
# map_data=cursor.fetchall()
# connect.close()
# print(map_data)

engine=create_engine('mysql+pymysql://root:123@localhost:3306/china_all')
sql=text('select * from china_map')
connect = engine.connect()
all_data=pd.read_sql(sql,connect)
print(all_data.info())
# print(all_data)
sql=text('select * from province_temp')
connect = engine.connect()
all_data1=pd.read_sql(sql,connect)
print(all_data1.info())
# print(all_data1)