#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback

from flask import render_template
from flask import Response, request
from flask import send_file


from cpabew import CPABEAlg
from cpabe_key_gen import gen_cpabe_master_keys, gen_cpabe_org_secret_key
from de import RSADOAEP, rsa_key
from ore_key_gen import gen_ore_key_rand

DE_key_location = "/secrets/DE_key.pem" 
ORE_key_location = "/secrets/ORE_key.bin"


def normalize_str(st):
   return st.replace("/","_")


def normalize_attribs(attribs):
   return list(map(normalize_str, attribs))


def index():
   # return Response(status=403)
   return "up", 200

def gen_de_key():
   global DE_key_location

   try:
      return = open(DE_key_location, "r").read()
   except FileNotFoundError:
      pem = rsa_key()
      open(DE_key_location, "w").write(pem)
      return pem

def get_de_key():
   global DE_key_location

   try:
      return open(DE_key_location, "r").read()
   except FileNotFoundError:
      return Response(status=500)


def gen_ore_key():
   global ORE_key_location

   try:
      return open(ORE_key_location, "rb").read()
   except FileNotFoundError:
      ore_key = gen_ore_key_rand()
      open(ORE_key_location, "wb").write(ore_key)
      return ore_key


def get_ore_key():
   global ORE_key_location

   try:
      return open(ORE_key_location, "rb").read()
   except FileNotFoundError:
      return Response(status=500)

def gen_cpabe_master_keys():
   bsw07 = CPABEAlg()
   pk_mk = gen_cpabe_master_keys(bsw07)

def get_cpabe_pub_key():
   bsw07 = CPABEAlg()

   pk = load_cpabe_master_keys(bsw07, pub_only=True):

   # return send_file(bsw07.serialize_charm_obj(pk))
   return bsw07.serialize_charm_obj(pk)


def create_org_cpabe_secret():
   # req_data = request.get_json()

   # todo check if already exists

   try:

      req_data = request.json
      name = normalize_str(req_data['name'])
      attribs = normalize_attribs(req_data['atttributes'])

   except:
      return Response(status=400)
   
   try:
      bsw07 = CPABEAlg()


      pk_mk = gen_cpabe_master_keys(bsw07)
       
      cpabe_pubkey = pk_mk[0]

      if pk_mk:
         sk = gen_cpabe_org_secret_key(cpabe_alg, pk_mk, org_name, attribs):


      return {
         "pk": bsw07.serialize_charm_obj(cpabe_pubkey), 
         "sk": bsw07.serialize_charm_obj(sk),
         "name": name,
         "atttributes": attribs
      }, 201
   except:
      return Response(status=500)


# def other():
#     return render_template('other.html')