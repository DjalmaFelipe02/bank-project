from django.shortcuts import render
from perfil.models import Categoria
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def definir_planejamento (request):
    categorias = Categoria.objects.all()
    return render(request, 'definir_planejamento.html', {'categorias': categorias})


@csrf_exempt # Isenta essa View do CSRF_token
def update_valor_categoria(request, id):
    novo_valor = json.load(request)['novo_valor'] # Carrega a request como JSON, e pega o atributo "novo-valor"
    categoria = Categoria.objects.get(id=id) # Pegar o ID da categoria, que seja igual a do ID passada pelo parâmetro 
    categoria.valor_planejamento = novo_valor # Aplicar o novo valor do planejamento
    categoria.save() 

    return JsonResponse({'status': 'Sucesso'})

def ver_planejamento(request):
    categorias = Categoria.objects.all()
    return render(request, 'ver_planejamento.html', {'categorias': categorias})