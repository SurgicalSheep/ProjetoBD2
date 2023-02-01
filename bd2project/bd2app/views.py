import datetime
from decimal import Decimal
import json
from pprint import pprint
from bson import Decimal128
from bson.objectid import ObjectId
from django.shortcuts import redirect, render, get_object_or_404
from bd2app.forms import *
from bd2app.models import *
from bd2app.other import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.http import JsonResponse
from bson.objectid import ObjectId
from .templatetags.math_extras import mul
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
from django.contrib import messages #import messages
import xml.etree.ElementTree as ET
from django.core import serializers
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        if request.session: 
            if request.session["tipouser"] == "Fornecedor":
                return redirect('homepage_fornecedores')
            elif request.session["tipouser"] == "Parceiro":
                return redirect('produtos_parceiro')
            elif request.session["tipouser"] == "Comercial Tipo 1" or request.session["tipouser"] == "Administrador":
                return redirect('todos_produtos')
    col = bd["produtos"]
    produtos_promocao = col.find({'active': True, 'desconto': {'$gt': 0}}).sort("desconto", -1).limit(6) #maybe mudar isto para nao serem só 6?
    produtos_nao_ativos = col.find({'active': False})
    inactive_product_ids = [int(str(product['id'])) for product in produtos_nao_ativos]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM top6_itens_mais_vendidos(%s)", (inactive_product_ids,)) #e aqui tb
    top6 = cursor.fetchall()
    product_ids = [item[0] for item in top6]
    produtos_mais_vendidos = col.find({'id': {'$in': product_ids}})
    categorias = col.distinct("categoria")
    col2 = bd["produtos_visitados"]
    # Find all unique product IDs visited by the current user
    product_ids = col2.find({"id_user": request.user.id}).sort([("quantidade", -1)])
    # Create a new list containing the id_produto field
    sorted_product_ids = [product["id_produto"] for product in product_ids]
    # Find all products corresponding to the product IDs
    recomendacoes = []
    counter = 0
    for product_id in sorted_product_ids:
        product = col.find_one({"id": product_id, "active": True})
        if product:
            recomendacoes.append(product)
            counter += 1
        if counter >= 6:
            break
    produtos_marketplace = col.find({'active': True, 'belongs_store': False}).sort("desconto", -1).limit(6)
    return render(request, 'index.html', {'produtos_promocao':produtos_promocao, 'produtos_mais_vendidos':produtos_mais_vendidos, 'categorias':categorias, 'recomendacoes':recomendacoes, 'produtos_marketplace':produtos_marketplace})

def error404(request,exception=None):
    return render(request, '404.html')

@login_required
def verPerfil(request):
    userMongo = bd["utilizadores"].find_one({"id":request.user.id})
    return render(request, 'showPerfil.html', {'user': userMongo})

@login_required
def editarPerfil(request):
    userMongo = bd["utilizadores"].find_one({"id":request.user.id})
    if request.method == 'POST':
        nome = request.POST["nome"]
        email = request.POST["email"]
        morada = request.POST["morada"]
        user = User.objects.get(id=request.user.id)
        if user is not None:
            updatePerfil(request.user.id, nome, email, morada)
            user.email = email
            user.save()
            return redirect('verPerfil')
    return render(request, 'editPerfil.html', {'user': userMongo})

@login_required
def mudarPass(request):
    if request.method == 'POST':
        oldPass = request.POST["oldPass"]
        newPass = request.POST["newPass"]
        confNewPass = request.POST["confNewPass"]
        user = User.objects.get(id=request.user.id)
        if user is not None:
            if user.check_password(oldPass):
                if newPass == confNewPass:
                    user.set_password(newPass)
                    user.save()
                    return redirect('logoutUser')
                else:
                    return HttpResponse("Passwords don't match")#meter bonito
            return HttpResponse("A password está mal!")#meter bonito
    return render(request, 'changePassword.html')

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
            insere_ut(u.id, nome, tipouser, morada, username, email)
            request.session['tipouser'] = tipouser
            request.session['nome'] = nome
            print(request.user.id)
            logout(request)
        return redirect('loginUser')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'registro.html', context)

def registroAdmin(request):
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
            insere_ut(u.id, nome, tipouser, morada, username, email)
        return redirect('index')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'registro.html', context)


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('index')
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
                    if not userMongo["approved"]:
                        return HttpResponse("User not approved")#meter isto bonito
                    tipoUser = userMongo["tipouser"]
                    nome = userMongo["nome"]
                    request.session['tipouser'] = tipoUser
                    request.session['nome'] = nome
                    if 'carrinhoAnonimo' in request.session:
                        carrinhoAnonimo = request.session['carrinhoAnonimo']
                        if tipoUser == "Cliente":
                            if len(carrinhoAnonimo) > 0:
                                x = "'["
                                l = len(carrinhoAnonimo)
                                y=0
                                for item in carrinhoAnonimo:
                                    y+=1
                                    x+="{"
                                    x+="\"id\":"+str(item["id"])+","
                                    x+="\"quantidade\":"+str(item["quantidade"])+","
                                    x+="\"preco\":"+str(item["preco"])+","
                                    x+="\"stock\":"+str(item["stock"])
                                    x+="}"
                                    if y < l:
                                        x+=","
                                x+="]'"
                                cursor = connection.cursor()
                                cursor.execute("call carrinho_anonimo("+x+","+str(user.id)+")")
                        if 'carrinhoAnonimo' in request.session:
                            del request.session['carrinhoAnonimo']
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
   
