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


# key_gen
app.add_url_rule('/gen/key/de', methods=['POST'], view_func=views.gen_de_key)
app.add_url_rule('/gen/key/ore', methods=['POST'], view_func=views.gen_ore_key)
app.add_url_rule('/gen/key/cpabe-pk-mk', methods=['POST'], view_func=views.gen_cpabe_master_keys_endpoint)
app.add_url_rule('/gen/key/cpabe-sk', methods=['POST'], view_func=views.create_org_cpabe_secret)

# key retrieval
app.add_url_rule('/get/key/de', methods=['GET'], view_func=views.get_de_key)
app.add_url_rule('/get/key/ore', methods=['GET'], view_func=views.get_ore_key)
app.add_url_rule('/get/key/cpabe-pk', methods=['GET'], view_func=views.get_cpabe_pub_key)
app.add_url_rule('/get/key/cpabe-sk', methods=['GET'], view_func=views.get_org_cpabe_secret)

app.add_url_rule('/get/attributes', methods=['GET'], view_func=views.list_all_attributes)


if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000 , debug=DEBUG, use_reloader=DEBUG)