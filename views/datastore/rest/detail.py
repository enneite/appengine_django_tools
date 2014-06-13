#  django views for RESt/JSON application
# with relation against datastore modeling
import json
import sys
import logging
import pprint

from django import http
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from  base import BaseRestView
from  django.views.generic.edit import ModelFormMixin
from ..crud import CrudEntityMixin


class RestView(BaseRestView, CrudEntityMixin):
    
    white_list = []
    black_list = []   
            
    #serialize the object in a dict of scalar values
    def serialize (self,obj) :
        objDict = db.to_dict(obj, {'id' : obj.key().id()})
        for key in self.filter(objDict) :
            objDict[key] = unicode(objDict[key])
        return objDict
    # filter the columns to send in the response (using white_list first OR black_list if white_list is empty)
    def filter(self,obj):
        if(len(self.white_list) == 0 and len(self.black_list) == 0) :
            return obj
        if(len(self.white_list) > 0) :
            out = obj
            for key in obj.keys() :
                if key not in self.white_list :
                    del out[key]
            return out
        if(len(self.black_list) > 0) :
            out = obj
            for key in obj.keys() :                
                if key in self.black_list :
                    del out[key]
            return out
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_entity(self.getRessourceId(request))
        if self.object :
            objName = obj.__class__.__name__
            return self.sendResponse({'success' : 'OK', objName : self.serialize(obj) })
        else :
            return http.HttpResponseNotFound()
    
    def post(self, request, *args, **kwargs) :
        post = self.getData(request)
        obj = self.create_entity(post)
        if obj :
            objName = obj.__class__.__name__
            return self.sendResponse({'success' : 'OK', objName : self.serialize(obj) })
        else :
            return http.HttpResponseNotFound()           
    
    def put(self, request, *args, **kwargs):
        post = self.getData(request)
        obj = self.get_entity(self.getRessourceId(request))
        if obj :
            obj = self.update_entity(post)
            objName = obj.__class__.__name__
            return self.sendResponse({'success' : 'OK', objName : self.serialize(obj) })
        else :
            return http.HttpResponseNotFound() 
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_entity(self.getRessourceId(request))
        if obj :
            res = self.delete_entity()
            data ={ 'success': "OK"}
            return self.sendResponse(data)
        else :
            return http.HttpResponseNotFound()
        
    
    # in rest application ans requesting
    # you don't need token validator to validate posted value     
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(RestView, self).dispatch(*args, **kwargs)    


#detail view using modelForm Validation :    
class RestFormView(RestView, ModelFormMixin) :
    #modelForm object used for data validation :
    form = None
    
    # validation of data before send the response 
    def post(self, request, *args, **kwargs) :
        form = self.init_form(request)    
        if form.is_valid() :
            return super(DetailFormRestView, self).post(request, *args, **kwargs)
        else :
            return self.sendResponse({'success' : 'KO', 'error_messages' : {}})          
    # validation of data before send the response 
    def put(self, request, *args, **kwargs):
        form = self.init_form(request)    
        if form.is_valid() :
            return super(DetailFormRestView, self).put(request, *args, **kwargs)
        else :
            return self.sendResponse({'success' : 'KO', 'error_messages' : {}}) 
    
    # init and populate form
    def init_form(self,request, *args, **kwargs) :        
        modForm = __import__(self.form.__module__, fromlist=[self.form.__name__])
        classForm = getattr(modForm, self.form.__name__)                       
        if self.getRessourceId(request) <> 0 :
            obj = self.getModelInstance(request)
            form = classForm(self.getData(request), instance=obj)
        else:
            form = classForm(self.getData(request))
        return form

    
    