@login_required
def logoutUser(request):
    try:
        if 'tipouser' in request.session:
            del request.session['tipouser']
        logout(request)
    except KeyError:
        pass
    return redirect('/')

@login_required
def novo_produto(request):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1" or getTipoUserMongo(request.user.id) == "Parceiro"):
        return redirect("index")
    context = {}
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        descricao = data.get("descricao")
        imagem = data.get("imagem")
        preco = float(data.get("preco"))
        desconto = int(data.get("desconto"))
        marca = data.get("marca")
        cor = data.get("cor")
        stock = int(data.get("stock"))
        categoria = data.get("categoria")
        novo_produto_insert(nome, preco, marca, cor, imagem,
                            descricao, stock, desconto, categoria, request.user.id)
        if getTipoUserMongo(request.user.id) == "Parceiro":
            return redirect('index')
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'novo_produto.html', context)

def todos_produtos(request):
    if request.user.is_authenticated:
        if getTipoUserMongo(request.user.id) == "Parceiro" or getTipoUserMongo(request.user.id) == "Fornecedor" or getTipoUserMongo(request.user.id) == "Comercial Tipo 2":
            return redirect('index')
    if request.method == 'GET':
        if 'pesquisa' in request.GET:
            search = request.GET['pesquisa']
            products = todos_produtos_other_search(search)
            return render(request, "todos_produtos.html", {'products': products})
        products = todos_produtos_other()
        return render(request, "todos_produtos.html", {'products': products})

def todos_produtos_marketplace(request):
    if request.user.is_authenticated:
        if getTipoUserMongo(request.user.id) == "Parceiro" or getTipoUserMongo(request.user.id) == "Fornecedor" or getTipoUserMongo(request.user.id) == "Comercial Tipo 2":
            return redirect('index')
    if request.method == 'GET':
        if 'pesquisa' in request.GET:
            search = request.GET['pesquisa']
            products = todos_produtos_other_marketplace_search(search)
            return render(request, "todos_produtos_marketplace.html", {'products': products})
        products = todos_produtos_other_marketplace()
        return render(request, "todos_produtos_marketplace.html", {'products': products})

@login_required
def todos_users(request):
    context = {}
    if request.method == 'GET':
        pag = 'todos_users.html'
        users = todos_users_other()
        return render(request, pag, {'users': users})

def detalhes_produto(request, produto_id):
    col = bd["produtos"]
    products = col.find_one({"id": produto_id})
    if request.user.is_authenticated:
        col2 = bd["produtos_visitados"]
        # Check if the product has already been visited by the user
        existing_visit = col2.find_one({"id_produto": produto_id, "id_user": request.user.id})

        if existing_visit:
        # If the product has already been visited, increment the quantity field by 1
            col2.update_one({"id_produto": produto_id, "id_user": request.user.id}, {"$inc": {"quantidade": 1}})
        else:
            # If the product has not been visited, insert a new document with quantity set to 1
            col2.insert_one({"id_produto": produto_id, "id_user": request.user.id, "quantidade": 1})

    return render(request, 'detalhes_produto.html', {'products': products})

@login_required
def desativar_produto(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
            desativar_produto_other(produto_id, request.user.id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'desativar_produto.html', context)

@login_required
def todos_pedidos(request):
    if getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
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
    else:
        return redirect('pedidos_cliente')
# ainda por acabar e meio que um teste


# def novo_pedido(request):
#     utilizador = todos_pedidos_model(
#         id_pedido=1, id_utilizador=1, preco=50, data='2020-12-12', estado='pendente')
#     utilizador.save()

#@login_required
def carrinho(request):
    if request.user.is_authenticated:
        carrinho = carrinho_compras.objects.get(id_cliente=request.user.id) 
        itens_pg = itens_carrinho_model.objects.filter(id_carrinho=request.user.id).order_by('id_produto')
        col = bd["produtos"]
        product_ids = [item.id_produto for item in itens_pg]
        itens2 = col.find({'id': {'$in': product_ids}}) 
        return render(request, 'carrinho.html', {'itens2': itens2,'itens_pg':itens_pg, 'carrinho': carrinho})
    else:
        if not 'carrinhoAnonimo' in request.session:
            request.session['carrinhoAnonimo'] = []
        carrinhoAnonimo = request.session['carrinhoAnonimo']
        precoTotal = 0
        for x in carrinhoAnonimo:
            precoTotal += x['preco'] * (100 - x['desconto']) / 100 * x['quantidade'] #mudei isto
        precoTotal = round(precoTotal, 2)
        return render(request,'carrinhoAnonimoV2.html',{'carrinho':carrinhoAnonimo,'precoTotal':precoTotal})

def adicionar_carrinho(request, produto_id):
    col = bd["produtos"]
    stock = col.find_one({"id": produto_id})["stock"]
    produto_preco = col.find_one({"id": produto_id})["preco"]
    produto_desconto = col.find_one({"id": produto_id})["desconto"]
    produto_preco_com_desconto = produto_preco * (100 - produto_desconto) / 100
    if request.method == 'POST':
        quantity = int(request.POST.get('quantidade'))
        #no form ja meti verificacao mas convem ter verificacao no backend tbm entao
        #se o utilizador conseguir pedir mais do que o stock (alterando o html)
        if stock < quantity:
            return redirect('out_of_stock')
        if request.user.is_authenticated:
            ##fazer cena normal
            verificacao = itens_carrinho_model.objects.filter(id_carrinho=request.user.id, id_produto=produto_id).first()
            if verificacao:
                verificacao.quantidade += quantity
                verificacao.save()
                return redirect('todos_produtos')
            else:
                cursor = connection.cursor()
                cursor.execute("call insert_itens_carrinho(" + str(request.user.id) + "," + str(produto_id) + "," + str(quantity) + "," + str(produto_preco_com_desconto) + ")")
                return redirect('todos_produtos')
        else:
            #carrinho anonimo
            if 'carrinhoAnonimo' not in request.session:
                request.session['carrinhoAnonimo'] = []
            carrinhoAnonimo = request.session['carrinhoAnonimo']
            produtoExists = False
            col = bd['produtos']
            for item in carrinhoAnonimo:
                if item['id'] == produto_id:
                    item["quantidade"] += quantity
                    produtoExists = True
                    break
            if not produtoExists:
                produto = col.find_one({"id": produto_id})
                del produto["_id"]
                produto["quantidade"] = quantity
                carrinhoAnonimo.append(produto)
            request.session.modified = True
            return redirect('index')
    else:
        form = request.POST
        return render(request, 'adicionar_carrinho.html', {'form': form, 'stock': stock})

#@login_required acho q precisa
def remover_produto_carrinho(request, produto_id):
    
    if request.method == 'POST':
        remover_produto_carrinho_other(produto_id,request.user.id)
        return redirect('carrinho')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'carrinho.html', context)

