import uuid

from django.core.exceptions import ValidationError
from django.db import models

from core.helpers import TimeStampedModel


class Survey(TimeStampedModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(unique=True, blank=False, null=False, max_length=255)

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    RADIO = 'radio'
    SELECT = 'select'
    MULTI_SELECT = 'multi_select'
    SHORT_TEXT = 'short_text'
    LONG_TEXT = 'long_text'
    QUESTION_TYPE_CHOICES = (
        (RADIO, 'Radio'),
        (SELECT, 'Select'),
        (MULTI_SELECT, 'Multi select'),
        (SHORT_TEXT, 'Short text'),
        (LONG_TEXT, 'Long text'),
    )

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
    END = 'end'
    JUMP = 'jump'
    NO_ROUTING = None
    ROUTING_CHOICES = (
        (END, 'Go to end'),
        (NO_ROUTING, 'None, go to next question'),
        (JUMP, 'Jump to a different question'),
    )
    ADDITIONAL_ROUTING_ERROR = 'Multi-select questions cannot have more than one choice with additional routing.'

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

    additional_routing = models.CharField(
        blank=True,
        null=True,
        default=NO_ROUTING,
        choices=ROUTING_CHOICES,
        max_length=4,
        help_text='''If a user selects this choice, is there any additional routing?
        Or do they go to the next question in order.''',
    )

    question_to_jump_to = models.ForeignKey(
        Question,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text='''The question that the user will be shown next if they select this choice.
        This field is mandatory if additional routing is set to 'Jump to different question'.''',
    )

    def clean_fields(self, *args, **kwargs):
        if self.additional_routing == self.JUMP:
            if not self.question_to_jump_to:
                raise ValidationError({'question_to_jump_to': ['This field is required.']})
        return super().clean_fields(*args, **kwargs)
