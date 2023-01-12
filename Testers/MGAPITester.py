import unittest
import sys
from time import time, time_ns
import MadGradesAPIConnector
import signal
import requests

failures = []
errors = []
test_output = []

# Checks the response time of a specified page
class testResponseTime(unittest.TestCase):
    def test_response_time(self):
        url = '/'
        start_time = time_ns()
        r = requests.request('GET', url=url)
        end_time = time_ns
        # TODO: check time seconds * 1000 * 1000 * 1000
        timeMilSecs = (end_time - start_time) * 1000 * 1000 # Milliseconds
        self.assertAlmostEqual(5000, timeMilSecs ) # Likely doesn't work
        # Response Code: 200 (ok status) 
        self.assertEqual('200', r.status_code)
        pass

# Function to time execution and gather performance metrics ( NOT USED RIGHT NOW)
# def timeit(func):
#     def timed_func(*args, **kwargs):
#         global failures, errors
#         t0 = time()
#         try:
#             out = func(*args, **kwargs)
#             runtime = time() - t0
#         except AssertionError as e:
#             test_output.append(f'FAILED {func.__name__}')
#             failures += [func.__name__]
#             raise e
#         except Exception as e:
#             test_output.append(f'ERROR  {func.__name__}')
#             errors += [func.__name__]
#             raise e
#         test_output.append(f'PASSED {func.__name__}{" "*(22-len(func.__name__))}in {(runtime)*1000:.2f}ms')
#     return timed_func

def retrieveData():
    # Retrieve Courses and Grades ( Heavy Operation, so only want to do once for all tests. )
    return None

class Test1LoadData(unittest.TestCase):
    #@timeit
    def test1_load_data(self):
        print("Executing test1_load_data")
        signal.signal(signal.SIGALRM, MadGradesAPIConnector.get_courses_and_grades) # Setting timeout sig
        signal.alarm(1000) # Defining alotted time till timeout ( in ms)
        try:
            courses_and_grades = MadGradesAPIConnector.get_courses_and_grades()
        except:
            print("Unable to retrieve data after 10 Seconds")
            return 
        
        # We should have a {datatype}
        self.assertIsInstance(courses_and_grades,dict)

        # The elements of the list should be dictionaries
        for element in courses_and_grades:
            self.assertIsInstance(element, dict)

        # We should load exactly X entries? 
        #self.assertEqual(len(courses_and_grades), X)
        
        return courses_and_grades

# class Test2MGConnection(unittest.TestCase):
#     #@timeit
#     def test2_find_data(self):
#         print("Executing test2_find_data")
#         signal.signal(signal.SIGALRM, MadGradesAPIConnector.get_courses_and_grades) # Setting timeout sig
#         signal.alarm(1000) # Defining alotted time till timeout ( in ms )
#         try:
#             courses_and_grades = MadGradesAPIConnector.get_courses_and_grades()
#         except:
#             print("Unable to retrieve data after 10 Seconds")
#             return 
        
#         # We should have a {datatype}
#         self.assertIsInstance(courses_and_grades,dict)

#         # The elements of the list should be dictionaries
#         for element in courses_and_grades:
#             self.assertIsInstance(element, dict)

#         # We should load exactly X entries? 
#         #self.assertEqual(len(courses_and_grades), X)
        
#         return courses_and_grades

if __name__ == '__main__':

    # Should call all tests on main
    unittest.main()
    
    for message in test_output:
        print(message)
    print()
    if not failures and not errors:
        print('\nPassed all tests successfully\n')
    if failures:
        print('The following tests failed:\n' + '\n'.join(failures) + '\n')
    if errors:
        print('The following tests had exceptions when running:\n' + '\n'.join(errors) + '\n')
    if failures or errors:
        print('Please see the Traceback above for where there were issues')
