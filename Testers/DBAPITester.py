import unittest
import sys
from time import time
import MadGradesAPIConnector
import signal

failures = []
errors = []
test_output = []

''' 
database_api Tester
    - Test insert operations 
    - Test exception handling
    - Test performance
    - Test connection to database
    - Test disconnection to database
    - Test queries ( search_* )
    - Check for vulnerabilities 
'''

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