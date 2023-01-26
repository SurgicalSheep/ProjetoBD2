from django import forms

class registo_util(forms.Form):
    logut = forms.CharField(label='Login', max_length=100,required=True)
    passut = forms.CharField(widget=forms.PasswordInput,label='Password', 
max_length=30,required=True)
    typeut = forms.CharField(label='Tipo de Utilizador', max_length=30,required=True)

class loginUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100,required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}),label='Password')

    
