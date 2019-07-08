from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

import boto3

from accounts.models import Organization, OrganizationUser, OrganizationEmailDomain
from staticsites.models import StaticSite, IndexPage

from ..models import NewsPage, NewsItem


S3_CLIENT = boto3.client(
    's3',
    endpoint_url=settings.BOTO3_ENDPOINTS['s3'],
)


NEWS_FIXTURES_DIRECTORY = Path(__file__).parent.parent / 'fixtures'


class NewsPageTestCase(TestCase):
    fixtures = [
        'accounts_test'
    ]

    def setUp(self):

        # create media bucket
        S3_CLIENT.create_bucket(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME
        )

        # prepare account information
        self.org = Organization.objects.all()[0]
        self.orgemaildomain = OrganizationEmailDomain.objects.all()[0]
        self.system_admin_user = OrganizationUser.objects.get(username='system-admin')

        # prepare buckets for site
        self.staging_bucket_name = 'staticsite-staging-test'
        self.production_bucket_name = 'staticsite-production-test'

        S3_CLIENT.create_bucket(
            Bucket=self.staging_bucket_name
        )
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

        self.indexpage = IndexPage(
            site=self.staticsite,
            created_by=self.system_admin_user,
            updated_by=self.system_admin_user,
        )
        self.indexpage.save()

        self.newspage = NewsPage(
            site=self.staticsite,
            index=self.indexpage,
            created_by=self.system_admin_user,
            updated_by=self.system_admin_user,
        )
        self.newspage.save()

    def _get_dummy_image_file(self, sample_image_filename: str = 'sample-photo.jpeg'):
        sample_image_filepath = NEWS_FIXTURES_DIRECTORY / 'images' / sample_image_filename
        uploaded_image_file_mock = SimpleUploadedFile(
            name=sample_image_filename,
            content=sample_image_filepath.open('rb').read(),
            content_type='image/jpeg'
        )
        return uploaded_image_file_mock

    def test_get_total_pages(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_count = 15
        for i in range(publshed_newsitems_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        # create unpublished items
        one_day_from_now = timezone.now() + timezone.timedelta(days=1)
        for i in range(25):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_from_now,
                is_published=False,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        items_per_page = 10
        expected_total_pages = 2
        self.assertTrue(self.newspage.get_total_pages(items_per_page) == expected_total_pages)

    def test_get_newsitems_pages__singlepage(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_count = 1
        for i in range(publshed_newsitems_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        # create unpublished items
        one_day_from_now = timezone.now() + timezone.timedelta(days=1)
        for i in range(25):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_from_now,
                is_published=False,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()
        items_per_page = 3
        expected_page_count = 1
        page_querysets = list(self.newspage.get_newsitems_pages(items_per_page))
        self.assertTrue(
            len(page_querysets) == expected_page_count,
            f'ACTUAL len(page_querysets)({len(page_querysets)}) != expected_page_count({expected_page_count})'
        )

        total_newsitem_count = 0
        for qs in page_querysets:
            total_newsitem_count += qs.count()
        self.assertTrue(
            total_newsitem_count == publshed_newsitems_count,
            f'total_newsitem_count({total_newsitem_count}) != publshed_newsitems_count({publshed_newsitems_count})'
        )

    def test_get_newsitems_pages__multipage(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_count = 12
        for i in range(publshed_newsitems_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                title=f'newsitem({i})',
                text='text',
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        # create unpublished items
        one_day_from_now = timezone.now() + timezone.timedelta(days=1)
        for i in range(25):
            newsitem = NewsItem(
                newspage=self.newspage,
                title=f'newsitem({i})',
                text='text',
                publish_on=one_day_from_now,
                is_published=False,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()
        items_per_page = 5
        expected_page_count = ceil(publshed_newsitems_count / items_per_page)  # 3
        page_querysets = list(self.newspage.get_newsitems_pages(items_per_page))
        self.assertTrue(
            len(page_querysets) == expected_page_count,
            f'Actual: len(page_querysets)({len(page_querysets)}) != expected_page_count({expected_page_count})'
        )

        total_newsitem_count = 0
        count = 0
        for qs in page_querysets:
            total_newsitem_count += qs.count()
            count += 1

        self.assertTrue(
            total_newsitem_count == publshed_newsitems_count,
            f'total_newsitem_count({total_newsitem_count}) != publshed_newsitems_count({publshed_newsitems_count})'
        )

    def test_get_latest_n_published(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_onedayago_count = 3
        for i in range(publshed_newsitems_onedayago_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        published_newsitems_twodaysago_count = 5
        for i in range(published_newsitems_twodaysago_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=two_days_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        # create unpublished items
        for i in range(25):
            newsitem = NewsItem(
                newspage=self.newspage,
                publish_on=one_day_ago,
                is_published=False,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        latest_n = 5
        qs = self.newspage.get_latest_n_published(n=latest_n)
        actual_latest_newsitems = list(qs)
        self.assertTrue(len(actual_latest_newsitems) == latest_n)

        # check publish_on datetimes
        expected_onedayago_count = 3
        actual_onedayago_count = len([item for item in actual_latest_newsitems if item.publish_on == one_day_ago])
        self.assertTrue(actual_onedayago_count == expected_onedayago_count)

        expected_twodayago_count = 2
        actual_twodayago_count = len([item for item in actual_latest_newsitems if item.publish_on == two_days_ago])
        self.assertTrue(actual_twodayago_count == expected_twodayago_count)

    def test_instantiate__single_newspage(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_count = 5
        for i in range(publshed_newsitems_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                title=f'newsitem({i})',
                text='text',
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        items_per_page = 5
        expected_page_count = ceil(publshed_newsitems_count / items_per_page)  # 3
        site_test_prefix = 'news_test_'
        with TemporaryDirectory(prefix=site_test_prefix) as tempdir:
            result_page_data = self.newspage.instantiate(
                Path(tempdir),
                items_per_page=items_per_page
            )
            self.assertTrue(len(result_page_data) == expected_page_count)
            for page_data in result_page_data:
                instantiated_news_absolute_filepath = page_data['absolute_path']
                self.assertTrue(instantiated_news_absolute_filepath.exists())

    def test_instantiate__multi_newspages(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        # create is_publish items
        publshed_newsitems_count = 12
        for i in range(publshed_newsitems_count):
            newsitem = NewsItem(
                newspage=self.newspage,
                title=f'newsitem({i})',
                text='text',
                publish_on=one_day_ago,
                is_published=True,
                image=self._get_dummy_image_file(),
                created_by=self.system_admin_user,
                updated_by=self.system_admin_user,
            )
            newsitem.save()

        items_per_page = 5
        expected_page_count = ceil(publshed_newsitems_count / items_per_page)  # 3
        site_test_prefix = 'news_test_'
        with TemporaryDirectory(prefix=site_test_prefix) as tempdir:
            result_page_data = self.newspage.instantiate(
                Path(tempdir),
                items_per_page=items_per_page
            )
            self.assertTrue(len(result_page_data) == expected_page_count)
            for page_data in result_page_data:
                instantiated_news_absolute_filepath = page_data['absolute_path']
                self.assertTrue(instantiated_news_absolute_filepath.exists())

#    def test_instantiate__multi_newspages(self):
#        raise NotImplementedError()

    # def test_save(self):
    #     raise NotImplementedError()
    #
