from django.urls import path
from . import views
from . import other
<<<<<<< HEAD
#teste 2
=======
#teste 1
>>>>>>> feature/test1
urlpatterns = [
    path('',views.index, name='index'),
    path('login', views.login, name='login'),
    path('registro',views.registro, name='registro'),
    path('novo_produto',views.novo_produto, name='novo_produto'),
    path('todos_produtos',views.todos_produtos, name='todos_produtos'),
    path('todos_users',views.todos_users, name='todos_users'),
    path('produto/<int:produto_id>/', views.detalhes_produto, name='detalhes_produto'),
    path('produto/apagar_produto/<int:produto_id>', views.apagar_produto, name='apagar_produto')
]