import requests
import re
import sqlite3
import os
import random
from flask import Flask, render_template, jsonify, request
import base64

# 图片工具类
class ImageTool:
    # 存储图片的目录
    PORTRAIT_IMG_FOLDER = '/portrait_img_folder'
    # 获取图片的 API
    PORTRAIT_IMG_API = 'https://xxxxxx'

    # 根据员工编号范围, 获取指定数量的员工图片
    # 注: 待优化, 可使用多线程及队列实现快速下载!!!
    def get_portrait_img(employee_id_range):
        # GET 请求头部, 数据摘自浏览器, 防止被发现俺是一只可爱滴小蛛蛛～
        get_headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding' :'gzip, deflate, br',
        'Accept-Language' : 'zh-CN,zh;q=0.9',
        'Cache-Control' :'max-age=0',
        'Connection' : 'keep-alive',
        'Host' : 'www.ec.idpbg.foxconn.com',
        'Sec-Ch-Ua' : '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Sec-Ch-Ua-Mobile' : '?0',
        'Sec-Ch-Ua-Platform' : '"macOS"',
        'Sec-Fetch-Dest' : 'document',
        'Sec-Fetch-Mode' : 'navigate',
        'Sec-Fetch-Site' : 'none',
        'Sec-Fetch-User' : '?1',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }
        # GET Payload
        get_payload = {
            'userno': ''
        }
        # 计算要下载的图片数量
        portrait_img_num_pattern = r'(\d+)'
        match = re.findall(pattern=portrait_img_num_pattern, string=employee_id_range)
        employee_id_range_begin, employee_id_range_end = match[0], match[1]
        portrait_img_count = (int(employee_id_range_end) - int(employee_id_range_begin))
        print(f'GET Require Count : {portrait_img_count + 1}')
        # 截取起始范围员工编号末尾非 0 的前半部分
        # 例如 employee_id_range_begin = 1245000, 则经过遍历 employee_id_begin = ‘F1245’
        employee_id_begin = 'F'
        for c in employee_id_range_begin:
            if c != '0':
                employee_id_begin += c
        # 根据员工编号范围, 构造要下载的图片名称(这里的名称是指员工编号)
        # 例如 employee_id = employee_id_begin + str(employee_id_end) = 'F1245' + '001' = 'F1245001',
        employee_id_end_len = len('Fxxxxxxx') - len(employee_id_begin)
        for i in range(portrait_img_count + 1):
            employee_id = ''
            employee_id_end = ''
            zero_count = employee_id_end_len - len(str(i))
            if zero_count != 0:
                for ii in range(zero_count):
                    employee_id_end += '0'
            employee_id_end += str(i)            
            employee_id = employee_id_begin + str(employee_id_end)
            # 填充 GET Payload
            get_payload['userno'] = employee_id
            # 发送 GET 请求, 获取图片
            portrait_img_response = requests.get(url=ImageTool.PORTRAIT_IMG_API, data=get_payload, headers=get_headers)
            print(f'Employee ID : {employee_id}, Img Response Status Code : {CommonTool.print_with_color(portrait_img_response.status_code)}, Img Length : {len(portrait_img_response.content)}')
            # 将图片存存储到本地
            ImageTool.store_img_into_file(employee_id, portrait_img_response.status_code, portrait_img_response.content)

    # 将图片存储到本地的指定目录下
    store_img_count = 0
    def store_img_into_file(employee_id, response_status_code, img_content):
        global store_img_count
        if response_status_code == 200:
            if len(img_content) != 3981:
                with open(f'{ImageTool.PORTRAIT_IMG_FOLDER}/{employee_id}.jpeg', 'wb') as file:
                    file.write(img_content)
                    store_img_count += 1
                    print(f'{employee_id}.jpeg has been stored successfully')
                    print(f'A total of [{CommonTool.print_with_color(store_img_count)}] portrait images has been stored\n')
            else:
                print("It is not a portrait image, so don't store it\n")
        else:
            print("Can't store this portrait image\n")
    
    # 获取指定目录下各个图片的名称和图片数据
    def get_img_name_and_content():
        img_name_and_content_dict = {}
        current_path = os.getcwd() + ImageTool.PORTRAIT_IMG_FOLDER
        print(current_path)
        for portrait_img_name in os.listdir(current_path):
            with open(f'{current_path}/{portrait_img_name}', 'rb') as file: # !!!读写图片记得加 b!!!
                portrait_img_content = file.read()
                img_name_and_content_dict[portrait_img_name] = portrait_img_content
        return img_name_and_content_dict

