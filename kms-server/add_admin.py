#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file
import db_common
from common import normalize_str, hash_pass

from pprint import pprint
import traceback


import os
from flask_jwt_extended import create_access_token



conf = load_yaml_file("/config.yaml")

backed_DB_uri = conf["backed_DB_uri"]
db_name = conf["db_name"]
user_col_name = conf["users_col_name"]

USER_COL = db_common.get_collection(backed_DB_uri,db_name=db_name, col_name=user_col_name)


def find_user(username):
   global USER_COL
   try:
      return USER_COL.find_one({"username":username},{"_id":0})
   except:
      return None


def add_admin(username, password):
   global USER_COL

   try:
      username = normalize_str(username)
      if type(username) != str:
         return False
   except:
      print("Bad username")
      return False

   if find_user(username):
      print("user already exists")
      return False

   salt = os.urandom(32)
   p_hash = hash_pass(password, salt)
   if not p_hash:
      traceback.print_exc()
      return False

   user_record = {"salt": salt, "password": p_hash, "username":username, "admin":True}

   # add user to DB
   try:
      USER_COL.insert_one(dict(user_record))
   except:
      print("failed to insert new user to DB")
      traceback.print_exc()
      return False

   access_token = create_access_token(identity=username)
   pprint({"access_token": access_token, "username": username, "admin": True})
   return True



from server import app # import the context
with app.app_context():
   add_admin(sys.argv[1].strip(), sys.argv[2].strip())




# JWT_SECRET_KEY = conf["FLASK_JWT_SECRET_KEY"]


# from flask import Flask
# from flask import jsonify
# from flask import request
# from flask_jwt_extended import JWTManager


# import views

# app = Flask(__name__)

# app.config["JWT_SECRET_KEY"] = bytes.fromhex(JWT_SECRET_KEY)
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
# app.config["JWT_HEADER_NAME"] = "X-Authorization"
# app.config["JWT_HEADER_TYPE"] = "Bearer"

# jwt = JWTManager(app)