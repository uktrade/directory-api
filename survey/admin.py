from django.contrib import admin

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


class ChoiceInlineAdmin(admin.TabularInline):
    model = Choice
    extra = 1
    fk_name = 'question'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('title', 'survey__name')
    list_display = ('title', 'survey')
    inlines = (ChoiceInlineAdmin,)


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
