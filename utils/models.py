from django.db import models

# Create your models here.

class Mappable():
    def __getitem__(self, key):
        try:
            return self.map[key]
        except:
            method = getattr(self, 'get'+key[0].capitalize() + key[1:])
            value = method()
            self[key] = value
        return self.map[key]
    def __setitem__(self, key, value):
        try:
            self.map[key] = value
        except:
            self.map = {}
            self.map[key] = value