import logging
import MySQLdb as mysql

class Cursor():
    def __init__(self, config):
        self.config = dict([(k[6:], config[k]) for k in config if k.startswith('mysql_')])
        if 'port' in self.config:
            self.config['port'] = int(self.config['port'])
        if self.config:
            self.connect_db()

    def connect_db(self):
        self.db = mysql.connect(**self.config)
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

    def insert_sql(self, table_name, data):
        fields, values = [], []
        for k, v in data.items():
            fields.append(k)
            values.append("'%s'" % v)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, ','.join(fields), ','.join(values))
        logging.getLogger().info("Insert sql: %s" % sql)
        return sql

    def execute_insert_sql(self, table_name, data):
        sql = self.insert_sql(table_name, data)
        return self.execute(sql)

    def select_sql(self, table_name, fields, where=None, limit=None):
        if isinstance(where, dict) and where:
            conditions = []
            for k, v in where.items():
                if isinstance(v, list):
                    conditions.append("%s IN (%s)" % (k, ','.join(v)))
                elif isinstance(v, str) or isinstance(v, unicode):
                    conditions.append("%s='%s'" % (k, v))
                elif isinstance(v, int):
                    conditions.append("%s=%s" % (k, v))
 
            sql = "SELECT %s FROM %s WHERE %s" % (','.join(fields), table_name, ' AND '.join(conditions))
        elif not where:
            sql = "SELECT %s FROM %s" % (','.join(fields), table_name)
        else:
            sql = ""
        if limit and isinstance(limit, tuple) and len(limit) == 2:
            sql = "%s LIMIT %s,%s" % (sql, limit[0], limit[1])
        logging.getLogger().info("Select sql: %s" % sql)
        return sql

    def get_one_result(self, table_name, fields, where=None, limit=None):
        sql = self.select_sql(table_name, fields, where, limit)
        if not sql:
            return None
        self.execute(sql)
        result_set = self.fetchone()
        if result_set:
            return dict([(k, '' if result_set[i] is None else result_set[i]) for i,k in enumerate(fields)])
        else:
            return {}

    def get_results(self, table_name, fields, where=None, limit=None):
        sql = self.select_sql(table_name, fields, where, limit)
        self.execute(sql)
        result_sets = self.fetchall()
        return [dict([(k, '' if row[i] is None else row[i]) for i,k in enumerate(fields)]) for row in result_sets]

    def update_sql(self, table_name, data, where, fields=None):
        if not (where and isinstance(where, dict)):
            return ""
        where_cond = ["%s='%s'" % (k, v) for k,v in where.items()]
        if fields:
            conditions = ["%s='%s'" % (k, data[k]) for k in fields]
        else:
            conditions = ["%s='%s'" % (k, data[k]) for k in data]
        sql = "UPDATE %s SET %s WHERE %s" % (table_name, ','.join(conditions), ' AND '.join(where_cond))
        logging.getLogger().info("Update sql: %s" % sql)
        return sql

    def execute_update_sql(self, table_name, data, where, fields=None):
        sql = self.update_sql(table_name, data, where, fields)
        if sql:
            return self.execute(sql)
        else:
            return ""

    def delete_sql(self, table_name, where):
        if not (where and isinstance(where, dict)):
            return ""
        where_cond = ["%s='%s'" % (k, v) for k,v in where.items()]
        sql = "DELETE FROM %s WHERE %s" % (table_name, ' AND '.join(where_cond))
        logging.getLogger().info("Delete sql: %s" % sql)
        return sql

    def execute_delete_sql(self, table_name, where):
        sql = self.delete_sql(table_name, where)
        if sql:
            return self.execute(sql)
        else:
            return ""

    def if_userid_exist(self, user_id):
        result = self.get_one_result('user', ['id'], {'id': user_id})
        if result:
            return True
        else:
            logging.getLogger().error("user '%s' is not exist" % user_id)
            return False

    def if_groupid_exist(self, group_id):
        result = self.get_one_result('group', ['id'], {'id': group_id})
        if result:
            return True
        else:
            logging.getLogger().error("group '%s' is not exist" % group_id)
            return False
