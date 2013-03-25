from django.http import HttpResponse, Http404
from models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
import math
from datetime import date
import tools

def showConta(request, conta_id, year=None, month=None):
    'exibe os lancamentos de uma conta'
    try:
        conta = Conta.objects.get(id=conta_id)
    except Conta.DoesNotExist :
        raise Http404
    
    def parseLancamento(lancamento):
        lancamento.valor = lancamento['valor']
        lancamento.trans = lancamento['transacao']
        lancamento.saldoAnt = lancamento['saldoAnt']
        lancamento.thirdName = lancamento['thirdName']
        lancamento.data = lancamento['data']
        if math.pow(lancamento.saldo - (lancamento.saldoAnt + lancamento.valor), 2) > 0.00000001:
            lancamento.saldo = lancamento.saldoAnt + lancamento.valor
            super(Lancamento,lancamento).save()
            lancamento.fixed = True
        if lancamento['transacao'].tipo.nome == 'Saldo':
            lancamento.isSaldo = True
        else:
            lancamento.isSaldo = False
        return lancamento
    
    today = date.today()
    if month == None and year == None:
        mark = date.today()
    elif month == None:
        mark = date(int(year), 1,1)
    else:
        mark = date(int(year), int(month),1)
    if month == None:
        start = date(mark.year, 1,1)
        end =  date(mark.year+1, 1,1)
    else:
        start = date(mark.year, mark.month,1)
        end =  (month == '12') and date(mark.year+1, 1,1) or date(mark.year, mark.month+1,1)
    
    year = mark.year
    month = (month != None) and int(month) or 0
    
    
    list = conta.getLancamentos(start, end)
    monthList = tools.monthList();
    monthList.insert(0,{'name':'Mes','id':0})
    context = {
        'conta':conta,
        'lancamentos':[parseLancamento(l) for l in list],
        'start':start,
        'end':end,
        'month':month,
        'year':year,
        'months':monthList,
    }
    return render_to_response('bank/templates/lancamentos.html', context, context_instance=RequestContext(request))




def showContas(request, user_id):
    'exibe todas as contas de um usuario'
    try:
        contas = Conta.objects.filter(user=user_id, ativa=True)
    except Conta.DoesNotExist :
        raise Http404
    
    total = 0
    subtotal = 0
    dividas = 0
    poupanca = 0
    credito = 0
    for c in contas:
        if c.poupanca:
            poupanca += c.saldo
        elif c.divida:
            dividas += c.saldo
            subtotal += c.saldo
        else:
            credito += c.saldo
            subtotal += c.saldo
        
        total += c.saldo
    
    context = {
        'contas':contas,
        'credito':credito,
        'subtotal':subtotal,
        'dividas':dividas,
        'poupanca':poupanca,
        'total':total
    }
    return render_to_response('bank/templates/contas.html', context, context_instance=RequestContext(request))

def confirmarTransacao(request, transacao_id):
    'confirma uma transacao'
    try:
        t = Transacao.objects.get(id=transacao_id)
    except Transacao.DoesNotExist :
        raise Http404
    t.confirmed = True
    t.save()
    return HttpResponse('')
    
    