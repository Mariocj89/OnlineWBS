#from models import *

from django import forms
from django.core.exceptions import ValidationError
    

class WBSUserForm(forms.Form):
    """
        Form for CRUD on Users within OWBS
        It is a facade on auth.user
    """
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(max_length=50,widget=forms.PasswordInput)
    repeat_password = forms.CharField(max_length=50,widget=forms.PasswordInput)
    
    def clean(self):
        """
            Set up cleaned data and perform the validation
        """
        cleaned_data = super(WBSUserForm, self).clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("repeat_password")
        #username = cleaned_data.get("username")
        #email = cleaned_data.get("email")
        isValid = True
        if p1 != p2:
            isValid = False
            raise ValidationError("Passwords don't match", code='invalid')
        if p1 and len(p1) < 5:
            isValid = False
            raise ValidationError("Password is too short!", code='invalid')       
        return isValid
 

class WBSUpdateUserForm(WBSUserForm):
    """
        Form containing fields to update an user.
        
        It inherits from the creation one but adding the preferences.
    """
    showInlineCost = forms.BooleanField(label='Task Inline Cost',initial=False,required=False)
    showInlineCompletion = forms.BooleanField(label='Task Inline Completion',initial=False,required=False)  