from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group

from home.models import AppUser
from portfolio.models import Broker, Portfolio, Security, Transaction


# custom admin site
class StockfolioAdminSite(admin.AdminSite):
    site_header = "Administracion Stockfolio"
    site_title = "Administracion usurio con privilegios"
    index_title = "Administracion del sitio"
    empty_value_display = "No hay datos para visualizar"


class TransactionInline(admin.TabularInline):
    model = Transaction


class PortfolioAdmin(admin.ModelAdmin):
    inlines = [
        TransactionInline,
    ]


custon_adm_site = StockfolioAdminSite(name="staff")
custon_adm_site.register(Security)
custon_adm_site.register(Portfolio, PortfolioAdmin)
custon_adm_site.register(Broker)
custon_adm_site.register(AppUser, UserAdmin)
custon_adm_site.register(Group, GroupAdmin)
