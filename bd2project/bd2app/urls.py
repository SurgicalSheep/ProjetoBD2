from django.urls import path
from . import views
from . import other

urlpatterns = [
    path('',views.index, name='index'),
    path('login', views.loginUser, name='loginUser'),
    path('logout', views.logoutUser, name='logoutUser'),
    path('registro',views.registro, name='registro'),
    path('novo_produto',views.novo_produto, name='novo_produto'),
    path('todos_produtos',views.todos_produtos, name='todos_produtos'),
    path('todos_users',views.todos_users, name='todos_users'),
    path('produto/<int:produto_id>/', views.detalhes_produto, name='detalhes_produto'),
    path('categoria/<str:categoria>/', views.categoria, name='categoria'),
    path('produto/apagar_produto/<int:produto_id>', views.apagar_produto, name='apagar_produto'),
    path('produto/editar_produto/<int:produto_id>', views.editar_produto, name='editar_produto'),
    path('pedidos_cliente', views.pedidos_cliente, name='pedidos_cliente'),
    path('todos_pedidos', views.todos_pedidos, name='todos_pedidos'),#teste
    path('produto/remover_produto_carrinho/<int:produto_id>', views.remover_produto_carrinho, name='remover_produto_carrinho'),
    path('produto/adicionar_carrinho/<int:produto_id>/<int:produto_desconto>/<str:produto_nome>/<str:produto_preco>/<path:produto_imagem>', views.adicionar_carrinho, name='adicionar_carrinho'),
    #path('itens_carrinho', views.itens_carrinho, name='itens_carrinho'),#teste
    path('carrinho', views.carrinho, name='carrinho'),
    path('pagamento/<int:id_carrinho>', views.pagamento, name='pagamento'),
    path('utilizador_por_confirmar', views.utilizador_por_confirmar, name='utilizador_por_confirmar'),
    path('acao_utilizador/<int:id_user>/<str:acao>/<str:nome>', views.acaoutilizador, name='acao_utilizador'),
    path('aceitar_utilizador/<int:id_user>', views.aceitar_utilizador, name='aceitar_utilizador'),
    path('rejeitar_utilizador/<int:id_user>', views.rejeitar_utilizador, name='rejeitar_utilizador'),
    path('homepage_fornecedores', views.homepage_fornecedores, name='homepage_fornecedores'),
    path('desativar_produto_fornecedor/<int:id_produto>', views.desativar_produto_fornecedor, name='desativar_produto_fornecedor'),
    path('ativar_produto_fornecedor/<int:id_produto>', views.ativar_produto_fornecedor, name='ativar_produto_fornecedor'),
    path('editarUsers/', views.editarUsers, name='editarUsers'),
    path('editarUser/<int:id_user>', views.editarUser, name='editarUser'),
    path('desativarUser/<int:id_user>/save', views.desativarUser, name='desativarUser'),
    path('ativarUser/<int:id_user>/save', views.ativarUser, name='ativarUser'),
    #path('editar_preco_carrinho', views.editar_preco_carrinho, name='editar_preco_carrinho'),
    #path('edit_product/<int:produto_id>/<int:carrinho_id>', views.edit_product, name='edit_product'),   pus de lado por enquanto pq estava a dar um erro da treta
    #path('edit_quantity_cart/<int:produto_id>/<int:carrinho_id>', views.edit_quantity_cart, name='edit_quantity_cart'),   #tinha posto de lado por um erro da treta
    #path('produto/adicionar_carrinho/<int:produto_id>', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('increment_quantity/<int:id_carrinho>/<int:id_produto>/', views.increment_quantity, name='increment_quantity'),
    path('decrement_quantity/<int:id_carrinho>/<int:id_produto>/', views.decrement_quantity, name='decrement_quantity'),
]