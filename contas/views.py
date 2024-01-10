from datetime import datetime
from django.shortcuts import render, redirect
from perfil.models import Categoria
from .models import *
from django.contrib import messages
from django.contrib.messages import constants

def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/definir_contas')

def ver_contas(request):
    MES_ATUAL = datetime.now().month #Pegando o Mes Atual
    DIA_ATUAL = datetime.now().day #Pegando o Dia Atual
    
    contas = ContaPagar.objects.all()
    #Filtra as contas pagas do mes atual e pega o valor do ID da conta na qual foi paga
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')
    # As contas vencidas são contas que estão em um dia menor do que o dia atual, por isso usasse o "__lt", e exclui as contas pagas já que elas podem ter sido pagas apos o vencimento.
    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    # Pegara o valor do dia atual e será acrescentado mais 5, se a soma for 'maior-igual', o usuário será alertado. E tambem pegando o dia de pagamento seja maior que o dia atual, e depois exclui as contas pagas
    # "__lte" = 'maior-igual'     "__gte" = 'maior que'
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)

    return render(request, 'ver_contas.html', {'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento, 'restantes': restantes})
