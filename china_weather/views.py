from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from sqlalchemy import create_engine, text

from .models import UserFavorite, UserProfile, BrowseHistory

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


# ==========================================
# 8. 读取省份历史数据（用于省份详情页）
# ==========================================
# 尝试读取历史数据表，如果不存在则跳过
province_history = {}
try:
    sql = text('select * from province_temp_all')
    with engine.connect() as connect:
        province_temp_all = pd.read_sql(sql, connect)
    
    province_temp_all['temp'] = np.round(province_temp_all['temp'] / 10, 1)
    province_temp_all['year'] = province_temp_all['year'].astype(int)
    province_temp_all['month'] = province_temp_all['month'].astype(int)
    
    # 按省份组织历史数据
    for province in provinces:
        pdata = province_temp_all[province_temp_all['province'] == province].copy()
        if len(pdata) == 0:
            continue
        
        # 构建年月气温数据
        history = {}
        for year in sorted(pdata['year'].unique()):
            year_data = pdata[pdata['year'] == year].sort_values('month')
            history[int(year)] = {
                'months': [int(m) for m in year_data['month'].values],
                'temps': [float(t) for t in year_data['temp'].values]
            }
        province_history[province] = history
except Exception as e:
    print(f"[WARNING] 读取 province_temp_all 表失败: {e}")
    print("[INFO] 省份详情页的历史数据功能将不可用")


def province_detail(request, province_name):
    """省份详情页视图函数"""
    # 检查省份是否存在
    if province_name not in provinces:
        from django.http import Http404
        raise Http404(f"省份 {province_name} 不存在")
    
    # 记录浏览历史
    record_browse_history(request.user, province_name)
    
    # 检查是否已收藏
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = UserFavorite.objects.filter(user=request.user, province=province_name).exists()
    
    # 获取该省份的折线图数据（月度温度）
    province_line = line_data.get(province_name, {})
    
    # 获取该省份的历史数据
    province_hist = province_history.get(province_name, {})
    
    # 获取该省份每月的气温数据（从 map_data1）
    temps = []
    for month_key in sorted(map_data1.keys()):
        for item in map_data1[month_key]:
            if item['name'] == province_name:
                temps.append(item['value'])
                break
    
    # 获取该省份每月的风速数据（从 map_data2）
    winds = []
    for month_key in sorted(map_data2.keys()):
        for item in map_data2[month_key]:
            if item['name'] == province_name:
                winds.append(item['value'])
                break
    
    # 获取该省份每月的气压数据（从 tree_data）
    pressures = []
    for month_key in sorted(tree_data.keys()):
        for item in tree_data[month_key]:
            if item['name'] == province_name:
                pressures.append(item['value'])
                break
    
    # 计算统计数据
    stats = {}
    if temps:
        stats['avg_temp'] = round(sum(temps) / len(temps), 1)
        stats['max_temp'] = max(temps)
        stats['min_temp'] = min(temps)
        stats['max_temp_month'] = temps.index(max(temps)) + 1
        stats['min_temp_month'] = temps.index(min(temps)) + 1
        stats['temp_range'] = round(max(temps) - min(temps), 1)
        
        # 计算全国排名
        all_province_avg = []
        for p in provinces:
            p_temps = []
            for month_key in sorted(map_data1.keys()):
                for item in map_data1[month_key]:
                    if item['name'] == p:
                        p_temps.append(item['value'])
                        break
            if p_temps:
                all_province_avg.append({'name': p, 'avg': sum(p_temps) / len(p_temps)})
        all_province_avg.sort(key=lambda x: x['avg'], reverse=True)
        for i, item in enumerate(all_province_avg):
            if item['name'] == province_name:
                stats['temp_rank'] = i + 1
                break
    else:
        stats['avg_temp'] = 0
        stats['max_temp'] = 0
        stats['min_temp'] = 0
        stats['max_temp_month'] = 1
        stats['min_temp_month'] = 1
        stats['temp_range'] = 0
        stats['temp_rank'] = '-'
    
    if winds:
        stats['avg_wind'] = round(sum(winds) / len(winds), 1)
        stats['max_wind'] = max(winds)
        stats['main_wind_dir'] = '偏北风'  # 模拟数据
        stats['wind_level'] = '2-3级'
    else:
        stats['avg_wind'] = 0
        stats['max_wind'] = 0
        stats['main_wind_dir'] = '-'
        stats['wind_level'] = '-'
    
    if pressures:
        stats['avg_pressure'] = round(sum(pressures) / len(pressures), 1)
        stats['pressure_stability'] = '稳定'
    else:
        stats['avg_pressure'] = 0
        stats['pressure_stability'] = '-'
    
    # 降水数据（模拟）
    stats['avg_rain'] = round(np.random.uniform(50, 150), 1)
    stats['total_rain'] = round(stats['avg_rain'] * 12, 1)
    stats['max_rain_month'] = np.random.randint(6, 9)
    stats['rain_type'] = '季风型'
    
    # 构建月度数据供图表使用
    monthly_data = {
        'months': ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        'avg_temps': temps if temps else [0] * 12,
        'max_temps': [t + np.random.uniform(2, 5) for t in temps] if temps else [0] * 12,
        'min_temps': [t - np.random.uniform(2, 5) for t in temps] if temps else [0] * 12,
    }
    
    # 构建历史数据供图表使用
    history_data = {'years': [], 'temps': []}
    if province_hist:
        for year in sorted(province_hist.keys()):
            year_temps = province_hist[year].get('temps', [])
            if year_temps:
                history_data['years'].append(year)
                history_data['temps'].append(round(sum(year_temps) / len(year_temps), 1))
    
    # 构建风向数据（模拟8个方向的风频）
    wind_data = {
        'values': [np.random.randint(10, 30) for _ in range(8)]
    }
    
    # 构建未来7天预报（模拟数据）
    forecast = []
    base_temp = stats['avg_temp'] if stats['avg_temp'] else 20
    weather_icons = ['☀️', '⛅', '🌤️', '🌥️', '☁️', '🌧️', '⛈️']
    for i in range(7):
        day_date = datetime.now() + timedelta(days=i)
        temp = round(base_temp + np.random.uniform(-5, 5), 1)
        forecast.append({
            'date': day_date.strftime('%m/%d'),
            'icon': np.random.choice(weather_icons),
            'temp': temp,
            'high': round(temp + np.random.uniform(3, 6), 0),
            'low': round(temp - np.random.uniform(3, 6), 0),
        })
    
    return render(request, 'province_detail.html', {
        'province': province_name,
        'provinces': json.dumps(provinces, ensure_ascii=False),
        'months': mark_safe(months),
        'monthly_data': json.dumps(monthly_data, ensure_ascii=False),
        'history_data': json.dumps(history_data, ensure_ascii=False),
        'wind_data': json.dumps(wind_data, ensure_ascii=False),
        'stats': stats,
        'forecast': forecast,
        'is_favorite': is_favorite,
        'active_page': 'province',
    })


