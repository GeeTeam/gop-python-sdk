#!coding:utf8
import sys
import random
import json
import requests
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from hashlib import md5
import base64


if sys.version_info >= (3,):
    xrange = range    

VERSION = "1.0.1"

RSA_KEY = b"""-----BEGIN RSA PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDB45NNFhRGWzMFPn9I7k7IexS5
XviJR3E9Je7L/350x5d9AtwdlFH3ndXRwQwprLaptNb7fQoCebZxnhdyVl8Jr2J3
FZGSIa75GJnK4IwNaG10iyCjYDviMYymvCtZcGWSqSGdC/Bcn2UCOiHSMwgHJSrg
Bm1Zzu+l8nSOqAurgQIDAQAB
-----END RSA PUBLIC KEY-----\n"""


class GMessageLib(object):

    API_URL = "http://onepass.geetest.com"
    GATEWAY_HANDLER = "/check_gateway.php"
    MESSAGE_HANDLER = "/check_message.php"
    JSON_FORMAT = False

    def __init__(self, custom_id, private_key):
        self.private_key = private_key
        self.custom_id = custom_id
        self.sdk_version = VERSION

    def _check_method(self,method,**kwargs):
        """
        method for gateway check
        """
        if method == "gateway":
            process_id = kwargs["process_id"]
            accesscode = kwargs["accesscode"]
            phone = kwargs["phone"]
            user_id = kwargs.get("user_id","")
            callback = kwargs.get("callback","")
            testbutton = kwargs.get("testbutton", True)
            if not self._check_para(process_id, accesscode, phone):
                return 0
            send_url = "{api_url}{handler}".format(
                api_url=self.API_URL, handler=self.GATEWAY_HANDLER)
            query = {
                "process_id": process_id,
                "sdk": ''.join( ["python_",self.sdk_version]),
                "user_id": user_id,
                "timestamp":time.time(),
                "accesscode":accesscode,
                "callback":callback,
                "custom":self.custom_id,
                "phone":phone,
            }
            if not testbutton:
                sign_data = self.custom_id + "&&" + self._md5_encode(self.private_key) + "&&" + str(time.time()*1000)
                sign = self.rsa_encrypt(sign_data)
                query.update({"sign": sign})
        elif method == "message":
            process_id = kwargs["process_id"]
            message_id = kwargs["message_id"]
            message_number = kwargs["message_number"]
            phone = kwargs["phone"]
            user_id = kwargs.get("user_id","")
            callback = kwargs.get("callback","")
            if not self._check_para(process_id, message_id, phone):
                return 0
            if not phone:
                return 0
            send_url = "{api_url}{handler}".format(
                api_url=self.API_URL, handler=self.MESSAGE_HANDLER)
            query = {
                "process_id": process_id,
                "sdk": ''.join( ["python_",self.sdk_version]),
                "user_id": user_id,
                "timestamp":time.time(),
                "message_id":message_id,
                "message_number":message_number,
                "callback":callback,
                "custom":self.custom_id,
            }
        else:
            send_url,query,process_id ="","","" #avoid warning
        backinfo = self._post_values(send_url, query)
        backinfo = json.loads(backinfo)
        if str(backinfo["result"]) == "0":
            if self._check_result(process_id, backinfo.get("content")):
                return 1
            else:
                return 0
        else:
            return 0

    def check_gateway(self, process_id, accesscode, phone, user_id=None, callback=None, testbutton=True):
        """
        method for gateway check
        """
        result = self._check_method("gateway", process_id=process_id, accesscode=accesscode, phone=phone, user_id=user_id, callback=callback, testbutton=testbutton)
        return result

    def check_message(self, process_id, message_id, message_number,phone, user_id=None,callback=None):
        """
        method for message check
        """
        result = self._check_method("message",process_id=process_id,message_id=message_id,message_number=message_number,phone=phone,user_id=user_id,callback=callback)
        return result

    def _post_values(self, apiserver, data):
        response = requests.post(apiserver, data)
        return response.text

    def _check_result(self, origin, validate):
        encodeStr = self._md5_encode(self.private_key + "gtmessage" + origin)
        if validate == encodeStr:
            return True
        else:
            return False

    def _check_para(self, str1, str2, str3):
        return (bool(str1.strip()) and bool(str2.strip()) and  bool(str3.strip()))

    def _md5_encode(self, values):
        if type(values) == str:
            values = values.encode()
        m = md5(values)
        return m.hexdigest()

    def rsa_encrypt(self, text):
        rsa_key = RSA.importKey(RSA_KEY)
        cipher = PKCS1_v1_5.new(rsa_key)
        result = base64.encodebytes(cipher.encrypt(text.encode())).decode()
        return result



