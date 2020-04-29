import pymysql

from Record import Record


class DatabaseManager:
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.user = 'root'
        self.password = '123456'
        self.database = 'db_fintech'

    def verify_insurance(self, user_id, insurance_id):
        connection = pymysql.connect(host=self.host,
                                     port=self.port,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database)
        sql = ("SELECT * FROM tb_insurance WHERE user_id = '%s';" % (user_id))
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return bool(rows[0][0] == insurance_id)

    def save_record(self, record):
        connection = pymysql.connect(host=self.host,
                                     port=self.port,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database)
        cursor = connection.cursor()
        sql = (
                "INSERT INTO tb_records(image,location,create_time,user_id,insurance_id)" + " VALUES ('%s','%s', '%s','%s','%s')" % (
            record.image, record.location, record.create_time, record.user_id, record.insurance_id))
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()

    def find_record(self, user_id):
        connection = pymysql.connect(host=self.host,
                                     port=self.port,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database)
        sql = ("SELECT * FROM tb_records WHERE user_id = '%s';" % (user_id))
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        record = Record()
        record.insurance_id = rows[0][5]
        record.image = rows[0][1]
        record.location = rows[0][2]
        record.create_time = rows[0][3]
        return record
