"""
Testes de Carga com Locust para o Chatbot de Acessibilidade Digital

Este arquivo define cenários de carga para testar o comportamento da API
sob diferentes níveis de tráfego.

Execução:
    # Interface web (recomendado)
    locust -f tests/load/locustfile.py --host=http://localhost:8000
    
    # Modo headless (sem interface)
    locust -f tests/load/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 60s --headless

Cenários:
    - ChatbotUser: Simula usuários fazendo perguntas sobre acessibilidade
    - HealthCheckUser: Simula monitoramento constante do health check
    - MixedUser: Simula uso misto (chat + health + métricas)
"""

from locust import HttpUser, task, between, constant
import random


class ChatbotUser(HttpUser):
    """
    Simula usuários fazendo perguntas sobre acessibilidade.
    
    Comportamento:
        - Espera entre 1 e 3 segundos entre requisições
        - Faz perguntas variadas sobre acessibilidade
        - Simula cache hits e misses
    """
    
    wait_time = between(1, 3)
    
    # Perguntas de exemplo para simular diferentes cenários
    perguntas = [
        "Como testar contraste de cores?",
        "O que é WCAG 2.1?",
        "Como tornar um site acessível a leitores de tela?",
        "Quais são os critérios de sucesso do WCAG AA?",
        "Como testar navegação por teclado?",
        "O que é ARIA?",
        "Como implementar skip links?",
        "Qual a diferença entre WCAG A, AA e AAA?",
        "Como testar acessibilidade com axe-core?",
        "O que são landmarks ARIA?",
    ]
    
    @task(10)
    def chat_request(self):
        """
        Envia uma pergunta para o endpoint de chat.
        Peso: 10 (mais frequente)
        """
        pergunta = random.choice(self.perguntas)
        
        with self.client.post(
            "/api/chat",
            json={"pergunta": pergunta},
            catch_response=True,
            name="/api/chat [POST]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                # Rate limit é esperado em testes de carga
                response.failure("Rate limit exceeded")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def health_check(self):
        """
        Verifica o health check da API.
        Peso: 2 (menos frequente)
        """
        with self.client.get("/api/health", name="/api/health [GET]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """
        Obtém métricas da API.
        Peso: 1 (raro)
        """
        with self.client.get("/api/metrics", name="/api/metrics [GET]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics failed: {response.status_code}")


class HealthCheckUser(HttpUser):
    """
    Simula monitoramento constante do health check.
    
    Comportamento:
        - Espera 5 segundos entre requisições (constante)
        - Apenas verifica health check
        - Simula load balancers e sistemas de monitoramento
    """
    
    wait_time = constant(5)
    
    @task
    def health_check(self):
        """Verifica health check constantemente"""
        with self.client.get("/api/health", name="/api/health [GET]") as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")


class MixedUser(HttpUser):
    """
    Simula uso misto da API (mais realista).
    
    Comportamento:
        - Espera entre 2 e 5 segundos entre requisições
        - Mistura chat, health check, config e métricas
        - Simula usuários reais navegando pela aplicação
    """
    
    wait_time = between(2, 5)
    
    perguntas = ChatbotUser.perguntas
    
    @task(15)
    def chat_request(self):
        """Pergunta sobre acessibilidade (mais frequente)"""
        pergunta = random.choice(self.perguntas)
        
        with self.client.post(
            "/api/chat",
            json={"pergunta": pergunta},
            catch_response=True,
            name="/api/chat [POST]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limit exceeded")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(3)
    def get_config(self):
        """Obtém configurações do frontend"""
        with self.client.get("/api/config", name="/api/config [GET]") as response:
            if response.status_code != 200:
                response.failure(f"Config failed: {response.status_code}")
    
    @task(2)
    def health_check(self):
        """Verifica health check"""
        with self.client.get("/api/health", name="/api/health [GET]") as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """Obtém métricas"""
        with self.client.get("/api/metrics", name="/api/metrics [GET]") as response:
            if response.status_code != 200:
                response.failure(f"Metrics failed: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Teste de stress - requisições rápidas e contínuas.
    
    Comportamento:
        - Espera apenas 0.1 a 0.5 segundos entre requisições
        - Testa limites do rate limiting
        - Identifica pontos de falha sob carga extrema
    
    Uso: Execute separadamente para testes de stress
    """
    
    wait_time = between(0.1, 0.5)
    
    perguntas = ChatbotUser.perguntas
    
    @task
    def rapid_chat_requests(self):
        """Requisições rápidas para testar rate limiting"""
        pergunta = random.choice(self.perguntas)
        
        with self.client.post(
            "/api/chat",
            json={"pergunta": pergunta},
            catch_response=True,
            name="/api/chat [POST] - Stress"
        ) as response:
            # Em stress test, rate limit é esperado
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
