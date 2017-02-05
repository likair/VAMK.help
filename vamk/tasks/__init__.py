# -*- coding: utf-8 -*-
"""
    vamk.tasks.__init__
    ~~~~~~~~~~~~~~~~~~~
    Implements initialization of the database.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from vamk.tasks.student import Base

# create a database engine
engine = create_engine('mysql://root:Hr9493..@vamk-help.ccjzpaz0yqpf.us-west-2.rds.amazonaws.com/vamk_help_db',
                       echo=True)

# initialize the database
Base.metadata.create_all(engine)

# instantiate a database Session
Session = sessionmaker(bind=engine)
session = Session()
