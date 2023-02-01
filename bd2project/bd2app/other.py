import pymongo
from django.shortcuts import get_object_or_404, redirect
from bd2app.models import *
bd = pymongo.MongoClient("mongodb+srv://eletropoggers_admin:faroladlucas@projetobd2-onlinedb.833ybao.mongodb.net/test")["bd2_mongo"]
import re

def insere_ut(id,nome,tipouser,morada,username,email):
    col = bd["utilizadores"]
    doc = {"id": id,"nome":nome,"tipouser":tipouser,"morada":morada, "username":username, "email":email,"active":True}
    x = col.insert_one(doc)
    #criar tambem um carrinho de compras para o user
    if tipouser == "Cliente":
        carrinho = carrinho_compras(id_carrinho=id,id_cliente=id,preco_total=0)
        carrinho.save()
    return x

def novo_produto_insert(nome, preco, marca, cor, imagem, descricao, stock, desconto, categoria, idgestor):
    col = bd["produtos"]
    if getTipoUserMongo(idgestor) == "Parceiro":
        doc = {"id": product_max_id(),"nome":nome, "preco":preco, "marca":marca, "cor":cor, "imagem":imagem, "descricao":descricao, "stock":stock, "desconto":desconto, "categoria":categoria, "active":False, "id_utilizador": idgestor, "belongs_store": False, "active_parceiro": True, "id_parceiro": idgestor} 
    else:
        doc = {"id": product_max_id(),"nome":nome, "preco":preco, "marca":marca, "cor":cor, "imagem":imagem, "descricao":descricao, "stock":stock, "desconto":desconto, "categoria":categoria, "active":True, "id_utilizador": idgestor, "belongs_store": True} 
    x = col.insert_one(doc)
    return x

def todos_produtos_other():
    collection = bd['produtos']
    return collection.find({'belongs_store': True})

def todos_produtos_other_search(search):
    if search == "":
        return todos_produtos_other()

    collection = bd['produtos']

    pattern = re.compile(search, re.IGNORECASE)

    query = {
        "$or": [
            {"nome": {"$regex": pattern}},
            {"preco": {"$regex": pattern}},
            {"marca": {"$regex": pattern}},
            {"cor": {"$regex": pattern}},
            {"descricao": {"$regex": pattern}},
            {"categoria": {"$regex": pattern}},
        ],
        "belongs_store": True
    }

    return collection.find(query)

def todos_produtos_other_marketplace():
    collection = bd['produtos']
    return collection.find({'belongs_store': False})
    
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

def desativar_produto_other(id, idgestor):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active": False, "id_utilizador": idgestor}})
    return x

def ativar_produto_other(id, idgestor):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active": True, "id_utilizador": idgestor}})
    return x

def remover_produto_carrinho_other(produto_id, carrinho_id):
    item = get_object_or_404(itens_carrinho_model, id_produto=produto_id,id_carrinho=carrinho_id)
    item.delete()
    return redirect('carrinho')

def getTipoUserMongo(id):
    collection = bd['utilizadores']
    user = collection.find_one({"id": id})
    return user["tipouser"]

def updateUserMongo(id_user, nome, email, morada, tipouser, active, idgestor):
    collection = bd['utilizadores']
    collection.update_one({"id": id_user}, {"$set": {"nome": nome, "morada": morada, "email": email, "active": bool(active), "tipouser": tipouser, "id_utilizador": idgestor}})

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

def todos_produtos_fornecedor_n_fornece_other(idfornecedor):
    collection = bd['produtos_fornecedores']
    collection2 = bd['produtos']
    produtos_que_fornece = [x["id_produto"] for x in collection.find({"id_fornecedor": idfornecedor}, {"_id": 0,"id_produto": 1})]
    produtos = collection2.find({ "id": { "$nin": produtos_que_fornece } }, {"_id": 0,"id": 1, "nome":1}).sort("nome",1)
    return produtos

def nome_cliente_other(id_user):
    collection = bd["vw_nome_clientes"]
    aux = collection.find({"id": id_user})
    nome = aux[0]["nome"]
    return nome

def todos_produtos_parceiro_other(id_parceiro):
    collection = bd['produtos']
    return list(collection.find({"id_parceiro": id_parceiro, "belongs_store": False}))

def ids_produtos_parceiro_other(id_parceiro):
    collection = bd['vw_ids_produtos_parceiros']
    results=[]
    ids = collection.find({"id_parceiro": id_parceiro}, {"id": 1})
    for x in ids:
        results.append(x["id"])
    return results

def ativar_produto_parceiro_other(id, idgestor):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active_parceiro": True, "id_utilizador": idgestor}})
    return x

def desativar_produto_parceiro_other(id, idgestor):
    collection = bd['produtos']
    x = collection.update_one({"id": id}, {"$set": {"active_parceiro": False, "id_utilizador": idgestor}})
    return x

def get_active_produto_other(id_produto):
    collection = bd['produtos']
    x = collection.find({"id": id_produto}, {"_id": 0, "active": 1})
    return x[0]