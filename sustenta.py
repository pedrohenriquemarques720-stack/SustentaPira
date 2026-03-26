import requests
import json
from datetime import datetime

# ========== CONFIGURAÇÃO ==========
SHEETDB_URL = 'https://sheetdb.io/api/v1/pxcozyw0d91x8'

# ========== FUNÇÕES PRINCIPAIS ==========

def carregar_usuarios():
    """Carrega todos os usuários da planilha"""
    try:
        response = requests.get(SHEETDB_URL)
        if response.status_code == 200:
            usuarios = response.json()
            print(f"✅ {len(usuarios)} usuários carregados com sucesso!")
            return usuarios
        else:
            print(f"❌ Erro ao carregar usuários: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return []

def buscar_usuario(email):
    """Busca um usuário específico pelo email"""
    try:
        response = requests.get(f"{SHEETDB_URL}/search?email={email}")
        if response.status_code == 200:
            usuarios = response.json()
            if usuarios:
                return usuarios[0]
            else:
                print(f"❌ Usuário com email {email} não encontrado")
                return None
        else:
            print(f"❌ Erro ao buscar usuário: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def criar_usuario(nome, email, senha, telefone=""):
    """Cria um novo usuário na planilha"""
    try:
        novo_usuario = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "telefone": telefone,
            "cidade": "Piracicaba",
            "data_cadastro": datetime.now().strftime("%d/%m/%Y"),
            "pontos": "0",
            "nivel": "🌱 EcoIniciante",
            "streak": "1",
            "desafios": "0",
            "conquistas": "🌱 Primeiro passo"
        }
        
        response = requests.post(
            SHEETDB_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"data": [novo_usuario]})
        )
        
        if response.status_code == 201:
            print(f"✅ Usuário {nome} criado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao criar usuário: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def atualizar_usuario(email, dados):
    """Atualiza dados de um usuário existente"""
    try:
        response = requests.patch(
            f"{SHEETDB_URL}/email/{email}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(dados)
        )
        
        if response.status_code == 200:
            print(f"✅ Usuário {email} atualizado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao atualizar usuário: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def adicionar_pontos(email, pontos):
    """Adiciona pontos a um usuário e atualiza seu nível"""
    usuario = buscar_usuario(email)
    if not usuario:
        return False
    
    pontos_atuais = int(usuario.get("pontos", 0))
    novos_pontos = pontos_atuais + pontos
    
    # Determinar novo nível baseado nos pontos
    if novos_pontos >= 5000:
        novo_nivel = "🏆 EcoHerói Supremo"
    elif novos_pontos >= 1000:
        novo_nivel = "🌳 EcoMestre"
    elif novos_pontos >= 500:
        novo_nivel = "🍃 EcoGuardião"
    elif novos_pontos >= 100:
        novo_nivel = "🌿 EcoAprendiz"
    else:
        novo_nivel = "🌱 EcoIniciante"
    
    # Atualizar streak (simplificado)
    streak_atual = int(usuario.get("streak", 0))
    desafios_atual = int(usuario.get("desafios", 0))
    
    dados_atualizacao = {
        "pontos": str(novos_pontos),
        "nivel": novo_nivel,
        "streak": str(streak_atual + 1),
        "desafios": str(desafios_atual + 1)
    }
    
    return atualizar_usuario(email, dados_atualizacao)

def adicionar_conquista(email, conquista):
    """Adiciona uma conquista ao usuário"""
    usuario = buscar_usuario(email)
    if not usuario:
        return False
    
    conquistas_atuais = usuario.get("conquistas", "")
    if conquista not in conquistas_atuais:
        novas_conquistas = conquistas_atuais + f",{conquista}" if conquistas_atuais else conquista
        return atualizar_usuario(email, {"conquistas": novas_conquistas})
    return True

def estatisticas_gerais():
    """Retorna estatísticas gerais do sistema"""
    usuarios = carregar_usuarios()
    if not usuarios:
        return {}
    
    total_pontos = sum(int(u.get("pontos", 0)) for u in usuarios)
    media_pontos = total_pontos // len(usuarios) if usuarios else 0
    total_desafios = sum(int(u.get("desafios", 0)) for u in usuarios)
    
    # Ranking
    ranking = sorted(usuarios, key=lambda x: int(x.get("pontos", 0)), reverse=True)
    
    return {
        "total_usuarios": len(usuarios),
        "total_pontos": total_pontos,
        "media_pontos": media_pontos,
        "total_desafios": total_desafios,
        "ranking": ranking[:10]  # Top 10
    }

def exibir_menu():
    """Exibe o menu principal"""
    print("\n" + "="*50)
    print("        🌿 SUSTENTAPIRA - ADMINISTRAÇÃO 🌿")
    print("="*50)
    print("1. 📋 Listar todos os usuários")
    print("2. 🔍 Buscar usuário por email")
    print("3. ➕ Criar novo usuário")
    print("4. ⭐ Adicionar pontos a um usuário")
    print("5. 🏆 Ver ranking geral")
    print("6. 📊 Estatísticas do sistema")
    print("7. 🎖️ Adicionar conquista a usuário")
    print("8. 🚪 Sair")
    print("="*50)

def listar_usuarios():
    """Lista todos os usuários cadastrados"""
    usuarios = carregar_usuarios()
    if not usuarios:
        print("❌ Nenhum usuário encontrado.")
        return
    
    print("\n" + "-"*80)
    print(f"{'NOME':<25} {'EMAIL':<30} {'PONTOS':<10} {'NÍVEL':<20}")
    print("-"*80)
    for u in usuarios:
        nome = u.get('nome', 'N/A')[:24]
        email = u.get('email', 'N/A')[:29]
        pontos = u.get('pontos', '0')
        nivel = u.get('nivel', 'N/A')[:19]
        print(f"{nome:<25} {email:<30} {pontos:<10} {nivel:<20}")
    print("-"*80)
    print(f"Total: {len(usuarios)} usuários")

def buscar_usuario_interativo():
    """Busca usuário por email de forma interativa"""
    email = input("Digite o email do usuário: ").strip()
    usuario = buscar_usuario(email)
    
    if usuario:
        print("\n" + "-"*60)
        print(f"📧 Email: {usuario.get('email')}")
        print(f"👤 Nome: {usuario.get('nome')}")
        print(f"📞 Telefone: {usuario.get('telefone', 'N/A')}")
        print(f"📍 Cidade: {usuario.get('cidade', 'N/A')}")
        print(f"📅 Cadastro: {usuario.get('data_cadastro', 'N/A')}")
        print(f"⭐ Pontos: {usuario.get('pontos', 0)}")
        print(f"🏆 Nível: {usuario.get('nivel', 'N/A')}")
        print(f"🔥 Streak: {usuario.get('streak', 0)} dias")
        print(f"✅ Desafios: {usuario.get('desafios', 0)}")
        print(f"🎖️ Conquistas: {usuario.get('conquistas', 'Nenhuma')}")
        print("-"*60)
    else:
        print("❌ Usuário não encontrado.")

def criar_usuario_interativo():
    """Cria um novo usuário de forma interativa"""
    print("\n--- Criar Novo Usuário ---")
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()
    telefone = input("Telefone (opcional): ").strip()
    
    if not nome or not email or not senha:
        print("❌ Nome, email e senha são obrigatórios!")
        return
    
    if criar_usuario(nome, email, senha, telefone):
        print(f"✅ Usuário {nome} criado com sucesso!")
    else:
        print("❌ Erro ao criar usuário.")

def adicionar_pontos_interativo():
    """Adiciona pontos a um usuário de forma interativa"""
    email = input("Digite o email do usuário: ").strip()
    try:
        pontos = int(input("Quantos pontos adicionar? "))
    except ValueError:
        print("❌ Valor inválido!")
        return
    
    if adicionar_pontos(email, pontos):
        print(f"✅ {pontos} pontos adicionados com sucesso!")
    else:
        print("❌ Erro ao adicionar pontos.")

def ver_ranking():
    """Mostra o ranking dos usuários"""
    stats = estatisticas_gerais()
    if not stats or not stats.get("ranking"):
        print("❌ Nenhum dado disponível.")
        return
    
    print("\n" + "="*60)
    print("                    🏆 RANKING ECOCIDADÃOS 🏆")
    print("="*60)
    print(f"{'POS':<5} {'NOME':<25} {'PONTOS':<10} {'NÍVEL':<20}")
    print("-"*60)
    
    for i, u in enumerate(stats["ranking"], 1):
        medalha = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
        nome = u.get('nome', 'N/A')[:24]
        pontos = u.get('pontos', 0)
        nivel = u.get('nivel', 'N/A')[:19]
        print(f"{medalha:<5} {nome:<25} {pontos:<10} {nivel:<20}")
    
    print("="*60)

def ver_estatisticas():
    """Mostra estatísticas gerais do sistema"""
    stats = estatisticas_gerais()
    if not stats:
        print("❌ Erro ao carregar estatísticas.")
        return
    
    print("\n" + "="*50)
    print("            📊 ESTATÍSTICAS DO SISTEMA")
    print("="*50)
    print(f"👥 Total de usuários: {stats['total_usuarios']}")
    print(f"⭐ Total de pontos acumulados: {stats['total_pontos']}")
    print(f"📈 Média de pontos por usuário: {stats['media_pontos']}")
    print(f"✅ Total de desafios completados: {stats['total_desafios']}")
    if stats['total_usuarios'] > 0:
        print(f"🏆 Média de desafios por usuário: {stats['total_desafios'] // stats['total_usuarios']}")
    print("="*50)

def adicionar_conquista_interativo():
    """Adiciona uma conquista a um usuário"""
    email = input("Digite o email do usuário: ").strip()
    conquista = input("Digite o nome da conquista: ").strip()
    
    if adicionar_conquista(email, conquista):
        print(f"✅ Conquista '{conquista}' adicionada com sucesso!")
    else:
        print("❌ Erro ao adicionar conquista.")

# ========== EXECUÇÃO PRINCIPAL ==========
def main():
    print("\n🌿 SustentaPira - Sistema de Gerenciamento 🌿")
    print("Conectando ao banco de dados...")
    
    # Testar conexão
    usuarios = carregar_usuarios()
    if usuarios:
        print(f"✅ Conexão estabelecida! {len(usuarios)} usuários encontrados.")
    else:
        print("⚠️ Nenhum usuário encontrado ou erro de conexão.")
    
    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            listar_usuarios()
        elif opcao == "2":
            buscar_usuario_interativo()
        elif opcao == "3":
            criar_usuario_interativo()
        elif opcao == "4":
            adicionar_pontos_interativo()
        elif opcao == "5":
            ver_ranking()
        elif opcao == "6":
            ver_estatisticas()
        elif opcao == "7":
            adicionar_conquista_interativo()
        elif opcao == "8":
            print("\n🌱 Obrigado por usar o SustentaPira! 🌿")
            print("Continue fazendo a diferença! ♻️")
            break
        else:
            print("❌ Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
