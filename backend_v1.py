from database_api import Database
from forms import *
from MadGradesAPIConnector import MadGradesAPIConnector
from flask import Flask, render_template, redirect, url_for,session, request
from helper import *
from flask_login import LoginManager,login_user,logout_user,login_required,UserMixin
import math
from werkzeug.security import check_password_hash,generate_password_hash
from os import walk
import matplotlib.pyplot as plt
import json


def create_app():
    """This function creates the Flask and configures some parameters"""
    app = Flask(__name__) #Creates the falsk APP
    app.config["SECRET_KEY"] = "mySecret" # For security reasons
    app.config['TESTING'] = False #A requirement for Flask logins
    return app

"""Beginning of the Code """
DB = Database() # DB connection. DO NOT CALL ANY PRIVATE VARS/METHODS. Will auto connect
MG = MadGradesAPIConnector() #Connector to Madgrades API
app = create_app()
letterGrades = ['A', 'AB', 'B', 'BC', 'C', 'D', 'F'] # Grades to be used in the classes Page
# CR: see if we still need plt
plt.switch_backend("Agg") #To avoid the closing of the drawing Thread from the main thread
login_manager = LoginManager()
login_manager.init_app(app)


"""The following functions are related to login"""
@app.before_first_request
def init_app():
    # CR: check what happens to multiple users
    logout_user()

class User(UserMixin):
    def __init__(self,user_id,email,password):
        self.id = user_id
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id:str):
    """Flask function that loads in a user. Due to flask requirements, user_id must be a string"""
    user = DB.search_user(userId=user_id)
    # CR: check query result length if it is not equal to 1
    if user ==None or len(user) ==0: return None
    # if user is None or the list is empty then None is returned

    #otherwise if a user was found then return a user object
    user = user[0] # the database returns a single unique user because it was given a userId
    # userId is the primary key
    return User(user_id=user['userId'], email=user["email"],password=user["password"]) 

@login_manager.unauthorized_handler
def unauthorized():
    # CR: create and redirect to error handler page
    return "You are not logged in. Click here to get <a href="+ str("/")+">back to Landing Page</a>"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    if 'recommended_courses' in session:
        session.pop('recommended_courses')
    return redirect("/home")

"""Login related functions end here"""


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/professors", methods=["GET", "POST"])
def professors():
    searchForm = SearchForm(csrf_enabled=False)
    if searchForm.validate_on_submit():
        # Result is a list of dictionary that is returned from the DB. 
        # Each dictionary matches the user query
        results = DB.search_professor(prof_name=searchForm.data['searchInput'])
        """Format of the each result dictionary:

        """
        return render_template("professorsResults.html", searchForm=searchForm, results=results)

    return render_template("professors.html", searchForm=searchForm)


@app.route("/classes", methods=["GET", "POST"])
def classes():
    searchForm = SearchForm(csrf_enabled=False)
    if searchForm.validate_on_submit():
        # Result is a list of dictionary that is returned from the DB. 
        # Each dictionary matches the user query
        results = DB.search_course(courseName=searchForm.data['searchInput'])
        """Format of the each result dictionary:
        {courseID: 2
        "courseName: Comp Sci 506
        courseDept:Computer Sciences}
        """
        # CR: search course department and joint the list
        return render_template("classesResults.html", searchForm=searchForm, results=results)
    return render_template("classes.html", searchForm=searchForm)

@app.route("/login", methods=["GET", "POST"])
def login():
    loginForm = LoginForm(csrf_enabled=False) 
    #the following code is executed when a POST request is submitted
    #with valid data as prescribed by loginForm in forms.py
    if loginForm.validate_on_submit():
        username = loginForm.username.data
        email = loginForm.email.data
        password = loginForm.password.data
        #TODO: create the hash of the password

        #Authenticating the user
        user = DB.search_user(userId=None,name=username,email=email)

        #If the user could not be found in the DB, then they are redirected to the unauthorized route
        if user ==None or len(user)== 0:return login_manager.unauthorized()

        # for u in user:
        #     if check_password_hash( u["password"], password):
        #         u = User(user_id=u['userId'], email=u["email"],password=u["password"])
        #         login_user(u) #adds user to the flask session
        #         return redirect(url_for("home"))
        #Otherwise the user is redirected to the home page
        u = user[0]
        u = User(user_id=u['userId'], email=u["email"],password=u["password"])
        login_user(u) #adds user to the flask session
        return redirect(url_for("home"))
       

    return render_template("login.html", loginForm=loginForm)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    signupForm = SignupForm(csrf_enabled=False)
    #the following code is executed when all input fields are provided by user and passwords match
    if signupForm.validate_on_submit():

        #It is already ensured that the passwords match
        userName = signupForm.username.data
        password = signupForm.password1.data
        # password = generate_password_hash(password=password)
        email = signupForm.email.data
        DB.insert_user(name=userName,role="Student",email=email,password=password)
        #CR: If a user is succesfully logged then let the user know,
        #CR: a signed up user to be also logged in
        return redirect(url_for("home"))
        
    return render_template("signup.html", signupForm=signupForm)

