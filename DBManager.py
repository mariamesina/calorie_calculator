import cx_Oracle
import config
import hashlib


class DBManager:
    instance = None

    def __init__(self):
        if not DBManager.instance:
            try:
                self.connection = cx_Oracle.connect(
                    config.username,
                    config.password,
                    config.dsn,
                    encoding=config.encoding)
                self.cur = self.connection.cursor()
                DBManager.instance = self
            except cx_Oracle.Error as error:
                print(error)
        else:
            raise Exception("Multiple instances of a singleton class")

    def close_connection(self):
            if self.connection:
                self.connection.close()

    def log_in(self, username, password):
        passhash = hashlib.md5(password.encode('utf-8')).hexdigest()
        statement = 'select id from accounts where login = \'%s\' and passwordhash = \'%s\'' % (username, passhash)
        result = self.cur.execute(statement)
        account_id = result.fetchone()
        if account_id:
            statement = 'select id from users where id = \'%s\'' % account_id
            self.cur.execute(statement)
            current_account = self.cur.fetchone()[0]
            return current_account
        else:
            return None

    def create_user(self, params):
        statement = 'insert into accounts values(user_id.nextval, \'%s\', \'%s\')' % (params[0], hashlib.md5(params[1].encode('utf-8')).hexdigest())
        self.cur.execute(statement)
        self.connection.commit()

        statement = 'insert into users values(user_id.currval, \'%s\', %d, \'%s\', %d, %d, DEFAULT)' % (params[2], params[3], params[4], params[5], params[6])
        self.cur.execute(statement)
        self.connection.commit()

    def get_foods(self):
        statement = 'select name from foods'
        result = self.cur.execute(statement)
        foods_list = [''.join(i) for i in result.fetchall()]
        return foods_list

    def get_food_info(self, food_name):
        statement = 'select * from foods where name = \'%s\'' % food_name
        result = self.cur.execute(statement)
        food_info = [cell for row in result.fetchall() for cell in row]
        return food_info

    def get_user_info(self, account_id):
        statement = 'select sex, age, weight, height, TO_CHAR(registration_date, \'dd-MM-YYYY\') from users where id = %d' % account_id
        result = self.cur.execute(statement)
        result = result.fetchone()
        return result

    def add_entry(self, account_id, food_id, meal_time, grammage, calories):
        statement = 'insert into history values(%d, %d, TO_DATE(\'%s\', \'YYYY-MM-DD HH24:MI:SS\'), %d, %d)' % (account_id, food_id, meal_time, grammage, calories)
        self.cur.execute(statement)
        self.connection.commit()

    def get_entries(self, account_id, date = None):
        if not date:
            statement = '''select TO_CHAR(h.meal_time, \'DD-MON-YYYY HH24:MI:SS\'), f.name, h.grammage, h.calories 
            from foods f, history h where h.user_id = %d and h.food_id = f.id''' % account_id
        else:
            statement = '''select TO_CHAR(h.meal_time, \'DD-MON-YYYY HH24:MI:SS\'), f.name, h.grammage, h.calories 
                        from foods f, history h 
                        where h.user_id = %d 
                        and h.food_id = f.id 
                        and TO_CHAR(h.meal_time, \'DD-MM-YYYY\') = \'%s\'''' % (account_id, date)
        result = self.cur.execute(statement)
        return result.fetchall()

    def delete_entry(self, account_id, meal_time, food_name, grammage):
        statement = '''delete from history where user_id = %d and meal_time = TO_DATE( \'%s\', 'DD-MON-YYYY HH24:MI:SS') and grammage = %d
        and food_id = (select food_id from foods where name = \'%s\') ''' % (account_id, meal_time, grammage, food_name)
        self.cur.execute(statement)
        self.connection.commit()

    def update_entry(self, account_id, old_meal_time, old_food_name, old_grammage, meal_time,food_name, grammage, calories):
        statement = ''' update history
                            set meal_time = TO_DATE( \'%s\', 'YYYY-MM-DD HH24:MI:SS'),
                            food_id =  (select id from foods where name = \'%s\'),
                            grammage = %d,
                            calories = %d 
                            where user_id = %d 
                            and meal_time = TO_DATE( \'%s\', 'DD-MM-YYYY HH24:MI:SS') 
                            and grammage = %d
                            and food_id = (select id from foods where name = \'%s\')''' % (meal_time, food_name, int(grammage), int(calories), account_id, old_meal_time, int(old_grammage), old_food_name)
        self.cur.execute(statement)
        self.connection.commit()

    def insert_new_food(self, food_name, calories, portion_size):
        statement = 'select count(*) from foods'
        result = self.cur.execute(statement)
        (food_id,) = result.fetchone()
        food_id = int(food_id)+1
        statement = 'insert into foods values(%d, \'%s\', %d, %d)' % (food_id, food_name, int(calories), int(portion_size))
        self.cur.execute(statement)
        self.connection.commit()

    def check_username(self, username):
        statement = 'select id from accounts where login = \'%s\'' % username
        result = self.cur.execute(statement).fetchone()
        return result

    def check_entry(self, account_id, food_id, meal_time, grammage):
        statement = '''select * from history 
        where user_id = %d
        and food_id = %d
        and meal_time = TO_DATE(\'%s\', \'YYYY-MM-DD HH24:MI:SS\')
        and grammage = %d''' % (account_id, food_id, meal_time, grammage)
        result = self.cur.execute(statement).fetchone()
        return result

    @staticmethod
    def get_instance():
        if not DBManager.instance:
            return DBManager()
        else:
            return DBManager.instance
