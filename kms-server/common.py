 
import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback
import pymongo 
import hashlib


def normalize_str(st):
   st = st.replace("/","__")
   st = st.replace(" ","_")
   return st

def normalize_attribs(attribs):
   return list(map(normalize_str, attribs))


def get_config(f_name):
   with open(f_name) as f:
      print("Loading data from {}...".format(f_name))
      data = yaml.load(f, Loader=yaml.FullLoader)
      return data

def create_index(col, name):
   col.create_index(name)

def get_collection(uri, col_name, db_name="priv_kms", connect=False):
   myclient = pymongo.MongoClient(uri,connect=connect)
   mydb = myclient[db_name]
   mycol = mydb[col_name]
   return mycol


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