# 操作 SQLite3 数据库的类
class SQLite3DB:
    DATABASE_NAME = 'portrait_image.db'
    TABLE_NAME = 'IMAGE'
    TABLE_NAME_2 = 'IMAGE_VISTOR'
    
    # 获取数据库连接
    def get_sqlite3_conn():
        conn = sqlite3.connect(SQLite3DB.DATABASE_NAME)
        print(f"sqlite3.connect('fx_portrait_image6.db') : {conn}", end='')
        return conn

    # 创建 IMAGE 与 IMAGE_VISTOR 表
    def create_table():
        # IMAGE 的表结构
        image_table_structure = f'''
        CREATE TABLE IF NOT EXISTS {SQLite3DB.TABLE_NAME}
        (
            NAME TEXT PRIMARY KEY NOT NULL,
            CONTENT BLOB NOT NULL,
            RANKING INTEGER NOT NULL DEFAULT {ELORankingAlgorithm.DEFAULT_RANKING}
        );
        '''
        # IMAGE_VISTOR 的表结构
        image_vistor_table_structure = f'''
        CREATE TABLE IF NOT EXISTS {SQLite3DB.TABLE_NAME_2}
        (
            IP TEXT PRIMARY KEY NOT NULL,
            PK_COUNT INTEGER NOT NULL DEFAULT 0
        );
        '''
        # 获取数据库连接进而创建一个游标
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        # 创建 IMAGE 表
        result = cursor.execute(image_table_structure)
        conn.commit()
        print(image_table_structure, end='')
        print(f'c.execute(image_table_structure) : {result}')
        # 创建 IMAGE_VISTOR 表
        result2 = cursor.execute(image_vistor_table_structure)
        conn.commit()
        print(image_vistor_table_structure, end='')
        print(f'cursor.execute(image_vistor_table_structure) : {result2}\n')
        # 关闭数据库连接及游标, 即释放资源
        SQLite3DB.release_resource(cursor, conn)

    # 将图片插入到数据库中
    def insert_img_into_db(employeeID, portrait_img):
        insert_img_sql = f'''
        INSERT INTO {SQLite3DB.TABLE_NAME}
        (NAME,CONTENT)
        VALUES
        (?,?)
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        result = cursor.execute(insert_img_sql, (employeeID, portrait_img))
        print(insert_img_sql, end='')
        print(f'c.execute(insert_img_sql) : {result}\n')
        conn.commit()
        SQLite3DB.release_resource(cursor, conn)
    
    # 通过 ip 查询访客 ip 是否已被插入到数据库中
    def select_vistor_ip_by_ip(vistor_ip_address):
        select_vistor_ip_sql = f'''
        SELECT IP FROM {SQLite3DB.TABLE_NAME_2}
        WHERE IP = '{vistor_ip_address}'
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        select_result = cursor.execute(select_vistor_ip_sql)
        print(select_vistor_ip_sql, end='')
        print(f'cursor.execute(select_vistor_ip_sql) : {select_result}\n')
        ip = ''
        for row in select_result:
            ip = row[0]
        SQLite3DB.release_resource(cursor, conn)
        return True if (ip == vistor_ip_address) else False

    # 将新访客 ip 插入数据库
    def insert_vistor_ip_into_db(vistor_ip_address):
        insert_vistor_ip_sql = f'''
        INSERT INTO {SQLite3DB.TABLE_NAME_2}
        (IP)
        VALUES
        ('{vistor_ip_address}')
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        result = cursor.execute(insert_vistor_ip_sql)
        print(insert_vistor_ip_sql, end='')
        print(f'cursor.execute(insert_vistor_sql, (ip_address, ip_address_pk_count)) : {result}\n')
        conn.commit()
        SQLite3DB.release_resource(cursor, conn)

    # 通过访客ip, 更新访客在页面点击 PK 按钮(小心心)的次数
    def update_vistor_pk_count_by_ip(vistor_ip_address):
        update_vistor_pk_count_sql = f'''
        UPDATE {SQLite3DB.TABLE_NAME_2}
        SET PK_COUNT = PK_COUNT + 1
        WHERE IP = '{vistor_ip_address}'
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        udpated_result = cursor.execute(update_vistor_pk_count_sql)
        conn.commit()
        print(update_vistor_pk_count_sql, end='')
        print(f'cursor.execute(update_vistor_pk_count_sql) : {udpated_result}')
        SQLite3DB.release_resource(cursor, conn)
    
    # 获取访客数量, 即 ip 的数量
    def select_vistor_count():
        select_vistor_count_sql = f'''
        SELECT COUNT(IP)
        FROM {SQLite3DB.TABLE_NAME_2}
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        select_result = cursor.execute(select_vistor_count_sql)
        print(select_vistor_count_sql, end='')
        print(f'cursor.execute(select_vistor_count_sql) : {select_result}\n')
        vistor_count = cursor.fetchone()[0]
        SQLite3DB.release_resource(cursor, conn)
        return vistor_count

    # 获取 pk_count 的总数量, 即累加各个 ip 对应的 pk_count
    def select_pk_count():
        select_pk_count_sql = f'''
        SELECT SUM(PK_COUNT)
        FROM {SQLite3DB.TABLE_NAME_2}
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        select_result = cursor.execute(select_pk_count_sql)
        print(select_pk_count_sql, end='')
        print(f'execute(select_pk_count_sql) : {select_result}\n')
        pk_count = cursor.fetchone()[0]
        SQLite3DB.release_resource(cursor, conn)
        return pk_count

    # 将指定目录下的所有图片存储到数据库
    def store_img_into_db():
        image_inserted_db_count = 0
        img_name_and_content_dict = ImageTool.get_img_name_and_content()
        for img_name, img_content in img_name_and_content_dict.items():
            SQLite3DB.insert_img_into_db(img_name, img_content)
            image_inserted_db_count += 1
            print(f'A total of [{CommonTool.print_with_color(image_inserted_db_count)}] images has been inserted into database\n')

    # 通过员工编号, 即图片名称从数据中获取指定图片信息
    def select_img_by_id(employeeID):
        select_img_by_id_sql = f'''
        SELECT NAME,CONTENT,RANKING 
        FROM {SQLite3DB.TABLE_NAME} 
        WHERE NAME = '{employeeID}'
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        img = cursor.execute(select_img_by_id_sql)
        print(select_img_by_id_sql, end='')
        print(f'c.execute(select_img_by_id_sql) : {img}\n')
        image_name = ''
        image_content = ''
        image_ranking = 0
        for row in img:
            image_name = row[0] # image name
            image_content = row[1] # image content
            image_ranking = row[2] # image ranking
        SQLite3DB.release_resource(cursor, conn)
        return image_name, image_content, image_ranking

    # 获取数据库中所有的图片名称, 即员工编号
    def select_all_img_ids():
        all_img_ids_list = []
        select_all_img_ids_sql = f'SELECT NAME FROM {SQLite3DB.TABLE_NAME}'
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        img_ids = cursor.execute(select_all_img_ids_sql)
        print(select_all_img_ids_sql, end='')
        print(f'c.execute(select_all_img_ids_sql) : {img_ids}\n')
        for img_id in img_ids:
            all_img_ids_list.append(img_id[0])
        SQLite3DB.release_resource(cursor, conn)
        return all_img_ids_list

    # 从数据库中随机抽取两条图片信息
    def random_get_two_img():
        img_ids_list = SQLite3DB.select_all_img_ids()
        # shuffle(): 对列表中的元素进行随机排序, 即修改原始列表中的各元素的位置
        random.shuffle(img_ids_list)
        # choice(): 随机获取一个元素
        two_img_id = [random.choice(img_ids_list) for _ in range(2)]
        f_img_id, s_img_id = two_img_id[0], two_img_id[1]
        f_img_name, f_img_content, f_img_ranking = SQLite3DB.select_img_by_id(f_img_id)
        s_img_name, s_img_content, s_img_ranking  = SQLite3DB.select_img_by_id(s_img_id)
        f_img_dict = {'name' : f_img_name, 'content' : f_img_content, 'ranking' : f_img_ranking}
        s_img_dict = {'name' : s_img_name, 'content' : s_img_content, 'ranking' : s_img_ranking}
        return f_img_dict, s_img_dict

    # 从数据库中随机抽取一条图片信息
    def random_get_one_img(loser_img_id):
        img_ids_list = SQLite3DB.select_all_img_ids()
        img_ids_list.remove(loser_img_id) # 删除 old_img_id
        random.shuffle(img_ids_list)
        img_id = random.choice(img_ids_list)
        img_name, img_content, img_ranking = SQLite3DB.select_img_by_id(img_id)
        img_dict = {'name' : img_name, 'content' : img_content, 'ranking' : img_ranking}
        return img_dict

    # 通过员工编号, 即图片名称更新数据库中指定图片的积分排名 ranking
    def update_ranking_by_id(employeeID, newRanking):
        update_ranking_by_id_sql = f'''
        UPDATE {SQLite3DB.TABLE_NAME}
        SET RANKING = {newRanking} 
        WHERE NAME = '{employeeID}'
        '''
        # 查询旧的积分(排名) ranking
        oldRanking  = SQLite3DB.select_ranking_by_id(employeeID)
        # 更新 ranking
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        update_result = cursor.execute(update_ranking_by_id_sql)
        conn.commit()
        print(update_ranking_by_id_sql, end='')
        print(f'cursor.execute(update_ranking_by_id_sql) : {update_result}', end='')
        # 检查是否更新成功
        updated_ranking = SQLite3DB.select_ranking_by_id(employeeID)
        if updated_ranking == newRanking: 
            print(f"[{employeeID}]'s Old Ranking: [{oldRanking}], And New Ranking: [{newRanking}]\n")
        # 关闭数据库连接, 释放资源
        SQLite3DB.release_resource(cursor, conn)
    
    # 通过员工编号, 即图片名称获取数据库中指定图片的积分排名 ranking
    def select_ranking_by_id(employeeID):
        select_ranking_by_id_sql = f'''
        SELECT RANKING FROM {SQLite3DB.TABLE_NAME}
        WHERE NAME = '{employeeID}'
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        select_result = cursor.execute(select_ranking_by_id_sql)
        print(select_ranking_by_id_sql, end='')
        print(f'cursor.execute(select_ranking_by_id_sql) : {select_result}\n')
        img_ranking = 0
        for row in select_result:
            img_ranking = row[0]
        SQLite3DB.release_resource(cursor, conn)
        return img_ranking
    
    # 从数据中获取积分排名 ranking 前 top_number 的图片信息
    def select_top_ranking_imgs(top_number):
        select_top_ranking_img_sql = f'''
        SELECT NAME,CONTENT,RANKING FROM {SQLite3DB.TABLE_NAME}
        ORDER BY RANKING DESC
        LIMIT {top_number};
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        top_ranking_imgs = cursor.execute(select_top_ranking_img_sql)
        print(select_top_ranking_img_sql, end='')
        print(f'cursor.execute(select_top_ranking_img_sql) : {top_ranking_imgs}\n')
        top_ranking_img_dict_list = [] 
        for img in top_ranking_imgs:
            top_ranking_img_dict = {}
            top_ranking_img_dict['name'] = img[0]
            top_ranking_img_dict['content'] = img[1]
            top_ranking_img_dict['ranking'] = img[2]
            top_ranking_img_dict_list.append(top_ranking_img_dict)
        SQLite3DB.release_resource(cursor, conn)
        return top_ranking_img_dict_list
    
    # 重置数据库表中的数值, 即将所有表中的数值重置为建表时的初始值
    def reset_data():
        # 重置所有图片的积分排名 ranking
        reset_ranking_sql = f'''
        UPDATE {SQLite3DB.TABLE_NAME}
        SET RANKING = {ELORankingAlgorithm.DEFAULT_RANKING}
        '''
        # 重置所有的访客数据, 即清空所有的访客数据
        reset_vistor_sql = f'''
        DELETE FROM {SQLite3DB.TABLE_NAME_2}
        '''
        conn = SQLite3DB.get_sqlite3_conn()
        cursor = conn.cursor()
        update_result = cursor.execute(reset_ranking_sql)
        delete_result = cursor.execute(reset_vistor_sql)
        conn.commit()
        SQLite3DB.release_resource(cursor, conn)
        # 打印日志信息
        print(reset_ranking_sql, end='')
        print(f'cursor.execute(reset_ranking_sql) : {update_result}')
        print(reset_vistor_sql, end='')
        print(f'cursor.execute(reset_vistor_sql) : {delete_result}\n')
    
    # 关闭数据库连接, 释放资源
    def release_resource(sqlite3_conn_cursor, sqlite3_conn):
        sqlite3_conn_cursor.close()
        sqlite3_conn.close()

# 公共工具类
class CommonTool:
    # 打印彩色字符
    def print_with_color(string, *color):
        if not color: # default color is red
            return f'\x1b[31m{string}\x1b[0m'
        
    # 对图片数据进行 Base64 编码, 方便在网络上传输
    def b64encode_and_update_img_dict(img_dict):
        image_content_b64encode =  base64.b64encode(img_dict['content']).decode('utf-8')
        img_dict['content'] = image_content_b64encode
    
    # 数值的小数部分仅保留小数点的后 4 位
    def number_handle(number_1, number_2):
        num_pattern = r'\d+.\d{4}'
        num_pattern_obj = re.compile(num_pattern)
        # 若无小数部分, 例如 1400, 则不处理
        if type(number_1) != int:
            # 若小数点后只有 4 或小于 4 位, 例如 0.5123, 则不处理
            if len(str(number_1).split('.')[1]) > 4:
                number_1 = num_pattern_obj.match(str(number_1)).group()
        if type(number_2) != int:
            if len(str(number_2).split('.')[1]) > 4:
                number_2 = num_pattern_obj.match(str(number_2)).group()
        # 均转换为字符串格式并返回
        return str(number_1), str(number_2)
    
    # 仅保留数值中的整数部分
    def int_handle(num):
        return str(num).split('.')[0]
        
    # "获胜期望值 winE"及"积分排名 ranking"的小数部分仅保留小数点后 4 位
    def update_winE_and_ranking_number(img_dict):
        img_winE, img_ranking = img_dict['winE'], img_dict['ranking'] 
        img_dict['winE'], img_dict['ranking'] = CommonTool.number_handle(img_winE, img_ranking)
    
    # 仅保留"积分(排名) ranking"的整数部分
    def update_ranking_number(img_dict):
        img_dict['ranking'] = CommonTool.int_handle(img_dict['ranking'])
    
    # 获取访客的 ip 地址
    # 注意: 在 Flask 中, 你可以通过访问 request 对象来获取客户端 ip 地址,
    # 具体来说, 你可以使用 request.remote_addr 属性来获取客户端的真实 ip 地址,
    # 如果你的应用程序在生产环境中使用了负载均衡器或代理服务器(如Cloudflare),
    # 你可能需要使用 X-Forwarded-For 标头来获取客户端 ip 地址...
    def get_vistor_ip():
        # 使用 X-Forwarded-For 标头获取 ip 地址, 如果存在的话
        vistor_ip_address = request.headers.get('X-Forwarded-For')
        # 如果使用代理, 可能会有多个 ip 地址, 这里取第一个
        if vistor_ip_address:
            vistor_ip_address = vistor_ip_address.split(',')[0]
        else:
            vistor_ip_address = request.remote_addr
        return vistor_ip_address
    
    # 记录日志信息
    def record_log():
        pass

# ELO 排名算法类
class ELORankingAlgorithm:
    # 初始积分排名
    DEFAULT_RANKING = 1400

    # 根据两选手各自的积分排名 R(ranking), 计算选手各自的期望胜率, 即获胜期望值 E(winE)
    # Ea = 1 / ( 1 + 10^((Rb−Ra)/400) )
    def compute_expect_win_rate(obj_a_ranking, obj_b_ranking):
        obj_a_win_E = 1 / (1 + pow(10, (obj_b_ranking - obj_a_ranking) / 400))
        obj_b_win_E = 1 / (1 + pow(10, (obj_a_ranking - obj_b_ranking) / 400))
        return obj_a_win_E, obj_b_win_E

    # 根据选手各自的获胜期望值 E(winE)、评比结果 W、原积分排名 R(ranking) 及 K 值, 更新选手各自的积分排名 R(ranking)
    # Rn = Ro + K( W − E )
    def compute_rank(obj_a_ranking, obj_b_ranking, obj_a_E, obj_b_E, obj_a_W, obj_b_W):
        obj_a_ranking = obj_a_ranking + ELORankingAlgorithm.compute_K(obj_a_ranking) * (obj_a_W - obj_a_E)
        obj_b_ranking = obj_b_ranking + ELORankingAlgorithm.compute_K(obj_b_ranking) * (obj_b_W - obj_b_E)
        return obj_a_ranking, obj_b_ranking

    # 动态获取 K
    # 注: K 是一个加成系数, 由玩家当前分值水平决定, 分值越高 K 越小,
    # 这么设计的目的是为了避免仅仅进行少数场比赛就能改变高端顶尖玩家的排名, 总之就是尽可能保证排名数据精确!
    # !!! 后期需要根据比赛规模, 如人数来决定 K 的动态取值情况 !!!
    def compute_K(obj_rank):
        if obj_rank >= 2400:
            return 16
        if obj_rank >= 2100:
            return 24
        else:
            return 36

# web控制层, 即与 web 前端进行数据交互的类
class WebController:
    app = Flask(__name__)

    # 访问 web 主页
    @app.route('/')
    def index():
        return render_template('index.html')

    # 获取访客的 ip 地址
    @app.route('/api/get_vistor_ip')
    def get_vistor_ip():
        # 1.首次访问主页/刷新主页, 获取访客 ip
        vistor_ip_address = CommonTool.get_vistor_ip()
        # 2.判断该访客 ip 是否已经存在, 若不存在则将其插入到数据库
        exists = SQLite3DB.select_vistor_ip_by_ip(vistor_ip_address)
        if not exists:
            SQLite3DB.insert_vistor_ip_into_db(vistor_ip_address)
        # 打印日志信息
        print(f'\nVistor ip address is: {vistor_ip_address}\n')
        # 将封装后的响应数据转换为 json 格式并返回给前端页面
        vistor_ip_data = {'vistor_ip_address' : vistor_ip_address}
        return jsonify(vistor_ip_data)

    # 3.当访客在前端页面点击 PK 按钮(小心心)时, 更新访客 ip 对应的 pk_count, 即 pk_count++
    @app.route('/api/update_vistor_pk_count', methods=['POST'])
    def update_vistor_pk_count():
        vistor_ip_address = CommonTool.get_vistor_ip()
        SQLite3DB.update_vistor_pk_count_by_ip(vistor_ip_address)
        update_result = f"[{vistor_ip_address}]'s pk count be updated successfully"
        # Log
        print(f'\n{update_result}\n')
        # Return
        return update_result
    
    # 获取网页访客总数及 PK 次数总数
    @app.route('/api/get_vistor_and_pk_count')
    def get_vistor_and_pk_count():
        vistor_count = SQLite3DB.select_vistor_count()
        pk_count = SQLite3DB.select_pk_count()
        vistor_and_pk_count_datas = {'vistor_count' : vistor_count, 'pk_count' : pk_count}
        return jsonify(vistor_and_pk_count_datas)
    
    # 从数据库中随机抽取两条图片信息
    @app.route('/api/get_two_imgs')
    def get_two_imgs():
        # 获取两条图片信息
        f_img_dict, s_img_dict = SQLite3DB.random_get_two_img()
        # 获取图片的积分排名
        f_img_ranking, s_img_ranking = f_img_dict['ranking'], s_img_dict['ranking']
        # 并图片数据对其进行 Base64 编码, 方便在网络上传输
        CommonTool.b64encode_and_update_img_dict(f_img_dict)
        CommonTool.b64encode_and_update_img_dict(s_img_dict)
        # 根据积分(排名) ranking 计算新的获胜期望值 winE
        f_img_dict['winE'], s_img_dict['winE'] = ELORankingAlgorithm.compute_expect_win_rate(f_img_ranking, s_img_ranking)
        # 数值的小数部分仅保留小数点的后 4 位
        CommonTool.update_winE_and_ranking_number(f_img_dict)
        CommonTool.update_winE_and_ranking_number(s_img_dict)
        # 封装响应数据
        two_imgs_data = {'first_image' : f_img_dict, 'second_image' : s_img_dict}
        # 将封装后的响应数据转换为 json 格式并返回给前端页面
        return jsonify(two_imgs_data)

    # 从数据中获取积分排名 ranking 前 top_number 的图片信息
    @app.route('/api/get_top_10_ranking_imgs')
    def get_top_ranking_imgs():
        count = 1
        ten_imgs_data = {}
        top_ranking_img_dict_list = SQLite3DB.select_top_ranking_imgs(10)
        for img_dict in top_ranking_img_dict_list:
            CommonTool.b64encode_and_update_img_dict(img_dict)
            CommonTool.update_ranking_number(img_dict)
            ten_imgs_data[count] = img_dict
            count += 1
        return jsonify(ten_imgs_data)

    # 接收前端发来的 PK 结果:
    # 首先解析请求数据, 其次根据 PK 结果对数据进行相应的逻辑处理, 最后发送响应数据   
    @app.route('/api/pk_result', methods=['POST'])
    def get_one_img():
        # 获取请求数据
        image_json_datas = request.json
        # 解析请求数据
        f_img_dict, s_img_dict = image_json_datas['first_image'], image_json_datas['second_image']
        f_ranking, s_ranking = float(f_img_dict['ranking']), float(s_img_dict['ranking'])
        f_winE, s_winE = float(f_img_dict['winE']), float(s_img_dict['winE'])
        f_W, s_W = f_img_dict['W'], s_img_dict['W']
        f_name, s_name = f_img_dict['name'], s_img_dict['name']
        # 根据获胜期望值 winE、评比结果 W(1/0)、积分排名 ranking 及 K 值, 更新选手各自的积分排名 ranking
        # Rn = Ro + K( W − E )
        f_new_ranking, s_new_ranking = ELORankingAlgorithm.compute_rank(f_ranking, s_ranking, f_winE, s_winE, f_W, s_W)
        # 将更新后的积分排名 ranking 更新到数据库
        SQLite3DB.update_ranking_by_id(f_name, f_new_ranking)
        SQLite3DB.update_ranking_by_id(s_name, s_new_ranking)
        # PK 结果的处理:
        # 1.更新页面中获胜选手的'积分排名ranking',
        # 2.更新页面中失败选手的信息, 即从数据库中随机查询一个新的选手信息对其进行替换,
        # 3.根据获胜选手及新选手各自的积分排名 ranking, `更新`获胜选手的'获胜期望值 winE', `获取`失败选手的'获胜期望值 winE'.
        if f_W == 1:
            # 更新积分排名 ranking
            f_img_dict['ranking'] = f_new_ranking
            # 从数据库中随机获取一个新的选手信息, 并对其中的图片数据进行 Base64 编码, 便于在网络上传输
            new_s_img_dict = SQLite3DB.random_get_one_img(loser_img_id=s_name)
            CommonTool.b64encode_and_update_img_dict(new_s_img_dict)
            # 根据双方的积分排名 ranking, 计算在这场还未开始的, 即新一轮的PK中, 双方各自的获胜期望值 winE
            # eg.Ea = 1 / ( 1 + 10^((Rb−Ra)/400) )
            f_img_winE, new_s_img_winE = ELORankingAlgorithm.compute_expect_win_rate(f_new_ranking, new_s_img_dict['ranking'])
            f_img_dict['winE'], new_s_img_dict['winE'] = f_img_winE, new_s_img_winE
            # 'winE' 与 'ranking' 的小数部分仅保留小数点的后 4 位, 便于页面显示
            CommonTool.update_winE_and_ranking_number(f_img_dict)
            CommonTool.update_winE_and_ranking_number(new_s_img_dict)
            # 封装响应数据
            two_imgs_data = {'first_image' : f_img_dict, 'new_second_image' : new_s_img_dict}
        if s_W == 1:
            s_img_dict['ranking'] = s_new_ranking
            new_f_img_dict = SQLite3DB.random_get_one_img(loser_img_id=f_name)
            CommonTool.b64encode_and_update_img_dict(new_f_img_dict)
            new_f_img_winE, s_img_winE = ELORankingAlgorithm.compute_expect_win_rate(new_f_img_dict['ranking'], s_new_ranking)
            new_f_img_dict['winE'], s_img_dict['winE'] = new_f_img_winE, s_img_winE
            CommonTool.update_winE_and_ranking_number(new_f_img_dict)
            CommonTool.update_winE_and_ranking_number(s_img_dict)
            two_imgs_data = {'new_first_image' : new_f_img_dict, 'second_image' : s_img_dict}
        # 删除选手信息中不需要的键 'W' 及其对应的值
        del f_img_dict['W']
        del s_img_dict['W']
        # 将封装后的响应数据转换为 json 格式并返回给前端页面
        return jsonify(two_imgs_data)

# 测试: 图片工具类
class ImageToolTest:
    # F1245000 <= x <= F1245999, 1000 portrait images
    # get_portrait_img('F1245000 ~ F1245999')
    pass

# 测试: 公共工具类
class CommonToolTest:
    pass

# 测试: SQLite3数据库类
class SQLite3DBTest:
    pass

# 测试: ELO排名算法类
class ELORankingAlgorithmTest:
    pass

# 测试: web控制层, 即与 web 前端进行数据交互的类
class WebControllerTest:
    WebController.app.run(host='0.0.0.0', port=80, debug=True)