from django.db import models
from django.conf import settings


class UserCreatedDatetimeModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="%(app_label)s_%(class)s_created_by"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="%(app_label)s_%(class)s_updated_by"
    )
    created_datetime = models.DateTimeField(
        auto_now_add=True,
    )
    updated_datetime = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True