def removerProdutoCarrinhoAnonimo(request, produto_id):
    carrinhoAnonimo = request.session['carrinhoAnonimo']
    if request.method == 'POST':
        for x in carrinhoAnonimo:
            if x['id'] == produto_id:
                request.session['carrinhoAnonimo'].remove(x)
                request.session.modified = True
                break
        return redirect('carrinho')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'carrinhoAnonimo.html', context)

@login_required
def pagamento(request,id_carrinho):
    context = {}
    if request.method == 'POST':
        morada = request.POST.get('address')
        inserir_pedido(id_carrinho,morada)
        return redirect('pedidos_cliente')
    else:
        form = request.POST
        context = {'form': form}
    return render(request, 'pagamento.html', context=context)

def inserir_pedido(id_carrinho,morada):
    itens_carrinho = itens_carrinho_model.objects.filter(id_carrinho=id_carrinho)
    carrinho = carrinho_compras.objects.get(id_carrinho=id_carrinho)
    cursor = connection.cursor()
    data = "'" + str(datetime.datetime.now()) + "'"
    cursor.execute("call insert_pedidos(" + str(id_carrinho) + "," + str(carrinho.preco_total) + "," + data +  ",'" + str(morada) + "')")
    latest_pedido = todos_pedidos_model.objects.filter(id_cliente=id_carrinho).latest('id_pedido')
    id_pedido_x = latest_pedido.id_pedido 
    for item_carrinho in itens_carrinho:
        cursor.execute("call insert_itens_pedidos(" + str(id_pedido_x) + "," + str(item_carrinho.id_produto) + "," + str(item_carrinho.quantidade) + "," + str(item_carrinho.preco_produto) + ")")
        # Update stock in MongoDB collection
        col = bd["produtos"]
        col.update_one({"id": item_carrinho.id_produto}, {"$inc": {"stock": -item_carrinho.quantidade}})   
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

@login_required
def acaoutilizador(request, id_user, acao, nome):
    return render(request, 'acao_utilizador.html', {'id_user': id_user, 'acao': acao, 'nome': nome})

@login_required  
def utilizador_por_confirmar(request):
    collection = bd['utilizadores']
    users = list(collection.find({"approved": False}))
    return render(request, 'utilizador_por_confirmar.html', {'users': users})

@login_required
def aceitar_utilizador(request, id_user):
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"approved": True, "id_utilizador": request.user.id}})
    return redirect('utilizador_por_confirmar')

@login_required
def rejeitar_utilizador(request, id_user):
    user = User.objects.filter(id=id_user)
    user.delete()
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"id_utilizador": request.user.id}})
    collection.delete_one({"id": id_user})
    return redirect('utilizador_por_confirmar')

def categoria(request, categoria):
    col = bd["produtos"]
    products = col.find({"categoria": categoria})
    #print(products)
    return render(request, 'categoria.html', {'products': products, 'categoria': categoria})

@login_required
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

