from django.urls import path
from . import views
from . import other

urlpatterns = [
    path('',views.index, name='index'),
    path('login', views.loginUser, name='loginUser'),
    path('logout', views.logoutUser, name='logoutUser'),
    path('registro',views.registro, name='registro'),
    path('registroAdmin',views.registroAdmin, name='registroAdmin'),
    path('novo_produto',views.novo_produto, name='novo_produto'),
    path('todos_produtos/marketplace',views.todos_produtos_marketplace, name='todos_produtos'),
    path('todos_produtos',views.todos_produtos, name='todos_produtos'),
    path('todos_users',views.todos_users, name='todos_users'),
    path('produto/<int:produto_id>/', views.detalhes_produto, name='detalhes_produto'),
    path('categoria/<str:categoria>/', views.categoria, name='categoria'),
    path('produto/desativar_produto/<int:produto_id>', views.desativar_produto, name='desativar_produto'),
    path('produto/ativar_produto/<int:produto_id>', views.ativar_produto, name='ativar_produto'),
    path('produto/editar_produto/<int:produto_id>', views.editar_produto, name='editar_produto'),
    path('verPerfil/', views.verPerfil, name='verPerfil'),
    path('verPerfilAdmin/<int:idUser>', views.verPerfilAdmin, name='verPerfilAdmin'),
    path('editarPerfil/', views.editarPerfil, name='editarPerfil'),
    path('mudarPass/', views.mudarPass, name='mudarPass'),
    path('todos_pedidos', views.todos_pedidos, name='todos_pedidos'),#teste
    path('produto/remover_produto_carrinho/<int:produto_id>', views.remover_produto_carrinho, name='remover_produto_carrinho'),
    path('produto/removerProdutoCarrinhoAnonimo/<int:produto_id>', views.removerProdutoCarrinhoAnonimo, name='removerProdutoCarrinhoAnonimo'),
    path('produto/adicionar_carrinho/<int:produto_id>', views.adicionar_carrinho, name='adicionar_carrinho'),
    #path('itens_carrinho', views.itens_carrinho, name='itens_carrinho'),#teste
    path('carrinho', views.carrinho, name='carrinho'),
    path('pagamento/<int:id_carrinho>', views.pagamento, name='pagamento'),
    path('utilizador_por_confirmar', views.utilizador_por_confirmar, name='utilizador_por_confirmar'),
    path('acao_utilizador/<int:id_user>/<str:acao>/<str:nome>', views.acaoutilizador, name='acao_utilizador'),
    path('aceitar_utilizador/<int:id_user>', views.aceitar_utilizador, name='aceitar_utilizador'),
    path('rejeitar_utilizador/<int:id_user>', views.rejeitar_utilizador, name='rejeitar_utilizador'),
    path('homepage_fornecedores', views.homepage_fornecedores, name='homepage_fornecedores'),
    path('desativar_produto_fornecedor/<int:id_produto>/<int:id_fornecedor>', views.desativar_produto_fornecedor, name='desativar_produto_fornecedor'),
    path('ativar_produto_fornecedor/<int:id_produto>/<int:id_fornecedor>', views.ativar_produto_fornecedor, name='ativar_produto_fornecedor'),
    #path('editarUsers/', views.editarUsers, name='editarUsers'), # falta sitio para abrir isto
    path('editarUser/<int:id_user>', views.editarUser, name='editarUser'),
    path('desativarUser/<int:id_user>/save', views.desativarUser, name='desativarUser'),
    path('ativarUser/<int:id_user>/save', views.ativarUser, name='ativarUser'),
    path('mudarEstadoClientes/', views.mudarEstadoClientes, name='mudarEstadoClientes'), # falta sitio para abrir isto
    #path('editar_preco_carrinho', views.editar_preco_carrinho, name='editar_preco_carrinho'),
    path('produto/solicitar_produto/<int:id_product>', views.solicitar_produto, name='solicitar_produto'),
    #path('edit_product/<int:produto_id>/<int:carrinho_id>', views.edit_product, name='edit_product'),   pus de lado por enquanto pq estava a dar um erro da treta
    #path('edit_quantity_cart/<int:produto_id>/<int:carrinho_id>', views.edit_quantity_cart, name='edit_quantity_cart'),   #tinha posto de lado por um erro da treta
    #path('produto/adicionar_carrinho/<int:produto_id>', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('increment_quantity/<int:id_carrinho>/<int:id_produto>/', views.increment_quantity, name='increment_quantity'),
    path('decrement_quantity/<int:id_carrinho>/<int:id_produto>/', views.decrement_quantity, name='decrement_quantity'),
    path('incrementQuantityAnonimo/<int:id_produto>/', views.incrementQuantityAnonimo, name='incrementQuantityAnonimo'),
    path('decrementQuantityAnonimo/<int:id_produto>/', views.decrementQuantityAnonimo, name='decrementQuantityAnonimo'),
    #path('404', views.error404, name='error404'),
    path('encomendas_cliente/<int:id_user>', views.encomendas_cliente, name='encomendas_cliente'),
    path('encomenda/<int:id_encomenda>', views.encomenda, name='encomenda'),
    path('encomenda_cancelar/<int:id_encomenda>', views.encomenda_cancelar, name='encomenda_cancelar'),
    path('pedidos_cliente', views.pedidos_cliente, name='pedidos_cliente'),
    path('pedidos_fornecedor', views.pedidos_fornecedor, name='pedidos_fornecedor'),
    path('aceitar_pedidos_fornecedor/<int:id_pedidofornecedor>/<int:id_produto>/<int:quantidade>', views.aceitar_pedidos_fornecedor, name='aceitar_pedidos_fornecedor'),
    path('rejeitar_pedidos_fornecedor/<int:id_pedidofornecedor>', views.rejeitar_pedidos_fornecedor, name='rejeitar_pedidos_fornecedor'),
    path('out_of_stock', views.out_of_stock, name='out_of_stock'),
    path('gerir_clientes', views.gerir_clientes, name='gerir_clientes'),
    path('gerir_fornecedores', views.gerir_fornecedores, name='gerir_fornecedores'),
    path('gerir_comerciais', views.gerir_comerciais, name='gerir_comerciais'),
    path('gerir_parceiros', views.gerir_parceiros, name='gerir_parceiros'), 
    path('gerir_produtos_fornecedor/<int:id_user>', views.gerir_produtos_fornecedor, name='gerir_produtos_fornecedor'),
    path('add_produtos_fornecedor/<int:id_fornecedor>', views.add_produtos_fornecedor, name='add_produtos_fornecedor'),
    path('estatisticas/<int:acao>', views.estatisticas, name='estatisticas'),
    path('estatisticas_cliente/<int:id_user>/<int:acao>', views.estatisticas_cliente, name='estatisticas_cliente'),
    path('criarProdutosPorFicheiro',views.criarProdutosPorFicheiro, name='criarProdutosPorFicheiro'),
    path('exportProdutos/<str:format>',views.exportProdutos, name='exportProdutos'),
    path('exportProdutosMarketplace/<str:format>',views.exportProdutosMarketPlace, name='exportProdutosMarketplace'),
    path('produtos_parceiro',views.produtos_parceiro, name='produtos_parceiro'),
    path('ativar_produto_parceiro/<int:produto_id>',views.ativar_produto_parceiro, name='ativar_produto_parceiro'),
    path('desativar_produto_parceiro/<int:produto_id>',views.desativar_produto_parceiro, name='desativar_produto_parceiro'),
    path('showLogs/',views.showLogs, name='showLogs'),
    path('gerir_produtos_parceiro/<int:id_user>', views.gerir_produtos_parceiro, name='gerir_produtos_parceiro'),
    path('loja_ativar_produto_parceiro/<int:produto_id>/<int:id_parceiro>',views.loja_ativar_produto_parceiro, name='loja_ativar_produto_parceiro'),
    path('loja_desativar_produto_parceiro/<int:produto_id>/<int:id_parceiro>',views.loja_desativar_produto_parceiro, name='loja_desativar_produto_parceiro'),
]
handler404='bd2app.views.error404'