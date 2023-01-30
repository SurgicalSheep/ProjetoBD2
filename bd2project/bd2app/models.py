from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import pymongo
bd = pymongo.MongoClient("mongodb+srv://eletropoggers_admin:faroladlucas@projetobd2-onlinedb.833ybao.mongodb.net/test")["bd2_mongo"]
# Create your models here.

class produtoMongo(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    nome = models.CharField(max_length=100)
    preco = models.FloatField()
    marca = models.CharField(max_length=100)
    cor = models.CharField(max_length=100)
    imagem = models.CharField(max_length=100)
    descricao = models.TextField()
    stock = models.IntegerField()
    desconto = models.FloatField()
    categoria = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    id_utilizador = models.CharField(max_length=100)
    belongs_store = models.CharField(max_length=100)

    @classmethod
    def getDataStore(cls):
        collection = bd['produtos']
        data = collection.find({'belongs_store': True})
        return data
    @classmethod
    def getDataMarketplace(cls):
        collection = bd['produtos']
        data = collection.find({'belongs_store': False})
        return data


class todos_pedidos_model(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.IntegerField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=255)
    data = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'pedidos'

class Itens_Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    id_pedido = models.IntegerField()
    id_produto = models.IntegerField()
    quantidade = models.IntegerField()
    preco_produto = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        managed = False
        db_table = 'itens_pedido'

class carrinho_compras(models.Model):
    id_carrinho = models.AutoField(primary_key=True)
    id_cliente = models.IntegerField()
    preco_total = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'carrinho_compras'

class itens_carrinho_model(models.Model):
    id = models.AutoField(primary_key=True)
    id_carrinho = models.IntegerField()
    id_produto = models.IntegerField()
    quantidade = models.IntegerField()
    preco_produto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        managed = False
        db_table = 'itens_carrinho'

class PedidoFornecedor(models.Model):
    id_pedidofornecedor = models.AutoField(primary_key=True)
    id_fornecedor = models.IntegerField()
    id_produto = models.IntegerField()
    quantidade = models.IntegerField()
    datapedido = models.DateTimeField()
    dataentrega = models.DateTimeField()
    estado = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'pedidos_fornecedor'

class Logs_plpgsql(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_utilizador = models.IntegerField(null=False)
    data = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, null=False)
    nome_tabela = models.CharField(max_length=255, null=False)
    class Meta:
        managed = False
        db_table = 'logs_plpgsql'