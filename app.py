from flask import Flask, request, make_response, jsonify
import requests
from flask import jsonify
from flask import make_response
import json
from pprint import pprint









import firebase_admin
from firebase_admin import credentials
from pprint import pprint
from firebase_admin import db
from random import randint

cred_obj = firebase_admin.credentials.Certificate('firebase.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':'https://wellbaked-default-rtdb.firebaseio.com/'
    })

ref = db.reference("/")

def is_user_present(name):
    user = ref.child('customers').get()
    flag = False
    for key, value in user.items():
        if key == name:
            flag = True
            break
    if flag:
        return True
    else:
        return False


def get_user_name_word(uname):
    random = randint(0, 15)
    with open('random_words.json') as fp:
        data = json.load(fp)
    list = data
    user = list["words"][random] + uname
    
    if is_user_present(user):
        print(user, " already present asiging new name")
        user = get_user_name_word(uname)
    return user


def add_user_word(name, age, address, mobile):
    current = 0
    fullmessage = ''
    if is_user_present(name):
        print('{} alreaddy present in our database assigning u new user name'.format(name))
        pkey = get_user_name_word(name)
        message = '{} alreaddy present in our database assigning u new user name \n'.format(name)
    else:
        pkey = name
    data = {
        'name': name,
        'age': age,
        'address': address,
        'mobile': mobile,
        'current_order': 0,
    }
    ref.child('customers').child(pkey).set(data)
    print('{} is your user id please remember userid for next purchace'.format(pkey))
    fullmessage += message+"{} is your user id please remember userid for next purchace\n".format(pkey)
    return fullmessage









app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/webhook', methods=['POST'], )
def webhook():

    req = request.get_json(silent =True, force=True)
    params = req['queryResult']['parameters']
    pprint(req['queryResult']['intent'])
    pprint(params)
    # pprint(req['queryResult'])









    speech = {

    "fulfillmentText": "Hello! How can I help you?",
    "fulfillmentMessages": [
      
     {
        "payload": {
          "richContent": [
            [
              {
                "type": "image",
                "rawUrl": "https://5.imimg.com/data5/QR/AN/MY-5742893/maggi-noodle-250x250.jpg",
                "accessibilityText": "MBD Image"
              }
            ]
          ]
        },
        "platform": "TELEGRAM"
      },
      {
        "text": {
          "text": [
            "here ur image"
          ]
        },
        "platform": "TELEGRAM"
      },
      {
        "image": {
          "imageUri": "https://mybigplunge.com/wp-content/uploads/2015/11/Maggie-is-back-1.jpg"
        },
        "platform": "TELEGRAM"
      },
      {
        "text": {
          "text": [
            ""
          ]
        }
      },
      {
        "payload": {
          "richContent": [
            [
              {
                "type": "image",
                "rawUrl": "https://5.imimg.com/data5/QR/AN/MY-5742893/maggi-noodle-250x250.jpg",
                "accessibilityText": "MBD Image"
              }
            ]
          ]
        }
      }
    ],
  }




















    if req['queryResult']['intent']['displayName'] == 'get details':
        message = add_user_word(params['person']['name'], params["age"]["amount"], params["street-address"], params["phone-number"])
        speech = {'fulfillmentText': message}
  
    return make_response(jsonify(speech))

if __name__ == '__main__':
   app.run()
