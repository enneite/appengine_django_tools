#========= appengine_django_tools.auth ============#
# This is a module used to authenticate user on your website
# The principe : the users can be authenticated with google account OR website account
# to use the module, specify the authentication backend in your settings :
# In settings.py add this line :
# custom authentication backend for appengine
# AUTHENTICATION_BACKENDS = ('dj_project.appengine_django_tools.auth.backends.DatastoreBackend',)
# WARNING : google appengine is a cloud plateform, so you can't use file based session
# if you are using datastore, you can't use database based session
# We recommended to use signed cookie based session :
# Add this line in settings.ini :
#SESSION_ENGINE ="django.contrib.sessions.backends.signed_cookies"
 
from google.appengine.api import users

# get_current_user()
# search an authenticated user on the web site
# if user not found then the function search the current google account authenticated on the website
# if google account not found : return none  
def get_current_user(request):
    if request.user.is_authenticated():
        return request.user.account # account type : db.UserProperty (from datastore)
    if users.get_current_user() :
        return users.get_current_user()
    return None