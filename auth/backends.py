#================ auth.backend =================#
# this is the default authentication backend for appengine / datastore web application
# The default datastoreModel to store website Users is UserPrefs
# you can create an custom model and specify it in project settings like this : 
#in settings.py  
#AUTH_USER_DATASTORE_MODEL = 'your_project.appengine_django_tools.auth.models.UserPrefs'

# an custom User Model must have 
# - an property named "account" with db.UserProperty type
# If you use to create an custom authentication backend, you need so :
# - an property named "username" with db.StringProperty type
# - an property named "password" with db.StringProperty type

import hashlib
import logging
import re

from google.appengine.api import users
from google.appengine.ext import db

from django.conf import settings

# default backend authentication : 
# an authentication backend must implement authenticate() method
class DatastoreBackend(object):
    
    def __init__(self):
        if hasattr(settings, 'AUTH_USER_DATASTORE_MODEL') :
            matchObj = re.match( r'(.*)\.([a-z0-9A-Z_]+)$', settings.AUTH_USER_DATASTORE_MODEL, re.M|re.I)
            moduleName = matchObj.group(1)
            className = matchObj.group(2)
        else :
            moduleName = self.__module__.replace('backends','models')
            className  = 'UserPrefs'                
        mod = __import__(moduleName, fromlist=[className])
        self.UserModel = getattr(mod, className) 
      
    #authentication with query on datastore :         
    def authenticate(self, username=None, password=None, **kwargs):
        prepared_query = "SELECT * FROM %s  WHERE username = :username" % self.UserModel.__name__
        q = db.GqlQuery(prepared_query, username = username )
        nb_results = q.count()
        
        if nb_results == 1 :
            userprefs = q.get()
            pwd_hash = userprefs.password
            if pwd_hash and pwd_hash <> '' :
                if pwd_hash == self.hash_password(password) :
                    logging.info('SUCCESS for auth !!!!!')
                    return UserForSession(userprefs)
            else :
                logging.info('user can\'t be authenticate  with a website account (could be possible with google account ?)')
        elif nb_results >1 :
            logging.info('to many values for this email')
        else :
            logging.info('account unknown')
        return None
    
    # hash the password because it is a bad idea to have no hashed password in your database !    
    def hash_password(self, pwd) :
        return hashlib.sha224(pwd).hexdigest()
    
    # get the user from de Model (UserPrefs by default)
    # for hight level performance, reimplements using memcache ??
    def get_user(self, user_id) :
        logging.info(user_id)        
        user = self.UserModel.get_by_id(int(user_id))
        if user : 
            return UserForSession(user)
        else :
            return None

# a custom class to push in session 
#this class is constructed with a datastore Model Instance
# signed-cookie based session can't support big objects (because size aof cookie is limited)        
class UserForSession(object):
    def __init__(self,userprefs):
        self.username = userprefs.username
        self.pk = userprefs.key().id()
        self.is_valid = True
        self.account = userprefs.account
        
    def save(self, update_fields=[], *args, **kwargs):
        return True
    
    def is_authenticated(self):
        return True
        
    
    
    