

def test_pagina_inicial_carrega(client):
    """Testa se a rota principal ('/') ou a página de login carrega com sucesso (HTTP 200)."""
    
   
    response = client.get('/')
    
    
    assert response.status_code == 200
   
    assert b"Login" in response.data 

def test_dashboard_redireciona_para_login(client):
    """Testa se a dashboard (que exige login) redireciona corretamente quando o usuário não está logado."""
    
   
    response = client.get('/dashboard', follow_redirects=True)
    
    
    assert response.status_code == 200
    assert b"Login" in response.data