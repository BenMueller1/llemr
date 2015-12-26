from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models

# Register your models here.
for model in [models.Language, models.Patient, models.Provider,
              models.ClinicDate, models.Workup, models.ClinicType,
              models.ActionInstruction, models.ActionItem, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.Document, models.DocumentType]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
