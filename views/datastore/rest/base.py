#  django views for RESt/JSON application
# with relation against datastore modeling
import json
import sys
import logging
import pprint

from django import http
from django.views.generic.base import View


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

