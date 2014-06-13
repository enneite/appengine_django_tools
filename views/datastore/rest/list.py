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


from base import BaseRestView

from ..list import MultipleEntitiesMixin

from ....auth import get_current_user
    
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
    
    
class RestAuthListView(RestListView):    
    user = None
    
    def get(self, request, *args, **kwargs ):
        self.user = get_current_user(request)
        return super(RestAuthListView, self).get(request, *args, **kwargs)    
    
    