#==== auth/models ========#
# UserPrefs the default datastoreModel to store website Users



from google.appengine.ext import db

class UserPrefs (db.Model):
    account = db.UserProperty(required = True) ### NECESSARY
    birthday = db.DateTimeProperty(required = False)
    username = db.StringProperty(required = False)
    email = db.EmailProperty(required = False)
    password = db.StringProperty(required = False)
    is_active = db.BooleanProperty(required = False)