# ==========================================
# 9. 省份列表页
# ==========================================
def province_list(request):
    """省份列表页 - 展示所有省份的概览"""
    # 计算每个省份的年均温度
    province_stats = []
    for province in provinces:
        temps = []
        winds = []
        for month_key, month_data in map_data1.items():
            for item in month_data:
                if item['name'] == province:
                    temps.append(item['value'])
                    break
        for month_key, month_data in map_data2.items():
            for item in month_data:
                if item['name'] == province:
                    winds.append(item['value'])
                    break
        
        avg_temp = round(sum(temps) / len(temps), 1) if temps else 0
        avg_wind = round(sum(winds) / len(winds), 1) if winds else 0
        max_temp = max(temps) if temps else 0
        min_temp = min(temps) if temps else 0
        
        province_stats.append({
            'name': province,
            'avg_temp': avg_temp,
            'avg_wind': avg_wind,
            'max_temp': max_temp,
            'min_temp': min_temp,
        })
    
    # 按年均温度排序
    province_stats.sort(key=lambda x: x['avg_temp'], reverse=True)
    
    return render(request, 'province_list.html', {
        'provinces': provinces,
        'province_stats': province_stats,
        'active_page': 'province',
    })


# ==========================================
# 10. 历史查询页
# ==========================================
def history_query(request):
    """历史数据查询页"""
    selected_province = request.GET.get('province', '')
    selected_month = request.GET.get('month', '')
    
    result_data = None
    if selected_province and selected_month:
        try:
            month_int = int(selected_month)
            # 获取该省份该月的数据
            temp_val = None
            wind_val = None
            pressure_val = None
            
            if month_int in map_data1:
                for item in map_data1[month_int]:
                    if item['name'] == selected_province:
                        temp_val = item['value']
                        break
            
            if month_int in map_data2:
                for item in map_data2[month_int]:
                    if item['name'] == selected_province:
                        wind_val = item['value']
                        break
            
            if month_int in tree_data:
                for item in tree_data[month_int]:
                    if item['name'] == selected_province:
                        pressure_val = item['value']
                        break
            
            result_data = {
                'province': selected_province,
                'month': month_int,
                'temp': temp_val,
                'wind': wind_val,
                'pressure': pressure_val,
            }
        except ValueError:
            pass
    
    return render(request, 'history_query.html', {
        'provinces': provinces,
        'months': months,
        'selected_province': selected_province,
        'selected_month': selected_month,
        'result_data': result_data,
        'active_page': 'history',
    })


