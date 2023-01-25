import pymongo
from django.shortcuts import get_object_or_404, redirect
from bd2app.models import *
bd = pymongo.MongoClient("mongodb+srv://eletropoggers_admin:faroladlucas@projetobd2-onlinedb.833ybao.mongodb.net/test")["bd2_mongo"]

def insere_ut(id,nome,tipouser,morada,username,email):
    col = bd["utilizadores"]
    doc = {"id": id,"nome":nome,"tipouser":tipouser,"morada":morada, "username":username, "email":email,"active":True}
    x = col.insert_one(doc)
    #criar tambem um carrinho de compras para o user
    carrinho = carrinho_compras(id_carrinho=id,id_cliente=id,preco_total=0)
    carrinho.save()
    return x

def novo_produto_insert(nome,preco,marca,cor,imagem,descricao,stock,desconto,categoria,preco_com_desconto):
    col = bd["produtos"]
    doc = {"id": product_max_id(),"nome":nome,"preco":preco,"marca":marca,"cor":cor,"imagem":imagem, "descricao":descricao,"stock":stock,"desconto":desconto,"categoria":categoria,"active":True,"preco_com_desconto":preco_com_desconto} 
    x = col.insert_one(doc)
    return x

def todos_produtos_other():
    collection = bd['produtos']
    return collection.find()

def todos_users_other():
    collection = bd['utilizadores']
    return collection.find()
    
def product_max_id():
    collection = bd['produtos']
    if collection.count_documents({}) == 0:
        newid = 1
    else:
        max_id = collection.find().sort('id', -1).limit(1)
        newid = max_id[0]['id'] + 1
    return newid

def user_max_id():
    collection = bd['utilizadores']
    if collection.count_documents({}) == 0:
        newid = 1
    else:
        max_id = collection.find().sort('id', -1).limit(1)
        newid = max_id[0]['id'] + 1
    return newid

def desativar_produto_other(id):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active": False}})
    return x

def ativar_produto_other(id):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active": True}})
    return x

def remover_produto_carrinho_other(produto_id, carrinho_id):
    item = get_object_or_404(itens_carrinho_model, id_produto=produto_id,id_carrinho=carrinho_id)
    item.delete()
    return redirect('carrinho')

def getTipoUserMongo(id):
    collection = bd['utilizadores']
    user = collection.find_one({"id": id})
    return user["tipouser"]

def updateUserMongo(id_user, nome, email, morada, tipouser, active):
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"nome": nome, "morada": morada, "email": email, "active": bool(active), "tipouser": tipouser}})

def updatePerfil(id_user, nome, email, morada):
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"nome": nome, "morada": morada, "email": email}})

def desativarUserMongo(id, idgestor):
    collection = bd['utilizadores']
    collection.update_one({"id": id}, {"$set": {"active": False, "id_utilizador": idgestor}})

def ativarUserMongo(id, idgestor):
    collection = bd['utilizadores']
    collection.update_one({"id": id}, {"$set": {"active": True, "id_utilizador": idgestor}})

def adicionarProdutoCarrinhoAnonimo(id):    
    #request.session['carrinho'].append(id)
    return 1

def converterCarrinhoAnonimoParaLogado(id):
    #carrinhoAnonimo = request.session['carrinho']
    return 1

def todos_fornecedores_produto_other(id_produto):
    collection = bd['produtos_fornecedores']
    return collection.find({"id_produto": id_produto})