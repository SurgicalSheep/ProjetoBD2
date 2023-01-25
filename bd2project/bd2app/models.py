from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

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