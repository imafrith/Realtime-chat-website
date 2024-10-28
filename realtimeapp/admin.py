from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Chatgroup)
admin.site.register(GroupMessage)
admin.site.register(Profile)