@login_required
def desativar_produto_fornecedor(request, id_produto, id_fornecedor):
    if not(getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1" or getTipoUserMongo(request.user.id) == "Fornecedor"):
        redirect('index')
    collection = bd['produtos_fornecedores']
    collection.update_one({"id_produto": id_produto, "id_fornecedor": id_fornecedor}, {"$set": {"disponivel": False, "id_utilizador": request.user.id}})
    if getTipoUserMongo(request.user.id) == "Fornecedor":
        return redirect('homepage_fornecedores')
    return redirect('/gerir_produtos_fornecedor/'+str(id_fornecedor))

@login_required
def ativar_produto_fornecedor(request, id_produto, id_fornecedor):
    if not(getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1" or getTipoUserMongo(request.user.id) == "Fornecedor"):
        redirect('index')
    collection = bd['produtos_fornecedores']
    collection.update_one({"id_produto": id_produto, "id_fornecedor": id_fornecedor}, {"$set": {"disponivel": True, "id_utilizador": request.user.id}})
    if getTipoUserMongo(request.user.id) == "Fornecedor":
        return redirect('homepage_fornecedores')
    return redirect('/gerir_produtos_fornecedor/'+str(id_fornecedor))

# @login_required
# def editarUsers(request):
#     if not getTipoUserMongo(request.user.id) == "Administrador":
#         return redirect('mudarEstadoClientes')
#     collection = bd['utilizadores']
#     users = collection.find({"approved": True})
#     return render(request, 'editUsers.html', {'users': users})

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
            updateUserMongo(id_user, nome, email, morada, tipouser, active, request.user.id)
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
    tipo_user = getTipoUserMongo(id_user)
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    if request.method == 'POST':
        desativarUserMongo(id_user, request.user.id)
        if tipo_user == "Cliente":
            return redirect('gerir_clientes')
        elif tipo_user == 'Fornecedor':
            return redirect('gerir_fornecedores')
        elif tipo_user == 'Comercial Tipo 1' or tipo_user == 'Comercial Tipo 2':
            return redirect('gerir_comerciais')
        elif tipo_user == 'Parceiro':
            return redirect('gerir_parceiros')
    return render(request,'desativarUser.html' ,{'id_user': id_user, "tipo_user": tipo_user})

@login_required
def ativarUser(request, id_user):
    tipo_user = getTipoUserMongo(id_user)
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('mudarEstadoClientes')
    if request.method == 'POST':
        ativarUserMongo(id_user, request.user.id)
        if tipo_user == "Cliente":
            return redirect('gerir_clientes')
        elif tipo_user == 'Fornecedor':
            return redirect('gerir_fornecedores')
        elif tipo_user == 'Comercial Tipo 1' or tipo_user == 'Comercial Tipo 2':
            return redirect('gerir_comerciais')
        elif tipo_user == 'Parceiro':
            return redirect('gerir_parceiros')
    return render(request,'ativarUser.html' ,{'id_user': id_user, "tipo_user": tipo_user})
    
def pedidos_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id)
    return render(request, 'pedidos_cliente.html', {'todos': todos})

@login_required #para alem destes login required tbm é preciso que haja um if para verificar se o user é admin ou comercial tipo 1
def editar_produto(request, produto_id):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1" or getTipoUserMongo(request.user.id) == "Parceiro"):
        return redirect('index')
    if (getTipoUserMongo(request.user.id) == "Parceiro"):
        list_ids_produtos_parceiro = ids_produtos_parceiro_other(request.user.id)
        if produto_id not in list_ids_produtos_parceiro:
            return redirect('index')
        active = get_active_produto_other(produto_id)
        if not active["active"]:
            return redirect('index') 
    if request.method == 'POST':
        data = request.POST
        nome = data.get("nome")
        descricao = data.get("descricao")
        imagem = data.get("imagem")
        preco = float(data.get("preco"))
        desconto = int(data.get("desconto"))
        marca = data.get("marca")
        cor = data.get("cor")
        stock = int(data.get("stock"))
        categoria = data.get("categoria")
        # update the document in the mongodb collection
        collection = bd['produtos']
        collection.update_one({"id": produto_id}, {"$set": {"nome": nome, "preco": preco, "marca": marca, "cor": cor, "imagem": imagem, "descricao": descricao, "stock": stock, "desconto": desconto, "categoria": categoria, "id_utilizador": request.user.id}})
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

#@login_required
def increment_quantity(request, id_carrinho, id_produto):
    col = bd['produtos']
    stock = col.find_one({"id": id_produto})["stock"]
    item = get_object_or_404(itens_carrinho_model, id_carrinho=id_carrinho, id_produto=id_produto)
    carrinho = carrinho_compras.objects.get(id_cliente=request.user.id)
    if item.quantidade < stock:
        item.quantidade += 1
        item.save()
        carrinho = carrinho_compras.objects.get(id_cliente=request.user.id) 
    else:
        messages.warning(request, 'Stock máximo atingido!') #not working
    return JsonResponse({'quantity': item.quantidade,'total': carrinho.preco_total})

#@login_required
def decrement_quantity(request, id_carrinho, id_produto):
    item = get_object_or_404(itens_carrinho_model, id_carrinho=id_carrinho, id_produto=id_produto)
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    carrinho = carrinho_compras.objects.get(id_cliente=request.user.id)
    return JsonResponse({'quantity': item.quantidade,'total': carrinho.preco_total})

def incrementQuantityAnonimo(request, id_produto):
    carrinhoAnonimo = request.session['carrinhoAnonimo']
    col = bd['produtos']
    produto = col.find_one({"id": id_produto})
    item = {}
    for x in carrinhoAnonimo:
        if x['id'] == id_produto:
            if x['quantidade'] < produto["stock"]:
                x['quantidade'] += 1
                item["quantidade"] = x["quantidade"]
                item["preco_com_desconto"] = x["preco"] * (100 - x["desconto"]) / 100 #mudei aqui
                request.session.modified = True
            else:
                 messages.warning(request, 'Stock máximo atingido!') #not working
    return JsonResponse({'quantity': item["quantidade"], 'total': round(item["preco_com_desconto"]*item['quantidade'], 2)})


def decrementQuantityAnonimo(request, id_produto):
    carrinhoAnonimo = request.session['carrinhoAnonimo']
    col = bd['produtos']
    produto = col.find_one({"id": id_produto})
    item = {}
    for x in carrinhoAnonimo:
        if x['id'] == id_produto:
            if x['quantidade'] > 1:
                x['quantidade'] -= 1
                item["quantidade"] = x["quantidade"]
                item["preco_com_desconto"] = x["preco"] * ((100 - x["desconto"]) / 100) #mudei aqui
                request.session.modified = True
    return JsonResponse({'quantity': item["quantidade"],'total': round(item["preco_com_desconto"]*item['quantidade'], 2)})

# def editar_preco_carrinho(request, id_produto):
#     item = get_object_or_404(itens_carrinho_model, id_produto=id_produto)
#     if request.method == 'POST':
#         data = request.POST
#         preco = Decimal128(data.get("preco"))
#         item.preco_produto = preco
#         item.save()
#         return 1

@login_required
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
        return redirect('todos_produtos')
    else:
        form = request.POST
        fornecedores = todos_fornecedores_produto_other(id_product)
        return render(request, "lista_fornecedores_produto.html", {'fornecedores': fornecedores,'form': form})

@login_required
def encomendas_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id, estado__in=["Encomenda Enviada!", "Encomenda Cancelada!"]).order_by('-data')
    return render(request, 'encomendas_cliente.html', {'todos': todos})

