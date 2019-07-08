from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import boto3

from accounts.models import Organization, OrganizationUser, OrganizationEmailDomain
from ..models import StaticSite, IndexPage, PageAsset

S3_CLIENT = boto3.client(
    's3',
    endpoint_url=settings.BOTO3_ENDPOINTS['s3'],
)

STATICSITES_FIXTURES_DIRECTORY = Path(__file__).parent.parent / 'fixtures'


class ModelsStaticSiteTestCase(TestCase):
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
        # make sure bucket is empty
        contents = S3_CLIENT.list_objects(Bucket=self.staging_bucket_name)['Contents']
        if 'Contents' in contents:
            S3_CLIENT.delete_objects(
                Bucket=self.staging_bucket_name,
                Objects=[{'Key': obj['Key']} for obj in contents['Contents']]
            )

        self.production_bucket_name = 'staticsite-production-test'
        S3_CLIENT.create_bucket(
            Bucket=self.production_bucket_name
        )
        # make sure bucket is empty
        contents = S3_CLIENT.list_objects(Bucket=self.production_bucket_name)['Contents']
        if 'Contents' in contents:
            S3_CLIENT.delete_objects(
                Bucket=self.production_bucket_name,
                Objects=[{'Key': obj['Key']} for obj in contents['Contents']]
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

    def test_method_sync_production__no_news(self):
        transferred_relative_paths = self.staticsite.sync(update_production=True)
        self.assertTrue(transferred_relative_paths)

        expected_keys = (
            'stylesheets/plugins/bootstrap3.min.css',
            'stylesheets/plugins/drawer.min.css',
            'stylesheets/style.css',
            'index.html'
        )
        objects = S3_CLIENT.list_objects(Bucket=self.production_bucket_name)['Contents']
        for obj in objects:
            self.assertTrue(obj['Key'] in expected_keys)

    def test_method_sync_staging__no_news(self):
        transferred_relative_paths = self.staticsite.sync(update_production=False)
        self.assertTrue(transferred_relative_paths)
        expected_keys = (
            'stylesheets/plugins/bootstrap3.min.css',
            'stylesheets/plugins/drawer.min.css',
            'stylesheets/style.css',
            'index.html'
        )
        objects = S3_CLIENT.list_objects(Bucket=self.staging_bucket_name)['Contents']
        for obj in objects:
            self.assertTrue(obj['Key'] in expected_keys)

    def test_method_sync_production__with_news(self):
        raise NotImplementedError()

    def test_method_sync_staging__with_news(self):
        raise NotImplementedError()


class ModelsSiteIndexPageTestCase(TestCase):
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

    def test_get_template_relpaths(self):
        expected_template_relpaths = (
            Path('stylesheets/plugins/bootstrap3.min.css'),
            Path('stylesheets/plugins/drawer.min.css'),
            Path('stylesheets/style.css'),
        )
        actual_template_relpaths = self.indexpage.get_template_relpaths()
        self.assertTrue(set(actual_template_relpaths) == set(expected_template_relpaths))

    def test__check_for_expected_assets(self):
        with self.assertRaises(ValueError):
            self.indexpage._check_for_expected_assets()

        # register missing assets
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
        results = self.indexpage._check_for_expected_assets()
        self.assertTrue(results)
