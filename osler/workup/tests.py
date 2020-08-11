from __future__ import unicode_literals
from builtins import str
from django.test import TestCase
from django.core import mail
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.management import call_command
from django.utils.timezone import now

from osler.core.tests.test_views import build_user, log_in_user
from osler.core.models import Patient

from osler.workup import validators
from osler.workup import models

import factory


def wu_dict(user=None, units=False, clinic_day_pk=False, dx_category=False):

    if not user:
        user = build_user()

    fake_text = factory.Faker('paragraph')

    wu = {'clinic_day': models.ClinicDate.objects.first(),
          'chief_complaint': "SOB",
          'diagnosis': "MI",
          'HPI': fake_text.generate(), 
          'PMH_PSH': fake_text.generate(), 
          'meds': fake_text.generate(), 
          'allergies': fake_text.generate(),
          'fam_hx': fake_text.generate(), 
          'soc_hx': fake_text.generate(),
          'ros': "f", 'pe': "f", 'A_and_P': "f",
          'hr': '89', 'bp_sys': '120', 'bp_dia': '80', 'rr': '16', 't': '98',
          'labs_ordered_internal': 'f', 'labs_ordered_quest': 'f',
          'got_voucher': False,
          'got_imaging_voucher': False,
          'will_return': True,
          'author': user,
          'author_type': user.groups.first(),
          'patient': Patient.objects.first()
          }

    if units:
        wu['temperature_units'] = 'F'
        wu['weight_units'] = 'lbs'
        wu['height_units'] = 'in'

    if clinic_day_pk:
        wu['clinic_day'] = wu['clinic_day'].pk

    if dx_category:
        wu['diagnosis_categories'] = [models.DiagnosisType.objects.first().pk]

    return wu

def pn_dict(user=None):

    if not user:
        user = build_user()

    pn = {
        'title': 'Good',
        'text': factory.Faker('paragraph').generate(),
        'author': user,
        'author_type': user.groups.first(),
        'patient': Patient.objects.first()
    }

    return pn

class TestEmailForUnsignedNotes(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):
        self.provider = log_in_user(
            self.client,
            build_user())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

    def test_unsigned_email(self):

        pt = Patient.objects.first()

        wu_signed = models.Workup.objects.create(**wu_dict())
        wu_signed.sign(
            self.provider.associated_user,
            active_role=self.provider.clinical_roles.filter(
                signs_charts=True).first())
        wu_signed.save()

        wu_unsigned = models.Workup.objects.create(**wu_dict())

        call_command('unsigned_wu_notify')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[OSLER] 1 Unattested Notes')
        self.assertIn(str(pt), mail.outbox[0].body)
        self.assertIn(self.provider.last_name, mail.outbox[0].body)

        self.assertIn(
            'https://osler.wustl.edu/workup/%s/' % wu_unsigned.pk,
            mail.outbox[0].body)


class TestClinDateViews(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):
        self.provider = log_in_user(
            self.client,
            build_user())

    def test_create_clindate(self):

        pt = Patient.objects.first()

        # First delete clindate that's created in the fixtures.
        models.ClinicDate.objects.all().delete()
        self.assertEqual(models.ClinicDate.objects.count(), 0)

        r = self.client.get(reverse('new-clindate', args=(pt.id,)))
        self.assertEqual(r.status_code, 200)

        r = self.client.post(
            reverse('new-clindate', args=(pt.id,)),
            {'clinic_type': models.ClinicType.objects.first().pk})

        self.assertRedirects(r, reverse('new-workup', args=(pt.id,)))
        self.assertEqual(models.ClinicDate.objects.count(), 1)

        # what happens if we submit twice?
        r = self.client.post(
            reverse('new-clindate', args=(pt.id,)),
            {'clinic_type': models.ClinicType.objects.first().pk})
        self.assertRedirects(r, reverse('new-workup', args=(pt.id,)))
        self.assertEqual(models.ClinicDate.objects.count(), 1)


class TestWorkupFieldValidators(TestCase):
    '''
    TestCase to verify that validators are functioning.
    '''

    def test_validate_hr(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_hr("100"), None)
        self.assertEqual(validators.validate_hr("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_hr("902/")
        with self.assertRaises(ValidationError):
            validators.validate_hr("..90")
        with self.assertRaises(ValidationError):
            validators.validate_hr("93.232")

    def test_validate_rr(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_rr("100"), None)
        self.assertEqual(validators.validate_rr("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_rr("90/")
        with self.assertRaises(ValidationError):
            validators.validate_rr("..90")
        with self.assertRaises(ValidationError):
            validators.validate_rr("93.232")

    def test_validate_t(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_t("100.11"), None)
        self.assertEqual(validators.validate_t("90.21"), None)

        with self.assertRaises(ValidationError):
            validators.validate_t("90x")

    def test_validate_height(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_height("100"), None)
        self.assertEqual(validators.validate_height("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_height("90x")
        with self.assertRaises(ValidationError):
            validators.validate_height("90.0")
        with self.assertRaises(ValidationError):
            validators.validate_height("93.232")

    def test_validate_weight(self):
        '''
        Test our validator for heart rate.
        '''
        self.assertEqual(validators.validate_weight("100"), None)
        self.assertEqual(validators.validate_weight("90"), None)

        with self.assertRaises(ValidationError):
            validators.validate_weight("90x")
        with self.assertRaises(ValidationError):
            validators.validate_weight("9.0")
        with self.assertRaises(ValidationError):
            validators.validate_weight("93.232")


class TestWorkupModel(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):
        self.provider = log_in_user(
            self.client,
            build_user())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

        self.valid_wu_dict = wu_dict()

    def test_sign(self):

        wu = models.Workup.objects.create(**self.valid_wu_dict)

        # attempt sign as non-attending
        disallowed_ptype = ProviderType.objects.\
            filter(signs_charts=False).first()
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                disallowed_ptype)
        wu.save()

        # attempt sign without missing ProviderType
        unassociated_ptype = ProviderType.objects.create(
            long_name="New", short_name="New", signs_charts=True)
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                unassociated_ptype)

        # attempt sign as attending
        allowed_ptype = ProviderType.objects.\
            filter(signs_charts=True).first()
        wu.sign(
            self.provider.associated_user,
            allowed_ptype)
        wu.save()