@login_required
def encomenda(request,id_encomenda): #falta checkar esta
    todos = todos_pedidos_model.objects.get(id_pedido=id_encomenda)
    encomenda = Itens_Pedido.objects.filter(id_pedido=id_encomenda)
    col = bd["produtos"]
    product_ids = [item.id_produto for item in encomenda]
    itens2 = col.find({'id': {'$in': product_ids}}) 
    return render(request, 'encomenda.html', {'encomenda': encomenda,'todos': todos,'itens2': itens2})

@login_required
def pedidos_cliente(request):
    todos = todos_pedidos_model.objects.filter(id_cliente=request.user.id, estado="Em Processamento!").order_by('-data')
    return render(request, 'pedidos_cliente.html', {'todos': todos})

@login_required
def encomenda_cancelar(request, id_encomenda): #falta atualizar o stock depois de cancelar
    todos = todos_pedidos_model.objects.get(id_pedido=id_encomenda, estado="Em Processamento!")
    todos.estado = "Encomenda Cancelada!"
    todos.save()
    itens_pedido = Itens_Pedido.objects.filter(id_pedido=id_encomenda)
    for item_pedido in itens_pedido:
        # Update stock in MongoDB collection
        collection = bd['produtos']
        collection.update_one({"id": item_pedido.id_produto}, {"$inc": {"stock": item_pedido.quantidade}})
    return redirect('pedidos_cliente')

