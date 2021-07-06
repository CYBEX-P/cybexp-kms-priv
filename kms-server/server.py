#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file


from pprint import pprint
import traceback

# ref: split into files
#h ttps://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files

conf = load_yaml_file("/config.yaml")
DEBUG = conf["FLASK_DEBUG"]
JWT_SECRET_KEY = conf["FLASK_JWT_SECRET_KEY"]

from flask import Flask
from flask import jsonify
from flask import request
from flask_jwt_extended import JWTManager

import views

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = bytes.fromhex(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_HEADER_NAME"] = "X-Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

jwt = JWTManager(app)

if __name__ == '__main__': # dont define rest of app if we are just importing context

   if not views.generate_system_keys():
      sys.exit("Failed to generate system keys. Exiting.")

   app.add_url_rule('/', methods=['GET'], view_func=views.index)

   # key retrieval
   app.add_url_rule('/get/key/de', methods=['GET'], view_func=views.get_de_key)
   app.add_url_rule('/get/key/ore', methods=['GET'], view_func=views.get_ore_key)
   app.add_url_rule('/get/key/cpabe-pk', methods=['GET'], view_func=views.get_cpabe_pub_key)
   app.add_url_rule('/get/key/cpabe-sk', methods=['POST'], view_func=views.get_org_cpabe_secret)
   app.add_url_rule('/get/attributes', methods=['GET'], view_func=views.list_all_attributes)



   # user management
   app.add_url_rule('/login', methods=['POST'], view_func=views.login)
   # app.add_url_rule('/logout', methods=['POST'], view_func=views.logout)
   app.add_url_rule('/user/create', methods=['POST'], view_func=views.create_user) # will autogenerate sk for user
   app.add_url_rule('/user/me', methods=['GET'], view_func=views.me)

   # key regeneration, use only if keys are accidentally delted for a user. system autgens them at user creation time
   app.add_url_rule('/user/rekey', methods=['POST'], view_func=views.recreate_user_private_keys) # callable by admins only

   # misc
   app.add_url_rule('/get/range/ore', methods=['GET'], view_func=views.get_ore_params)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000 , debug=DEBUG, use_reloader=DEBUG)