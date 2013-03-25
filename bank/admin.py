from models import *
from django.contrib import admin
from django import forms
from django.forms.models import modelformset_factory

class LancamentoForm(forms.ModelForm):
    conta=forms.ModelChoiceField(queryset=Conta.objects.order_by('nome'))
    class Meta:
        exclude=['saldo']

class LancamentoAdmin(admin.ModelAdmin):
    form=LancamentoForm
    list_display=('conta',)
    

class ThirdLancamentoForm(forms.ModelForm):
    third=forms.ModelChoiceField(queryset=Third.objects.order_by('name'))
    class Meta:
        exclude=['saldo', 'lancamento']

class ThirdLancamentoAdmin(admin.ModelAdmin):
    form=ThirdLancamentoForm
    list_display=('third',)

class TransacaoForm(forms.ModelForm):
    desc=forms.CharField(widget=forms.Textarea(), required=False)
    tipo=forms.ModelChoiceField(queryset=TipoTransacao.objects.order_by('nome'))
    '''
    owner=forms.ModelChoiceField(queryset=Conta.objects.all())
    third=forms.ModelChoiceField(queryset=Third.objects.all())
    def is_valid(self):
        data = self.data
        l = Lancamento()
        l.conta = Conta.objects.get(id=data['owner'])
        l.save()
        t = ThirdLancamento()
        t.third = Third.objects.get(id=data['third'])
        t.save()
        self.instance.owner = l
        self.instance.third = t
        data['owner'] = l.id
        data['third'] = t.id
        self.data = data
        return super(TransacaoForm, self).is_valid();
    def save_form_data(self):
        data = self.data
        l = Lancamento()
        l.conta = Conta.objects.get(id=data['owner'])
        l.save()
        t = ThirdLancamento()
        t.third = Third.objects.get(id=data['third'])
        t.save()
        self.instance.owner = l
        self.instance.third = t
        data['owner'] = l.id
        data['third'] = t.id
        self.data = data
        return super(TransacaoForm, self).save_form_data;
        
    def _html_output(self):
        a = 1
        a = a.a
        return super(TransacaoForm, self)
        '''

class TransacaoAdmin(admin.ModelAdmin):
    form=TransacaoForm

admin.site.register(Bank)
admin.site.register(Conta)
admin.site.register(Transacao,TransacaoAdmin)
admin.site.register(TipoTransacao)
admin.site.register(Lancamento,LancamentoAdmin)
admin.site.register(Third)
admin.site.register(ThirdLancamento,ThirdLancamentoAdmin)