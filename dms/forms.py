from django import forms
from django.contrib.contenttypes.models import ContentType

class DocumentForm(forms.Form):
    file = forms.FileField()
    related_objects = forms.MultipleChoiceField(choices=[])
    model_type = forms.ChoiceField(choices=[(ct.id, ct.model) for ct in ContentType.objects.all()])
