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

from  django.views.generic.edit import ModelFormMixin

from list import MultipleEntitiesMixin
from crud import CrudEntityMixin

class BaseRestView(View):
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
        klassForm = getattr(modForm, self.form.__name__)                       
        if self.getRessourceId(request) <> 0 :
            obj = self.getModelInstance(request)
            form = klassForm(self.getData(request), instance=obj)
        else:
            form = klassForm(self.getData(request))
        return form

    
    
class RestListView(BaseRestView, MultipleEntitiesMixin) : 
    
    # the queryset to execute on datastore
    queryset = None
    
    # a white list : if not empty :
    # then only the specified colums of this list will be send in the response
    white_list = []
    # a white list : if not empty :
    # then only the columns  not specified in this list will be send in the response
    black_list = []
    
    def get(self,request, *args, **kwargs) :
        
        if(self.queryset == None) :
            self.queryset = model.all()
        
        return self.sendResponse(self.queryset_to_list(self.queryset))
    
    #format the queryset result in dict format filtering columns for the response
    def queryset_to_list(self,queryset) :
        result = []
        for entry in queryset :
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
    
    def put(self, request, *args, **kwargs):
        return http.HttpResponseForbidden()
    
    def post(self, request, *args, **kwargs):
        return http.HttpResponseForbidden()
    
    def delete(self, request, *args, **kwargs):
        return http.HttpResponseForbidden()
    