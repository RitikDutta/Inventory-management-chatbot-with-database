from flask import Flask, request, make_response, jsonify
from flask.globals import current_app
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



def is_product_available(product, pack=1):
    data = ref.child('products').child(product).child("{}_pack_{}".format(pack, product)).get()
#     pprint(data)
    if not bool(data):
        print("product not available")
        quantity=0
        price = 0
    else:
        quantity = data['quantity']
        price = data['price']
        print(quantity, price)
    return quantity, price


def add_order_dict(name, product, quantity=1):
  text = ''
  if is_product_available(product)[0] >= quantity:
    user = ref.child('customers').child(name).get()
    current_order = user['current_order']
    orders = user['order{}'.format(current_order)]
    orders[product] = orders.get(product, 0) + quantity
    orders['total']+=is_product_available(product)[1]*quantity
    user['order{}'.format(current_order)].update(orders)
    ref.child('customers').child(name).update(user)
    pprint(user)
    text = '{} {} added'.format(quantity, product)
  else:
    pprint("not applicable")
    text = 'sorry this item is unavailable'
  return text





# def get_all_orders(name):
#     text = ''
#     total = 0
#     user = ref.child('customers').child(name).get()
#     current_order = user['current_order']
#     orders = user['order{}'.format(current_order)]
#     text+='quantity\tproduct\tprice\ttotal\n'
#     for a in orders:
#         text+='{}\t\t{}\t{}\t{}'.format(orders[a], a, is_product_available(a)[1], is_product_available('maggie')[1]*orders[a])
#         text+='\n'
#         total+=is_product_available('maggie')[1]*orders[a]
#     text+='\nyour total is: {}'.format(total)
#     return text


def get_all_orders2(name):
    text = 'Your orders are:-'
    total = 0
    user = ref.child('customers').child(name).get()
    current_order = user['current_order']
    orders = user['order{}'.format(current_order)]
    for a in orders:
        if a=='total':
            continue
        text += '\n{} {}"(s)"'.format(orders[a], a)
    text+='\nYour total is {}'.format(orders['total'])
    return text




