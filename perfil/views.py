from datetime import datetime
from django.shortcuts import render , redirect
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
from .utils import calcula_equilibrio_financeiro, calcula_total
from extrato.models import Valores
from contas.models import ContaPagar , ContaPaga

def home(request):
    contas = Conta.objects.all()

    #Gerenciador de Contas
    MES_ATUAL = datetime.now().month #Pegando o Mes Atual
    DIA_ATUAL = datetime.now().day #Pegando o Dia Atual
    cont = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')
    
    contas_vencidas = cont.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
   
    contas_proximas_vencimento = cont.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    #print(contas_vencidas)
    #print(contas_proximas_vencimento)

    #EQUILIBRIO FINANCEIRO
    #Maneira diferente, rápida e eficiente de fazer o somatório do valor das contas
    conta_mes = Conta.objects.filter(banco = MES_ATUAL)
    print(conta_mes)
    saldo_total = calcula_total(contas, 'valor')

    valores = Valores.objects.filter(data__month=MES_ATUAL)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    total_livre = total_entradas - total_saidas
    
    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    return render(request, 'home.html', {'contas':contas, 'saldo_total':saldo_total,'total_entradas':total_entradas,'total_saidas':total_saidas,'percentual_gastos_essenciais': int(percentual_gastos_essenciais), 
                                        'percentual_gastos_nao_essenciais':int(percentual_gastos_nao_essenciais), 'contas_vencidas':len(contas_vencidas), 'contas_proximas_vencimento':len(contas_proximas_vencimento),
                                        'total_livre':total_livre})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    #total_contas = contas.aggregate(Sum('valor'))
    valor_total_contas = 0

    for conta in contas: #Somatório total de todas as contas
        valor_total_contas += conta.valor

    context = {
        'contas':contas,
        'valor_total_contas':valor_total_contas,
        'categorias':categorias
    }
    return render(request, "gerenciar.html", context)

def cadastrar_banco(request):
    apelido = request.POST.get('apelido') #Pegando os dados do do formulário(input) a partir do seu "name"
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0: #Validação do 'apelido' e 'valor'
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    conta = Conta( #Passando os valores do formulário para o 'models'
        apelido = apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save() #Salvando os valores do formulário no banco de dados

    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!!')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete() #Apagando a conta a partir do seu ID no banco de dados
    
    messages.add_message(request, constants.SUCCESS, 'Conta removida com sucesso')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    if len(nome.strip()) == 0: #Validação do 'apelido' e 'valor'
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    #POR VALIDACOES DO FORMS
    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria) 
        for v in valores:
            total += v.valor
        #print(f'{categoria} -> {total}')    TESTE no terminal
        dados[categoria.categoria] = total
         
    #dados[categoria.categoria] = Valores.objects.filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum'] OUTRA maneira de se fazer
    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})

