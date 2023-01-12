import requests
import json


class MadGradesAPIConnector:
    def __init__(self, token="7b92a3d962cc4020a805f4cfae15252e"):
        self.header = {"Authorization": "Token token=" + token}
        self.address = "https://api.madgrades.com/v1/"

    def get_json_from_request(self, url):
        '''
        get the content of url using requests

        :param url: the API url
        :return: the results in json format
        '''
        content_json = requests.get(url, headers=self.header).content.decode()
        return json.loads(content_json)

    def get_all_items(self, item_name=None):
        '''
        collect information of all subjects using MadGradesAPI

        :return: A list of dictionaries and each dict represents one item
            subject keys:   code -> subject name string (example: "Surgery")
                            name -> code string (example: "936")
                            abbreviation -> abbreviation string
                            courseUrl -> url of courses under this subject
            instructor keys:    id -> instructor id in integer (example: 105628)
                                name -> instructor name in uppercase  (example: "PETER MORAN")
                                abbreviation -> abbreviation string
                                url -> url of this exact instructor
            course keys:    uuid -> course id string
                            name -> standard course name string
                            names -> name list (other names for this course)
                            number -> course number
                            subjects -> corresponding subjects (subject+number is the course code, example: COMP SCI 506)
                            url -> url of this exact course
        '''
        try:
            assert item_name in ["subjects", "instructors", "courses"]
        except:
            print("Invalid item name")
            return None

        items = []
        next_page_url = self.address + item_name + "?page=1"
        # go through all pages
        while True:
            content_dict = self.get_json_from_request(next_page_url)
            items += content_dict["results"]
            next_page_url = content_dict["nextPageUrl"]
            if next_page_url == None:
                total_count = content_dict["totalCount"]
                break
            print(len(items))
        assert total_count == len(items)

        return items


# this method is only an example,
# pulling all data at once requires long processing time
def get_courses_and_grades():
    '''
    use connector to get all courses and search for grades distribution of each course

    :return: a course-grades dictionary
        key: course uuid
        value: grades dictionary
            grades keys:    courseUuid
                            cumulative: cumulative grade numbers of all time (example:
                                                        {"total": 3777,"aCount": 3470,"abCount": 148,...})
                            courseOfferings: a list of grade numbers by term, for each term keys:{"termCode",
                                                                                        "cumulative","sections"}
    '''
    mg = MadGradesAPIConnector()
    # get all courses
    course_grades_dict = {}
    courses = mg.get_all_items("courses")
    #for course in courses:
    #    course_grades_dict = {**course_grades_dict,
    #                          course['uuid']: mg.get_json_from_request(course['url'] + "/grades")}

    return courses

if __name__ == '__main__':
    # with open('madGradesOutput.json', 'w') as file:
    #     json.dump(get_courses_and_grades(),file)

    with open('madGradesOutput.json', 'r') as file:
        print(json.load(file)[100])
        """The format of each file ine is:
        uuid:


        """