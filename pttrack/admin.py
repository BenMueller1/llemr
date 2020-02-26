from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.admin import ModelAdmin
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _

from . import models

@admin.register(models.PatientSummary)
class PatientSummaryAdmin(ModelAdmin):
    change_list_template = 'admin/patient_summary_change_list.html'
    date_hierarchy = 'date_of_birth'

    def changelist_view(self, request, extra_content=None):
        response = super(PatientSummaryAdmin, self).changelist_view(
            request, extra_content)

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('languages', distinct=True)
        }

        response.context_data['languages'] = list(
            models.Language.objects.all()
            .annotate(count_spoken=Count('patient'))
            .order_by('-count_spoken')[:10]
        )

        response.context_data['ethnicities'] = list(
            models.Ethnicity.objects.all()
            .annotate(count=Count('patient'))
            .order_by('-count')
        )

        # print(models.Ethnicity.objects.all().aggregate(Sum('count')))

        print( models.Ethnicity.objects.all()
            .annotate(count=Count('patient'))
            .aggregate(Sum('count')))
        response.context_data['ethnicities_total'] = dict(
            models.Ethnicity.objects.all()
            .annotate(count=Count('patient'))
            .aggregate(Sum('count'))
        )

        # list(
        #     qs.values('languages').distinct().annotate(**metrics))

        # print(qs.values('languages'))
        # # Distinct does not work
        # print(qs.values('languages').annotate(**metrics))
        # print(models.Patient.objects.aggregate(**metrics))

        # for language in models.Language.objects.all():
        #     print(language, language.patient_set.count())

        test = models.Language.objects.all().annotate(count_spoken=Count('patient')).order_by('-count_spoken') 
        # print(test[0:10])
        # print(test[0].count_spoken)
        # print(test[0])
        return response

class CompletionFilter(SimpleListFilter):
    title = _('Completion')
    parameter_name = 'completion_status'

    def lookups(self, request, model_admin):
        return (
            ("Complete", _('Completed')),
            ("Unresolved", _('Unresolved')),
        )

    def queryset(self, request, queryset):
        if self.value() == "Complete":
            return queryset.exclude(completion_date=None)
        if self.value() == "Unresolved":
            return queryset.filter(completion_date=None)


class NoteAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')
    list_display = ('__str__', 'written_datetime', 'patient', 'author',
                    'last_modified')


class ActionItemAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')
    date_hierarchy = 'due_date'
    list_display = ('__str__', 'written_datetime', 'patient', 'author',
                    'last_modified')
    list_filter = ('instruction', CompletionFilter, )


for model in [models.Language, models.Patient, models.Provider,
              models.ActionInstruction, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)

admin.site.register(models.Document, NoteAdmin)
admin.site.register(models.ActionItem, ActionItemAdmin)
