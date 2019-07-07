from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _

from commons.models import UserCreatedDatetimeModel
from staticsites.models import IndexPage, StaticPageBase


class NewsPage(StaticPageBase):
    index = models.OneToOneField(
        IndexPage,
        on_delete=models.CASCADE,
    )

    def get_latest_n_published(self, n: int = 6):
        return NewsItem.objects.filter(is_published=True).order_by('-publish_on')[:n]

    def save(self, *args, **kwargs):
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
    text = models.TextField(
        validators=[MinLengthValidator(limit_value=10)]
    )
