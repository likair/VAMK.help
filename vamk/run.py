# -*- coding: utf-8 -*-
"""
    vamk.run
    ~~~~~~~~
    Implements the entry of this application.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from vamk.app import app

# Starting the application on the built-in server.
app.run(host=app.config['HOST'],
        threaded=app.config['THREADED'],
        debug=app.config['DEBUG'],
        port=app.config['PORT'])
