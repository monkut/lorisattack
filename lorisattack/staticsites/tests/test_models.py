

from django.test import TestCase

from accounts.models import Organization, OrganizationUser, OrganizationEmailDomain
from ..models import StaticSite, SiteIndexPage


class ModelsStaticSiteTestCase(TestCase):

    def test_method_sync_production(self):
        raise NotImplementedError()

    def test_method_sync_staging(self):
        raise NotImplementedError()


class ModelsSiteIndexPageTestCase(TestCase):

    def test_missing_assets(self):
        raise NotImplementedError()
