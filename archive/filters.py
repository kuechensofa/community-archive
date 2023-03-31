from django.utils.translation import gettext as _
from django.forms.widgets import CheckboxSelectMultiple
import django_filters
from archive.models import Record, RecordTag, RecordCategory


class RecordFilter(django_filters.FilterSet):
    title_contains = django_filters.CharFilter('title', 'icontains', label=_('Title'))
    physical_location = django_filters.CharFilter('physical_location', 'icontains', label=_('Physical location'))
    physical_signature = django_filters.CharFilter('physical_signature', 'icontains', label=_('Physical signature'))
    tags = django_filters.ModelMultipleChoiceFilter(queryset=RecordTag.objects.all(), widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['origin_date__year'] = django_filters.MultipleChoiceFilter('origin_date__year',
                                                                                label=_('Year of origin'),
                                                                                widget=CheckboxSelectMultiple,
                                                                                choices=self._get_collection_years())
        self.filters['category'] = \
            django_filters.ModelMultipleChoiceFilter(field_name='category', label=_('Category'),
                                                     queryset=self._get_category_queryset(),
                                                     widget=CheckboxSelectMultiple)

    def _get_collection_years(self):
        values = self.queryset.values()
        years = [value['origin_date'].year for value in values if 'origin_date' in value and value['origin_date']]
        years = list(set(years))
        years = sorted(years, reverse=True)
        years = [(year, str(year)) for year in years]

        return years

    def _get_category_queryset(self):
        return RecordCategory.objects.filter(records__in=self.queryset)

    class Meta:
        model = Record
        fields = []
