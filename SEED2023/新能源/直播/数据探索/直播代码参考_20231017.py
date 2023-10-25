# 直播代码参考 - 2023-10-17

############################ 绘图函数
def my_plot(df, id_encode, start_date, end_date, groupby, predict=False): 
    # 绘制折线图
    fig = plt.figure(figsize=(20,10))
    df = df.loc[(df['ds'] >= start_date) & (df['ds'] <= end_date)]
    if id_encode > -1:
        df = df.loc[df['id_encode'] == id_encode]
    else:
        pass
    if groupby == 'hour':
        plt.plot(df['new_date'], df['power'], color = 'blue')
        if predict == True:
            plt.plot(df['new_date'], df['power_pre'], color = 'red')
        try:
            plt.plot(df['new_date'], df['temp_max'], color = 'brown')
            plt.plot(df['new_date'], df['temp_min'], color = 'green')
        except:
            pass
    elif groupby == 'day':
        df_power = df.groupby(by = 'ds_date')['power'].sum().reset_index()
        plt.plot(df_power['ds_date'], df_power['power'], color = 'blue')
        if predict == True:
            df_power_pre = df.groupby(by = 'ds_date')['power_pre'].sum().reset_index()
            plt.plot(df_power_pre['ds_date'], df_power_pre['power_pre'], color = 'red')
            
    # 添加标题和轴标签
    plt.title('Power vs Date')
    plt.xlabel('Date')
    plt.ylabel('Power')

    # 显示图形
    plt.show()


############################ h3解析
# 把H3编码转换成经纬度坐标
from h3 import h3
df_stub = pd.read_csv('./训练集/stub_info.csv')
df_stub['center'] = df_stub['h3'].apply(lambda x: h3.h3_to_geo(x))

# 绘制地图
import folium
def geo_map(df):
    # 拆分经纬度坐标
    df[['latitude', 'longitude']] = pd.DataFrame(df['center'].tolist(), columns=['latitude', 'longitude'])
    

    # 创建地图
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)

    # 添加标记点
    for index, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['id_encode']
        ).add_to(m)

    # 显示地图
    return m

stub_m = geo_map(df_stub)
display(stub_m)



####################################### 调取百度api获取经纬度对应地址信息
# 需要先进入百度web服务api网站注册账号, 获取对应的ak 跟sk, 需阅读网站指引
# https://lbsyun.baidu.com/faq/api?title=webapi
# 里面有不少案例, 以下代码也是直接引用上面提供的案例代码
# 直接用的话需要提供代码中的 ak 跟 sk 两个key

# encoding:utf-8
# 根据您选择的AK已为您生成调用代码
# 检测您当前的AK设置了sn检验，本示例中已为您生成sn计算代码
import requests
import urllib
import hashlib
# 建立访问函数
def get_city_frombd(row):
    # 服务地址
    host = "https://api.map.baidu.com"
    # 接口地址
    uri = "/reverse_geocoding/v3"
    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    ak = ""
    # 此处填写你在控制台-应用管理-创建应用时，校验方式选择sn校验后生成的SK
    sk = ""
    # 设置您的请求参数
    coordinate = str(row['latitude']) + ',' + str(row['longitude'])
    params = {
        "ak":       ak,
        "output":    "json",
        "coordtype":    "wgs84ll",
        "extensions_poi":    "0",
        "location":   coordinate,
    }
    # 拼接请求字符串
    paramsArr = []
    for key in params:
        paramsArr.append(key + "=" + params[key])
    queryStr = uri + "?" + "&".join(paramsArr)

    # 对queryStr进行转码，safe内的保留字符不转换
    encodedStr = urllib.request.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")

    # 在最后直接追加上您的SK
    rawStr = encodedStr + sk

    # 计算sn
    sn = hashlib.md5(urllib.parse.quote_plus(rawStr).encode("utf8")).hexdigest()

    # 将sn参数添加到请求中
    queryStr = queryStr + "&sn=" + sn

    # 请注意，此处打印的url为非urlencode后的请求串
    # 如果将该请求串直接粘贴到浏览器中发起请求，由于浏览器会自动进行urlencode，会导致返回sn校验失败
    url = host + queryStr
    response = requests.get(url)
    return response.json().get('result').get('addressComponent')

def df_stub_process(df):
    df['center'] = df['h3'].apply(lambda x: h3.h3_to_geo(x))
    df[['latitude', 'longitude']] = pd.DataFrame(df['center'].tolist(), columns=['latitude', 'longitude'])
    df['latitude'] = df['latitude'].apply(lambda x: round(x,6))
    df['longitude'] = df['longitude'].apply(lambda x: round(x,6))
    # 通过百度api返回城市信息
    df['address'] = df[['latitude','longitude']].apply(get_city_frombd, axis = 1)
    return df

df_stub = df_stub_process(df_stub)

# 爬虫是通过scrapy爬取天气网, 可自行上官网找对应的教程,以及B站的教学视频学习
# https://lishi.tianqi.com/changzhou/202303.html
