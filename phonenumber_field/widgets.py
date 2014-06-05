#-*- coding: utf-8 -*-

from babel import Locale

from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.utils.safestring import mark_safe
import phonenumbers


class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        locale = Locale('en', 'US')
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            prefix = '+%d' % prefix
            if initial and initial in values:
                self.initial = prefix
            for country_code in values:
                country_name = locale.territories.get(country_code)
                if country_name:
                    choices.append((prefix, u'%s %s' % (country_name, prefix)))

        super(PhonePrefixSelect, self).__init__(choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        return super(PhonePrefixSelect, self).render(name, value or self.initial, *args, **kwargs)

class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (PhonePrefixSelect(initial, ), TextInput(), TextInput(),)
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, phonenumbers.phonenumber.PhoneNumber):
                return ['+{0}'.format(value.country_code), value.national_number, value.extension]
            else:
                return value.split('.')

        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(data, files, name)
        return '%s.%s.%s' % tuple(values)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append('<div class="col-xs-3"> %s </div>' % (widget.render(name + '_%s' % i, widget_value, final_attrs)))
        return mark_safe(self.format_output(output))