@app.route("/profile")
def profile():
    if "_user_id" in session.keys():
        # expample result for recommended_courses
        # {course_id:courseName, ...}
        
        if "recommended_courses" not in session:
            recommended_courses=get_recommended_courses(session['_user_id'])
            session["recommended_courses"]=recommended_courses
        return render_template("profile.html",recommended_courses=session.get('recommended_courses'))
    return render_template("profile.html")


@app.route("/professorsInfo/<int:profID>", methods=["GET", "POST"])
def professorsInfo(profID):
    searchForm = SearchForm(csrf_enable=False)
    loggedInUserForm = UserDataForm(csrf_enable = False)

    # We have a logged in user
    if "_user_id" in session.keys():
        if loggedInUserForm.validate_on_submit():
            rating = loggedInUserForm.rating.data
            comment = loggedInUserForm.text.data
            if not DB.insert_comment(profId=profID,
                                    comment=comment,
                                    userId=session['_user_id'],
                                    courseId=None,
                                    score=int(rating)):
                return "Could not insert the query"

    result = DB.search_professor(profID=profID)[0]
    comments = DB.search_comments(profId=profID)
    
    # Placeholder values for static professors' rating graphs
    ratings=[0]*5
    
    for comment in comments:
        if 'score' in comment:
            ratings[comment['score']-1]+=1
        
    return render_template("professorsInfo.html", searchForm=searchForm, loggedInUserForm=loggedInUserForm,
        result = result, comments=comments, ratings=ratings)

@app.route("/classesInfo/<int:courseId>", methods=["GET", "POST"])
def classesInfo(courseId):

    searchForm = SearchForm(csrf_enable=False)
    loggedInUserForm = UserDataForm(csrf_enable = False)
    

     #We have a logged in user
    if "_user_id" in session.keys():
        if loggedInUserForm.validate_on_submit():
            rating = loggedInUserForm.rating.data
            comment = loggedInUserForm.text.data
            # print(f"user_id:{session['_user_id']} courseid:{courseId}, rating:{rating}, comment{comment}")
            if not DB.insert_comment(profId=None,comment=comment,userId=session['_user_id'],courseId=courseId,score=int(rating)):
                return "Could not insert the query"

    
    
    #Searching our Database for the course that the user that in the classesResults Page
    # Result is a list of dictionary, with each dictioinary corresponding to a match from
    # the user. Searching CourseId will return a list of size 1
    # It is guaranteed that the course corresponding to the courseId exists
    result = DB.search_course(courseId=courseId)[0]
    courseName = result["courseName"]
    #Comments is a list of dict for that course, it those comments exists
    comments = DB.search_comments(courseId=courseId)

    uuid, url = course_name_to_uuid_url(courseName=courseName)
    if uuid =="-1" : print("Failed with exit code 1")
    #Querying the madgrades API to get all the information about the course

    gradeDistribution=MG.get_json_from_request(url+"/grades")
    # print(gradeDistribution)

    cumulativeTotal = gradeDistribution["cumulative"].get("total")
    studentPercentages = list(round((gradeDistribution["cumulative"][f"{e.lower()}Count"] / cumulativeTotal) * 100,2) for e in letterGrades)
    
    #Grade History Plot
    term_dict=MG.get_json_from_request("https://api.madgrades.com/v1/terms")
    print(term_dict)
    term_dict = dict(reversed(term_dict.items())) # Reversing for frontend
    term_dict.update({'-1' :'Recent Terms'})
    termcode = list(term_dict[str(gradeDistribution["courseOfferings"][e]["termCode"])] for e in range(len(gradeDistribution["courseOfferings"])))
    # grades = specific semester grades ( used in dropdown menu)

    # grades = specific semester grades ( used in dropdown menu)
    grades = [
        [gradeDistribution["courseOfferings"][e]["cumulative"][f"{i.lower()}Count"]
            for i in letterGrades ]
                for e in range(len(gradeDistribution["courseOfferings"]))
    ]
    grades = [round(calculateGPA(e),2) for e in grades]
    # print(termcode)
    # print(grades)
    """
    The next block of check checks if the user selected to filter by a single semester by checking the form object
    in the classesInfo.html returns a semCode param. semCode refers to code used by madgrades to identify a particular
    semester. If semCode is present the following lines assign the semesterGradesDict dictionary and pass it to 
    classesInfo.html once again. On the classesInfo.html check if semesterGradesDict is None before plotting
    """
    semesterGradesDict = None
    displayTerm = 'Cumulative'
    if "semCode" in request.form.keys():
        semCode =int(request.form["semCode"])
        print("semCode Requested")
        if semCode != -1:
            print(f'Semcode: {semCode}')
            for diction in gradeDistribution["courseOfferings"]:
                if diction["termCode"] == semCode:
                    semesterGradesDict = diction["cumulative"]
                    break; 
            total = semesterGradesDict["total"]
            #convert from # to percent for each grade in letterGrades
            # Loads specific grades and reloads page with info
            studentPercentages = list(round((semesterGradesDict[f"{e.lower()}Count"]/total) * 100,2) for e in letterGrades) 
            displayTerm = term_dict.get(f'{semCode}')
            print(f'Display Term = {displayTerm}')
            print("new display should be set")

    print(f'Display Term = {displayTerm}')
    """
    Returns the template for classesInfor
    """
    return render_template("classesInfo.html", searchForm=searchForm, 
    loggedInUserForm=loggedInUserForm, courseName = courseName, courseId=courseId, 
    comments=comments,letterGrades = letterGrades, studentPercentages = studentPercentages,
    term_dict=term_dict, semesterGradesDict = semesterGradesDict, termcode = termcode, grades = grades, displayTerm = displayTerm)

