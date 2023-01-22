import datetime
from decimal import Decimal
import json
from pprint import pprint
from bson import Decimal128
from django.shortcuts import redirect, render, get_object_or_404
from bd2app.forms import registo_util,loginUserForm
from bd2app.models import *
from bd2app.other import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.http import JsonResponse
from bson.objectid import ObjectId
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        if request.session:
            if request.session["tipouser"] == "Fornecedor":
                return redirect('homepage_fornecedores')
            elif request.session["tipouser"] == "Comercial Tipo 1":
                return redirect('homepage_comerciantetipo1')
    col = bd["produtos"]
    produtos_promocao = col.find({'active': True}).sort("desconto", -1).limit(6)
    produtos_nao_ativos = col.find({'active': False})
    inactive_product_ids = [int(str(product['id'])) for product in produtos_nao_ativos]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM top6_itens_mais_vendidos(%s)", (inactive_product_ids,))
    top6 = cursor.fetchall()
    product_ids = [item[0] for item in top6]
    produtos_mais_vendidos = col.find({'id': {'$in': product_ids}})
    categorias = col.distinct("categoria")
    return render(request, 'index.html', {'produtos_promocao':produtos_promocao, 'produtos_mais_vendidos':produtos_mais_vendidos, 'categorias':categorias})

def error404(request,exception=None):
    return render(request, '404.html')

def registro(request):
    context = {}
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        username = data.get("username")
        password = data.get("password")
        tipouser = data.get("tipouser")
        morada = data.get("morada")
        email = data.get("email")

        try:
            u = User.objects.get(username=username)
            return HttpResponse("Username exists")#meter isto bonito
        except User.DoesNotExist:
            u = User.objects.create_user(username=username,password=password)
            u.save()
            login(request,u)
            insere_ut(request.user.id,nome, tipouser, morada, username, email)
            request.session['tipouser'] = tipouser
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
                    userMongo = bd["utilizadores"].find_one({"id":user.id})
                    if not userMongo["active"]:
                        return HttpResponse("User not active")#meter isto bonito
                    tipoUser = userMongo["tipouser"]
                    request.session['tipouser'] = tipoUser
                    login(request,user)
                    return redirect("/")
                else:
                    context = {'form': form}
                    pag = 'login.html'
    else:
        form = loginUserForm(request.POST)
        pag = 'login.html'
        context = {'form': form}
    return render(request, pag, context)

def logoutUser(request):
    try:
        if 'tipouser' in request.session:
            del request.session['tipouser']
        logout(request)
    except KeyError:
        pass
    return redirect('/')

def novo_produto(request):
    context = {}
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        descricao = data.get("descricao")
        imagem = data.get("imagem")
        preco = Decimal128(data.get("preco"))
        desconto = int(data.get("desconto"))
        marca = data.get("marca")
        cor = data.get("cor")
        stock = int(data.get("stock"))
        categoria = data.get("categoria")
        novo_produto_insert(nome, preco, marca, cor, imagem,
                            descricao, stock, desconto, categoria)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'novo_produto.html', context)

def todos_produtos(request):
    if request.method == 'GET':
        products = todos_produtos_other()
        return render(request, "todos_produtos.html", {'products': products})


def todos_users(request):
    context = {}
    if request.method == 'GET':
        pag = 'todos_users.html'
        users = todos_users_other()
        return render(request, pag, {'users': users})


def detalhes_produto(request, produto_id):
    col = bd["produtos"]
    products = col.find_one({"id": produto_id})
    return render(request, 'detalhes_produto.html', {'products': products})

