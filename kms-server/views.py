#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback

#from flask import render_template
from flask import Response, request
from flask import send_file


from cpabew import CPABEAlg
from cpabe_key_gen import gen_cpabe_master_keys, gen_cpabe_org_secret_key, load_cpabe_org_secret_key_from_name, load_cpabe_master_keys
from de import RSADOAEP, rsa_key
from ore_key_gen import gen_ore_key_rand

DE_key_location = "/secrets/DE_key.pem" 
ORE_key_location = "/secrets/ORE_key.bin"


def normalize_str(st):
   st = st.replace("/","__")
   st = st.replace(" ","_")
   return st

def normalize_attribs(attribs):
   return list(map(normalize_str, attribs))


def index():
   # return Response(status=403)
   return "up", 200

def gen_de_key():
   global DE_key_location

   try:
      k = open(DE_key_location, "r").read().encode()
      return "Already exists", 409
   except FileNotFoundError:
      print("read failed, generating",flush=True)
      pem = rsa_key().decode()
      open(DE_key_location, "w").write(pem)
      return "Ok", 201
   except:
      traceback.print_exc()
      return Response(status=500)


def get_de_key():
   global DE_key_location

   try:
      k = open(DE_key_location, "r").read().encode()
      return k
   except FileNotFoundError:
      return Response(status=500)


def gen_ore_key():
   global ORE_key_location

   try:
      k = open(ORE_key_location, "rb").read()
      return "Already exists", 409
   except FileNotFoundError:
      ore_key = gen_ore_key_rand()
      open(ORE_key_location, "wb").write(ore_key)
      return "Ok", 201


def get_ore_key():
   global ORE_key_location

   try:
      k = open(ORE_key_location, "rb").read()
      return k
   except FileNotFoundError:
      return Response(status=500)

def gen_cpabe_master_keys_endpoint():
   bsw07 = CPABEAlg()
   pk_mk = gen_cpabe_master_keys(bsw07)

   return "Ok", 201

def get_cpabe_pub_key():
   try:
      bsw07 = CPABEAlg()

      pk = load_cpabe_master_keys(bsw07, pub_only=True)

      # return send_file(bsw07.serialize_charm_obj(pk))
      return bsw07.serialize_charm_obj(pk)
   except:
      traceback.print_exc()
      return Response(status=500)



def create_org_cpabe_secret():
   # req_data = request.get_json()

   # todo check if already exists

   try:

      req_data = request.json
      name = normalize_str(req_data['name'])
      attribs = normalize_attribs(req_data['attributes'])
      attribs = list(map(lambda x:x.upper(),attribs))

   except:
      return Response(status=400)
   
   try:
      bsw07 = CPABEAlg()

      try:
         sk = load_cpabe_org_secret_key_from_name(bsw07, name)
         return "Already exists", 409
      except FileNotFoundError:
         pk_mk = gen_cpabe_master_keys(bsw07)
         if pk_mk:
            # the following also checks the file to see if it exits already
            sk = gen_cpabe_org_secret_key(bsw07, pk_mk, name, attribs)
            return {
                     "name": name,
                     "atttributes": attribs
                   }, 201

         return Response(status=500)
      
   except:
      traceback.print_exc()
      return Response(status=500)

def get_org_cpabe_secret():
   # req_data = request.get_json()

   # todo check if already exists

   try:

      req_data = request.json
      name = req_data['name'].replace("/","")

   except:
      return Response(status=400)
   
   try:
      bsw07 = CPABEAlg()
       
      sk = load_cpabe_org_secret_key_from_name(bsw07, name)
      print("{} sk[attribs]: {}".format(name, sk["S"]),flush=True)

      ser_sk = bsw07.serialize_charm_obj(sk)
      return ser_sk
         
   except FileNotFoundError:
      return Response(status=400)

   except:
      traceback.print_exc()
      return Response(status=500)


def list_all_attributes():
   return "Not implemented", 200