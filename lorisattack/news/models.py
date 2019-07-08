from math import ceil
from pathlib import Path
from typing import Generator

from django.db import models
from django.template import engines
from django.db.models import QuerySet
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _

from commons.models import UserCreatedDatetimeModel
from staticsites.models import IndexPage, StaticPageBase


DEFAULT_ITEMS_PER_PAGE = 5


class NewsPage(StaticPageBase):
    index = models.OneToOneField(
        IndexPage,
        on_delete=models.CASCADE,
    )

    def get_total_pages(self, items_per_page: int = 10) -> int:
        return ceil(NewsItem.objects.filter(is_published=True).order_by('-publish_on').count() / items_per_page)

    def get_newsitems_pages(self, items_per_page: int = 10) -> Generator[QuerySet, None, None]:
        qs = NewsItem.objects \
            .filter(
                newspage=self,
                is_published=True,
            )\
            .order_by('-publish_on')

        for page_number in range(self.get_total_pages(items_per_page)):
            offset = items_per_page * page_number
            yield qs[offset: offset + items_per_page]

    def get_latest_n_published(self, n: int = 6) -> QuerySet:
        return NewsItem.objects.filter(is_published=True).order_by('-publish_on')[:n]

    def instantiate(self, root_directory: Path, items_per_page: int = DEFAULT_ITEMS_PER_PAGE) -> list:
        """
        Create instantiated HTML and images in given root_directory
        """
        # prepare template
        django_engine = engines['django']
        template = django_engine.from_string(self.template)

        result_page_data = []
        for page_count, page_queryset in enumerate(self.get_newsitems_pages(items_per_page)):
            page_numbered_filename = str(self.filename.format(page_count))
            relative_filepath = Path(str(self.relative_path), page_numbered_filename)
            absolute_filepath = root_directory / relative_filepath

            # make directories for target news html file
            absolute_filepath.parent.mkdir(parents=True, exist_ok=True)
            with absolute_filepath.open('w', encoding='utf8') as html_out:
                html = template.render(context={
                    self.index.newsitems_template_variablename: page_queryset
                })
                html_out.write(html)
            page_data = {
                'relative_path': relative_filepath,
                'absolute_path': absolute_filepath,
                'filename': page_numbered_filename,
                'page_count': page_count
            }
            result_page_data.append(page_data)
        return result_page_data

    def save(self, *args, **kwargs):
        self.filename = 'news_{}.html'  # TODO: May want multiple pages here
        self.relative_path = 'news'
        self.type = 'news'  # auto-populate 'type' field
        super().save(*args, **kwargs)


class NewsItem(UserCreatedDatetimeModel):
    newspage = models.ForeignKey(
        NewsPage,
        on_delete=models.CASCADE
    )
    publish_on = models.DateTimeField()
    is_published = models.BooleanField(
        default=False
    )
    image = models.ImageField(
        null=True,
        blank=True,
    )
    image_relpath = models.CharField(
        max_length=250,
        default='imgs/news'
    )
    title = models.CharField(
        max_length=150,
        help_text=_('News Item Title')
    )
    text = models.TextField(
        validators=[MinLengthValidator(limit_value=10)]
    )