@login_required
def ativar_produto(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1":
            ativar_produto_other(produto_id, request.user.id)
        return redirect('todos_produtos')
    else:
        form = request.POST
        context = {'form': form}
        return render(request, 'ativar_produto.html', context)

@login_required
def pedidos_fornecedor(request):
    collection2 = bd['produtos']
    class class_pedidos_fornecedor:
            def __init__(self, id_pedidofornecedor, id_fornecedor, id_produto, nome_produto, quantidade, datapedido):
                self.id_pedidofornecedor = id_pedidofornecedor
                self.id_fornecedor = id_fornecedor
                self.id_produto = id_produto
                self.nome_produto = nome_produto
                self.quantidade = quantidade
                self.datapedido = datapedido
    aux_pedidos_fornecedor = PedidoFornecedor.objects.filter(id_fornecedor=request.user.id, estado="Por verificar").values()
    pedidos_fornecedor = []
    for x in aux_pedidos_fornecedor:
            varproduto = collection2.find_one({"id": x["id_produto"]})
            varid_pedidofornecedor = x["id_pedidofornecedor"]
            varid_produto = x["id_produto"]
            varid_fornecedor = x["id_fornecedor"]
            varnome_produto = varproduto["nome"]
            varquantidade = x["quantidade"]
            vardatapedido = x["datapedido"]
            p = class_pedidos_fornecedor(varid_pedidofornecedor, varid_fornecedor, varid_produto, varnome_produto, varquantidade, vardatapedido)
            pedidos_fornecedor.append(p)
    return render(request, 'pedidos_fornecedor.html', {'pedidos_fornecedor': pedidos_fornecedor})

@login_required
def aceitar_pedidos_fornecedor(request, id_pedidofornecedor, id_produto, quantidade):
    collection = bd['produtos']
    item = get_object_or_404(PedidoFornecedor, id_pedidofornecedor = id_pedidofornecedor)
    item.estado = "Aceite!"
    item.dataentrega = datetime.datetime.now()
    item.save()
    collection.update_one({"id": id_produto}, {"$inc": {"stock": quantidade}})
    return redirect('pedidos_fornecedor')

@login_required
def rejeitar_pedidos_fornecedor(request, id_pedidofornecedor):
    item = get_object_or_404(PedidoFornecedor, id_pedidofornecedor = id_pedidofornecedor)
    item.delete()
    return redirect('pedidos_fornecedor')

def out_of_stock(request):
    return render(request, 'out_of_stock.html')

def number_sells_per_day():
    cursor = connection.cursor()
    cursor.execute("select * from n_sells_per_day()")
    results = cursor.fetchall()
    #for x in results:
        #print(x[0])
        #print(x[1])
    return 0

def number_users():
    collection = bd['utilizadores']
    n_users = collection.count_documents({'active': True, 'approved': True})
    print(n_users)
    return 0

@login_required
def gerir_clientes (request):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    collection = bd['vw_clientes']
    users = collection.find()
    return render(request, 'gerir_utilizadores.html', {'users': users, 'tipo_user': "Cliente"})

@login_required
def gerir_fornecedores (request):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    collection = bd['vw_fornecedores']
    users = collection.find()
    return render(request, 'gerir_utilizadores.html', {'users': users, 'tipo_user': "Fornecedor"})

@login_required
def gerir_comerciais (request):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    collection = bd['vw_comerciais']
    users = collection.find()
    return render(request, 'gerir_utilizadores.html', {'users': users, 'tipo_user': "Comercial"})

@login_required
def gerir_parceiros (request):
    if not (getTipoUserMongo(request.user.id) == "Administrador" or getTipoUserMongo(request.user.id) == "Comercial Tipo 1"):
        return redirect('index')
    collection = bd['vw_parceiros']
    users = collection.find()
    return render(request, 'gerir_utilizadores.html', {'users': users, 'tipo_user': "Parceiro"})

@login_required
def gerir_produtos_fornecedor (request, id_user):
    if not (getTipoUserMongo(request.user.id) == "Comercial Tipo 1" or getTipoUserMongo(request.user.id) == "Administrador"):
        return redirect('index')
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
    collection3 = bd['utilizadores']
    fornecedor = collection3.find_one({"id": id_user}, {"_id": 0, "id": 1, "nome": 1})
    produtos=[]
    produtos_fornecedor = collection.find({"id_fornecedor": id_user})
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
    
    return render(request, 'gerir_produtos_fornecedor.html', {'produtos': produtos, 'fornecedor': fornecedor})

@login_required
def add_produtos_fornecedor(request, id_fornecedor):
    context = {}
    if request.method == 'POST':
        collection = bd['produtos_fornecedores']
        data = request.POST
        id_produto = int(data.get("id_produto"))
        preco_unitario =  float(data.get("preco_unitario"))
        collection.insert_one({"id_fornecedor": id_fornecedor,"id_produto": id_produto,"preco_unitario":preco_unitario,"disponivel": True, "id_utilizador": request.user.id})
        return redirect('/gerir_produtos_fornecedor/'+str(id_fornecedor))
    else:
        form = request.POST
        produtos = todos_produtos_fornecedor_n_fornece_other(id_fornecedor)
        return render(request, "novo_produto_fornecedor.html", {'id_fornecedor': id_fornecedor,'form': form, 'produtos': produtos})

def info_sells_year_month(ano, mes):
    cursor = connection.cursor()
    cursor.execute("select * from info_sells_year_month(" + str(ano) + "," + str(mes) + ")")
    results = cursor.fetchall()
    return results

def return_ano():
    cursor = connection.cursor()
    cursor.execute("select * from view_anos_pedidos")
    results = cursor.fetchall()
    anos = [int(item[0]) for item in results]
    return anos

def return_mes():
    cursor = connection.cursor()
    cursor.execute("select * from view_meses_pedidos")
    results = cursor.fetchall()
    meses = [int(item[0]) for item in results]
    return meses

def get_info_sells():
    cursor = connection.cursor()
    cursor.execute("select * from info_sells();")
    results = cursor.fetchall()
    return results[0]

@login_required
def estatisticas(request, acao):
    context = {}
    info = []
    dias = []
    ano = -1
    mes = -1
    anos = return_ano()
    meses = return_mes()
    info_sells = get_info_sells()
    valorvendas = (info_sells[0])
    nvendas = (info_sells[1])
    context = {}
    if request.method == 'POST':
        data = request.POST
        ano = int(data.get("ano"))
        mes =  int(data.get("mes"))
        array_diasmes = [31,28,31,30,31,30,31,31,30,31,30,31]
        if ano % 4 == 0: 
            array_diasmes = [31,29,31,30,31,30,31,31,30,31,30,31]
        for x in range(0, array_diasmes[mes-1]):
            info.append(0)
            dias.append(x)
        # Create data for the bar graph
        results = info_sells_year_month(ano, mes)
        for x in results:
            info[x[0]] = x[acao]
        # Create the bar graph
        if acao == 1:
            df = pd.DataFrame({
            "dia": dias,
            "valor_vendas": info,
            })
            fig = px.bar(df, x="dia", y="valor_vendas", barmode="group")
            fig.update_layout(xaxis=dict(range=[0, array_diasmes[mes-1]], tick0=1, dtick=1, tickvals=list(range(1, array_diasmes[mes-1]+1))), xaxis_title='dia',yaxis_title='valor_vendas', xaxis_fixedrange=True, yaxis_fixedrange=True)
        if acao == 2:
            df = pd.DataFrame({
            "dia": dias,
            "n_vendas": info,
            })
            fig = px.bar(df, x="dia", y="n_vendas", barmode="group")
            fig.update_layout(xaxis=dict(range=[0, array_diasmes[mes-1]], tick0=1, dtick=1, tickvals=list(range(1, array_diasmes[mes-1]+1))), yaxis=dict(dtick=1), xaxis_title='dia', yaxis_title='n_vendas', xaxis_fixedrange=True, yaxis_fixedrange=True) 
        # Convert the figure to a JSON string
        fig_json = fig.to_json()
        # Pass the JSON string to the template
        return render(request, "estatisticas.html", {"fig_json": fig_json, "ano": anos, "mes": meses, "anoselected": ano, "messelected": mes, "valorvendas": valorvendas, "nvendas": nvendas})
    else:
        form = request.POST
        return render(request, "estatisticas.html", {'form': form, "ano": anos, "mes": meses, "anoselected": ano, "messelected": mes, "valorvendas": valorvendas, "nvendas": nvendas})

def criarProdutosPorFicheiro(request):
    if(request.session["tipouser"] != "Administrador" and request.session["tipouser"] != "Comercial Tipo 1" and request.session["tipouser"] != "Parceiro"):
        return redirect('index')
    if request.method == 'POST':
        if 'inserirMultiple' in request.POST:
            form = uploadFile(request.POST, request.FILES)
            file = request.FILES['file']
            if not (str(file).endswith(".xml") or str(file).endswith(".json")):
                return HttpResponse("Ficheiro não é XML ou JSON")#meter bonito
            if str(file).endswith(".xml"):
                tree = ET.parse(file)
                root = tree.getroot()
                #verificar se o ficheiro está bem formatado
                for child in root:
                    for value in child:
                        if not (value.tag == "nome" or value.tag == "preco" or value.tag == "marca" or value.tag == "cor" or value.tag == "imagem" or value.tag == "descricao" or value.tag == "stock" or value.tag == "desconto" or value.tag == "categoria"):
                            return HttpResponse("Ficheiro XML mal formatado")
                #inserir na bd
                for child in root:
                    dados = {}
                    for value in child:
                        if value.tag == "preco":
                            try:
                                dados[value.tag] = float(value.text)
                            except:
                                return HttpResponse("Ficheiro XML mal formatado")
                        elif value.tag == "stock" or value.tag == "desconto":
                            try:
                                dados[value.tag] = int(value.text)
                            except:
                                return HttpResponse("Ficheiro XML mal formatado")
                        else:
                            dados[value.tag] = value.text
                    #inserir na bd
                    novo_produto_insert(dados["nome"], dados["preco"], dados["marca"], dados["cor"], dados["imagem"], dados["descricao"], dados["stock"], dados["desconto"], dados["categoria"],request.user.id)
            if str(file).endswith(".json"):
                dadosFicheiro = json.load(file)
                #verificar se o ficheiro está bem formatado
                for produto in dadosFicheiro:
                    if not (produto["nome"] and produto["preco"] and produto["marca"] and produto["cor"] and produto["imagem"] and produto["descricao"] and produto["stock"] and produto["desconto"] and produto["categoria"]):
                        return HttpResponse("Ficheiro JSON mal formatado")
                #inserir na bd
                for produto in dadosFicheiro:
                    #inserir na bd
                    novo_produto_insert(produto["nome"], produto["preco"], produto["marca"], produto["cor"], produto["imagem"], produto["descricao"], produto["stock"], produto["desconto"], produto["categoria"],request.user.id)
            return redirect("index") 
        if 'inserirSingle' in request.POST:
            data = request.POST
            nome = data.get("nome")
            descricao = data.get("descricao")
            imagem = data.get("imagem")
            preco = float(data.get("preco"))
            desconto = int(data.get("desconto"))
            marca = data.get("marca")
            cor = data.get("cor")
            stock = int(data.get("stock"))
            categoria = data.get("categoria")
            novo_produto_insert(nome, preco, marca, cor, imagem,descricao, stock, desconto, categoria, request.user.id)
            return redirect('todos_produtos')
    else:
        form = uploadFile()
        return render(request, 'criarProdutosPorFicheiro.html', {'form': form})

@login_required
def exportProdutos(request,format):
    if getTipoUserMongo(request.user.id) != "Administrador" and getTipoUserMongo(request.user.id) != "Comercial Tipo 1" and getTipoUserMongo(request.user.id) != "Parceiro":
        return redirect('index')
    pesquisa = request.GET.get('pesquisa', "")
    if pesquisa == 'null':
        pesquisa=""
    produtos = todos_produtos_other_search(pesquisa)
    produtos = [product for product in produtos]
    #json
    if format == 'json':
        for product in produtos:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        produtos = json.dumps(produtos)
        response = HttpResponse(produtos, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="produtos.json"'
        return response
    #xml
    if format == 'xml':
        root = ET.Element("root")
        for product in produtos:
            prod = ET.SubElement(root, "produto")
            for key, value in product.items():
                elem = ET.SubElement(prod, key)
                elem.text = str(value)

        xml_str = ET.tostring(root).decode("utf-8")
        response = HttpResponse(xml_str, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="produtos.xml"'
        return response

@login_required
def exportProdutosMarketPlace(request,format):
    if getTipoUserMongo(request.user.id) != "Administrador" and getTipoUserMongo(request.user.id) != "Comercial Tipo 1" and getTipoUserMongo(request.user.id) != "Parceiro":
        return redirect('index')
    pesquisa = request.GET.get('pesquisa', "")
    if pesquisa == 'null':
        pesquisa=""
    produtos = todos_produtos_other_marketplace_search(pesquisa)
    produtos = [product for product in produtos]
    #json
    if format == 'json':
        for product in produtos:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        produtos = json.dumps(produtos)
        response = HttpResponse(produtos, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="produtos.json"'
        return response
    #xml
    if format == 'xml':
        root = ET.Element("root")
        for product in produtos:
            prod = ET.SubElement(root, "produto")
            for key, value in product.items():
                elem = ET.SubElement(prod, key)
                elem.text = str(value)

        xml_str = ET.tostring(root).decode("utf-8")
        response = HttpResponse(xml_str, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="produtos.xml"'
        return response

def get_info_cliente(id_client):
    cursor = connection.cursor()
    cursor.execute("select * from info_sells_client(" + str(id_client) + ");")
    results = cursor.fetchall()
    return results[0]

def return_ano_client(id_client):
    cursor = connection.cursor()
    cursor.execute("select * from anos_pedidos_client(" + str(id_client) + ");")
    results = cursor.fetchall()
    anos = [int(item[0]) for item in results]
    return anos

def return_mes_client(id_client):
    cursor = connection.cursor()
    cursor.execute("select * from meses_pedidos_client(" + str(id_client) + ");")
    results = cursor.fetchall()
    meses = [int(item[0]) for item in results]
    return meses

def client_info_sells_year_month(ano, mes, id_client):
    cursor = connection.cursor()
    cursor.execute("select * from client_info_sells_year_month(" + str(ano) + "," + str(mes) + "," + str(id_client) + ")")
    results = cursor.fetchall()
    return results

@login_required
def estatisticas_cliente(request, id_user, acao):
    context = {}
    info = []
    dias = []
    ano = -1
    mes = -1
    anos = return_ano_client(id_user)
    meses = return_mes_client(id_user)
    context = {}
    client_info = get_info_cliente(id_user)
    client_valorvendas = (client_info[0])
    client_nvendas = (client_info[1])
    nomecliente = nome_cliente_other(id_user)
    if request.method == 'POST':
        data = request.POST
        ano = int(data.get("ano"))
        mes =  int(data.get("mes"))
        array_diasmes = [31,28,31,30,31,30,31,31,30,31,30,31]
        if ano % 4 == 0: 
            array_diasmes = [31,29,31,30,31,30,31,31,30,31,30,31]
        for x in range(0, array_diasmes[mes-1]):
            info.append(0)
            dias.append(x)
        # Create data for the bar graph
        results = client_info_sells_year_month(ano, mes, id_user)
        for x in results:
            info[x[0]] = x[acao]
        # Create the bar graph
        if acao == 1:
            df = pd.DataFrame({
            "dia": dias,
            "valor_vendas": info,
            })
            fig = px.bar(df, x="dia", y="valor_vendas", barmode="group")
            fig.update_layout(xaxis=dict(range=[0, array_diasmes[mes-1]], tick0=1, dtick=1, tickvals=list(range(1, array_diasmes[mes-1]+1))), xaxis_title='dia',yaxis_title='valor_vendas', xaxis_fixedrange=True, yaxis_fixedrange=True)
        if acao == 2:
            df = pd.DataFrame({
            "dia": dias,
            "n_vendas": info,
            })
            fig = px.bar(df, x="dia", y="n_vendas", barmode="group")
            fig.update_layout(xaxis=dict(range=[0, array_diasmes[mes-1]], tick0=1, dtick=1, tickvals=list(range(1, array_diasmes[mes-1]+1))), yaxis=dict(dtick=1), xaxis_title='dia', yaxis_title='n_vendas', xaxis_fixedrange=True, yaxis_fixedrange=True) 
        # Convert the figure to a JSON string
        fig_json = fig.to_json()
        # Pass the JSON string to the template
        return render(request, "estatisticas_cliente.html", {"fig_json": fig_json, "ano": anos, "mes": meses, "anoselected": ano, "messelected": mes, "client_valorvendas": client_valorvendas, "client_nvendas": client_nvendas, "idcliente": id_user, "nomecliente": nomecliente})
    else:
        form = request.POST
        return render(request, "estatisticas_cliente.html", {'form': form, "ano": anos, "mes": meses, "anoselected": ano, "messelected": mes, "client_valorvendas": client_valorvendas, "client_nvendas": client_nvendas, "idcliente": id_user, "nomecliente": nomecliente})

@login_required
def produtos_parceiro(request):
    if getTipoUserMongo(request.user.id) == "Parceiro":
        products = todos_produtos_parceiro_other(request.user.id)
        return render(request, "produtos_parceiro.html", {'products': products})
    return redirect('index')

@login_required
def ativar_produto_parceiro(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Parceiro":
            list_ids_produtos_parceiro = ids_produtos_parceiro_other(request.user.id)
            if produto_id not in list_ids_produtos_parceiro:
                return redirect('index')
            active = get_active_produto_other(produto_id)
            if not active["active"]:
                return redirect('index')
            ativar_produto_parceiro_other(produto_id, request.user.id)
        return redirect('index')
    else:
        form = request.POST
        context = {'form': form}
        active = get_active_produto_other(produto_id)
        if not active["active"]:
            return redirect('index') 
        return render(request, 'ativar_produto_parceiro.html', context)

@login_required
def desativar_produto_parceiro(request, produto_id):
    context = {}
    if request.method == 'POST':
        if getTipoUserMongo(request.user.id) == "Parceiro":
            list_ids_produtos_parceiro = ids_produtos_parceiro_other(request.user.id)
            if produto_id not in list_ids_produtos_parceiro:
                return redirect('index')
            active = get_active_produto_other(produto_id)
            if not active["active"]:
                return redirect('index')     
            desativar_produto_parceiro_other(produto_id, request.user.id)
        return redirect('index')
    else:
        form = request.POST
        context = {'form': form}
        active = get_active_produto_other(produto_id)
        if not active["active"]:
            return redirect('index') 
        return render(request, 'desativar_produto_parceiro.html', context)