@login_required
def desativar_produto(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
            desativar_produto_other(produto_id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'desativar_produto.html', context)


def todos_pedidos(request):
    if request.method == 'POST':
        data = request.POST
        id_pedido = data.get("id_pedido")
        pedido_update = todos_pedidos_model.objects.get(id_pedido=id_pedido)
        pedido_update.estado = "Encomenda Enviada!"
        pedido_update.save()
        return redirect('todos_pedidos')
    else:
        form = request.POST
        todos = todos_pedidos_model.objects.all().order_by('estado','-id_pedido')
        return render(request, 'todos_pedidos.html', {'todos': todos, 'form': form})
# ainda por acabar e meio que um teste


def novo_pedido(request):
    utilizador = todos_pedidos_model(
        id_pedido=1, id_utilizador=1, preco=50, data='2020-12-12', estado='pendente')
    utilizador.save()

#@login_required
def carrinho(request):
    carrinho = carrinho_compras.objects.get(id_cliente=request.user.id) 
    itens = itens_carrinho_model.objects.filter(id_carrinho=request.user.id).order_by('id_produto') #nao esquecer que o id do carrinho vai ter que ser sempre igual ao do cliente
    return render(request, 'carrinho.html', {'itens': itens, 'carrinho': carrinho})


def adicionar_carrinho(request, produto_id, produto_desconto,produto_nome,produto_preco,produto_imagem):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantidade'))
        if request.user.is_authenticated:
        ##fazer cena normal
        #else:
        ##fazer carrinho anonimo
            verificacao = itens_carrinho_model.objects.filter(id_carrinho=request.user.id, id_produto=produto_id).first()
            if verificacao:
                verificacao.quantidade += quantity
                verificacao.save()
                return redirect('todos_produtos')
            else:
                item = itens_carrinho_model.objects.create(**{
                    'id_carrinho': request.user.id,
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
        return render(request, 'adicionar_carrinho.html', {'form': form})

def remover_produto_carrinho(request, produto_id):
    
    if request.method == 'POST':
        remover_produto_carrinho_other(produto_id,request.user.id)
        return redirect('carrinho')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'carrinho.html', context)

def pagamento(request,id_carrinho):
    context = {}
    if request.method == 'POST':
        inserir_pedido(id_carrinho)
        return redirect('todos_pedidos')
    else:
        form = request.POST
        context = {'form': form}
    return render(request, 'pagamento.html', context=context)

def inserir_pedido(id_carrinho):
    itens_carrinho = itens_carrinho_model.objects.filter(id_carrinho=id_carrinho)
    carrinho = carrinho_compras.objects.get(id_carrinho=id_carrinho)
    pedido = todos_pedidos_model.objects.create(**{
        'id_cliente': id_carrinho, 
        'preco_total': carrinho.preco_total,
        'data': datetime.datetime.now(),
        'estado': 'Em Processamento!'
    })
    pedido.save()
    latest_pedido = todos_pedidos_model.objects.filter(id_cliente=id_carrinho).latest('id_pedido')
    id_pedido_x = latest_pedido.id_pedido 
    for item_carrinho in itens_carrinho:
        itens_pedido = Itens_Pedido.objects.create(
            id_pedido=id_pedido_x,
            id_produto=item_carrinho.id_produto,
            quantidade=item_carrinho.quantidade,
            nome_produto=item_carrinho.nome_produto,
            preco_produto=item_carrinho.preco_produto,
            imagem_produto=item_carrinho.imagem_produto,
            desconto_produto=item_carrinho.desconto_produto
    )
    itens_pedido.save()
    delete_carrinho(id_carrinho)
    return 1

def delete_carrinho(id_carrinho):
    itens_carrinho = itens_carrinho_model.objects.filter(id_carrinho=id_carrinho)
    for item_carrinho in itens_carrinho:
        item_carrinho.delete()
    carrinho = carrinho_compras.objects.get(id_carrinho=id_carrinho)
    carrinho.preco_total = 0
    carrinho.save()
    return 1

#def edit_quantity_cart(request, produto_id,carrinho_id):
#    if request.method == 'POST':
#        itens_carrinho = itens_carrinho_model.objects.get(id_produto=produto_id,id_carrinho=carrinho_id)
#        itens_carrinho.quantidade = request.POST.get("quantidade")
#        itens_carrinho.save()

def acaoutilizador(request, id_user, acao, nome):
    return render(request, 'acao_utilizador.html', {'id_user': id_user, 'acao': acao, 'nome': nome})
    
def utilizador_por_confirmar(request):
    collection = bd['utilizadores']
    users = collection.find({"approved": False})
    return render(request, 'utilizador_por_confirmar.html', {'users': users})

def aceitar_utilizador(request, id_user):
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"approved": True}})
    return redirect('utilizador_por_confirmar')

