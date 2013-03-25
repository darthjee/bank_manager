from django.db import models
from django.contrib.auth.models import User
from utils.models import Mappable
from datetime import datetime
from warnings import catch_warnings
# Create your models here.


class Bank(models.Model):
    '''banco'''
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    
    class Meta():
        app_label = 'bank'
    
    
class TipoTransacao(models.Model):
    '''categoria da transacao (serve para se criar filtros de busca)'''
    nome = models.CharField(max_length=32, unique=True);
    TYPES=((None,'----'),('S','Starter'),)
    type = models.CharField(max_length=1, choices=TYPES, default=None, null=True,blank=True)
    def __unicode__(self):
        return self.nome
    
    class Meta():
        app_label = 'bank'
    
    
class Conta(models.Model, Mappable):
    '''conta do usuario'''
    bank = models.ForeignKey(Bank, related_name='contas')
    user = models.ForeignKey(User, related_name='contas')
    nome = models.CharField(max_length=32);
    saldo = models.FloatField(default=0)
    poupanca = models.BooleanField(blank=True, default=False,null=False)
    divida = models.BooleanField(blank=True, default=False,null=False)
    ativa = models.BooleanField(blank=True, default=True,null=False)
    desc = models.CharField(max_length=100,blank=True, null=True)
    def __unicode__(self):
        map = {'bank':self.bank, 'user':self.user, 'nome':self.nome, 'saldo':None}
        if self.saldo < 0:
            map["saldo"] = u"(%.2f)" % self.saldo
        else:
            map["saldo"] = u"%+.2f" % self.saldo
        return u"%(bank)s - %(user)s - %(nome)s - %(saldo)s" % map
    def save(self):
        '''salva criando um lancamento inicial e um third relacionado'''
        if self.id == None:
            valor = self.saldo
            self.saldo=0
            super(Conta,self).save()
            if valor != 0:
                l = Lancamento()
                l.conta = self
                l.save()
                th = ThirdLancamento()
                th.third = Third.objects.get(type='S')
                th.save()
                t = Transacao()
                t.owner = l
                t.third = th
                t.valor = valor
                t.tipo = TipoTransacao.objects.get(type='S')
                t.data = datetime.now()
                t.save()
            t = Third()
            t.conta = self
            t.desc = self.desc
            t.name = "%(bank)s - %(user)s" % {'bank':self.bank, 'user':self.user}
            t.save()
        else:
            super(Conta,self).save()
    
    def getThird(self):
        try:
            return self.third.all()[0]
        except:
            return None
            
    def getLancamentos(self, start=None, end=None):
        '''retorna todos os lancamentos para a conta ordenados pela data da transacao'''
        query = '''SELECT l.* FROM bank_lancamento l
        LEFT JOIN bank_thirdlancamento h ON l.id=h.lancamento_id
        LEFT JOIN bank_transacao t ON t.owner_id=l.id OR t.third_id = h.id
        WHERE l.conta_id = %(id)s AND t.data BETWEEN %(start)s AND %(end)s
        ORDER BY t.data ASC'''
        return Lancamento.objects.raw(query, {'id':self.id, 'start':start,'end':end})
    
    class Meta():
        app_label = 'bank'


class Lancamento(models.Model, Mappable):
    '''Lancamentos na conta'''
    conta = models.ForeignKey(Conta, related_name='lancamentos')
    saldo = models.FloatField(blank=True, default=0)
    def __unicode__(self):
        mapa = {'conta':self.conta.nome, 'origem':None, 'valor':None}
        valor = self['valor']
        if valor > 0:
            mapa['valor'] = "%.2f *********************" % valor
        elif valor != None:
            mapa['valor'] = "(%.2f)" % valor
        try:
            mapa['origem'] = self.transacao.all()[0].third.third.name
        except:
            try:
                mapa['origem'] = self.third.all()[0].transacao.all()[0].owner.conta.nome
            except:
                pass
        return u"%(conta)s - %(origem)s - %(valor)s" % mapa
    def save(self):
        '''O salvamento deve antes atualizar o saldo'''
        super(Lancamento,self).save()
        valor = self['valor']
        if valor != None:
            self.conta.saldo += valor
            self.conta.save()
            try:
                self.saldo = self.getPrev().saldo+valor
            except:
                self.saldo = valor
        super(Lancamento,self).save()
    def getTransacao(self):
        '''retorna o objeto transacao do lancamento'''
        try:
            trans = self.transacao.all()[0]
            self.isThird = False
        except:
            try:
                third = self.third.all()[0]
                trans = third.transacao.all()[0]
                self.isThird = True
            except:
                return None
        self['transacao'] = trans
        return trans
    def getValor(self):
        '''retorna o valor de um lancamento atraves da transacao'''
        try:
            valor = self['transacao'].valor
            if self.isThird:
                valor = -valor
        except:
            valor = None
        self['valor'] = valor
        return valor
    def getRelative(self, type, index=1):
        '''retorna um lancamento relativo ao lancamento atual
        podendo ser o proximo (next) ou anterior (prev)
        index determina a distancia (padrao 1)'''
        if type == 'prev':
            relative = '<'
            order = 'DESC'
        else:
            relative = '>'
            order = 'ASC'
        trans = self.getTransacao()
        if (trans == None):
            return None
        rel = Lancamento.objects.raw('''SELECT l.* FROM bank_lancamento l
        LEFT JOIN bank_thirdlancamento h ON l.id=h.lancamento_id
        LEFT JOIN bank_transacao t ON t.owner_id=l.id OR t.third_id = h.id
        WHERE (t.data %(relative)s %%s OR (t.data = %%s AND t.id %(relative)s %(transid)s)) AND l.conta_id = %%s AND l.id != %%s
        ORDER BY t.data %(order)s, t.id %(order)s LIMIT 1''' % {'relative':relative, 'order':order, 'transid':trans.id},
        [trans.data.isoformat().replace('T',' '),trans.data.isoformat().replace('T',' '), self.conta.id, self.id])
        return rel[index-1]
    def getNext(self, index=1):
        '''retorna o proximo lancamento
        index determina a distancia (padrao 1)'''
        self['next'] = self.getRelative('next', index)
        return self['next']
    def getPrev(self, index=1):
        '''retorna o lancamento anterior
        index determina a distancia (padrao 1)'''
        self['prev'] = self.getRelative('prev', index)
        return self['prev']
    def getSaldoAnt(self):
        '''retorna o saldo anterior do lancamento'''
        try:
            return self['prev'].saldo
        except:
            return 0
    def getThirdName(self):
        '''retorna o nome da outra entidade envolvida na transacao'''
        transacao = self['transacao']
        if self.isThird:
            return transacao.owner.conta.nome
        else:
            return transacao.third.third['nome']
    def getData(self):
        '''retorna a data do lancamento'''
        transacao = self['transacao']
        self['data'] = transacao.data
        return self['data']
    def delegate(self, conta):
        '''delega um lancamento a outra conta'''
        t = self['transacao']
        valor = t.valor
        t.valor = 0
        t.save()
        self.conta = conta
        self.save()
        t = Transacao.objects.get(id=t.id)
        t.valor = valor
        t.save()
    
    class Meta():
        app_label = 'bank'




