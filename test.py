import PySide2.QtCore
import cx_Oracle
import config

# # Prints PySide2 version
# # e.g. 5.11.1a1
# print(PySide2.__version__)
#
# # Gets a tuple with each version component
# # e.g. (5, 11, 1, 'a', 1)
# print(PySide2.__version_info__)
#
# # Prints the Qt version used to compile PySide2
# # e.g. "5.11.2"
# print(PySide2.QtCore.__version__)
#
# # Gets a tuple with each version components of Qt used to compile PySide2
# # e.g. (5, 11, 2)
# print(PySide2.QtCore.__version_info__)
#
# connection = None
# try:
#     connection = cx_Oracle.connect(
#         config.username,
#         config.password,
#         config.dsn,
#         encoding=config.encoding)
#
#     # show the version of the Oracle Database
#     print(connection.version)
#     c = connection.cursor()
#     c.execute("""declare
# v_sql LONG;
# begin
#
# v_sql:='CREATE TABLE accounts(
#     login VARCHAR(25) PRIMARY KEY,
#     passwordHash VARCHAR(40) NOT NULL )';
# execute immediate v_sql;
#
# EXCEPTION
#     WHEN OTHERS THEN
#       IF SQLCODE = -955 THEN
#         NULL; -- suppresses ORA-00955 exception
#       ELSE
#          RAISE;
#       END IF;
# END;
# """)
# except cx_Oracle.Error as error:
#     print(error)
# finally
#     # release the connection
#     if connection:
#         connection.close()

import hashlib
print(hashlib.md5("cana".encode('utf-8')).hexdigest())

