#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import mechanicalsoup

class GottaCatchEmCourses:
    URL_OES_LOGIN = 'http://oes.rmit.edu.vn/'
    COURSE_STATE = {'UNAVAILABLE': 0,
                    'AVAILABLE'  : 1,
                    'SELECTED'   : 2}
    COURSE_TYPE = {'ROADMAP': 0,
                   'PE'     : 1,
                   'GE'     : 2}

    def __init__(self, username, password):
        self.setup_browser()
        self.open_login_page()
        self.submit_login_credentials(username, password)

    def __del__(self):
        self.close_browser()

    def setup_browser(self):
        DEFAULT_PARSER = 'lxml'

        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config = {'features': DEFAULT_PARSER},
        )
        print("browser initialized...")

    def open_login_page(self):
        #FIXME look for another solution instead of not verifying certificate
        self.browser.open(self.URL_OES_LOGIN, verify = False)
        print("login page loaded...")

    def submit_login_credentials(self, username, password):
        self.browser.select_form('#fm1')
        self.browser['username'] = username
        self.browser['password'] = password
        self.browser.submit_selected()
        print("form submitted...")

    def get_roadmap_courses(self, html_content):
        roadmap_courses_table = html_content.find('table', attrs = {'class': 'tbl-courses'})
        roadmap_courses_table_rows = roadmap_courses_table.find_all('tr')
        roadmap_courses = []

        for index, row in enumerate(roadmap_courses_table_rows):
            if index == 0 or index == 1:
                #skip table headers
                continue
            if (self.is_completed_course(row)):
                #skip completed courses
                continue
            columns = row.find_all('td')
            course_code = columns[1].text.strip()
            if (course_code):   
                course = {} 
                course['code'] = course_code
                course['name'] = columns[2].text.strip()
                course['type'] = self.COURSE_TYPE['ROADMAP']
                course['sem_1'] = self.get_roadmap_course_state(columns[4])
                course['sem_2'] = self.get_roadmap_course_state(columns[5])
                course['sem_3'] = self.get_roadmap_course_state(columns[6])
                roadmap_courses.append(course)
        return roadmap_courses

    def get_elective_courses(self, html_content, type):
        if (type == self.COURSE_TYPE['PE']):
            elective_courses_container = html_content.find('div', id = 'programElective')
            course_type = self.COURSE_TYPE['PE']
        else:
            elective_courses_container = html_content.find('div', id = 'generalElective')
            course_type = self.COURSE_TYPE['GE']

        elective_courses_table = elective_courses_container.find('table')
        elective_courses_table_rows = elective_courses_table.find_all('tr')
        elective_courses = []
        
        for index, row in enumerate(elective_courses_table_rows):
            if index == 0:
                #skipping table headers 
                continue

            course = {}
            columns = row.find_all('td')
            course['code'] = columns[0].text.strip()
            course['name'] = columns[1].text.strip()
            course['type'] = course_type
            course['sem_1'] = self.get_roadmap_course_state(columns[5])
            course['sem_2'] = self.get_roadmap_course_state(columns[6])
            course['sem_3'] = self.get_roadmap_course_state(columns[7])
            elective_courses.append(course)
        return elective_courses

    def get_roadmap_course_state(self, html_content):
        if (html_content.find('input')):
            if (html_content.find('input', checked = 'checked')):
                return self.COURSE_STATE['SELECTED']
            else:
                return self.COURSE_STATE['AVAILABLE']
        else: 
            return self.COURSE_STATE['UNAVAILABLE']

    def get_elective_course_state(self, html_content):
        if (html_content.find('i')):
            return self.COURSE_STATE['AVAILABLE']
        else: 
            return self.COURSE_STATE['UNAVAILABLE']

    def is_completed_course(self, course):
        if (course.find('span', class_ = 'course-success')):
            return True
        else:
            return False

    def close_browser(self):
        self.browser.close()

    def start_tracking(self, refresh_cycle = 60, 
                             semester = 1,
                             tracking_courses = []):
        while True:
            page_content = self.browser.get_current_page()
            courses = self.get_all_courses(page_content)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for course in courses:
                if (course['code'] in tracking_courses and
                    self.is_available(course, semester)):
                    print('[{}] {} IS AVAILABLE!!!'.format(current_time, 
                                                           course['name']))
            time.sleep(refresh_cycle)
            self.browser.refresh()

    def get_all_courses(self, html_content):
        courses = []
        courses.extend(self.get_roadmap_courses(html_content)) 
        courses.extend(self.get_elective_courses(html_content, self.COURSE_TYPE['GE']))
        courses.extend(self.get_elective_courses(html_content, self.COURSE_TYPE['PE']))
        return courses

    def is_available(self, course, tracking_semester):
        if (tracking_semester == 1 and course['sem_1'] == self.COURSE_STATE['AVAILABLE']):
            return True
        elif (tracking_semester == 2 and course['sem_2'] == self.COURSE_STATE['AVAILABLE']):
            return True
        elif (tracking_semester == 3 and course['sem_3'] == self.COURSE_STATE['AVAILABLE']):
            return True
        else:
            return False