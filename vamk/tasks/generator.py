# -*- coding: utf-8 -*-
"""
    vamk.tasks.generator
    ~~~~~~~~~~~~~~~~~~~~
    Implements courses calendar database generating.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import io
import json
import time

import os
import re
import requests


class Generator:
    """Downloads calendars from the school server based on group codes and converts them to the courses events list that
    can be resolved by FullCalendar.

    """
    CALENDAR_DIR = '../data/calendar_db/'
    # Calendar for department of technology.
    TECHNOLOGY_CALENDAR_DB = CALENDAR_DIR + 'technology.ics'
    # Calendar for department of business.
    BUSINESS_CALENDAR_DB = CALENDAR_DIR + 'business.ics'
    # Total courses json, the final courses calendar database.
    TOTAL_COURSES_JSON = CALENDAR_DIR + 'courses.json'

    # The group codes of department of business from the website
    # (http://www.bet.puv.fi/studies/lukujarj/2015-2016/K16/week043.htm).
    BUSINESS_GROUP_CODES_SOURCE = u'''
    T-IB-1-1:1. year, IB, International Business, Group 1    T-IB-1-2:1. year, IB, International Business, Group 2    T-IB-2-1:2. year, IB, International Business
    T-IB-2-2:2. year, IB, International Business    T-IB-3-1:3. year, International Business    T-IB-3-2:3. year, International Business
    T-IB-EX:IB Exchange students    T-IB-EX1:IB Exchange students    T-IB-EX2:IB Exchange students
    T-LT-1-1:1. vuosi, LT - ryhmä 1    T-LT-1-2:1. Vuosi, LT - ryhmä 2    T-LT-1-3:1. vuosi, LT - ryhmä 3
    T-LT-1-4:1. vuosi, LT- ryhmä 4    T-LT-1V:Monimuoto - 1. vuosi, Liiketalous    T-LT-2K:2. vuosi, LT - KV kaupan sv
    T-LT-2M:2. vuosi, LT - Markkinoinnin sv    T-LT-2O:2. vuosi, LT - Oikeushallinnon sv    T-LT-2T1:2. vuosi, LT - Taloushallinnon sv
    T-LT-2T2:2. vuosi, LT - Taloushallinnon sv    T-LT-2VT:Monimuoto - 2. vuosi, Liiketalous    T-LT-2VT1:T-LT-2VT1
    T-LT-2VT2:T-LT-2VT2    T-LT-3K1:3. vuosi, LT - KV kaupan sv    T-LT-3K2:3. vuosi, LT - KV kaupan sv
    T-LT-3M:3. vuosi, LT - Markkinoinnin sv    T-LT-3O:3. vuosi, LT - Oikeushallinnon sv    T-LT-3T:3. vuosi, LT - Taloushallinnon sv
    T-LT-3VKM:Monimuoto - 3. vuosi, Liiketalous    T-LY-1Y:Ylempi AMK-tutkinto, 1. vuosikurssi    T-TK-1-1:1. vuosi, Tiet.käs. - ryhmä 1
    T-TK-1-2:1. vuosi, Tiet.käs. - ryhmä 2    T-TK-2DI:2. vuosi, Tiet.käs. - Digitaaliset yrpalv    T-TK-2TH:2. vuosi, Tiet.käs. - Tietohallinto
    T-TK-3DI:3. vuosi, Tiet.käs. - digitaaliset yrityspalvelut    T-TK-3TH:3. vuosi, Tiet.käs. - Tietohallinto     
    '''

    # The group codes of department of technology from the website
    # (http://www.bet.puv.fi/schedule/P4_15_16/week044.htm).
    TECHNOLOGY_GROUP_CODES_SOURCE = u'''
    I-EM-3N:Energy Management Gr 3N    I-EM-4N:Energy Management Gr 4N    I-EY-1N1:Energia- ja ympäristötekniikka ry 1N1
    I-EY-1N2:Energia- ja ympäristötekniikka ry 1N2    I-EY-1N3:Energia- ja ympäristötekniikka ry 1N3    I-EY-1N4:Energia- ja ympäristötekniikka ry 1N4
    I-EY-1V1:Energia- ja ympäristötekniikka ry 1V1    I-EY-1V2:Energia- ja ympäristötekniikka ry 1V2    I-EY-2N1:Energia- ja ympäristötekniikka ry 2N1
    I-EY-2N2:Energia- ja ympäristötekniikka ry 2N2    I-EY-2N3:Energia- ja ympäristötekniikka ry 2N3    I-EY-2N4:Energia- ja ympäristötekniikka ry 2N4
    I-IT-1N1:Information Technology Gr 1N1    I-IT-1N2:Information Technology Gr 1N2    I-IT-1N3:Information Technology Gr 1N3
    I-IT-1N4:Information Technology Gr 1N4    I-IT-2N1:Information Technology Gr 2N1    I-IT-2N2:Information Technology Gr 2N2
    I-IT-3N1:Information Technology Gr 3N1    I-IT-3N2:Information Technology Gr 3N1    I-IT-4N1:Information Technology Gr 4N1
    I-IT-4N2:Information Technology Gr 4N2    I-KT-1N1:Kone- ja tuotantotekniikka ry 1N1    I-KT-1N2:Kone- ja tuotantotekniikka ry 1N2
    I-KT-1N3:Kone- ja tuotantotekniikka ry 1N3    I-KT-1N4:Kone- ja tuotantotekniikka ry 1N4    I-KT-2N1:Kone- ja tuotantotekniikka ry 2N1
    I-KT-2N2:Kone- ja tuotantotekniikka ry 2N2    I-KT-2N3:Kone- ja tuotantotekniikka ry 2N3    I-KT-2N4:Kone- ja tuotantotekniikka ry 2N4
    I-KT-2V1:Kone- ja tuotantotekniikka ry 2V1    I-KT-2V2:Kone- ja tuotantotekniikka ry 2V2    I-KT-3N2:Kone- ja tuotantotekniikka ry 3N2
    I-KT-3N3:Kone- ja tuotantotekniikka ry 3N3    I-KT-3N4:Kone- ja tuotantotekniikka ry 3N4    I-KT-3N5:Kone- ja tuotantotekniikka ry 3N5
    I-KT-4N1:Kone- ja tuotantotekniikka ry 4N1    I-KT-4N2:Kone- ja tuotantotekniikka ry 4N2    I-KT-4N3:Kone- ja tuotantotekniikka ry 4N3
    I-KT-4N4:Kone- ja tuotantotekniikka ry 4N4    I-KT-4V1:Kone- ja tuotantotekniikka ry 4V1    I-KT-4V3:Kone- ja tuotantotekniikka ry 4V3
    I-MX-4N:Energy Management MX Gr 4N    I-RJ-1Y1:Rakentamisen ylempi amk, 1Y1    I-RJ-1Y2:Rakentamisen ylempi amk, 1Y2
    I-RT-1N1:Rakennustekniikka ry 1N1    I-RT-1N2:Rakennustekniikka ry 1N2    I-RT-1N3:Rakennustekniikka ry 1N3
    I-RT-1N4:Rakennustekniikka ry 1N4    I-RT-1V1:Rakennustekniikka ry 1V1    I-RT-1V2:Rakennustekniikka ry 1V2
    I-RT-2N1:Rakennustekniikka ry 2N1    I-RT-2N2:Rakennustekniikka ry 2N2    I-RT-2N3:Rakennustekniikka ry 2N3
    I-RT-2N4:Rakennustekniikka ry 2N4    I-RT-3N1:Rakennustekniikka ry 3N1 (rakennetekn.)    I-RT-3N2:Rakennustekniikka ry 3N2 (tuotantotekniikka)
    I-RT-3V1:Rakennustekniikka ry 3V1    I-RT-3V2:Rakennustekniikka ry 3V2    I-RT-4N1:Rakennustekniikka ry 4N1
    I-RT-4N2:Rakennustekniikka ry 4N2    I-ST-1N1:Sähkötekniikka ry 1N1    I-ST-1N2:Sähkötekniikka ry 1N2
    I-ST-1N3:Sähkötekniikka ry 1N3    I-ST-1N4:Sähkötekniikka ry 1N4    I-ST-1N5:Sähkötekniikka ry 1N5
    I-ST-1N6:Sähkötekniikka ry 1N6    I-ST-2N1:Sähkötekniikka ry 2N1    I-ST-2N2:Sähkötekniikka ry 2N2
    I-ST-2N3:Sähkötekniikka ry 2N3    I-ST-2N4:Sähkötekniikka ry 2N4    I-ST-2V1:Sähkötekniikka ry 2V1
    I-ST-2V2:Sähkötekniikka ry 2V2    I-ST-3N1:Sähkötekniikka ry 3N1    I-ST-3N2:Sähkötekniikka ry 3N2
    I-ST-3N3:Sähkötekniikka ry 3N3    I-ST-3N4:Sähkötekniikka ry 3N4    I-ST-4N1:Sähkötekniikka ry 4N1
    I-ST-4N2:Sähkötekniikka ry 4N2    I-ST-4N3:Sähkötekniikka ry 4N3    I-ST-4N4:Sähkötekniikka ry 4N4
    I-ST-4V:Sähkötekniikka ry 4V    I-TT-1N1:Tietotekniikka ry 1N1    I-TT-1N2:Tietotekniikka ry 1N2
    I-TT-1N3:Tietotekniikka ry 1N3    I-TT-1N4:Tietotekniikka ry 1N4    I-TT-2N1:Tietotekniikka ry 2N1
    I-TT-2N2:Tietotekniikka ry 2N2    I-TT-2V:Tietotekniikka ry 2V    I-TT-3N1:Tietotekniikka ry 3N1
    I-TT-3N2:Tietotekniikka ry 3N2    I-TT-4N1:Tietotekniikka ry 4N1    I-TT-4N2:Tietotekniikka ry 4N2
    I-YT-3N1:Ympäristöteknologia ry 3N1    I-YT-3N2:Ympäristöteknologia ry 3N2    I-YT-4N:Ympäristöteknologia ry 4N
    I-YT-4V:Ympäristöteknologia ry 4V
    '''

    def __init__(self):
        """Does some initialization.
        """
        # Extracting the group codes information from the source.
        self.business_group_codes = self.get_business_group_codes()
        self.technology_group_codes = self.get_technology_group_codes()

        # Creating the calendar directory if not exits.
        if not os.path.exists(Generator.CALENDAR_DIR):
            os.makedirs(Generator.CALENDAR_DIR)

    def get_business_group_codes(self):
        """Gets the group codes of the department of business by regex.

        :return: business_group_codes: a list: [GROUP_CODE1, GROUP_CODE2...]
        """
        business_group_codes = re.findall(r'(T-\S*?):', Generator.BUSINESS_GROUP_CODES_SOURCE)
        return business_group_codes

    def get_technology_group_codes(self):
        """Gets the group codes of the department of technology by regex.

        :return: technology_group_codes: a list: [GROUP_CODE1, GROUP_CODE2...]
        """
        technology_group_codes = re.findall(r'(I-\S*?):', Generator.TECHNOLOGY_GROUP_CODES_SOURCE)
        return technology_group_codes

    def get_calendar_source(self, group_code):
        """Download the *.ics from the school server.

        :param group_code: a list: [GROUP_CODE1, GROUP_CODE2...]

        :return:
        """
        # Building the calendar url by the first Character of the group code.
        # For the department of technology.
        if group_code[0] == 'T':
            calendar_url = 'http://www.bet.puv.fi/studies/lukujarj/iCal/' + group_code + '.ics'
        # group_code[0] == 'I', for the department of business.
        else:
            calendar_url = 'http://www.bet.puv.fi/schedule/ical/' + group_code + '.ics'

        # Getting the calendar from the school server.
        r = requests.get(calendar_url)
        return r.text

    def get_business_calendar(self):
        """Downloads the calendar of department of business and write to the file.
        """
        with io.open(Generator.BUSINESS_CALENDAR_DB, 'w', encoding='utf-8') as f:
            for group_code in self.business_group_codes:
                f.write(self.get_calendar_source(group_code))

    def get_technology_calendar(self):
        """Downloads the calendar of department of technology and write to the file.
        """
        with io.open(Generator.TECHNOLOGY_CALENDAR_DB, 'w', encoding='utf-8') as f:
            for group_code in self.technology_group_codes:
                f.write(self.get_calendar_source(group_code))

    @staticmethod
    def get_all_courses_with_group_code_list():
        """Builds the courses calendar database.

        :return:
        """
        # courses is a dict: {COURSE_NAME1:{GROUP_CODE1:EVENTS_LIST1, GROUP_CODE2:EVENTS_LIST2...}
        courses = {}

        # Converting ics to the format of json that can be resolved by fullcalendar.
        for cd in [Generator.BUSINESS_CALENDAR_DB, Generator.TECHNOLOGY_CALENDAR_DB]:
            with io.open(cd, 'r', encoding='utf-8') as f:
                calendar_source = f.read()
                # Building the regex pattern.
                # Parsing the data like [('2016', '04', '04', '11', '30', '2016', '04', '04', '14', '15', 'A3006',
                # 'I-EM-3N', 'Basics of Mathematical Software')]
                pattern = r'BEGIN.*?DTSTART:(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})\d{2}Z.*?DTEND:(\d{4})' \
                          r'(\d{2})(\d{2})T(\d{2})(\d{2})\d{2}Z.*?LOCATION:(.*?)\n.*?SUMMARY:\[(.*?):.*' \
                          r'?\]\s(.*?)\s?\n.*?END:VEVENT'

                # Finding all strings matches the pattern.
                # DOTALL flag means '.' matches any character including a newline.
                # all_courses_calendars is a list containing tuples.
                all_courses_calendars = re.findall(pattern, calendar_source, re.DOTALL)

                # Further processing the data to populate courses dict.
                for c in all_courses_calendars:
                    course_name = c[12]
                    group_code = c[11]
                    location = c[10]
                    event = {'title': course_name + ', ' + group_code + ', ' + location,
                             'start': c[0] + '-' + c[1] + '-' + c[2] + 'T' + c[3] + ':' + c[4] + 'Z',
                             'end': c[5] + '-' + c[6] + '-' + c[7] + 'T' + c[8] + ':' + c[9] + 'Z'}

                    if courses.has_key(course_name):
                        if courses[course_name].has_key(group_code):
                            courses[course_name][group_code].append(event)
                        else:
                            courses[course_name][group_code] = [event]
                    else:
                        courses[course_name] = {}
                        courses[course_name][group_code] = [event]

        # Writing to the file to persist the courses calendar database.
        with io.open(Generator.TOTAL_COURSES_JSON, 'w', encoding='utf-8') as f:
            f.write(json.dumps(courses, ensure_ascii=False))


if __name__ == '__main__':
    # Calculating the time consumed in this generating.
    start = time.time()
    g = Generator()
    g.get_business_calendar()
    g.get_technology_calendar()
    g.get_all_courses_with_group_code_list()
    end = time.time()

    print 'OK!' + str(round((end - start), 3)) + 's.'
