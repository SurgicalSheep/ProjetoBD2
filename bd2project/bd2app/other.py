import pymongo
from django.db import connections
conexaomongo = pymongo.MongoClient("mongodb+srv://eletropoggers_admin:faroladlucas@projetobd2-onlinedb.833ybao.mongodb.net/test")["bd2_mongo"]

def insere_ut(nome,username,password,tipouser,morada):
    bd = conexaomongo
    col = bd["utilizadores"]
    doc = {"id": user_max_id(),"nome":nome,"username":username,"password":password,"tipouser":tipouser,"morada":morada}
    x = col.insert_one(doc)
    return x

def novo_produto_insert(nome,preco,marca,cor,imagem,descricao,stock,desconto,categoria):
    bd = conexaomongo
    col = bd["produtos"]
    doc = {"id": product_max_id(),"nome":nome,"preco":preco,"marca":marca,"cor":cor,"imagem":imagem, "descricao":descricao,"stock":stock,"desconto":desconto,"categoria":categoria }
    x = col.insert_one(doc)
    return x

def todos_produtos_other():
    bd = conexaomongo
    collection = bd['produtos']
    return collection.find()

def todos_users_other():
    bd = conexaomongo
    collection = bd['utilizadores']
    return collection.find()
    
def product_max_id():
    bd = conexaomongo
    collection = bd['produtos']
    if collection.count_documents({}) == 0:
        newid = 1
    else:
        max_id = collection.find().sort('id', -1).limit(1)
        newid = max_id[0]['id'] + 1
    return newid

def user_max_id():
    bd = conexaomongo
    collection = bd['utilizadores']
    if collection.count_documents({}) == 0:
        newid = 1
    else:
        max_id = collection.find().sort('id', -1).limit(1)
        newid = max_id[0]['id'] + 1
    return newid

def apagar_produto_other(id):
    bd = conexaomongo
    col = bd["produtos"]
    x = col.delete_one({"id": id})
    return x