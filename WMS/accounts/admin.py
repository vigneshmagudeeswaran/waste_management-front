from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Query)
admin.site.register(Tag)
admin.site.register(Pickup)