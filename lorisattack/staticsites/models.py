import logging
from pathlib import Path
from typing import Generator, Tuple, List
from tempfile import TemporaryDirectory

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.template import engines
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _

import boto3
from bs4 import BeautifulSoup

from accounts.models import Organization
from commons.models import UserCreatedDatetimeModel


S3_RESOURCE = boto3.resource(
    's3',
    endpoint_url=settings.BOTO3_ENDPOINTS['s3']
)
S3_CLIENT = boto3.client(
    's3',
    endpoint_url=settings.BOTO3_ENDPOINTS['s3']
)

logger = logging.getLogger(__name__)


class StaticSite(UserCreatedDatetimeModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=150,
        help_text=_('Descriptor for Site')
    )
    staging_bucket = models.CharField(
        max_length=63,
        validators=[MinLengthValidator(limit_value=3)],
        help_text=_('S3 staging bucket name ')
    )
    production_bucket = models.CharField(
        max_length=63,
        validators=[MinLengthValidator(limit_value=3)],
        help_text=_('S3 production bucket name')
    )
    last_staging_sync_datetime = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    last_production_sync_datetime = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    def get_indexpage(self):
        return IndexPage.objects.get(site=self)

    def get_newspage(self):
        from news.models import NewsPage
        return NewsPage.objects.get(site=self)

    def pages(self):
        indexpage = self.get_indexpage()
        yield indexpage
        if indexpage.has_news:
            yield self.get_newspage()

    def sync(self, update_production=False):
        """Instantiate site and perform s3 bucket sync to update content in target bucket"""
        from .functions import instantiate_staticsite

        if update_production:
            bucket_name = self.production_bucket
        else:
            bucket_name = self.staging_bucket

        transferred_files = []
        try:
            self.get_indexpage()  # confirm that indexpage is defined (will throw DoesNotExist if not defined)
            site_prefix = f'site-{self.organization.pk}_'
            with TemporaryDirectory(prefix=site_prefix) as tempdir:
                tempdir_path = Path(tempdir)
                instantiate_staticsite(self, tempdir_path)
                for item in Path(tempdir).glob('**/*'):
                    if item.is_file():
                        relative_path = item.relative_to(tempdir_path)
                        transferred_files.append(relative_path)

                        key = str(relative_path)
                        logger.info(f'Uploading file ({item}) to: s3://{bucket_name}/{key}')
                        # transfer file
                        S3_CLIENT.upload_file(
                            str(item),
                            Bucket=bucket_name,
                            Key=key
                        )
        except IndexPage.DoesNotExist:
            raise  # adding for clarity, re-raise exception
        return transferred_files

    class Meta:
        unique_together = (
            'organization',
            'name'
        )


PAGE_TYPE_CHOICES = (
    ('index', 'index'),
    ('news', 'news'),
)


