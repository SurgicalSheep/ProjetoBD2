from django.shortcuts import redirect, render, get_object_or_404
from bd2app.forms import registo_util
from bd2app.models import *
from bd2app.other import *
from html_sanitizer.django import *
# Create your views here.

def index(request):
    context = {}
    return render(request,'index.html', context=context)

def login(request):
    return render(request,'login.html',{})

def registro(request):
    context = {}
    if request.method == 'POST':
        data = request.POST 
        nome = data.get("nome") 
        username = data.get("username")
        password = data.get("password")
        tipouser = data.get("tipouser")
        insere_ut(nome,username,password,tipouser)
        return redirect('todos_users') #esta linha vai ser apagada. só agora para testes mesmo
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'registro.html', context)

def login(request): 
    if request.method == 'POST':
        form = registo_util(request.POST)
        if 'entrar' in request.POST:
            if form.is_valid(): 
                inomev = form.cleaned_data["logut"]
                ipa = form.cleaned_data["passut"]
                va = login_ut(inomev,ipa)
                if va > 0:
                    pag = 'index.html'
                    context = {}
                else:
                    context = {'form': form,}
                    pag='login.html'
    else: 
        form = registo_util(request.POST)
        pag='login.html'
        context = {'form': form,
            }
    return render(request, pag, context)

def login_ut(username,password):
    bd = conexaomongo
    col = bd["utilizadores"]
    x = col.count_documents({"username": username,"password": password})
    return x

def novo_produto(request):
    context = {}
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        descricao = data.get("descricao")
        imagem = data.get("imagem")
        preco = data.get("preco")
        desconto = data.get("desconto")
        marca = data.get("marca")
        cor = data.get("cor")
        stock = data.get("stock")
        categoria = data.get("categoria")
        novo_produto_insert(nome,preco,marca,cor,imagem,descricao,stock,desconto,categoria)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'novo_produto.html', context)

def todos_produtos(request):
    context = {}
    if request.method == 'GET':
        pag = 'todos_produtos.html'
        products = todos_produtos_other()
        return render(request, pag, {'products': products})

def todos_users(request):
    context = {}
    if request.method == 'GET':
        pag = 'todos_users.html'
        users = todos_users_other()
        return render(request, pag, {'users': users})

def detalhes_produto(request, produto_id):
    bd = conexaomongo
    col = bd["produtos"]
    products = col.find_one({"id": produto_id})
    return render(request, 'detalhes_produto.html', {'products': products})

def apagar_produto(request,produto_id):
    context = {}
    if request.method == 'POST':
        apagar_produto_other(produto_id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'apagar_produto.html', context)
