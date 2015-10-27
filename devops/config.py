import MySQLdb as mysql

class Cursor():
    def __init__(self):
        self.connect_db()

    def connect_db(self):
        self.db = mysql.connect(user='liuziping',passwd='liuziping_123456',db='devops',host='192.168.1.251',charset='utf8')
        self.db.autocommit(True)
        self.cur = self.db.cursor()

    def close_db(self):
        self.cur.close()
        self.db.close()

    def execute(self, sql):
        try:
            return self.cur.execute(sql)
        except:
            self.close_db()
            self.connect_db()
            return self.cur.execute(sql)

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()
