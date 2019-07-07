from django.contrib import admin
from django.contrib.auth.models import Group
from social_django.models import Association, Nonce, UserSocialAuth

from commons.admin import UserDatetimeModelAdmin
from .models import Organization, OrganizationUser, OrganizationEmailDomain


class OrganizationEmailDomainInline(admin.StackedInline):
    model = OrganizationEmailDomain
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(UserDatetimeModelAdmin):
    inlines = [OrganizationEmailDomainInline]


@admin.register(OrganizationUser)
class OrganizationUserAdmin(UserDatetimeModelAdmin):
    pass


admin.site.unregister(Group)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
