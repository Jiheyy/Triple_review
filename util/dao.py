import sqlite3
import json

class DAO:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.data = None
        
        try:
            self.conn = sqlite3.connect('database.db')
            self.cursor = self.conn.cursor()
            print('get cursor!!')

        except Exception as ex:
            msg = "cannnot connect to database.db, Ex:%s" % (ex)
            print(msg)
            self.__del__()



    def __del__(self):
        print('---Bye')
        self.conn.commit()
        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()

    def execute(self, sql, args = []):
        result = None

        try:
            self.cursor.execute(sql%args)
            print(sql%args)

            result = self.__fetchall_to_json()

            return result, 200
        except Exception as ex:
            msg = "db error: cannot execute sql, sql: %s, args: %s, ex: %s" % (sql, args, ex)
            print(msg)

            return None, 500

    def __fetchall_to_json(self):
    
        keys = []
        json_data = []

        if self.cursor.description == None:
            return json_data

        for column in self.cursor.description:
            keys.append(column[0])

        key_number = len(keys)

        for row in self.cursor.fetchall():
            item = dict()

            for q in range(key_number):
                item[keys[q]] = row[q]

            json_data.append(item)

        return json_data
