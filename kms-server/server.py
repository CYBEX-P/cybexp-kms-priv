#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback

# ref: split into files
#h ttps://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files

DEBUG = True


import views
from flask import Flask

app = Flask(__name__)

app.add_url_rule('/', methods=['GET'], view_func=views.index)
app.add_url_rule('/create/group', methods=['GET'], view_func=views.create_group)

if __name__ == '__main__':
   app.run(host="0.0.0.0", debug=DEBUG, use_reloader=DEBUG)