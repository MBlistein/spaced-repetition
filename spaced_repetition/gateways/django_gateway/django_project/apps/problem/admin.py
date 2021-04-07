""" Register models here for visibility in admin view"""

from django.contrib import admin

from .models import Problem


admin.site.register(Problem)
