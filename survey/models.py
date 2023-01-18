import uuid

from django.db import models

from core.helpers import TimeStampedModel


class Survey(TimeStampedModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(unique=True, blank=False, null=False, max_length=255)

    def __str__(self):
        return self.name


QUESTION_TYPE_CHOICES = (
    ('RADIO', 'radio'),
    ('SELECT', 'select'),
    ('MULTI_SELECT', 'multi_select'),
    ('SHORT_TEXT', 'short_text'),
    ('LONG_TEXT', 'long_text'),
)


class Question(TimeStampedModel):
    title = models.CharField(unique=True, blank=False, null=False, max_length=255)
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    type = models.CharField(choices=QUESTION_TYPE_CHOICES, blank=False, null=False, max_length=255)
    add_other_option = models.BooleanField(
        default=False,
        verbose_name='Add \'other\' option',
        help_text='If selected, will display an option for users to enter a choice not listed.',
    )
    order = models.IntegerField(
        blank=False,
        null=False,
        help_text='The order in which the question appears in the survey.',
    )

    def __str__(self):
        return self.title


class Choice(TimeStampedModel):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    label = models.CharField(
        unique=False,
        blank=False,
        null=False,
        max_length=255,
        help_text='The text that will appear to users when the form is displayed',
    )
    value = models.CharField(
        unique=False,
        blank=False,
        null=False,
        max_length=255,
        help_text='The value that the choice will be saved as if a user selects it',
    )
    jump = models.ForeignKey(
        Question,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text='''The question that the user will be shown next if they select this choice,
         if left blank they will be taken to the next question in order''',
    )