class Third(models.Model, Mappable):
    '''terceiro na transacao (podendo se relacionar a uma conta)'''
    conta = models.ForeignKey(Conta, blank=True, related_name='third', null=True, unique=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(blank=True)
    TYPES=((None,'----'),('S','Starter'),)
    type = models.CharField(max_length=1, choices=TYPES, default=None, null=True,blank=True)
    def __unicode__(self):
        if self.conta == None:
            return self.name
        return u"%s" % self.conta
    def getNome(self):
        if self.conta != None:
            nome = self.conta.nome
        else:
            nome = self.name
        self['nome'] = nome
        return nome
    def getThirdTransacoes(self):
        return self.lancamentos.all()
    def delegate(self, third):
        transacoes = self.getThirdTransacoes()
        for t in transacoes:
            t.delegate(third)
    
    class Meta():
        app_label = 'bank'


class ThirdLancamento(models.Model, Mappable):
    '''lancamento especial para terceiros'''
    lancamento = models.ForeignKey(Lancamento, related_name='third', blank=True, unique=True, null=True)
    third = models.ForeignKey(Third, related_name='lancamentos', blank=False)
    def save(self):
        if self.third.conta != None and self.lancamento == None:
            l = Lancamento()
            l.conta = self.third.conta
            l.save()
            self.lancamento = l
        if self.lancamento != None:
            self.lancamento.save()
        super(ThirdLancamento,self).save()
    def __unicode__(self):
        map = {'owner':None, 'third':None, 'valor':0}
        try:
            map['third'] = self.third.name
        except:
            pass
        try:
            valor = self.transacao.all()[0].valor
            if valor < 0: 
                map['valor'] = "(%.2f)" % valor
            else:
                map['valor'] = "%.2f *********************" % valor
        except:
            pass
        try:
            map['owner'] = self.transacao.all()[0].owner.conta.nome
        except:
            pass
        return u"%(owner)s - %(third)s : %(valor)s" % map
    def delegate(self, third):
        '''delega um lancamento a outro third'''
        t = self['transacao']
        valor = t.valor
        t.valor = 0
        t.save()
        self.third = third
        self.save()
        t = Transacao.objects.get(id=t.id)
        t.valor = valor
        t.save()
    def getTransacao(self):
        try:
            return self.transacao.all()[0]
        except:
            pass
        return None
    
    class Meta():
        app_label = 'bank'


class Transacao(models.Model):
    '''Transacao entre uma conta e um terceiro'''
    owner = models.ForeignKey(Lancamento, related_name='transacao', unique=True)
    third = models.ForeignKey(ThirdLancamento, related_name='transacao', unique=True, null=True)
    valor = models.FloatField(default=0, blank=True)
    data = models.DateTimeField()
    desc = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.ForeignKey(TipoTransacao, related_name='+')
    confirmed = models.BooleanField(blank=True, default=False,null=False)
    def calcValueUpToDate(self):
        return self.owner.conta.saldo
    def save(self):
        if self.id != None:
            self.correctContas()
        super(Transacao,self).save()
        self.owner.save()
        self.third.save()
    def correctContas(self):
        oldValue = Transacao.objects.get(id=self.id).valor
        try:
            conta = self.owner.conta
            conta.saldo -= oldValue
            conta.save()
        except:
            pass
        try:
            conta = self.third.lancamento.conta
            conta.saldo += oldValue
            conta.save()
        except:
            pass
    def __unicode__(self):
        map = {'owner':None, 'third':None, 'valor':"", 'confirmed':""}
        valor = self.valor
        if valor < 0:
            map["valor"] = u"(%.2f)" % valor
        else:
            map["valor"] = u"%.2f *********************" % valor
        if not self.confirmed:
            map["confirmed"] = u"-------------"
        try:
            map['owner'] = self.owner.conta.nome
        except:
            pass
        try:
            map['third'] = self.third.third.name
        except:
            pass
        return u"%(owner)s : %(third)s : %(valor)s %(confirmed)s" % map
    
    class Meta():
        app_label = 'bank'