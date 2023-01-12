import os
import time
import dotenv
import mysql.connector
from threading import Lock, Thread
from mysql.connector import Error

class Database:
    """
    This is a wrapper class for interacting with a sql database designed for the mad men for Comp Sci 506
    """

    def __init__(self):
        """
        Creates the singleton instance of the Database.
        This loads information from the environment variables, connects to the database, and starts the auto reconnect.
        """
        dotenv.load_dotenv()
        self.__connection = None
        self.__cursor = None
        self.__host = os.environ['DB_HOST']
        self.__database_name = os.environ['DB_NAME']
        self.__user = os.environ['DB_USER']
        self.__password = os.environ['DB_PASSWORD']
        self.__lock = Lock()
        self.__keep_running = True
        self._connect()
        self.__repeater = Thread(None, self._refresh_connection)
        self.__repeater.start()


    def _refresh_connection(self):
        """
        Refreshes the connection to the database by checking a timer.
        """
        start_time = time.time_ns()
        while self.__keep_running: #CR: Increase time
            if time.time_ns() - start_time > 1000000000 * 300: # nano seconds -> 1 * 1000 * 1000 * 1000 = seconds * 300 -> check every 5 minutes
                print('refreshing the db connection')
                start_time = time.time_ns()
                self.__lock.acquire()
                if self.is_connected(): # get rid of old connection if connected
                    self._close()
                while not self.is_connected():
                    self._connect()
                self.__lock.release()
        
    def _execute_search(self, query, arg_list):
        """
        Executes the given search query if valid
        """
        # CR: remove arg_list
        # if self._is_injection_detected(arg_list): # return an empty list if SQL injection is detected
        #     print('fail 1')
        #     return []
        self.__lock.acquire()
        try:
            self.__cursor.execute(query)
            results = self.__cursor.fetchall()
        except Exception as e:
            print(e)
            print('fail 2')
            return []
        self.__lock.release()
        return results

    def _execute_insert(self, query, arg_list):
        """
        Executes the given insert query if valid
        """
        # CR: remove arg_list
        # if self._is_injection_detected(arg_list): # return false if SQL injection
        #     return False
        self.__lock.acquire()
        try:
            self.__cursor.execute(query)
            self.__connection.commit()
        except:
            # CR: print error message
            print(e)
            print('fail 2')
            return False
        self.__lock.release()
        return True

    def _connect(self):
        """
        Connect to the mysql database
        Returns True if successful, False otherwise
        """
        try:
            self.__connection = mysql.connector.connect(
                host = self.__host,
                database = self.__database_name,
                user = self.__user,
                password = self.__password,
                auth_plugin = 'mysql_native_password'
            )
            self.__cursor = self.__connection.cursor()
            print('Successfully connected to the db')
            return True
        except Error as e:
            print(e)
            return False

    def _close(self):
        """
        Closes the connection to the databse
        Returns True upon success, False otherwise
        """
        try :
            self.__cursor.close()
            self.__connection.close()
            return True
        except:
            return False

    def close(self):
        """
        Closes the connection to the database. 
        Called from the user.
        """
        self.__keep_running = False
        self._close()

    def is_connected(self):
        """
        Checks if the class is connected to the database
        Returns True if connected, False otherwise
        """
        if self.__connection == None:
            return False
        return self.__connection.is_connected()

    def search_course(self, courseId=None, courseName=None, courseDept=None):
        """
        Searches for courses with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table

        Return Format: list of dictionary ->
        [
            {
                item1col1: item1val1, 
                item1col2: item1val2
            }, 
            {
                item2col1: item2val1, 
                item2col2: item2val2
            }
        ]
        """
        if courseId == courseName == courseDept == None: # if every argument is None, then return None
            return None

        # query is built below:
        # if the most recent variable was not None, 
        # and at least one of the future variables is not None, 
        # then put an and into the query

        # string searches use mysql like -> % means any number of characters
        # string searches search for exact string in -> '%m L%' like 'Jim Lizzio' -> True and return the row

        query = 'select * from course where ' 
        query += ('courseId = ' + str(courseId)) if courseId != None else ''
        query += (' and ') if courseId != None and (courseName != None or courseDept != None) else ''
        query += ('courseName like \'%' + courseName + '%\'') if courseName != None else ''
        query += (' and ') if courseName != None and courseDept != None else ''
        query += ('courseDept like \'%' + courseDept + '%\'') if courseDept != None else ''
        query += ';'

        arg_list = [courseId, courseName, courseDept]
        results = self._execute_search(query, arg_list)

        to_return = []
        for result in results:
            to_return.append({
                'courseId': result[0],
                'courseName': result[1],
                'courseDept': result[2]
            })
        return to_return

    def search_professor(self, profID=None, prof_name=None):
        """
        Searches for professors with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table

        Return Format: list of dictionary ->
        [
            {
                item1col1: item1val1, 
                item1col2: item1val2
            }, 
            {
                item2col1: item2val1, 
                item2col2: item2val2
            }
        ]
        """
        if profID == prof_name == None: # if every argument is None, then return None
            return None

        # query is built below:
        # if the most recent variable was not None, 
        # and at least one of the future variables is not None, 
        # then put an and into the query

        # string searches use mysql like -> % means any number of characters
        # string searches search for exact string in -> '%m L%' like 'Jim Lizzio' -> True and return the row

        query = 'select * from professor where '
        query += ('profId = ' + str(profID)) if profID != None else ''
        query += (' and ') if profID != None and prof_name != None else ''
        query += ('prof_name like \'%' + prof_name + '%\'') if prof_name != None else ''
        query += ';'
        
        arg_list = [profID, prof_name]
        results = self._execute_search(query, arg_list)

        to_return = []
        for result in results:
            to_return.append({
                'profId': result[0],
                'prof_name': result[1]
            })
        return to_return

    def search_enrollment(self, enrollmentId=None, userId=None, courseId=None, profId=None, term=None, year=None):
        """
        Searches for enrollments with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table

        Return Format: list of dictionary ->
        [
            {
                item1col1: item1val1, 
                item1col2: item1val2
            }, 
            {
                item2col1: item2val1, 
                item2col2: item2val2
            }
        ]
        """
        eq_none = [enrollmentId == None, userId == None, courseId == None, profId == None, term == None, year == None]
        if all(eq_none): # if every argument is None, then return None
            return None

        # query is built below:
        # if the most recent variable was not None, 
        # and at least one of the future variables is not None, 
        # then put an and into the query

        # string searches use mysql like -> % means any number of characters
        # string searches search for exact string in -> '%m L%' like 'Jim Lizzio' -> True and return the row

        query = 'select * from enrollment where '
        query += ('enrollmentId = ' + str(enrollmentId)) if enrollmentId != None else ''
        query += (' and ') if enrollmentId != None and any((not item) for item in eq_none[1:len(eq_none)]) else ''
        query += ('userId = ' + str(userId)) if userId != None else ''
        query += (' and ') if userId != None and any((not item) for item in eq_none[2:len(eq_none)]) else ''
        query += ('courseId = ' + str(courseId)) if courseId != None else ''
        query += (' and ') if courseId != None and any((not item) for item in eq_none[3:len(eq_none)]) else ''
        query += ('profId = ' + str(profId)) if profId != None else ''
        query += (' and ') if profId != None and any((not item) for item in eq_none[4:len(eq_none)]) else ''
        query += ('term like \'%' + term + '%\'') if term != None else ''
        query += (' and ') if term != None and any((not item) for item in eq_none[5:len(eq_none)]) else ''
        query += ('year = ') if year != None else ''
        query += ';'
        
        arg_list = [enrollmentId, userId, courseId, profId, term, year]
        results = self._execute_search(query, arg_list)

        to_return = []
        for result in results:
            to_return.append({
                'enrollmentId': result[0],
                'userId': result[1],
                'courseId': result[2],
                'profId': result[3],
                'term': result[4],
                'year': result[5]
            })
        return to_return

    def search_comments(self, commentId=None, profId=None, comment=None, userId=None, courseId=None, score=None):
        """
        Searches for comments with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table

        Return Format: list of dictionary ->
        [
            {
                item1col1: item1val1, 
                item1col2: item1val2
            }, 
            {
                item2col1: item2val1, 
                item2col2: item2val2
            }
        ]
        """
        eq_none = [commentId == None, profId == None, comment == None, userId == None, courseId == None, score == None]
        if all(eq_none): # if every argument is None, then return None
            return None

        # query is built below:
        # if the most recent variable was not None, 
        # and at least one of the future variables is not None, 
        # then put an and into the query

        # string searches use mysql like -> % means any number of characters
        # string searches search for exact string in -> '%m L%' like 'Jim Lizzio' -> True and return the row

        query = 'select * from comments where '
        query += ('commentId = ' + str(commentId)) if commentId != None else ''
        query += (' and ') if commentId != None and any((not item) for item in eq_none[1:len(eq_none)]) else ''
        query += ('profId = ' + str(profId)) if profId != None else ''
        query += (' and ') if profId != None and any((not item) for item in eq_none[2:len(eq_none)]) else ''
        query += ('comment like \'%' + comment + '%\'') if comment != None else ''
        query += (' and ') if comment != None and any((not item) for item in eq_none[3:len(eq_none)]) else ''
        query += ('userId = ' + str(userId)) if userId != None else ''
        query += (' and ') if userId != None and any((not item) for item in eq_none[4:len(eq_none)]) else ''
        query += ('courseId = ' + str(courseId)) if courseId != None else ''
        query += (' and ') if courseId != None and any((not item) for item in eq_none[5: len(eq_none)]) else ''
        query += ('score = ' + str(score)) if score != None else ''
        query += ';'
        
        arg_list = [commentId, profId, comment, userId, courseId, score]
        results = self._execute_search(query, arg_list)
 
        to_return = []
        for result in results:
            to_return.append({
                'commentId': result[0],
                'profId': result[1],
                'comment': result[2],
                'userId': result[3],
                'courseId': result[4],
                'score':result[5]
            })
        return to_return

    def search_user(self, userId=None, name=None, email=None, password=None, role=None):
        """
        Searches for enrollments with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table

        Return Format: list of dictionary ->
        [
            {
                item1col1: item1val1, 
                item1col2: item1val2
            }, 
            {
                item2col1: item2val1, 
                item2col2: item2val2
            }
        ]
        """
        eq_none = [userId == None, name == None, email == None, password == None, role == None]
        if all(eq_none): # if every argument is None, then return None
            return None

        # query is built below:
        # if the most recent variable was not None, 
        # and at least one of the future variables is not None, 
        # then put an and into the query

        # string searches use mysql like -> % means any number of characters
        # string searches search for exact string in -> '%m L%' like 'Jim Lizzio' -> True and return the row

        query = 'select * from user where '
        query += ('userId = ' + str(userId)) if userId != None else ''
        query += (' and ') if userId != None and any((not item) for item in eq_none[1:len(eq_none)]) else ''
        query += ('name like \'%' + name + '%\'') if name != None else ''
        query += (' and ') if name != None and any((not item) for item in eq_none[2:len(eq_none)]) else ''
        query += ('email like \'%' + email + '%\'') if email != None else ''
        query += (' and ') if email != None and any((not item) for item in eq_none[3:len(eq_none)]) else ''
        query += ('password like \'' + password + '\'') if password != None else ''
        query += (' and ') if password != None and any((not item) for item in eq_none[4:len(eq_none)]) else ''
        query += ('role like \'%' + role + '%\'') if role != None else ''
        query += ';'

        arg_list = [userId, name, email, password, role]
        results = self._execute_search(query, arg_list)
        
        to_return = []
        for result in results:
            to_return.append({
                'userId': result[0],
                'name': result[1],
                'email': result[2],
                'password': result[3],
                'role': result[4]
            })
        return to_return

