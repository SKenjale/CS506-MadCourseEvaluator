
#DO NOT RUN THIS CODE
"""
from database_api import Database
db = Database()
with open('classNames.txt') as file:
    iter = 1
    for line in file:
        x = line.split("|")
        if(iter != 100):
            db.insert_course(x[0], x[1])
            iter += 1
        else:
            db.close()
            db._connect()
            db.insert_course(x[0], x[1])
            iter = 0
db.close()
print('done')
"""