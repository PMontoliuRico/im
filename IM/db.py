# IM - Infrastructure Manager
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Class to manage DB operations"""
import time

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    import sqlite3 as sqlite
    SQLITE3_AVAILABLE = True
    SQLITE_AVAILABLE = True
except Exception:
    SQLITE3_AVAILABLE = False
    SQLITE_AVAILABLE = False

if not SQLITE_AVAILABLE:
    try:
        import sqlite
        SQLITE_AVAILABLE = True
    except Exception:
        SQLITE_AVAILABLE = False

try:
    import MySQLdb as mdb
    MYSQL_AVAILABLE = True
except Exception:
    MYSQL_AVAILABLE = False

if not MYSQL_AVAILABLE:
    try:
        import pymysql as mdb
        MYSQL_AVAILABLE = True
    except Exception:
        MYSQL_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except Exception:
    MONGO_AVAILABLE = False


# Class to manage DB operations
class DataBase:
    """Class to manage DB operations"""

    db_available = SQLITE_AVAILABLE or MYSQL_AVAILABLE or MONGO_AVAILABLE
    RETRY_SLEEP = 2
    MAX_RETRIES = 15
    MONGO = "MONGO"
    MYSQL = "MySQL"
    SQLITE = "SQLite"
    DB_TYPES = [MYSQL, SQLITE]

    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
        self.db_type = None

    def connect(self):
        """ Function to connect to the DB

            Returns: True if the connection is established correctly
                     of False in case of errors.
        """
        uri = urlparse(self.db_url)
        protocol = uri[0]
        if protocol == "mongodb":
            return self._connect_mongo(uri[0] + "://" + uri[1], uri[2][1:])
        if protocol == "mysql":
            return self._connect_mysql(uri[1], uri[2][1:])
        elif protocol == "file" or protocol == "sqlite" or not protocol:  # sqlite is the default one
            return self._connect_sqlite(uri[2])

        return False

    @staticmethod
    def _get_user_pass_host_port(url):
        username = None
        password = None
        port = None
        if "@" in url:
            parts = url.split("@")
            user_pass = parts[0]
            server_port = parts[1]
            user_pass = user_pass.split(':')
            username = user_pass[0]
            if len(user_pass) > 1:
                password = user_pass[1]
        else:
            server_port = url

        server_port = server_port.split(':')
        server = server_port[0]
        if len(server_port) > 1:
            port = int(server_port[1])

        return username, password, server, port

    def _connect_mongo(self, url, db):
        if MONGO_AVAILABLE:
            client = MongoClient(url)
            self.connection = client[db]
            self.db_type = DataBase.MONGO
            return True
        else:
            return False

    def _connect_mysql(self, url, db):
        if MYSQL_AVAILABLE:
            username, password, server, port = self._get_user_pass_host_port(url)
            if not port:
                port = 3306
            self.connection = mdb.connect(server, username, password, db, port)
            self.db_type = DataBase.MYSQL
            return True
        else:
            return False

    def _connect_sqlite(self, db_filename):
        if SQLITE_AVAILABLE:
            self.connection = sqlite.connect(db_filename)
            self.db_type = DataBase.SQLITE
            return True
        else:
            return False

    def _execute_retry(self, sql, args, fetch=False):
        """ Function to execute a SQL function, retrying in case of locked DB

            Arguments:
            - sql: The SQL sentence
            - args: A List of arguments to substitute in the SQL sentence
            - fetch: If the function must fetch the results.
                    (Optional, default False)

            Returns: True if fetch is False and the operation is performed
                     correctly or a list with the "Fetch" of the results
        """

        if self.connection is None:
            raise Exception("DataBase object not connected")
        else:
            retries_cont = 0
            while retries_cont < self.MAX_RETRIES:
                try:
                    cursor = self.connection.cursor()
                    if args is not None:
                        if self.db_type == DataBase.SQLITE:
                            new_sql = sql.replace("%s", "?").replace("now()", "date('now')")
                        elif self.db_type == DataBase.MYSQL:
                            new_sql = sql.replace("?", "%s")
                        cursor.execute(new_sql, args)
                    else:
                        cursor.execute(sql)

                    if fetch:
                        res = list(cursor.fetchall())
                    else:
                        self.connection.commit()
                        res = True
                    return res
                # If the operational error is db lock, retry
                except sqlite.OperationalError as ex:
                    if str(ex).lower() == 'database is locked':
                        retries_cont += 1
                        # release the connection
                        self.close()
                        time.sleep(self.RETRY_SLEEP)
                        # and get it again
                        self.connect()
                    else:
                        raise ex
                except sqlite.IntegrityError:
                    raise IntegrityError()

    def execute(self, sql, args=None):
        """ Executes a SQL sentence without returning results

            Arguments:
            - sql: The SQL sentence
            - args: A List of arguments to substitute in the SQL sentence
                    (Optional, default None)

            Returns: True if the operation is performed correctly
        """
        if self.db_type == DataBase.MONGO:
            raise Exception("Operation not supported in MongoDB")
        return self._execute_retry(sql, args)

    def select(self, sql, args=None):
        """ Executes a SQL sentence that returns results

            Arguments:
            - sql: The SQL sentence
            - args: A List of arguments to substitute in the SQL sentence
                    (Optional, default None)

            Returns: A list with the "Fetch" of the results
        """
        if self.db_type == DataBase.MONGO:
            raise Exception("Operation not supported in MongoDB")
        return self._execute_retry(sql, args, fetch=True)

    def close(self):
        """ Closes the DB connection """
        if self.connection is None:
            return False
        else:
            try:
                if self.db_type == DataBase.MONGO:
                    self.connection.client.close()
                else:
                    self.connection.close()
                return True
            except Exception:
                return False

    def table_exists(self, table_name):
        """ Checks if a table exists in the DB

            Arguments:
            - table_name: The name of the table

            Returns: True if the table exists or False otherwise
        """
        if self.db_type == DataBase.SQLITE:
            res = self.select('select name from sqlite_master where type="table" and name= %s', (table_name,))
        elif self.db_type == DataBase.MYSQL:
            uri = urlparse(self.db_url)
            db = uri[2][1:]
            res = self.select('SELECT * FROM information_schema.tables WHERE table_name = %s and table_schema = %s',
                              (table_name, db))
        elif self.db_type == DataBase.MONGO:
            return table_name in self.connection.collection_names()
        else:
            return False

        if (len(res) == 0):
            return False
        else:
            return True

    def find(self, table_name, filt=None, projection=None, sort=None):
        """ find elements """
        if self.db_type != DataBase.MONGO:
            raise Exception("Operation only supported in MongoDB")

        if self.connection is None:
            raise Exception("DataBase object not connected")
        else:
            if projection:
                projection.update({'_id': False})
            return list(self.connection[table_name].find(filt, projection, sort=sort))

    def replace(self, table_name, filt, replacement):
        """ insert/replace elements """
        if self.db_type != DataBase.MONGO:
            raise Exception("Operation only supported in MongoDB")

        if self.connection is None:
            raise Exception("DataBase object not connected")
        else:
            res = self.connection[table_name].replace_one(filt, replacement, True)
            return res.modified_count == 1 or res.upserted_id is not None

    def delete(self, table_name, filt):
        """ delete elements """
        if self.db_type != DataBase.MONGO:
            raise Exception("Operation only supported in MongoDB")

        if self.connection is None:
            raise Exception("DataBase object not connected")
        else:
            return self.connection[table_name].delete_many(filt).deleted_count


try:
    class IntegrityError(sqlite.IntegrityError):
        """ Class to return IntegrityError independently of the DB used"""
        pass
except Exception:
    class IntegrityError(Exception):
        pass
