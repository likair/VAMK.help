# -*- coding: utf-8 -*-
"""
    vamk.api.crawler
    ~~~~~~~~~~~~~~~~
    Implements the Crawler base class.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""
import requests


class Crawler(object):
    """Crawler base class, which has the methods for login the website, request to get HTML documents and parse HTML
    documents to get desired data.
    """

    # Collecting all of the URLs needed
    URLS = {}

    # Encapsulating the request head so as to simulate the real browser
    HEAD = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/48.0.2564.116 Safari/537.36'}

    def __init__(self):
        # Persisting the session across all requests made from the session instance.
        self.session = requests.Session()

    def login(self):
        """Login the website by the provided credentials.
        """
        pass

    def get_html(self):
        """Request the website to get html document.
        """
        pass

    def get_data(self):
        """Parses the html document to get desired data.
        """
        pass
