#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file
import db_common
from common import normalize_str, normalize_attribs, hash_pass, check_passwd

from pprint import pprint
import traceback


import os, time
import hashlib
from numpy import random
from flask_jwt_extended import create_access_token
#from flask import render_template
from flask import Response, request
from flask import send_file
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask import jsonify

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

####################################
####### Helper Functions ###########
####################################



def find_user(username):
   global USER_COL
   try:
      return USER_COL.find_one({"username":username},{"_id":0})
   except:
      return None

####################################
########   Key Generators   ########
######## For admin use only ########
########   not endpoints    ########
####################################

KEY_GEN_STATUS_FAILED = 0
KEY_GEN_STATUS_GEN_SUCCESS = 1
KEY_GEN_STATUS_ALREADY_EXISTS = 2

def gen_de_key():
   global DE_key_location

   try:
      k = open(DE_key_location, "r").read().encode()
      return KEY_GEN_STATUS_ALREADY_EXISTS
   except FileNotFoundError:
      print("read failed, generating",flush=True)
      pem = rsa_key().decode()
      open(DE_key_location, "w").write(pem)
      return KEY_GEN_STATUS_GEN_SUCCESS
   except:
      traceback.print_exc()
      return KEY_GEN_STATUS_FAILED

def gen_ore_key():
   global ORE_key_location

   try:
      k = open(ORE_key_location, "rb").read()
      return KEY_GEN_STATUS_ALREADY_EXISTS
   except FileNotFoundError:
      ore_key = gen_ore_key_rand()
      open(ORE_key_location, "wb").write(ore_key)
      return KEY_GEN_STATUS_GEN_SUCCESS


def gen_cpabe_master_keys_func():
   bsw07 = CPABEAlg()
   pk_mk = gen_cpabe_master_keys(bsw07)

   return KEY_GEN_STATUS_GEN_SUCCESS

def create_org_cpabe_secret(username, attribs):
   global ATTIRB_COL

   try:
      bsw07 = CPABEAlg()

      try:
         sk = load_cpabe_org_secret_key_from_name(bsw07, username)
         return "Already exists", 409
      except FileNotFoundError:
         pk_mk = gen_cpabe_master_keys(bsw07)
         if pk_mk:
            # the following also checks the file to see if it exits already
            sk = gen_cpabe_org_secret_key(bsw07, pk_mk, username, attribs)

            doc = {
                     "username": username,
                     "attributes": attribs
                   }
            try:
               ATTIRB_COL.insert_one(dict(doc)) # this adds an id which is non serialasible, so deep copy
            except:
               traceback.print_exc()
               print("failed to insert to attrib table, user still added to system",flush=True)
            return doc

         return False
      
   except:
      traceback.print_exc()
      return False


def generate_system_keys():
   try:
      if not gen_de_key():
         return False
      if not gen_ore_key():
         return False
      if not gen_cpabe_master_keys_func():
         return False
      return True
   except:
      traceback.print_exc()
      return False


####################################
########### Endpoints ##############
####################################


def index():
   # return Response(status=403)
   return "up\n", 200


def login():
   global USER_COL

   time.sleep(random.uniform(1.0, 5.0)) # make it slower to login for safety

   username = request.json.get("username", None)
   password = request.json.get("password", None)
   user = find_user(username)
   if not user:
      return "Bad credentials", 401

   if not check_passwd(user["salt"], user["password"], password):
      return Response(status=403)

   access_token = create_access_token(identity=username)
   return jsonify(access_token=access_token)


@jwt_required()
def create_user():
   global USER_COL

   username = request.json.get("username", None)
   password = request.json.get("password", None)
   password2 = request.json.get("password2", None)
   attribs = request.json.get("attributes", None)

   # attributes normalization, username normalization
   try: 
      
      username = normalize_str(username)
      attribs = normalize_attribs(attribs)
      attribs = list(map(lambda x:x.upper(),attribs)) # important, key generation requirement
      if type(username) != str:
         return "name must be string", 400
      if type(attribs) != list:
       return "attributes must be list", 400
   except:
      # traceback.print_exc()
      return Response(status=400)

   if not username or not password or not password2 :#or not attribs:
      return "missing fileds, must include username, password, password2, attributes[list:str]", 400
   if password != password2:
      return"password and password2 must match", 400

   if find_user(username):
      return "user already exists", 409

   salt = os.urandom(32)
   p_hash = hash_pass(password, salt)
   if not p_hash:
      traceback.print_exc()
      return Response(status=500)

   user_record = {"salt": salt, "password": p_hash, "username":username, "admin":False}

   # generate user's private key before adding user to the system/DB
   priv_key_succes =  create_org_cpabe_secret(username, attribs)
   if not priv_key_succes:
      print("failed to create users secret")
      return Response(status=500)

   # add user to DB
   try:
      USER_COL.insert_one(dict(user_record))
   except:
      print("failed to insert new user")
      traceback.print_exc()
      return Response(status=500)


   access_token = create_access_token(identity=username)
   return jsonify(access_token=access_token, attributes=attribs, username=username)


@jwt_required()
def me():
   current_user = get_jwt_identity()
   return jsonify(logged_in_as=current_user), 200



# @jwt_required()
# def do_something():
#    username = get_jwt_identity()




####################################
####### Getters enpoints ###########
####################################

@jwt_required()
def get_ore_key():
   global ORE_key_location

   try:
      k = open(ORE_key_location, "rb").read()
      return k
   except FileNotFoundError:
      return Response(status=500)

@jwt_required()
def get_de_key():
   global DE_key_location

   try:
      k = open(DE_key_location, "r").read().encode()
      return k
   except FileNotFoundError:
      return Response(status=500)
      
@jwt_required()
def get_cpabe_pub_key():
   try:
      bsw07 = CPABEAlg()

      pk = load_cpabe_master_keys(bsw07, pub_only=True)

      # return send_file(bsw07.serialize_charm_obj(pk))
      return bsw07.serialize_charm_obj(pk)
   except:
      traceback.print_exc()
      return Response(status=500)

@jwt_required()
def get_org_cpabe_secret():
   # req_data = request.get_json()

   # todo check if already exists

   try:
      username = get_jwt_identity()
   except: # should never get here
      return Response(status=400)
   
   try:
      bsw07 = CPABEAlg()

      sk = load_cpabe_org_secret_key_from_name(bsw07, username)
      # print("{} sk[attribs]: {}".format(username, sk["S"]),flush=True)

      ser_sk = bsw07.serialize_charm_obj(sk)

      return ser_sk
         
   except FileNotFoundError:
      print("Could not retrieve secret key for user {}. Seems like file was deleted, must bb regenerated manually.".format(username))
      return Response(status=500)

   except:
      traceback.print_exc()
      return Response(status=500)

@jwt_required()
def list_all_attributes():
   global ATTIRB_COL

   al_records = ATTIRB_COL.find({}, {"attributes":1, "_id":0})
   all_attribs = list()

   print(al_records)
   for r in al_records:
      all_attribs += r["attributes"]

   return {"attributes": list(set(all_attribs))}, 200




