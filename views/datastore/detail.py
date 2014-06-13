from  django.views.generic.detail import SingleObjectMixin


class SingleEntityMixin(SingleObjectMixin) :
    entity = None
    
    def get_entity(self,id):
        if(self.entity == None):
            if id <> 0 :
                self.model_instance = self.model.get_by_id(int(id))
        return self.entity
    
        
        
""" 
todo : create class  DetalView() ...
"""