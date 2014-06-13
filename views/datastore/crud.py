#  django views for RESt/JSON application
# with relation against datastore modeling
import logging
import pprint
import re

from detail import SingleEntityMixin

class CrudEntityMixin(SingleEntityMixin):
    
    def create_entity(self, post):
        mod = __import__(self.model.__module__, fromlist=[self.model.__name__])
        entityClass = getattr(mod, self.model.__name__)
        obj =  entityClass()      
        return self.persist_entity(self,obj,post) 
        
    def update_entity(self, obj, post):
        return self.persist_entity(self,obj,post) 
        
    def delete_entity(self, obj):
        if obj.delete() :
            return true
        else :
            return false
        
        # persist the entity in the datastore     
    def persist_entity(self,obj,post) :
    #def update_model(model, values):
        for k, v in post.iteritems():
            if k in obj.properties() :
                setattr(obj, k, v)                             
        obj.put()
        return obj
    
