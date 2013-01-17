from django import forms


GRADE_CHOICES = ((u'---', u'---'),(u'G3', u'G3'), (u'G4', u'G4'), (u'G5',u'G5'), (u'G6',u'G6'), (u'G7',u'G7'), (u'G8',u'G8'), (u'G9',u'G9'))					
TEST_CHOICES = ((u'LL', u'LL'), (u'ML', u'ML'), (u'UL', u'UL'))
DAY_CHOICES = ((u'1', u'Mon'), (u'2', u'Tue'), (u'3', u'Wed'), (u'4', u'Thu'), (u'5', u'Fri'), (u'6', u'Sat'), (u'7', u'Sun'))

class AddUserForm(forms.Form):
	username = forms.CharField(max_length=20)
	password = forms.CharField(max_length=20)
	first_name = forms.CharField(max_length=20)
	last_name = forms.CharField(max_length=20)
	grade = forms.ChoiceField(choices=GRADE_CHOICES)
	email = forms.EmailField(required=False)

class DeleteUserForm(forms.Form):
	username = forms.CharField(max_length=20)
	
class AddClassForm(forms.Form):
	code = forms.CharField(max_length=20)
	description = forms.CharField(max_length=50)
	level = forms.ChoiceField(choices=TEST_CHOICES)
	day = forms.ChoiceField(choices=DAY_CHOICES)

class DeleteClassForm(forms.Form):
	code = forms.CharField(max_length=20)
	
class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(max_length=20, widget=forms.PasswordInput)
	new_password = forms.CharField(max_length=20, widget=forms.PasswordInput)
	confirm_new_password = forms.CharField(max_length=20, widget=forms.PasswordInput)
	
class EditUserForm(forms.Form):
	username = forms.CharField(max_length=20)
	password = forms.CharField(max_length=20, required=False)
	first_name = forms.CharField(max_length=20)
	last_name = forms.CharField(max_length=20)
	grade = forms.ChoiceField(choices=GRADE_CHOICES)
	email = forms.EmailField(required=False)