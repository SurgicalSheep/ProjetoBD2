from django.shortcuts import redirect, render, get_object_or_404
from bd2app.forms import registo_util,loginUserForm
from bd2app.models import *
from bd2app.other import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.


def index(request):
    context = {}
    return render(request, 'index.html', context=context)

def registro(request):
    context = {}
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        username = data.get("username")
        password = data.get("password")
        tipouser = data.get("tipouser")
        morada = data.get("morada")

        try:
            u = User.objects.get(username=username)
            return HttpResponse("Username exists")#meter isto bonito
        except User.DoesNotExist:
            u = User.objects.create_user(username=username,password=password)
            u.save()
            login(request,u)
            insere_ut(request.user.id,nome, tipouser, morada)
            print(request.user.id)

        return redirect('todos_users')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'registro.html', context)


def loginUser(request):
    if request.method == 'POST':
        form = loginUserForm(request.POST)
        if 'entrar' in request.POST:
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = authenticate(request,username = username,password = password)
                if user is not None:
                    login(request,user)
                    pag = 'index.html'
                    context = {}
                    print(user.id)
                else:
                    context = {'form': form}
                    pag = 'login.html'
    else:
        form = loginUserForm(request.POST)
        pag = 'login.html'
        context = {'form': form}
    return render(request, pag, context)

def logoutUser(request):
    logout(request)
    return redirect('/')

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
        novo_produto_insert(nome, preco, marca, cor, imagem,
                            descricao, stock, desconto, categoria)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'novo_produto.html', context)

def todos_produtos(request):
    context = {}
    user = request.user
    print (user.id)
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


def apagar_produto(request, produto_id):
    context = {}
    if request.method == 'POST':
        apagar_produto_other(produto_id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'apagar_produto.html', context)


def todos_pedidos(request):
    todos = todos_pedidos_model.objects.all()
    return render(request, 'todos_pedidos.html', {'todos': todos})

# ainda por acabar e meio que um teste


def novo_pedido(request):
    utilizador = todos_pedidos_model(
        id_pedido=1, id_utilizador=1, preco=50, data='2020-12-12', estado='pendente')
    utilizador.save()

#@login_required
def carrinho(request):
    itens = itens_carrinho_model.objects.all()
    carrinho = carrinho_compras.objects.get(id_cliente=1) #aqui vai o id do cliente ~~ request.user.id
    return render(request, 'carrinho.html', {'itens': itens, 'carrinho': carrinho})


def adicionar_carrinho(request, produto_id, produto_desconto,produto_nome,produto_preco,produto_imagem):
    context = {}
    print(produto_id, produto_desconto)
    quantity = request.POST.get('quantidade')
    if request.method == 'POST':
        item = itens_carrinho_model.objects.create(**{
            'id_carrinho': 1,
            'id_produto': produto_id,
            'quantidade': quantity,
            'nome_produto': produto_nome,
            'preco_produto': produto_preco,
            'imagem_produto': produto_imagem,
            'desconto_produto': produto_desconto
        })
        item.save()
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'adicionar_carrinho.html', context)

def remover_produto_carrinho(request, produto_id):
    context = {}
    if request.method == 'POST':
        remover_produto_carrinho_other(produto_id)
        return redirect('carrinho')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'carrinho.html', context)