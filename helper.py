from json import load
from os import walk


def __load_madgrades_courses__():
    """
    A private function that loads the output of madGrades API in memory.
    """
    with open('madGradesOutput.json', 'r') as file:
        return load(file)

def course_name_to_uuid_url(courseName: str):
    """
    This function takes in a courseName from the user and returns the uuid and url
    corresponding to that course.

    param: CourseName: a string representing the course
    Return: the uuid and url in that order of the course
    Return: "-1","-1" if the course could not be found in the madgrades API
    """
    courseTitle = courseName.split(':')
    
    courseTitle = courseTitle[0].split()
    courseCode = int(courseTitle[-1])

    courseAbbr = ''.join([e+" " for e in courseTitle[:-1]])
    courseAbbr= courseAbbr[:-1] # removes the final space

    courseAbbr = courseAbbr.upper() #change to uppercase for comparison
    for course in MAD_GRADES_COURSES:
        subjects=course['subjects']
        number=course['number']
        for subject in subjects:
            if courseAbbr in subject['abbreviation'] and courseCode == number:
                return course["uuid"],course["url"]

    
    return "-1", "-1" # could not find the course

def calculateGPA( arr:list):
    """arr is list of the number of students who get a particular grade"""
    GPA = 0
    Grade = 4.0
    total = sum(arr)

    for e in arr:
        GPA += e*Grade    
        Grade-=0.5

    return GPA/total        

def checkFileInDirectory(file:str,directory:str):
    """
    Checks for a file in a directory. 
    file: the file to be found
    directory: the directory to look inside
    Return: True if a file is found, False otherwise.
    """
    for _,_, files in walk(directory,topdown=False):
        if file in files: return True
    return False


# DO NOT RUN THE FUNCTIONS AND CODE BELOW
"""
def getClassesList():
    
    classes = set()
    with open('madGradesOutput.json') as file:
        entries = load(file)

    for entry in entries:
        last = " " + str(entry['number']) + ": "  + str(entry['name'])
        for subject in entry['subjects']:
            className = subject['abbreviation'] + "" + last + "|" + subject['name']
            classes.add(className)
   
    with open('classNames.txt', 'w') as file:
        for className in classes:
            file.write(className)
            file.write('\n') 
              
    
    # print('finished entries\nstarting writing to file')
    print('done')
"""

"""
def getProfessorsList():
    
    names = set()
    # print('loading madgrades courses')
    with open('professorOutput.json') as file:
        entries = load(file)
    # print('finished loading')
    # print('starting looping entries')
    for entry in entries:
        if entry['name'] != None:
            if entry['name'][:4] in ['X / ', 'S / ']:
                entry['name'] = entry['name'][4:]
            names.add(entry['name'])
    # print('finished entries\nstarting writing to file')
    with open('prof_names.txt', 'w') as file:
        for name in names:
            file.write(name)
            file.write('\n')
    print('done')
"""
"""
from database_api import Database
db = Database()
with open('prof_names.txt') as file:
    iter = 1
    for line in file:
        if(iter != 100):
            db.insert_professor(line[:-1])
            iter += 1
        else:
            db.close()
            db._connect()
            db.insert_professor(line[:-1])
            iter = 0
db.close()
print('done')
"""

MAD_GRADES_COURSES = __load_madgrades_courses__()
