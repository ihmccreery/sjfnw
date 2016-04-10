from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator

# pylint: disable=protected-access

# User username length patch
def patch_user_model(model):
  field = model._meta.get_field("username")
  field.max_length = 100
  field.help_text = ('Required, 100 characters or fewer. Only letters, numbers,'
                     ' and @, ., +, -, or _ characters.')

  # patch because validator doesn't change if we change max_length
  for validator in field.validators:
    if isinstance(validator, MaxLengthValidator):
      validator.limit_value = 100

  # patch admin site forms
  from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm

  # pylint: disable=unsubscriptable-object
  new_help_text = UserChangeForm.base_fields['username'].help_text.replace('30', '100')

  UserChangeForm.base_fields['username'].max_length = 100
  UserChangeForm.base_fields['username'].widget.attrs['maxlength'] = 100
  UserChangeForm.base_fields['username'].validators[0].limit_value = 100
  UserChangeForm.base_fields['username'].help_text = new_help_text

  UserCreationForm.base_fields['username'].max_length = 100
  UserCreationForm.base_fields['username'].widget.attrs['maxlength'] = 100
  UserCreationForm.base_fields['username'].validators[0].limit_value = 100
  UserCreationForm.base_fields['username'].help_text = new_help_text

  AuthenticationForm.base_fields['username'].max_length = 100
  AuthenticationForm.base_fields['username'].widget.attrs['maxlength'] = 100
  AuthenticationForm.base_fields['username'].validators[0].limit_value = 100
  AuthenticationForm.base_fields['username'].help_text = new_help_text

if User._meta.get_field("username").max_length != 100:
  patch_user_model(User)