def get_product(product, pack=1):
    pprint(ref.child('products').child(product).child("{}_pack_{}".format(pack,product)).get())
    data = ref.child('products').child(product).child("{}_pack_{}".format(pack,product)).get()
    speech = {

        "fulfillmentText": data['name'],
        "fulfillmentMessages": [
          
          {
            "text": {
              "text": [
                data['name']
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "image": {
              "imageUri": data["image_link"]
            },
            "platform": "TELEGRAM"
          },
          {
            "text": {
              "text": [
                data['discription']
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "text": {
              "text": [
                "Price: {}".format(data["price"])
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "text": {
              "text": [
                "{} left in stock".format(data["quantity"])
              ]
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
                    "rawUrl": data["image_link"],
                    "accessibilityText": "MBD Image"
                  }
                ]
              ]
            }
          },
          {
            "text": {
              "text": [
                data["discription"]
              ]
            }
          },
          {
            "text": {
              "text": [
                    "Price: {}".format(data["price"])
              ]
            }
          },
          {
            "text": {
              "text": [
                    "{} left in stock".format(data["quantity"])
              ]
            }
          },
        ],
      }
    return speech
def sub_product(product, quantity=1, pack=1):
    data = ref.child('products').child(product).child('{}_pack_{}'.format(pack, product)).get()
    data.update({'quantity':data['quantity']-quantity})
    ref.child('products').child(product).child('{}_pack_{}'.format(pack, product)).update(data)
    pprint(data)

def sub_product_main(name):
    user = ref.child('customers').child(name).get()
    current_order = user['current_order']
    orders = user['order{}'.format(current_order)]
    for a in orders:
        if a =='total':
            continue
        print(a, orders[a])
        sub_product(a, orders[a])

def update_current_order(name):
  user = ref.child('customers').child(name).get()
  user.update({'current_order': user['current_order']+1})
  ref.child('customers').child(name).update(user)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/webhook', methods=['POST'], )
def webhook():
    text = ''
    req = request.get_json(silent =True, force=True)
    params = req['queryResult']['parameters']
    print('*'*20)
    pprint(req['queryResult']['intent'])
    pprint(params)
    # pprint(req['queryResult']['outputContexts'][0]['parameters'])
    speech = {"fulfillmentText": "Hello! How can I help you?"}



    if req['queryResult']['intent']['displayName'] == 'get user name':
      print("{} {}".format(params['prename'], params['person']['name']))
      pprint(params)
      if is_user_present("{} {}".format(params['prename'], params['person']['name'])):
        speech = {"fulfillmentText": "{} {} please add your orders".format(params['prename'], params['person']['name'])}
      else:
        print("{} {} not present \n plesae enter correct name or create account".format(params['prename'], params['person']['name']))
        speech = {"fulfillmentText": "{} {} not present \n plesae enter correct name or create account".format(params['prename'], params['person']['name'])}


    if req['queryResult']['intent']['displayName'] == 'test 23':
      text = get_all_orders2("cool ronit")



    if req['queryResult']['intent']['displayName'] == 'add order':
      pprint(req['queryResult']['outputContexts'])
      print('+'*20)
      pprint(params)
      order_params = req['queryResult']['outputContexts'][1]['parameters']
      prename_params = req['queryResult']['outputContexts']
      if len(order_params['number']) == 0:
        no_items = 1
      else:
        no_items = int(order_params['number'][0])
      # pprint(order_params)
      # print(len(order_params['number']))
      # print("{} {} orders ".format(order_params['prename'], order_params['person']['name']))
      # print("{} {}".format(no_items, order_params['products'][0]))
      try:
        prename = req['queryResult']['outputContexts'][0]['parameters']['prename']
        name = req['queryResult']['outputContexts'][0]['parameters']['person']['name']
        print(prename, name)
        print('started on one go')
        # pprint(prename, name)
        text = add_order_dict("{} {}".format(prename, name), order_params['products'][0], no_items)

      except KeyError:
        prename = req['queryResult']['outputContexts'][1]['parameters']['prename']
        name = req['queryResult']['outputContexts'][1]['parameters']['person']['name']
        print('exception handelled')
        text = add_order_dict("{} {}".format(prename, name), order_params['products'][0], no_items)

      except KeyError:
        prename = req['queryResult']['outputContexts'][2]['parameters']['prename']
        name = req['queryResult']['outputContexts'][2]['parameters']['person']['name']
        print('exception handelled')
        text = add_order_dict("{} {}".format(prename, name), order_params['products'][0], no_items)

      except KeyError:
        prename = req['queryResult']['outputContexts'][3]['parameters']['prename']
        name = req['queryResult']['outputContexts'][3]['parameters']['person']['name']
        print('exception handelled')
        text = add_order_dict("{} {}".format(prename, name), order_params['products'][0], no_items)

      except KeyError:
        text = "something went wrong may be app is in testing phases"

      speech = {
        'fulfillmentText': text,
        "fulfillmentMessages": [
          {
            "text": {
              "text": [
                text
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "payload": {
              "richContent": [
                [
                  {
                    "type": "chips",
                    "options": [
                      {
                        "text": "Check Cart"
                      },
                      {
                        "text": "Confirm"
                      }
                    ]
                  }
                ]
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "quickReplies": {
              "title": "Please add next item",
              "quickReplies": [
                "Check Cart",
                "Confirm"
              ]
            },
            "platform": "TELEGRAM"
          },
          {
            "text": {
              "text": [
                text
              ]
            }
          },
          {
            "payload": {
              "richContent": [
                [
                  {
                    "options": [
                      {
                        "text": "Check Cart"
                      },
                      {
                        "text": "Confirm"
                      }
                    ],
                    "type": "chips"
                  }
                ]
              ]
            }
          }
        ]
      }

    if req['queryResult']['intent']['displayName'] == 'get product details':
        product = params['products']
        speech = get_product(product)


    if req['queryResult']['intent']['displayName'] == 'check cart' or req['queryResult']['intent']['displayName'] == 'order prompt':
      pprint(req['queryResult'])
      try:
        prename = req['queryResult']['outputContexts'][1]['parameters']['prename']
        name = req['queryResult']['outputContexts'][1]['parameters']['person']['name']
        print(prename, name)
        print('started on one go')
        text = get_all_orders2('{} {}'.format(prename, name))
        speech = {"fulfillmentText": text}
      except KeyError:
        prename = req['queryResult']['outputContexts'][2]['parameters']['prename']
        name = req['queryResult']['outputContexts'][2]['parameters']['person']['name']
        print('exception handelled 1')
        text = get_all_orders2('{} {}'.format(prename, name))
        speech = {"fulfillmentText": text}
      except KeyError:
        prename = req['queryResult']['outputContexts'][3]['parameters']['prename']
        name = req['queryResult']['outputContexts'][3]['parameters']['person']['name']
        print('exception handelled 2')
        text = get_all_orders2('{} {}'.format(prename, name))
        speech = {"fulfillmentText": text}
      except KeyError:
        prename = req['queryResult']['outputContexts'][4]['parameters']['prename']
        name = req['queryResult']['outputContexts'][4]['parameters']['person']['name']
        print('exception handelled 3')
        text = get_all_orders2('{} {}'.format(prename, name))
        speech = {"fulfillmentText": text}
      except KeyError:
        text = "something went wrong may be app is in testing phases"
      if req['queryResult']['intent']['displayName'] == 'order prompt':
        text+="\nAre You Sure"
      speech = {"fulfillmentText": text}

    if req['queryResult']['intent']['displayName'] == 'get details':
        message = add_user_word(params['person']['name'], params["age"]["amount"], params["street-address"], params["phone-number"])
        speech = {'fulfillmentText': message}
    
    if req['queryResult']['intent']['displayName'] == 'order prompt - yes':
      try:
        prename = req['queryResult']['outputContexts'][1]['parameters']['prename']
        name = req['queryResult']['outputContexts'][1]['parameters']['person']['name']
        print(prename, name)
        print('started on one go')
      except KeyError:
        prename = req['queryResult']['outputContexts'][2]['parameters']['prename']
        name = req['queryResult']['outputContexts'][2]['parameters']['person']['name']
        print('exception handelled 1')
      except KeyError:
        prename = req['queryResult']['outputContexts'][3]['parameters']['prename']
        name = req['queryResult']['outputContexts'][3]['parameters']['person']['name']
        print('exception handelled 2')
      except KeyError:
        prename = req['queryResult']['outputContexts'][4]['parameters']['prename']
        name = req['queryResult']['outputContexts'][4]['parameters']['person']['name']
        print('exception handelled 3')
      except KeyError:
        text = "something went wrong may be app is in testing phases"
      text = 'your order have been placed \nthankyou for shop whith us\nur order will deliver soon.'
      speech = {"fulfillmentText": text}
      ref.child('customers').child('{} {}'.format(prename, name)).update({'status': 'placed'})
      # sub_product_main("{} {}".format(prename, name))
      update_current_order("{} {}".format(prename, name))
    return make_response(jsonify(speech))


if __name__ == '__main__':
   app.run()
