#  django views for RESt/JSON application
# with relation against datastore modeling
import json
import sys
import logging
import pprint
import re

from django import http
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, render

from google.appengine.ext import db

#generic RestClass (based on Json)
class RestView(View):   
    
    # return response in json format
    def sendResponse(self,data):
        jsonData = json.dumps(data);
        return http.HttpResponse(jsonData,content_type='application/json')
    
    # extract data from request body    :
    def getData(self, request):
        #logging.info('Raw Data: "%s"' % request.body)  
        try :
            data = json.loads(request.body.encode('utf8'))
            #logging.info(json.dumps(data))
            return data;
        except :
            logging.error("can't convert body in json")
            return {};
    
    #find resource ID by analyse of request URI
    def getRessourceId(self, request):
        #search uri like :
        # - /module/entity/{{id}}
        # - /module/entity/id/{{id}}
        # - /module/entity/?id={{id}}
        matchObj1 = re.match( r'.*/id/([0-9]+).*', request.path, re.M|re.I)
        matchObj2 = re.match( r'/rest/[^/]+/([0-9]+)$', request.path, re.M|re.I)               
        id = None
        if 'id' in request.GET and request.GET['id']<>"" and request.GET['id']<> None :
            id = request.GET['id']
        elif matchObj1:
            id = matchObj1.group(1)
        elif matchObj2:
            id = matchObj2.group(1)    
        else :
            id = 0
        #logging.info(self.request.path)
        #logging.info(id)
        return id;

# List view to return a list of entities filtered with a queryset    
class ListRestView(RestView):
    # the queryset to execute on datastore
    query_set = None
    # if not queryset defined, use the model with model.all() queryset
    model = None
    # a white list : if not empty :
    # then only the specified colums of this list will be send in the response
    white_list = []
    # a white list : if not empty :
    # then only the columns  not specified in this list will be send in the response
    black_list = []
    
    def __init__(self):
        if(self.query_set == None) :
            self.query_set = model.all()
    
    def get(self,request, *args, **kwargs) :
        return self.sendResponse(self.query_set_to_list(self.query_set))
    
    #format the queryset result in dict format filtering columns for the response
    def query_set_to_list(self,query_set) :
        result = []
        for entry in query_set :
            row = {}
            row.update({'id' :entry.key().id()})        
            
            for p in entry.properties() :
                if(len(self.white_list)>0) :
                    if(p in self.white_list) :
                        row.update({p :unicode(getattr(entry, p))})                        
                elif(len(self.black_list)>0) :
                    if(p not in self.black_list) :
                        row.update({p :unicode(getattr(entry, p))})
                else : 
                    row.update({p :unicode(getattr(entry, p))})                     
            result.append(row)
              
        return result
    
# detail view
class DetailRestView(RestView) :
    #model used to manage data
    model = None
    # instance on the model
    # model instancied one's but call many times
    model_instance = None
    white_list = []
    black_list = []    
    
    def get(self, request, *args, **kwargs):
        obj = self.getModelInstance(request)
        if obj :
            objName = obj.__class__.__name__
            return self.sendResponse({'success' : 'OK', objName : self.serialize(obj) })
        else :
            return http.HttpResponseNotFound()
    
    def post(self, request, *args, **kwargs) :
        mod = __import__(self.model.__module__, fromlist=[self.model.__name__])
        klass = getattr(mod, self.model.__name__)
        obj =  klass()        
        return self.update(request,obj)                
    
    def put(self, request, *args, **kwargs):
        obj = self.getModelInstance(request)
        if obj : 
            return self.update(request,obj)
        else :
            return http.HttpResponseNotFound()
    
    def delete(self, request, *args, **kwargs):
        obj = self.getModelInstance(request)
        if obj :
            obj.delete()
            data ={ 'success': "OK"}
            return self.sendResponse(data)
        else :
            return http.HttpResponseNotFound()
    
    # update or create an entity in the datastore and send the response
    def update(self, request, obj, *args, **kwargs) :
        post = self.getData(request)
        obj = self.persist(obj,post)
        objName = obj.__class__.__name__
        return self.sendResponse({'success' : 'OK', objName : self.serialize(obj) })
    
    # persist the entity in the datastore     
    def persist(self,obj,post) :
    #def update_model(model, values):
        for k, v in post.iteritems():
            if k in obj.properties() :
                setattr(obj, k, v)                             
        obj.put()
        return obj
    
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
    # instance the model if None and return it    
    def getModelInstance(self, request) :
        if(self.model_instance == None):
            id = self.getRessourceId(request)
            if id <> 0 :
                self.model_instance = self.model.get_by_id(int(id))
        return self.model_instance
        
    # in rest application ans requesting
    # you don't need token validator to validate posted value     
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DetailRestView, self).dispatch(*args, **kwargs)    

#detail view using modelForm Validation :    
class DetailFormRestView(DetailRestView) :
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
        klassForm = getattr(modForm, self.form.__name__)                       
        if self.getRessourceId(request) <> 0 :
            obj = self.getModelInstance(request)
            form = klassForm(self.getData(request), instance=obj)
        else:
            form = klassForm(self.getData(request))
        return form
         
    
        
    