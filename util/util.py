import logging
from flask import jsonify


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('review.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 입력값 검증 함수
def check_input(value, input_type, is_optional=False):
    # 꼭 필요하지 않은 필드면 None이나 공백값도 허용
    if is_optional == True:
        if value == None or value == "":
            return True

    else:
        if value == None or type(value) is not str:
            return False

        elif input_type == 'type':
            if value != 'REVIEW':
                return False

        elif input_type == 'action':
            if value not in ['ADD', 'MOD', 'DEL']:
                return False
    
        return True

    return False
   
# pool에서 connection과 cursor를 획득하는 함수
def get_cursor(pool):
    try:
        m_pool = pool
        m_conn = m_pool.connection()
        m_cursor = m_conn.cursor()

    except Exception as ex:
        msg = "db error: cannot get db connection, ex: %s" % (ex)
        print(msg)

        # 에러발생 시 close
        if m_cursor:
            m_cursor.close()

        if m_conn:
            m_conn.close()

        return None, None

    return m_conn, m_cursor

# cursor와 connection을 close하는 함수
def close_cursor(conn, cursor):
    if cursor:
        cursor.close()

    if conn:
        conn.close()

    return True

# pymysql 결과 tuple을 json 형태로 바꿔주는 함수
def fetchall_to_json(cursor):
    keys = []
    json_data = []

    if cursor.description == None:
        return json_data

    for column in cursor.description:
        keys.append(column[0])

    key_number = len(keys)

    for row in cursor.fetchall():
        item = dict()
        for q in range(key_number):
            item[keys[q]] = row[q]

        json_data.append(item)

    return json_data

def create_msg(status, message='', data=None):
    result = {
            'status': status,
            'message': message,
            'data' : {}
    }

    if data and (isinstance(data, dict) == True):
        result['data'] = data

    elif data and (isinstance(data, list) == True):
        result['data'] = data

    logger.info(str(result))
    return jsonify(result)

