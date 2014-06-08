# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.core.exceptions import ValidationError
from django.db.models.fields import CharField, Field
from django.test import SimpleTestCase
from django.utils import six

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.models import SelectMultipleField


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]

    def test_instantiation(self):
        item = SelectMultipleField()
        self.assertIsInstance(item, Field)

    def test_get_internal_type(self):
        item = SelectMultipleField()
        charfield = CharField()
        self.assertEquals(item.get_internal_type(),
                          charfield.get_internal_type())

    def test_get_prep_value_none(self):
        """None stored as NULL in db"""
        item = SelectMultipleField()
        self.assertIs(item.get_prep_value(None), None)

    def test_get_prep_value_empty_list(self):
        """No choice stored as empty string"""
        item = SelectMultipleField()
        self.assertIsInstance(
            item.get_prep_value([]), six.string_types)
        self.assertEquals(
            item.get_prep_value([]), '')

    def test_get_prep_value_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(
            item.get_prep_value(self.choices_list), six.string_types)

    def test_to_python_none(self):
        item = SelectMultipleField()
        self.assertIs(item.to_python(None), None)

    def test_to_python_empty_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python([]), list)
        self.assertEquals(item.to_python([]), [])

    def test_to_python_list(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertTrue(item.choices)
        self.assertIsInstance(item.to_python(self.choices_list), list)
        self.assertEquals(item.to_python(self.choices_list), self.choices_list)

    def test_to_python_list_w_invalid_value(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertTrue(item.choices)
        invalid_list = ['InvalidChoice']
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_list)

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': invalid_list[0]})
        )

    def test_to_python_empty_string(self):
        item = SelectMultipleField()
        self.assertIsInstance(
            item.to_python(''), list)
        self.assertEquals(
            item.to_python(''), [])

    def test_to_python_single_string(self):
        item = SelectMultipleField()
        single = self.choices_list[3]
        self.assertIsInstance(
            item.to_python(single), list)
        self.assertEquals(
            item.to_python(single), [single])

    def test_to_python_string(self):
        item = SelectMultipleField()
        for i, v in enumerate(self.choices_list):
            subset = self.choices_list[0: i]
            encoded = encode_list_to_csv(subset)
            self.assertIsInstance(item.to_python(encoded), list)
            self.assertEqual(item.to_python(encoded), sorted(subset))

    def test_to_python_invalid_type(self):
        item = SelectMultipleField()
        invalid_type = True
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_type)

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_type']
                % {'value': type(invalid_type)}))

    def test_get_choices(self):
        """Overridden get_choices suppresses blank choice tuple"""
        item = SelectMultipleField(choices=self.choices)
        choices = item.get_choices()
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertNotIn(('', '---------'), choices)

    def test_validate(self):
        pass

    def test_validate_options_list_true(self):
        item = SelectMultipleField(choices=self.choices)
        value = self.choices_list
        self.assertTrue(item.validate_options_list(value))

    def test_validate_options_list_raises_validationerror(self):
        item = SelectMultipleField(choices=self.choices)
        value = ['InvalidChoice']
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate_options_list(value))

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': value[0]})
        )

    def test_validate_choice_true(self):
        item = SelectMultipleField(choices=self.choices)
        for n in range(len(self.choices_list) - 1):
            self.assertTrue(item.validate_option(self.choices_list[n]))

    def test_validate_choice_false(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertFalse(item.validate_option("InvalidChoice"))