# if __name__ == '__main__':
#     db = Database()
#     print('main sleeping for 10')
#     time.sleep(10)
#     print('main awake')
#     results = db.search_course(courseName='506')
#     for result in results:
#         print(result)
#     db.close()
           
    def insert_professor(self, profName=None):
        """
        Searches for professors with any of the given information.
        If no information is given, return None
        Otherwise, return the results from the table
        """
        if profName == None:
            return False
        query = f"insert into professor(prof_name) values(\"{profName}\");"

        arg_list = [profName]
        return self._execute_insert(query, arg_list)

    def insert_enrollment(self, year=None, userId=None, courseId=None, profId=None, term=None):
        eq_none = [year == None, profId == None, term == None, userId == None, courseId == None]
        if all(eq_none): 
            return False #CR: executes if all parameters are None

        # CR: NULL vs ''
        year = 'null' if year ==None else year
        profId = 'null' if profId ==None else profId
        courseId = 'null' if courseId ==None else courseId
        userId = 'null' if userId ==None else userId
        term = 'null' if term ==None else term

        query = f"insert into enrollment(year, userId, courseId, profId, term) values({year}, {userId}, {courseId}, {profId}, \"{term}\");"

        arg_list = [userId, courseId, profId, term, year]
        return self._execute_insert(query, arg_list)
    
    def insert_user(self, name=None, role=None, email=None, password=None):
        eq_none = [name == None, role == None, email == None, password == None]
        if all(eq_none):
            return False
        
        name = 'null' if name ==None else name
        role = 'null' if role ==None else role
        email = 'null' if email ==None else email
        password = 'null' if password ==None else password

        query = f"insert into user(name, role, email, password) values(\"{name}\", \"{role}\", \"{email}\", \"{password}\");"
        
        arg_list = [name, email, password, role]
        return self._execute_insert(query, arg_list)

    def insert_course(self, courseName=None, courseDept=None):
        eq_none = [courseName == None, courseDept == None]
        if all(eq_none):
            return False

        courseName = 'null' if courseName ==None else courseName
        courseDept = 'null' if courseDept ==None else courseDept

        query = f"insert into course(courseName, courseDept) values(\"{courseName}\", \"{courseDept}\");"
        
        arg_list = [courseName, courseDept]
        return self._execute_insert(query, arg_list)

    def insert_comment(self, userId, comment, score, profId=None,courseId=None):
        eq_none = [profId == None, comment == None, userId==None, courseId==None, score==None]
        if all(eq_none) or not comment or not userId or not score:
            return False
        
        profId = 'null' if profId ==None else profId
        courseId = 'null' if courseId ==None else courseId
       
        query = f"insert into comments(profId, comment, userId, courseId, score) values({profId}, \"{comment}\",{userId},{courseId},{score});"
        
        arg_list = [profId, comment, userId, courseId, score]
        return self._execute_insert(query, arg_list)