@login_required
def get_recommended_courses(userId=None):
    user_enrollments = DB.search_enrollment(userId=userId)
    if user_enrollments == None or len(user_enrollments) == 0:
        return []

    # get most common department for the user
    departments = {}
    for enrollment in user_enrollments:
        # enrollment is dict of userId, courseId, profId, term, year
        course = DB.search_course(courseId=enrollment['courseId'])
        if course == None or len(course) != 1: return []
        course = course[0]
        departments[course['courseDept']] = 1 if course['courseDept'] not in departments else departments[course['courseDept']] + 1
    max_dept = list(departments.keys())[0]
    for dept in departments:
        if departments[dept] > departments[max_dept]:
            max_dept = dept

    # Get the department courses
    department_courses = DB.search_course(courseDept=max_dept)
    if department_courses == None or len(department_courses) == 0: return []
    
    # search enrollment table and get counts for each course
    course_enrollment_score = {}
    course_rating_score = {}
    for course in department_courses:

        # set default score for enrollments and comments to 0
        course_enrollment_score[course['courseId']] = 0 
        course_rating_score[course['courseId']] = 0

        # make sure there are enrollments before proceeding
        course_enrollments = DB.search_enrollment(courseId=course['courseId'])
        if course_enrollments != None and len(course_enrollments) > 0:

            # sort the enrollments based on when taken
            course_enrollments = sorted(course_enrollments, key=lambda x: (x['year'], x['term'])) 

            # count the enrollments per year and term
            enrollment_counts = {}
            min_year = course_enrollments[0]['year']
            for enrollment in course_enrollments:
                # year gets mapped to first year = 0. Spring semester adds 0.5. Spring second year is 1.5, etc.
                mapped_year = enrollment['year'] - min_year + (0.5 if enrollment['term'].lower() == 'spring' else 0) # get the mapped year
                enrollment_counts[mapped_year] = 1 if mapped_year not in enrollment_counts else enrollment_counts[mapped_year] + 1 # incrememnt or initialize to 1

            # calculate weighted average for enrollments per term
            numerator = []
            demoninator = []
            for mapped_year in enrollment_counts:
                numerator.append(enrollment_counts[mapped_year] * (math.log(mapped_year + 1) + 1))
                demoninator.append(math.log(mapped_year + 1 + 1))

            # save to the specific enrollment score
            course_enrollment_score[course['courseId']] = sum(numerator) / sum(demoninator)

        # make sure there are comments
        course_comments = DB.search_comments(courseId=course['courseId'])
        if course_comments != None and len(course_comments) > 0:
            
            # calculate the mean of the comment scores 
            rating_scores = []
            for comment in course_comments:
                rating_scores.append(comment['score'])

            course_rating_score[course['courseId']] = sum(rating_scores) / len(rating_scores)

    # sort enrollment and rating scores to make percentile easy
    course_enrollment_score = sorted(course_enrollment_score.items(), key=lambda x: x[1])
    course_rating_score = sorted(course_rating_score.items(), key=lambda x: x[1])

    # define helper variables
    num_enrollments = len(course_enrollment_score)
    num_ratings = len(course_rating_score)

    course_total_score = {}
    ENROLLMENT_WEIGHT = 0.5
    RATING_WEIGHT = 0.5

    # calculate percentiles
    for i, courseId in enumerate(course_enrollment_score):
        course_total_score[courseId[0]] = (i / num_enrollments * 100) * ENROLLMENT_WEIGHT
    for i, courseId in enumerate(course_rating_score):
        course_total_score[courseId[0]] += (i / num_ratings * 100) * RATING_WEIGHT

    course_total_score = sorted(course_total_score.items(), key=lambda x: x[1], reverse=True)

    recommendations = {}
    num_added = 0
    # loop through the courses, starting from the "best"
    for i, courseId in enumerate(course_total_score):
        # get the current course from the db
        course = DB.search_course(courseId=courseId[0])[0]
        # empty result would cause error here
        if course==[]:
            continue

        # if the recommended course has not been taken yet
        if not any(course['courseId'] in enrollment for enrollment in user_enrollments):
            recommendations[course['courseId']]=course['courseName']
            num_added += 1
        # if 5 have already been recommended, end the loop
        if num_added >= 5:
            break
            
    return recommendations

if __name__ == "__main__":
    app.run(debug=True)
