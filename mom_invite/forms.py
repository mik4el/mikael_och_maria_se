from django.forms import ModelForm, TextInput
from django.forms import RadioSelect, ChoiceField
from datetime import datetime

from mom_invite.models import Guest

class GuestForm(ModelForm):
    """Form for adding and editing guests."""
    class Meta:
            model = Guest
            exclude = ('user','is_active',)