class StaticPageBase(UserCreatedDatetimeModel):
    site = models.ForeignKey(
        StaticSite,
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        choices=PAGE_TYPE_CHOICES,
        editable=False
    )
    filename = models.CharField(
        max_length=150,
        help_text=_('HTML Page filename')
    )
    relative_path = models.CharField(
        max_length=250,
        help_text=_('Relative Path from root index file where file exists')
    )
    template = models.TextField(
        help_text=_('Index template (in django template language format)')
    )

    def get_template_relpaths(self) -> list:
        """
        Get all relative paths contained in self.template for the following elements:

        - link
        - img
        - script

        > This is used in order to determine if all necessary relative assets are registered and provided
        """
        relative_path_files = []

        soup = BeautifulSoup(self.template, features="html.parser")
        links = soup.find_all('link')
        for link in links:
            href_attr = link.attrs.get('href')
            if href_attr and not href_attr.startswith('http'):
                relative_path_files.append(Path(href_attr))

        scripts = soup.find_all('script')
        for script in scripts:
            src_attr = script.attrs.get('src')
            if src_attr and not src_attr.startswith('http'):
                relative_path_files.append(Path(src_attr))

        images = soup.find_all('img')
        for image in images:
            src_attr = image.attrs.get('src')
            if src_attr and not src_attr.startswith('http'):
                relative_path_files.append(Path(src_attr))

        return relative_path_files

    @property
    def relative_filepath(self) -> Path:
        return Path(str(self.relative_path), str(self.filename))

    def _check_for_expected_assets(self) -> List[Path]:
        """
        check that expected assets are registered
        Raises ValueError if expected assets are *NOT* registered as PageAssets
        """
        expected_assets_relative_paths = self.get_template_relpaths()
        condition = None
        for relative_filepath in expected_assets_relative_paths:
            relative_path = str(relative_filepath.parent)
            filename = relative_filepath.name

            # update QuerySet with OR operation
            if not condition:
                condition = Q(
                    filename=filename,
                    relative_path=relative_path
                )
            else:
                condition |= Q(
                    filename=filename,
                    relative_path=relative_path
                )
        existing_assets_qs = PageAsset.objects.filter(condition)
        registered_assets = set(
            Path(a.relative_path, a.filename) for a in existing_assets_qs
        )
        if registered_assets != set(expected_assets_relative_paths):
            missing = set(expected_assets_relative_paths) - registered_assets
            raise ValueError(f'PageAssets in template not registered: {missing}')

        return expected_assets_relative_paths

    def prepare_assets(self, target_root_directory: Path) -> Generator[Tuple[Path, Path], None, None]:
        """
        Instantiate registered assets to the given target_root_directory
        """
        self._check_for_expected_assets()

        for asset in PageAsset.objects.filter(page=self):
            absolute_filepath = target_root_directory / str(asset.relative_path) / str(asset.filename)
            relative_filepath = Path(str(asset.relative_path), str(asset.filename))

            logger.info(f'Writing PageAsset({relative_filepath}) to ({target_root_directory}) ...')
            asset.instantiate(target_root_directory)
            yield absolute_filepath, relative_filepath

    class Meta:
        unique_together = (
            'site',
            'type'
        )


class IndexPage(StaticPageBase):
    newsitems_template_variablename = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text=_('Define if index template contains news items')
    )

    @property
    def has_news(self):
        if self.newsitems_template_variablename:
            return True
        return False

    def instantiate(self, root_directory: Path):

        # prepare template
        django_engine = engines['django']
        template = django_engine.from_string(self.template)

        news_context = None
        if self.has_news:
            newspage = self.site.get_newspage()

            # get latest MAX_INDEX_NEWSITEMS news items
            news_context = {
                self.newsitems_template_variablename: newspage.get_latest_n_published(n=settings.MAX_INDEX_NEWSITEMS)
            }
        filepath = root_directory / str(self.relative_path) / str(self.filename)
        with filepath.open('w', encoding='utf8') as html_out:
            html = template.render(context=news_context)
            html_out.write(html)

    def save(self, *args, **kwargs):
        self.filename = 'index.html'
        self.type = 'index'  # auto-populate 'type' field
        super().save(*args, **kwargs)


VALID_FILE_TYPE_CHOICES = (
    ('css', 'css'),
    ('js', 'javascript'),
    ('img', 'image'),
    ('pdf', 'pdf'),
)


class PageAsset(UserCreatedDatetimeModel):
    page = models.ForeignKey(
        StaticPageBase,
        on_delete=models.CASCADE,
    )
    file_type = models.CharField(
        max_length=15,
        choices=VALID_FILE_TYPE_CHOICES,
        help_text=_(f'Type of file ({VALID_FILE_TYPE_CHOICES})')
    )
    filename = models.CharField(
        max_length=150,
        help_text=_('Filename')
    )

    relative_path = models.CharField(
        max_length=250,
        help_text=_('Relative Path from root index file where file exists')
    )
    # to save file content use:
    # model.file_content.save(FILENAME, ContentFile(b'content'))
    file_content = models.FileField()

    @property
    def relative_filepath(self) -> Path:
        return Path(str(self.relative_path), str(self.filename))

    def instantiate(self, root_directory: Path) -> Path:
        """
        copy file from upload location to target path
        On upload, file is saved at MEDIA Bucket location, copy locally in order to instaniate for bucket sync operation
        """
        output_filepath = root_directory / str(self.relative_path) / str(self.filename)
        output_filepath.parent.mkdir(exist_ok=True, parents=True)  # create relative directories
        with output_filepath.open('wb') as output:
            output.write(self.file_content.read())
        return output_filepath
