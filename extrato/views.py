from datetime import datetime
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from perfil.models import Conta, Categoria
from .models import Valores
from django.contrib import messages
from django.contrib.messages import constants
import os
from django.template.loader import render_to_string
from django.conf import settings 
from weasyprint import HTML
from io import BytesIO # Biblioteca que permite salvar os Bytes em memória, em vez de salvar no disco.

def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        
        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        #Soma e subtração do valor da conta, dependendo do tipo do extrato
        if tipo == 'E':
            conta.valor += int(valor)
            messages.add_message(request, constants.SUCCESS, 'Entrada cadastrada com sucesso')
        else:
            conta.valor -= int(valor)
            messages.add_message(request, constants.SUCCESS, 'Saída cadastrada com sucesso')

        conta.save()

        return redirect('/extrato/novo_valor')

def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
        
    valores = Valores.objects.filter(data__month=datetime.now().month)
    
    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')

    if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)
    ########(Licao)botao para zerar filtro, e filtrar por periodo
    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})

def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')# Colocando o caminho do arquivo HYML em uma variável, pois não se pode usar o "extratos.html" como caminho para a função "render_to_string"
    path_output = BytesIO() # Para salvar o Bytes em memória RAM, para assim ja mandar para o ususário e depois elimin-lo da memoria, fazendo com que não gaste espaço em disco na propria máquina.

    template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})# Aqui ele tranforma o HTML do Django em um HTML normal, com os dados dos usuário, e sem as funcoes do Django.
    #print(template_render) ---> Aqui vemos que foi printado no terminal o html sem as funções do django, apenas os valores dos dados.
    #return HttpResponse(template_render)

    HTML(string=template_render).write_pdf(path_output) # Instaciando o HTML no weasyprint, para gerar o seu PDF e ser salvo no "path_output".

    path_output.seek(0) #Voltando o ponteiro para o começo do arquivo, pois se estiver no final ele vai considerar o arquivo vazio, já que ele lê tudo oque estiver na frente do ponteiro.
    #(Ex: É como digitar em um rascunho vazio e sempre o ponteiro de digitar irá ficar no final do texto, com esse código, faz o ponteiro retornar para o inicio provando assim a existencia de algo non arquivo).
    
    return FileResponse(path_output, filename="extrato.pdf") # Retorna para o usuário o arquivo PDF