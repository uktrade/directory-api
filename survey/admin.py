from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from survey.models import Choice, Question, Survey


class QuestionInlineAdmin(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    search_fields = (
        'id',
        'name',
    )

    list_display = (
        'name',
        'id',
    )
    readonly_fields = ('id',)
    inlines = (QuestionInlineAdmin,)


class ChoiceInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super(ChoiceInlineFormset, self).clean()
        if self.is_valid() and self.instance.type == Question.MULTI_SELECT:
            choices = self.cleaned_data
            choices_with_additional_routing = [c for c in choices if c.get('additional_routing')]
            if len(choices_with_additional_routing) > 1:
                raise ValidationError(Choice.ADDITIONAL_ROUTING_ERROR)


class ChoiceInlineAdmin(admin.TabularInline):
    model = Choice
    extra = 1
    fk_name = 'question'
    formset = ChoiceInlineFormset


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('title', 'survey__name')
    list_display = ('title', 'survey')
    inlines = (ChoiceInlineAdmin,)


class ChoiceAdminForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = '__all__'

    def clean(self):
        super(ChoiceAdminForm, self).clean()
        question = self.cleaned_data['question']
        if question.type == Question.MULTI_SELECT and self.cleaned_data['additional_routing']:
            if len([c for c in question.choices_with_additional_routing if c != self.instance]):
                raise ValidationError({'additional_routing': [Choice.ADDITIONAL_ROUTING_ERROR]})


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    search_fields = (
        'label',
        'question',
    )
    list_display = (
        'label',
        'question',
    )
    form = ChoiceAdminForm
