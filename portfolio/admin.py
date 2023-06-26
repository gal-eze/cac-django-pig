from django.contrib import admin
from portfolio.models import Security, Portfolio, Transaction

admin.site.register(Security)
admin.site.register(Portfolio)
admin.site.register(Transaction)
