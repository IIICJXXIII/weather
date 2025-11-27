from django.shortcuts import render
import pandas as pd
import numpy as np
from django.utils.safestring import mark_safe
from sqlalchemy import create_engine, text

# 1. 创建数据库连接
# 请确保 IP 地址是你的 Master 虚拟机 IP
engine = create_engine('mysql+pymysql://root:root@192.168.56.101:3306/china_all')
table_name = ['china_map', 'province_temp', 'province_pressure', 'city_temp', 'city_precipitation_top10']
sql_base = 'select * from '

# ==========================================
# 2. 读取并处理地图数据 (Map)
# ==========================================
sql = text(sql_base + table_name[0])
with engine.connect() as connect:
    map_data = pd.read_sql(sql, connect)

# 数据预处理
map_data['temp'] = np.round(map_data['temp'] / 10, 0)
map_data['wind_speed'] = np.round(map_data['wind_speed'] / 10, 0)
map_data['month'] = map_data['month'].astype(int)

# 获取纯 Python int 类型的月份列表
months = sorted([int(m) for m in map_data['month'].unique()])

map_data1 = dict()
map_data2 = dict()

for item in months:
    month_key = int(item)  # 确保 Key 是 int
    mydata = map_data[map_data['month'] == item]

    data_temp = []
    data_wind = []

    for i in mydata.index:
        # 气温数据
        dict_temp = {}
        dict_temp['name'] = str(mydata.loc[i, 'province'])
        dict_temp['value'] = float(mydata.loc[i, 'temp'])  # 强制转 float
        data_temp.append(dict_temp)

        # 风速数据
        dict_wind = {}
        dict_wind['name'] = str(mydata.loc[i, 'province'])
        dict_wind['value'] = float(mydata.loc[i, 'wind_speed'])  # 强制转 float
        data_wind.append(dict_wind)

    map_data1[month_key] = data_temp
    map_data2[month_key] = data_wind

# ==========================================
# 3. 读取并处理折线图数据 (Line Chart)
# ==========================================
sql = text(sql_base + table_name[1])
with engine.connect() as connect:
    temp_province_data = pd.read_sql(sql, connect)

temp_province_data['temp'] = np.round(temp_province_data['temp'] / 10, 1)  # 保留1位小数更精确
temp_province_data['temp_forecast'] = np.round(temp_province_data['temp_forecast'], 1)

# 获取省份列表
provinces = [str(p) for p in temp_province_data['province'].unique()]

line_data = {}
for item in provinces:
    temp_dict = {}
    temp_province = temp_province_data[temp_province_data['province'] == item].sort_values('month')

    # 【关键修复】列表推导式强制转换类型
    temp_dict['month'] = [int(x) for x in temp_province['month'].values]
    temp_dict['temp'] = [float(x) for x in temp_province['temp'].values]
    temp_dict['temp_forecast'] = [float(x) for x in temp_province['temp_forecast'].values]

    line_data[item] = temp_dict

# ==========================================
# 4. 读取并处理矩形树图数据 (TreeMap)
# ==========================================
sql = text(sql_base + table_name[2])
with engine.connect() as connect:
    pressure_data = pd.read_sql(sql, connect)

pressure_data['month'] = pressure_data['month'].astype(int)
# 气压通常较大，除以10可能数值偏小，根据实际需求调整，这里保持原逻辑
# pressure_data['pressure'] = pressure_data['pressure'] / 10 

tree_data = dict()
for item in months:
    mydata = pressure_data[pressure_data['month'] == item]
    pressure_month = []
    for i in mydata.index:
        pressure = dict()
        pressure['name'] = str(mydata.loc[i, 'province'])
        pressure['value'] = float(mydata.loc[i, 'pressure'])  # 强制转 float
        pressure_month.append(pressure)
    tree_data[int(item)] = pressure_month

# ==========================================
# 5. 读取并处理词云数据 (WordCloud)
# ==========================================
sql = text(sql_base + table_name[3])
with engine.connect() as connect:
    city_temp_data = pd.read_sql(sql, connect)

city_temp_data['temp'] = city_temp_data['temp'] / 10
city_temp_data = city_temp_data.dropna()
city_temp_data['month'] = city_temp_data['month'].astype(int)

word_data = dict()
for item in months:
    mydata = city_temp_data[city_temp_data['month'] == item]
    temp_month = []
    for i in mydata.index:
        temperature = dict()
        temperature['name'] = str(mydata.loc[i, 'city'])
        temperature['value'] = float(mydata.loc[i, 'temp'])  # 强制转 float
        temp_month.append(temperature)
    word_data[int(item)] = temp_month

# ==========================================
# 6. 读取并处理柱状图数据 (Bar Chart)
# ==========================================
sql = text(sql_base + table_name[4])
with engine.connect() as connect:
    precipitation_data = pd.read_sql(sql, connect)

precipitation_data['month'] = precipitation_data['month'].astype(int)
precipitation_data['precipitation_6'] = precipitation_data['precipitation_6'] / 10

bar_data = dict()
for item in months:
    # 取出当月数据并排序（降水从多到少）
    mydata = precipitation_data[precipitation_data['month'] == item].sort_values('precipitation_6', ascending=True)

    precipitation_month = {}
    # 【关键修复】强制转换列表中的元素
    precipitation_month['city'] = [str(x) for x in mydata['city'].values]
    precipitation_month['precipitation'] = [float(x) for x in mydata['precipitation_6'].values]

    bar_data[int(item)] = precipitation_month


# ==========================================
# 7. 视图函数
# ==========================================

def map_sample(request):
    return render(request, '地图对照模板.html')


def login(request):
    # 将所有数据通过 mark_safe 传递给模板，防止 HTML 转义
    # 这里的字典已经是纯 Python 类型，可以直接被 Django 模板渲染为合法的 JS 对象
    return render(request, 'index.html',
                  {'map_data1': mark_safe(map_data1),
                   'map_data2': mark_safe(map_data2),
                   'months': mark_safe(months),
                   'provinces': mark_safe(provinces),
                   'line_data': mark_safe(line_data),
                   'tree_data': mark_safe(tree_data),
                   'word_data': mark_safe(word_data),
                   'bar_data': mark_safe(bar_data),
                   })