import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _

from commons.models import UserCreatedDatetimeModel


logger = logging.getLogger(__name__)


class Organization(UserCreatedDatetimeModel):
    name = models.CharField(
        max_length=150,
        help_text=_('Name of your organization')
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f'Organization({self.name})'


class OrganizationEmailDomain(UserCreatedDatetimeModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
    domain = models.CharField(
        max_length=150,
        help_text=_('Email Domain used by the organization')
    )


class OrganizationUser(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        editable=False,
        null=True,
        on_delete=models.CASCADE
    )

    @property
    def email_domain(self):
        domain = self.email.split('@')[-1]  # NAME@DOMAIN.COM -> [ 'NAME', 'DOMAIN.COM']
        return domain

    @property
    def display_name(self):
        return f'{self.last_name}, {self.first_name}'

    def save(self, *args, **kwargs):
        # only update on initial creation
        # --> Will not have an ID on initial save
        if self.id is None:
            if not self.is_superuser:
                self.is_staff = True  # auto-add is_staff (so user can use the ADMIN)
                if not kwargs.get('ignore_email_domain_check', False):
                    # find the organization for the given user
                    try:
                        email_domain = OrganizationEmailDomain.objects.get(domain=self.email_domain)
                        self.organization = email_domain.organization
                    except OrganizationEmailDomain.DoesNotExist:
                        raise PermissionDenied('Organization does not exist for given Email Domain!')
                else:
                    logger.warning('Ignoring EMAIL DOMAIN check on user creation!')
            else:
                logger.warning(f'Creating superuser: {self.username}')
        if 'ignore_email_domain_check' in kwargs:
            del kwargs['ignore_email_domain_check']
        super().save(*args, **kwargs)
