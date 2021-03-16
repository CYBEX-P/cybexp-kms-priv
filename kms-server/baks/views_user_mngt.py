#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file
import db_common

from pprint import pprint
import traceback

import os
import hashlib
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

#from flask import render_template
from flask import Response, request
from flask import send_file


from cpabew import CPABEAlg
from cpabe_key_gen import gen_cpabe_master_keys, gen_cpabe_org_secret_key, load_cpabe_org_secret_key_from_name, load_cpabe_master_keys
from de import RSADOAEP, rsa_key
from ore_key_gen import gen_ore_key_rand




conf = load_yaml_file("/config.yaml")
DE_key_location = conf["DE_key_location"]
ORE_key_location = conf["ORE_key_location"]
backed_DB_uri = conf["backed_DB_uri"]

db_name = conf["db_name"]
attrib_col_name = conf["attrib_col_name"]
user_col_name = conf["users_col_name"]

ATTIRB_COL = db_common.get_collection(backed_DB_uri,db_name=db_name, col_name=attrib_col_name)
USER_COL = db_common.get_collection(backed_DB_uri,db_name=db_name, col_name=user_col_name)



def hash_pass(paswd,salt):
   try:
      key = hashlib.pbkdf2_hmac(
         'sha256', # The hash digest algorithm for HMAC
         paswd.encode('utf-8'), 
         salt, 
         100000,  
         dklen=128
      )
      return key
   except:
      return None

def check_passwd(salt, hash_val, in_passwd):
   try:
      in_hash = hash_pass(in_passwd,salt)
      return in_hash == hash_val
   except:
      return False

def find_user(username):
   global USER_COL
   try:
      USER_COL.find_one({"username":username},{"_id":0})
   except:
      return None


def login():
   global USER_COL

   username = request.json.get("username", None)
   password = request.json.get("password", None)
   user = find_user(username)
   if not user:
      return "Bad credentials", 401

   if not check_passwd(user["salt"], user["password"], password):
      return Response(status=403)

   access_token = create_access_token(identity=username)
   return jsonify(access_token=access_token)



def create_user():
   global USER_COL

   username = request.json.get("username", None)
   password = request.json.get("password", None)
   password2 = request.json.get("password", None)
   # attribs = request.json.get("attributes", None)
   attribs = [1,2,3,4]

   # TODO add attributes normalization, add username normalization
   username = username.replace("/","")


   if not username or not password or not password2 :#or not attribs:
      return Response(status=400)
   if password != password2:
      return"password and password2 must match", 400

   if find_user(username):
      return "user already exists", 409

   salt = os.urandom(32)
   p_hash = hash_pass(password, salt)
   if not p_hash:
      traceback.print_exc()
      return Response(status=500)

   record = {"salt": salt, "password": p_hash, "username":username, "attributes": attribs}


   try:
      USER_COL.insert_one(dict(doc))
   except:
      print("failed to insert new user")
      traceback.print_exc()
      return Response(status=500)


   # todo create keys
   access_token = create_access_token(identity=username)
   return jsonify(access_token=access_token, attributes=attribs, username=username)


@jwt_required()
def me():
   current_user = get_jwt_identity()
   return jsonify(logged_in_as=current_user), 200



@jwt_required()
def do_something():
   username = get_jwt_identity()

