from directory_constants.constants import exred_articles, exred_sector_names
from directory_validators.company import no_html
from directory_validators import enrolment as shared_validators

from django.db import models
from django.utils.functional import cached_property

from api.model_utils import TimeStampedModel

#  ('8b3f0454-5821-4635-a755-9e5a0214c594', 'ANALYSE_THE_COMPETITION')
EXREAD_ARTICLES_CHOICES = tuple(
    [(getattr(exred_articles, item), item,) for
     item in dir(exred_articles) if not item.startswith("__")]
)


class TriageResult(TimeStampedModel):
    sector = models.CharField(
        choices=exred_sector_names.SECTORS_CHOICES,
        max_length=255
    )
    exported_before = models.BooleanField()
    regular_exporter = models.BooleanField()
    used_online_marketplace = models.NullBooleanField()
    company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[no_html],
    )
    company_number = models.CharField(
        max_length=8,
        validators=[
            shared_validators.company_number,
            no_html,
        ],
        unique=True,
        null=True,
        blank=True,
    )
    sole_trader = models.BooleanField()
    sso_id = models.PositiveIntegerField(unique=True)

    @cached_property
    def sector_name(self):
        return exred_sector_names.CODES_SECTORS_DICT[self.sector]

    def __str__(self):  # pragma: no cover
        return self.company_name


class ArticleRead(TimeStampedModel):
    article_uuid = models.UUIDField(choices=EXREAD_ARTICLES_CHOICES)
    sso_id = models.PositiveIntegerField()


class TaskCompleted(TimeStampedModel):
    task_uuid = models.UUIDField()
    sso_id = models.PositiveIntegerField()