# ==========================================
# 11. 数据对比页
# ==========================================
def compare(request):
    """多省份数据对比页"""
    selected_provinces = request.GET.getlist('provinces')
    
    compare_data = []
    if selected_provinces:
        for province in selected_provinces:
            if province in provinces:
                temps = []
                winds = []
                for month_key in months:
                    if month_key in map_data1:
                        for item in map_data1[month_key]:
                            if item['name'] == province:
                                temps.append(item['value'])
                                break
                    if month_key in map_data2:
                        for item in map_data2[month_key]:
                            if item['name'] == province:
                                winds.append(item['value'])
                                break
                
                compare_data.append({
                    'name': province,
                    'temps': temps,
                    'winds': winds,
                })
    
    return render(request, 'compare.html', {
        'provinces': provinces,
        'months': mark_safe(months),
        'selected_provinces': selected_provinces,
        'compare_data': mark_safe(compare_data),
        'active_page': 'compare',
    })


# ==========================================
# 12. 关于项目页
# ==========================================
def about(request):
    """关于项目页面"""
    return render(request, 'about.html', {
        'active_page': 'about',
    })


# ==========================================
# 13. 数据分析页 - 降水量趋势、极端天气统计等
# ==========================================
def analysis(request):
    """数据分析页 - 更多可视化"""
    
    # 1. 统计卡片数据
    stats = {}
    
    # 计算全国年均温度
    all_temps = []
    max_temp_info = {'temp': -100, 'province': '', 'month': 0}
    min_temp_info = {'temp': 100, 'province': '', 'month': 0}
    
    for month_key, month_data in map_data1.items():
        for item in month_data:
            all_temps.append(item['value'])
            if item['value'] > max_temp_info['temp']:
                max_temp_info = {'temp': item['value'], 'province': item['name'], 'month': month_key}
            if item['value'] < min_temp_info['temp']:
                min_temp_info = {'temp': item['value'], 'province': item['name'], 'month': month_key}
    
    stats['avg_temp'] = round(sum(all_temps) / len(all_temps), 1) if all_temps else 0
    stats['temp_change'] = round(0.3, 1)  # 模拟数据
    stats['max_temp'] = max_temp_info['temp']
    stats['max_temp_province'] = max_temp_info['province']
    stats['max_temp_month'] = max_temp_info['month']
    stats['min_temp'] = min_temp_info['temp']
    stats['min_temp_province'] = min_temp_info['province']
    stats['min_temp_month'] = min_temp_info['month']
    
    # 最大降水城市（从 bar_data 统计）
    city_rain = {}
    for month_key, month_data in bar_data.items():
        if 'city' in month_data and 'precipitation' in month_data:
            for i, city in enumerate(month_data['city']):
                if city not in city_rain:
                    city_rain[city] = 0
                city_rain[city] += month_data['precipitation'][i]
    
    if city_rain:
        max_rain_city = max(city_rain.items(), key=lambda x: x[1])
        stats['max_rain_city'] = max_rain_city[0]
        stats['max_rain_value'] = round(max_rain_city[1], 1)
    else:
        stats['max_rain_city'] = '-'
        stats['max_rain_value'] = 0
    
    # 最大风速省份
    max_wind_info = {'wind': 0, 'province': ''}
    for month_key, month_data in map_data2.items():
        for item in month_data:
            if item['value'] > max_wind_info['wind']:
                max_wind_info = {'wind': item['value'], 'province': item['name']}
    stats['max_wind'] = max_wind_info['wind']
    stats['max_wind_province'] = max_wind_info['province']
    
    # 2. 极端天气数据
    extreme_data = {}
    
    # 高温排行（月均温度最高的10个省份-月份组合）
    temp_records = []
    for month_key, month_data in map_data1.items():
        for item in month_data:
            temp_records.append({
                'province': item['name'],
                'month': month_key,
                'temp': item['value']
            })
    
    temp_records.sort(key=lambda x: x['temp'], reverse=True)
    extreme_data['hot_rank'] = temp_records[:10]
    
    # 低温排行
    temp_records.sort(key=lambda x: x['temp'])
    extreme_data['cold_rank'] = temp_records[:10]
    
    # 热力图数据 [月份索引, 省份索引, 温度值]
    heatmap_data = []
    province_list = sorted(provinces)
    for month_key, month_data in map_data1.items():
        for item in month_data:
            if item['name'] in province_list:
                province_idx = province_list.index(item['name'])
                heatmap_data.append([month_key - 1, province_idx, item['value']])
    
    extreme_data['heatmap_data'] = heatmap_data
    extreme_data['province_list'] = province_list
    
    # 3. 季节数据
    seasonal_data = {}
    
    # 计算各省份四季平均温度
    def get_season(month):
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    province_seasonal = {p: {'spring': [], 'summer': [], 'autumn': [], 'winter': []} for p in provinces}
    
    for month_key, month_data in map_data1.items():
        season = get_season(month_key)
        for item in month_data:
            if item['name'] in province_seasonal:
                province_seasonal[item['name']][season].append(item['value'])
    
    # 堆叠图数据
    stack_data = {}
    for province, seasons in province_seasonal.items():
        stack_data[province] = {
            'spring': round(sum(seasons['spring']) / len(seasons['spring']), 1) if seasons['spring'] else 0,
            'summer': round(sum(seasons['summer']) / len(seasons['summer']), 1) if seasons['summer'] else 0,
            'autumn': round(sum(seasons['autumn']) / len(seasons['autumn']), 1) if seasons['autumn'] else 0,
            'winter': round(sum(seasons['winter']) / len(seasons['winter']), 1) if seasons['winter'] else 0,
        }
    seasonal_data['stack_data'] = stack_data
    
    # 雷达图数据（选取代表性省份）
    radar_provinces = ['黑龙江', '北京', '上海', '广东', '云南']
    radar_data = []
    colors = ['#FF6B6B', '#FFD93D', '#00D9A5', '#00C6FB', '#A29BFE']
    for i, p in enumerate(radar_provinces):
        if p in stack_data:
            radar_data.append({
                'name': p,
                'value': [
                    stack_data[p]['spring'],
                    stack_data[p]['summer'],
                    stack_data[p]['autumn'],
                    stack_data[p]['winter']
                ],
                'itemStyle': {'color': colors[i]},
                'lineStyle': {'color': colors[i]}
            })
    seasonal_data['radar_data'] = radar_data
    
    # 箱线图数据（所有省份各季节温度分布）
    all_seasonal = {'spring': [], 'summer': [], 'autumn': [], 'winter': []}
    for province, seasons in province_seasonal.items():
        for season in ['spring', 'summer', 'autumn', 'winter']:
            all_seasonal[season].extend(seasons[season])
    
    def calc_boxplot(data):
        if not data:
            return [0, 0, 0, 0, 0]
        sorted_data = sorted(data)
        n = len(sorted_data)
        return [
            sorted_data[0],  # min
            sorted_data[int(n * 0.25)],  # Q1
            sorted_data[int(n * 0.5)],  # median
            sorted_data[int(n * 0.75)],  # Q3
            sorted_data[-1]  # max
        ]
    
    seasonal_data['box_data'] = {
        'spring': calc_boxplot(all_seasonal['spring']),
        'summer': calc_boxplot(all_seasonal['summer']),
        'autumn': calc_boxplot(all_seasonal['autumn']),
        'winter': calc_boxplot(all_seasonal['winter']),
    }
    
    return render(request, 'analysis.html', {
        'months': mark_safe(months),
        'provinces': mark_safe(provinces),
        'precipitation_data': mark_safe(bar_data),
        'extreme_data': mark_safe(extreme_data),
        'history_data': mark_safe(province_history),
        'seasonal_data': mark_safe(seasonal_data),
        'stats': stats,
        'active_page': 'analysis',
    })


