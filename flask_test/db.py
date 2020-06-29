# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 22:43:15 2020

@author: tjusu
"""

from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from user import User

client = MongoClient("mongodb+srv://admin_test:admin_test@langrensha-zudzp.mongodb.net/<dbname>?retryWrites=true&w=majority")

langrensha_db = client.get_database("langrensha")
user_collection = langrensha_db.get_collection("users")

def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    user_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})
    
#save_user('nik', 'fda@dl.com', 'test')
def get_user(username):
    user_data = user_collection.find_one({'_id': username})
    if user_data:
        return User(user_data['_id'], user_data['email'], user_data['password'])
    else:
        return None