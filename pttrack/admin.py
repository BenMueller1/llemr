
from django.contrib import admin
from . import models
from . import followup_models

# Register your models here.
for model in [models.Language, models.Patient, models.Provider,
              models.ClinicDate, models.Workup, models.ClinicType,
              models.ActionInstruction, models.ActionItem, models.Ethnicity,
              ]:
    admin.site.register(model)

for model in [followup_models.ReferralType, followup_models.NoShowReason,
              followup_models.NoAptReason, followup_models.ContactMethod,
              followup_models.ContactResult, followup_models.PCPLocation,
              followup_models.LabFollowup]:
    admin.site.register(model)
