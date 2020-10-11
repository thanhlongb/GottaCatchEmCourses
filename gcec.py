#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import json
import pickle
import requests
import mechanicalsoup

from pushbullet import PushBullet

class GottaCatchEmCourses:
    URL_OES_LOGIN = 'http://oes.rmit.edu.vn/'
    URL_OES_PAGE = 'https://oes.rmit.edu.vn/enrolment'
    URL_SUCCESSFUL_SUBMISSION = 'https://oes.rmit.edu.vn/enrolment/submit'
    CourseState = {'UNAVAILABLE': 0,
                   'AVAILABLE': 1,
                   'SELECTED': 2}
    COURSE_TYPE = {'ROADMAP': 0,
                   'PE': 1,
                   'GE': 2}
    DEFAULT_PARSER = 'lxml'

    browser = None
    pushbullet = None

    def __init__(self, username, password, pushbullet_access_token):
        self.setup_browser()
        self.pushbullet = PushBullet(pushbullet_access_token)
        try:
            self.load_cookie()
        except Exception:
            self.open_login_page()
            self.submit_login_credentials(username, password)
            self.save_cookie()

    def __del__(self):
        self.close_browser()

    def setup_browser(self):
        self.browser = mechanicalsoup.StatefulBrowser(soup_config={'features': self.DEFAULT_PARSER})
        print("browser initialized...")

    def open_login_page(self):
        # FIXME look for another solution instead of not verifying certificate
        self.browser.open(self.URL_OES_LOGIN, verify=False)
        print("login page loaded...")

    def open_oes_page(self):
        self.browser.open(self.URL_OES_PAGE, verify=False)
        print("oes page loaded...")

    def submit_login_credentials(self, username, password):
        self.browser.select_form('.form-horizontal')
        self.browser['_username'] = username
        self.browser['_password'] = password
        self.browser.submit_selected()
        print("form submitted...")

    def get_roadmap_courses(self, html_content):
        roadmap_courses_table = html_content.find('table', attrs={'class': 'tbl-courses'})
        roadmap_courses_table_rows = roadmap_courses_table.find_all('tr')
        roadmap_courses = []

        for row in roadmap_courses_table_rows[2:]:
            # first and second row is skipped since they're table header
            if self.is_completed_course(row):
                # skip completed courses
                continue
            columns = row.find_all('td')
            # quick hack, TODO fix this
            course_code = ''
            try:
                course_code = re.search('[A-Z]+[0-9]+', columns[1].text).group(0)
            except AttributeError:
                pass
            if course_code:
                course = {'code': course_code, 'name': columns[2].text.strip(),
                          'type': self.COURSE_TYPE['ROADMAP'],
                          'sem_1': self.get_roadmap_course_state(columns[4]),
                          'sem_2': self.get_roadmap_course_state(columns[5]),
                          'sem_3': self.get_roadmap_course_state(columns[6])}
                roadmap_courses.append(course)
        return roadmap_courses

    def get_elective_courses(self, html_content, course_type):
        if course_type == self.COURSE_TYPE['PE']:
            elective_courses_container = html_content.find('div', id='programElective')
            course_type = self.COURSE_TYPE['PE']
        else:
            elective_courses_container = html_content.find('div', id='generalElective')
            course_type = self.COURSE_TYPE['GE']

        elective_courses_table = elective_courses_container.find('table')
        elective_courses_table_rows = elective_courses_table.find_all('tr')
        elective_courses = []

        for row in elective_courses_table_rows[1:]:
            # first row is skipped since it's table header
            course = {}
            columns = row.find_all('td')
            # quick hack, TODO fix this
            course_code = ''
            try:
                course_code = re.search('[A-Z]+[0-9]+', columns[0].text).group(0)
            except AttributeError:
                print("regex couldn't find course code")
                pass
            course['code'] = course_code
            course['name'] = columns[1].text.strip()
            course['type'] = course_type
            course['sem_1'] = self.get_elective_course_state(columns[5])
            course['sem_2'] = self.get_elective_course_state(columns[6])
            course['sem_3'] = self.get_elective_course_state(columns[7])
            elective_courses.append(course)
        return elective_courses

    def get_roadmap_course_state(self, html_content):
        if html_content.find('input'):
            if html_content.find('input', checked='checked'):
                return self.CourseState['SELECTED']
            else:
                return self.CourseState['AVAILABLE']
        else:
            return self.CourseState['UNAVAILABLE']

    def get_elective_course_state(self, html_content):
        if html_content.find('i'):
            return self.CourseState['AVAILABLE']
        else:
            return self.CourseState['UNAVAILABLE']

    def is_completed_course(self, course):
        if course.find('span', class_='course-success'):
            return True
        else:
            return False

    def close_browser(self):
        self.browser.close()

    def start_tracking(self, refresh_cycle=60, semester=1, tracking_courses=[]):
        while True:
            self.open_oes_page()
            page_content = self.browser.get_current_page()
            courses = self.get_all_courses(page_content)
            enrollable_courses = list()
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for course in courses:
                if course['code'] in tracking_courses and self.is_available(course, semester):
                    enrollable_courses.append(course)
            self.enroll(enrollable_courses, semester)
            self.parse_enroll_result()
            time.sleep(refresh_cycle)
            print('browser refreshed...')

    def parse_enroll_result(self):
        submission_response = json.loads(self.browser.get_current_page().text)
        if submission_response['success'] == True:
            print("Successfully enrolled in the courses")
            exit(0)
        else:
            print(submission_response['message'])
        
    def get_all_courses(self, html_content):
        courses = []
        courses.extend(self.get_roadmap_courses(html_content))
        courses.extend(self.get_elective_courses(html_content, self.COURSE_TYPE['GE']))
        courses.extend(self.get_elective_courses(html_content, self.COURSE_TYPE['PE']))
        return courses

    def is_available(self, course, tracking_semester):
        if tracking_semester == 1 and course['sem_1'] == self.CourseState['AVAILABLE']:
            return True
        elif tracking_semester == 2 and course['sem_2'] == self.CourseState['AVAILABLE']:
            return True
        elif tracking_semester == 3 and course['sem_3'] == self.CourseState['AVAILABLE']:
            return True
        else:
            return False

    def is_enrollment_succeed(self):
        return self.browser.get_url() == self.URL_SUCCESSFUL_SUBMISSION

    def enroll(self, courses, semester):
        for course in courses:
            course_checkbox_name = 'form[courses][{}-SEM{}]'.format(course['code'], semester)
            form = self.browser.select_form('#frmEnrolment')
            form.set_checkbox({course_checkbox_name: True}, False)
            print('{} checkbox checked.'.format(course['name']))
        self.browser.submit_selected()
        print("enrollment submitted...")

    def save_cookie(self):
        pickle.dump(self.browser.get_cookiejar(), open("cookie.txt", 'wb'))
        print('cookie saved...')

    def load_cookie(self):
        cookie_jar = pickle.load(open("cookie.txt", 'rb'))
        self.browser.set_cookiejar(cookie_jar)
        print('cookie loaded...')
