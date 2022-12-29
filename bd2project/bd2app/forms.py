from django import forms

class registo_util(forms.Form):
    logut = forms.CharField(label='Login', max_length=100,required=True)
    passut = forms.CharField(widget=forms.PasswordInput,label='Password', 
max_length=30,required=True)
    typeut = forms.CharField(label='Tipo de Utilizador', max_length=30,required=True)
    