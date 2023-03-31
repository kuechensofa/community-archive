from django.forms import Form, ModelForm, CharField
from django.utils.translation import gettext as _

from archive.models import RecordFile, RecordTag


class RecordTagForm(Form):
    tag = CharField(max_length=100, label=_('Tag'), required=True)

    def clean_tag(self):
        tag_name = self.data['tag']
        tag_name = tag_name.strip().lower()
        return RecordTag.objects.get_or_create(name=tag_name)[0]


class RecordFileForm(ModelForm):
    class Meta:
        model = RecordFile
        fields = ['file']