def rejeitar_utilizador(request, id_user):
    user = User.objects.filter(id=id_user)
    user.delete()
    collection = bd['utilizadores']
    collection.delete_one({"id": id_user})
    return redirect('utilizador_por_confirmar')

def categoria(request, categoria):
    col = bd["produtos"]
    products = col.find({"categoria": categoria})
    print(products)
    return render(request, 'categoria.html', {'products': products, 'categoria': categoria})

def homepage_fornecedores(request):
    if(request.user.is_authenticated):
        class produto:
            def __init__(self, id, nome, preco, imagem, desconto, disponivel):
                self.id = id
                self.nome = nome
                self.preco = preco
                self.imagem = imagem
                self.desconto = desconto
                self.disponivel = disponivel
        collection = bd['produtos_fornecedores']
        collection2 = bd['produtos']
        produtos=[]
        produtos_fornecedor = collection.find({"id_fornecedor": request.user.id})
        for x in produtos_fornecedor:
            varproduto = collection2.find_one({"id": x["id_produto"]})
            varid = varproduto["id"]
            varpreco = x["preco_unitario"]
            vardisponivel = x["disponivel"]
            varimagem = varproduto["imagem"]
            vardesconto = varproduto["desconto"]
            varnome = varproduto["nome"]
            p = produto(varid, varnome, varpreco, varimagem, vardesconto, vardisponivel)
            produtos.append(p)
    return render(request, 'homepage_fornecedores.html', {'produtos': produtos})

def desativar_produto_fornecedor(request, id_produto):
    collection = bd['produtos_fornecedores']
    collection.update_one({"id_produto": id_produto, "id_fornecedor": request.user.id}, {"$set": {"disponivel": False}})
    return redirect('homepage_fornecedores')

def ativar_produto_fornecedor(request, id_produto):
    collection = bd['produtos_fornecedores']
    collection.update_one({"id_produto": id_produto, "id_fornecedor": request.user.id}, {"$set": {"disponivel": True}})
    return redirect('homepage_fornecedores')

@login_required
def editarUsers(request):
    if not getTipoUserMongo(request.user.id) == "Administrador":
        return redirect('mudarEstadoClientes')
    collection = bd['utilizadores']
    users = collection.find({"approved": True})
    return render(request, 'editUsers.html', {'users': users})

@login_required
def editarUser(request, id_user):
    if not getTipoUserMongo(request.user.id) == "Administrador":
        return redirect('mudarEstadoClientes')
    userMongo = bd["utilizadores"].find_one({"id":id_user})
    if request.method == 'POST':
        nome = request.POST["nome"]
        email = request.POST["email"]
        morada = request.POST["morada"]
        tipouser = request.POST["tipouser"]
        active = request.POST["active"]
        user = User.objects.get(id=id_user)
        if user is not None:
            if active == "False":
                active = ""
            updateUserMongo(id_user, nome, email, morada, tipouser, active)
            user.email = email
            user.save()
            return redirect('editarUsers')
    return render(request, 'editUser.html', {'user': userMongo})

@login_required
def mudarEstadoClientes(request):
    if not getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
        return redirect('index')
    collection = bd['utilizadores']
    users = collection.find({"approved": True, "tipouser": "Cliente"})
    return render(request, 'alterarEstadoUser.html', {'users': users})

@login_required
def desativarUser(request, id_user):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    if request.method == 'POST':
        desativarUserMongo(id_user)
        return redirect('editarUsers')
    return render(request,'desativarUser.html' ,{'id_user': id_user})

@login_required
def ativarUser(request, id_user):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('mudarEstadoClientes')
    if request.method == 'POST':
        ativarUserMongo(id_user)
        return redirect('editarUsers')
    return render(request,'ativarUser.html' ,{'id_user': id_user})
    
def pedidos_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id)
    return render(request, 'pedidos_cliente.html', {'todos': todos})