# ==========================================
# 14. 用户系统 - 登录
# ==========================================
def user_login(request):
    """用户登录"""
    if request.user.is_authenticated:
        return redirect('user_profile')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # 记住我 - 设置session有效期
            if remember:
                request.session.set_expiry(7 * 24 * 60 * 60)  # 7天
            else:
                request.session.set_expiry(0)  # 关闭浏览器即过期
            
            # 跳转到之前的页面或首页
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误'})
    
    return render(request, 'login.html')


# ==========================================
# 15. 用户系统 - 注册
# ==========================================
def user_register(request):
    """用户注册"""
    if request.user.is_authenticated:
        return redirect('user_profile')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        location = request.POST.get('location', '').strip()
        
        form_data = {'username': username, 'email': email, 'location': location}
        
        # 验证
        if len(username) < 3:
            return render(request, 'register.html', {'error': '用户名至少需要3个字符', 'form_data': form_data})
        
        if len(password) < 6:
            return render(request, 'register.html', {'error': '密码至少需要6位', 'form_data': form_data})
        
        if password != password2:
            return render(request, 'register.html', {'error': '两次输入的密码不一致', 'form_data': form_data})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': '用户名已被占用', 'form_data': form_data})
        
        if email and User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': '邮箱已被注册', 'form_data': form_data})
        
        try:
            # 创建用户
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # 创建用户扩展信息
            UserProfile.objects.create(user=user, location=location)
            
            # 自动登录
            auth_login(request, user)
            messages.success(request, '注册成功！欢迎加入 NCDC 气象数据平台')
            return redirect('user_profile')
        except Exception as e:
            return render(request, 'register.html', {'error': f'注册失败: {str(e)}', 'form_data': form_data})
    
    return render(request, 'register.html')


