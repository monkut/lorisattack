import os
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import boto3

from accounts.models import Organization, OrganizationUser, OrganizationEmailDomain

from ..models import StaticSite, IndexPage, PageAsset
from ..functions import instantiate_staticsite

S3_CLIENT = boto3.client(
    's3',
    endpoint_url=settings.BOTO3_ENDPOINTS['s3'],
)

STATICSITES_FIXTURES_DIRECTORY = Path(__file__).parent.parent / 'fixtures'


class StaticSiteFunctionsTestCase(TestCase):
    fixtures = ['accounts_test']

    def setUp(self) -> None:
        # prepare account information
        self.org = Organization.objects.all()[0]
        self.orgemaildomain = OrganizationEmailDomain.objects.all()[0]
        self.system_admin_user = OrganizationUser.objects.get(username='system-admin')

        # prepare buckets for site
        self.staging_bucket_name = 'staticsite-staging-test'
        S3_CLIENT.create_bucket(
            Bucket=self.staging_bucket_name
        )

        self.production_bucket_name = 'staticsite-production-test'
        S3_CLIENT.create_bucket(
            Bucket=self.production_bucket_name
        )

        # prepare site information
        self.staticsite = StaticSite(
            organization=self.org,
            name='test-staticsite',
            staging_bucket=self.staging_bucket_name,
            production_bucket=self.production_bucket_name,
            created_by=self.system_admin_user,
            updated_by=self.system_admin_user,
        )
        self.staticsite.save()

        index_template_filepath = STATICSITES_FIXTURES_DIRECTORY / 'index-sample-1.html.template'
        with index_template_filepath.open('r', encoding='utf-8') as index_template:
            self.indexpage = IndexPage(
                site=self.staticsite,
                filename='index.html',
                relative_path='.',
                template=index_template.read(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            self.indexpage.save()

    def test_functions_instantiate_staticsite(self):
        expected_relfilepaths = [
            self.indexpage.relative_filepath,
        ]
        site_prefix = 'sometestprefix-'
        with TemporaryDirectory(prefix=site_prefix) as tempdir:
            with self.assertRaises(ValueError):
                instantiate_staticsite(
                    self.staticsite,
                    Path(tempdir)
                )

            # register  assets
            assets_directory = STATICSITES_FIXTURES_DIRECTORY / 'assets'
            expected_assets = (
                ('stylesheets/plugins', 'bootstrap3.min.css'),
                ('stylesheets/plugins', 'drawer.min.css'),
                ('stylesheets', 'style.css')
            )
            for relpath, filename in expected_assets:
                local_filepath = assets_directory / filename
                content = SimpleUploadedFile(
                    name=filename,
                    content=local_filepath.open('rb').read(),
                    content_type='image/jpeg'
                )
                asset = PageAsset(
                    page=self.indexpage,
                    file_type='css',
                    filename=filename,
                    relative_path=relpath,
                    file_content=content,
                    created_by=self.system_admin_user,
                    updated_by=self.system_admin_user
                )
                asset.save()

            instantiated_page_data = instantiate_staticsite(
                self.staticsite,
                Path(tempdir)
            )
            self.assertTrue(os.listdir(tempdir))
            self.assertTrue(instantiated_page_data)
            for page_data in instantiated_page_data:
                print(page_data)
                if page_data['asset_absolute_filepaths']:
                    for asset_absolute_path in page_data['asset_absolute_filepaths']:
                        self.assertTrue(asset_absolute_path.exists())

            expected_absolute_filepath = Path(tempdir) / self.indexpage.relative_filepath
            self.assertTrue(expected_absolute_filepath.exists(), f'Expected Filepath Not found: {expected_absolute_filepath}')