@login_required #para alem destes login required tbm é preciso que haja um if para verificar se o user é admin ou comercial tipo 1
def editar_produto(request, produto_id):
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        descricao = data.get("descricao")
        imagem = data.get("imagem")
        preco = Decimal128(data.get("preco"))
        desconto = int(data.get("desconto"))
        marca = data.get("marca")
        cor = data.get("cor")
        stock = int(data.get("stock"))
        categoria = data.get("categoria")
        # update the document in the mongodb collection
        collection = bd['produtos']
        collection.update_one({"id": produto_id}, {"$set": {"nome": nome, "preco": preco, "marca": marca, "cor": cor, "imagem": imagem, "descricao": descricao, "stock": stock, "desconto": desconto, "categoria": categoria}})
        #atualizar o produto nos carrinhos
        preco_pg = Decimal(data.get("preco"))
        itens_carrinho = itens_carrinho_model.objects.filter(id_produto=produto_id)
        for item in itens_carrinho:
            item.preco_produto = preco_pg
            item.save()
        return redirect('todos_produtos')
    else:
        collection = bd['produtos']
        produto = collection.find_one({"id": produto_id})
        return render(request, 'editar_produto.html', {'produto': produto})

def increment_quantity(request, id_carrinho, id_produto):
    item = get_object_or_404(itens_carrinho_model, id_carrinho=id_carrinho, id_produto=id_produto)
    item.quantidade += 1
    item.save()
    carrinho = carrinho_compras.objects.get(id_cliente=request.user.id)
    return JsonResponse({'quantity': item.quantidade,'total': carrinho.preco_total})

def decrement_quantity(request, id_carrinho, id_produto):
    item = get_object_or_404(itens_carrinho_model, id_carrinho=id_carrinho, id_produto=id_produto)
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    carrinho = carrinho_compras.objects.get(id_cliente=request.user.id)
    return JsonResponse({'quantity': item.quantidade,'total': carrinho.preco_total})

# def editar_preco_carrinho(request, id_produto):
#     item = get_object_or_404(itens_carrinho_model, id_produto=id_produto)
#     if request.method == 'POST':
#         data = request.POST
#         preco = Decimal128(data.get("preco"))
#         item.preco_produto = preco
#         item.save()
#         return 1

def homepage_comerciantetipo1(request):
    #if request.method == 'GET':
        products = todos_produtos_other()
        return render(request, "homepage_comerciantestipo1.html", {'products': products})

def solicitar_produto(request, id_product):
    context = {}
    if request.method == 'POST':
        data = request.POST
        quantidade = data.get("quantidade")
        id_fornecedor =  data.get("id_fornecedor")
        id_produto = data.get("id_produto")
        encomenda = PedidoFornecedor.objects.create(**{
        'id_fornecedor': id_fornecedor,
        'id_produto': id_produto,
        'quantidade': quantidade,
        'datapedido': datetime.datetime.now(),
        'estado': "Por verificar"
        })
        return redirect('homepage_comerciantetipo1')
    else:
        form = request.POST
        fornecedores = todos_fornecedores_produto_other(id_product)
        return render(request, "lista_fornecedores_produto.html", {'fornecedores': fornecedores,'form': form})

def encomendas_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id, estado__in=["Encomenda Enviada!", "Encomenda Cancelada!"]).order_by('-data')
    return render(request, 'encomendas_cliente.html', {'todos': todos})

def encomenda(request,id_encomenda):
    todos = todos_pedidos_model.objects.get(id_pedido=id_encomenda, estado="Encomenda Enviada!")
    encomenda = Itens_Pedido.objects.filter(id_pedido=id_encomenda)
    return render(request, 'encomenda.html', {'encomenda': encomenda,'todos': todos})

def pedidos_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id, estado="Em Processamento!").order_by('-data')
    return render(request, 'pedidos_cliente.html', {'todos': todos})

def encomenda_cancelar(request, id_encomenda): #falta atualizar o stock depois de cancelar
    todos = todos_pedidos_model.objects.get(id_pedido=id_encomenda, estado="Em Processamento!")
    todos.estado = "Encomenda Cancelada!"
    todos.save()
    return redirect('pedidos_cliente')

@login_required
def ativar_produto(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
            ativar_produto_other(produto_id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'ativar_produto.html', context)