# ==========================================
# 16. 用户系统 - 登出
# ==========================================
def user_logout(request):
    """用户登出"""
    auth_logout(request)
    messages.info(request, '您已安全退出')
    return redirect('home')


# ==========================================
# 17. 用户系统 - 个人中心
# ==========================================
@login_required(login_url='/login/')
def user_profile(request):
    """用户个人中心"""
    user = request.user
    
    # 获取或创建用户扩展信息
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # 获取收藏列表
    favorites = UserFavorite.objects.filter(user=user)[:12]
    favorites_count = UserFavorite.objects.filter(user=user).count()
    
    # 获取浏览历史
    history = BrowseHistory.objects.filter(user=user)[:10]
    history_count = BrowseHistory.objects.filter(user=user).count()
    
    # 计算加入天数
    days_joined = (datetime.now().date() - user.date_joined.date()).days + 1
    
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'favorites': favorites,
        'favorites_count': favorites_count,
        'history': history,
        'history_count': history_count,
        'total_provinces': len(provinces),
        'days_joined': days_joined,
        'active_page': 'profile',
    })


# ==========================================
# 18. 用户系统 - 账号设置
# ==========================================
@login_required(login_url='/login/')
def user_settings(request):
    """账号设置"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    success = None
    error = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # 更新基本信息
            email = request.POST.get('email', '').strip()
            location = request.POST.get('location', '').strip()
            avatar = request.POST.get('avatar', '').strip()
            bio = request.POST.get('bio', '').strip()
            
            # 检查邮箱是否被其他用户使用
            if email and User.objects.filter(email=email).exclude(id=user.id).exists():
                error = '该邮箱已被其他用户使用'
            else:
                user.email = email
                user.save()
                
                profile.location = location
                profile.avatar = avatar
                profile.bio = bio
                profile.save()
                
                success = '个人信息已更新'
        
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            new_password2 = request.POST.get('new_password2')
            
            if not user.check_password(old_password):
                error = '当前密码不正确'
            elif len(new_password) < 6:
                error = '新密码至少需要6位'
            elif new_password != new_password2:
                error = '两次输入的新密码不一致'
            else:
                user.set_password(new_password)
                user.save()
                # 重新登录
                auth_login(request, user)
                success = '密码修改成功'
    
    return render(request, 'settings.html', {
        'user': user,
        'profile': profile,
        'success': success,
        'error': error,
        'active_page': 'settings',
    })


# ==========================================
# 19. 收藏功能 - 添加收藏
# ==========================================
@login_required(login_url='/login/')
def add_favorite(request):
    """添加收藏"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            province = data.get('province', '').strip()
            note = data.get('note', '').strip()
            
            if not province:
                return JsonResponse({'success': False, 'message': '省份名称不能为空'})
            
            if province not in provinces:
                return JsonResponse({'success': False, 'message': '无效的省份名称'})
            
            # 检查是否已收藏
            if UserFavorite.objects.filter(user=request.user, province=province).exists():
                return JsonResponse({'success': False, 'message': '该省份已收藏'})
            
            # 添加收藏
            UserFavorite.objects.create(user=request.user, province=province, note=note)
            
            return JsonResponse({'success': True, 'message': '收藏成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


# ==========================================
# 20. 收藏功能 - 取消收藏
# ==========================================
@login_required(login_url='/login/')
def remove_favorite(request):
    """取消收藏"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fav_id = data.get('id')
            province = data.get('province')
            
            if fav_id:
                UserFavorite.objects.filter(id=fav_id, user=request.user).delete()
            elif province:
                UserFavorite.objects.filter(user=request.user, province=province).delete()
            else:
                return JsonResponse({'success': False, 'message': '缺少参数'})
            
            return JsonResponse({'success': True, 'message': '已取消收藏'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


# ==========================================
# 21. 检查收藏状态
# ==========================================
def check_favorite(request):
    """检查省份是否已收藏"""
    province = request.GET.get('province', '')
    
    if not request.user.is_authenticated:
        return JsonResponse({'is_favorite': False, 'logged_in': False})
    
    is_favorite = UserFavorite.objects.filter(user=request.user, province=province).exists()
    return JsonResponse({'is_favorite': is_favorite, 'logged_in': True})


# ==========================================
# 22. 切换收藏状态
# ==========================================
def toggle_favorite(request):
    """切换收藏状态（添加或取消）"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方式错误'})
    
    # 检查用户是否登录
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'message': '请先登录',
            'redirect': '/login/?next=' + request.META.get('HTTP_REFERER', '/')
        })
    
    try:
        data = json.loads(request.body)
        province = data.get('province', '').strip()
        
        if not province:
            return JsonResponse({'success': False, 'message': '省份名称不能为空'})
        
        if province not in provinces:
            return JsonResponse({'success': False, 'message': '无效的省份名称'})
        
        # 检查是否已收藏
        existing = UserFavorite.objects.filter(user=request.user, province=province).first()
        
        if existing:
            # 已收藏，则取消
            existing.delete()
            return JsonResponse({
                'success': True, 
                'is_favorite': False, 
                'message': '已取消收藏'
            })
        else:
            # 未收藏，则添加
            UserFavorite.objects.create(user=request.user, province=province)
            return JsonResponse({
                'success': True, 
                'is_favorite': True, 
                'message': '收藏成功'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ==========================================
# 23. 清空浏览历史
# ==========================================
@login_required(login_url='/login/')
def clear_history(request):
    """清空浏览历史"""
    if request.method == 'POST':
        BrowseHistory.objects.filter(user=request.user).delete()
        messages.success(request, '浏览记录已清空')
    return redirect('user_profile')


# ==========================================
# 23. 清空收藏
# ==========================================
@login_required(login_url='/login/')
def clear_favorites(request):
    """清空所有收藏"""
    if request.method == 'POST':
        UserFavorite.objects.filter(user=request.user).delete()
        messages.success(request, '收藏已清空')
    return redirect('user_profile')


# ==========================================
# 24. 记录浏览历史（辅助函数）
# ==========================================
def record_browse_history(user, province):
    """记录浏览历史"""
    if not user.is_authenticated:
        return
    
    # 更新或创建浏览记录
    history, created = BrowseHistory.objects.get_or_create(
        user=user,
        province=province,
        defaults={'visited_at': datetime.now()}
    )
    if not created:
        history.visited_at = datetime.now()
        history.save()

