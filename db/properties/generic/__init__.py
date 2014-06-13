#========== db.properties.generic ===========#
# cutom properties for datastore

from google.appengine.ext import db

# Django can convert numeric string from http request to int or float
# but python can't convert automaticaly int to float without de float() function
# so this is a custom properties who accept numeric values and return float
class NumericProperty(db.FloatProperty):
    data_type = float
    
    # validation function :
    def validate(self, value):
        if type(value) is float :
           return value
        if type(value) is int  or type(value) is long :
            out = 0.00 + value
            return out
        if type(value) is str :
            matchObj1 = re.match( r'^([0-9]+)\.([0-9]+)$', value, re.M|re.I)
            if matchObj1 : 
                return float(value)
            matchObj2 = re.match( r'^([0-9]+)$', value, re.M|re.I)
            if matchObj2 : 
                return float(value)
        return 0.00
                
            
        