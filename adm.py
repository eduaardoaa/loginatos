# adm.py
import mysql.connector
import streamlit as st
import pandas as pd

def verificar_permissao():
    """Verifica se o usuário está autenticado e tem permissão de admin"""
    if not st.session_state.get('authenticated', False):
        st.error("Você não está autenticado!")
        st.session_state.page = None
        st.rerun()
    
    if st.session_state.user_info.get('permissao') != 'adm':
        st.error("Acesso negado: Permissão insuficiente!")
        # Limpa a sessão
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.page = None
        st.rerun()

def conectarbanco():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="dudu2305",
            database="atoscapital"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def puxarusuarios():
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, `Nome/Empresa`, usuario, senha, numero, permissao FROM usuarios ORDER BY id ASC")
        usuarios = cursor.fetchall()
        conexao.close()
        return usuarios
    return []

def atualizacaousuarios(user_id, nome_empresa, usuario, senha, numero, permissao):
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s AND id != %s", (usuario, user_id))
        usuario_existente = cursor.fetchone()

        cursor.execute("SELECT id FROM usuarios WHERE numero = %s AND id != %s", (numero, user_id))
        numero_existente = cursor.fetchone()

        if usuario_existente:
            st.error("Nome de usuário já está sendo utilizado por outro usuário.")
            return False

        if numero_existente:
            st.error("Número já está sendo utilizado por outro usuário.")
            return False

        cursor.execute(
            "UPDATE usuarios SET `Nome/Empresa` = %s, usuario = %s, senha = %s, numero = %s, permissao = %s WHERE id = %s",
            (nome_empresa, usuario, senha, numero, permissao, user_id)
        )
        conexao.commit()
        conexao.close()
        return True
    return False

def excluirusuario(user_id):
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        conexao.commit()
        conexao.close()
        st.success("Usuário excluído com sucesso!")

def novousuario(nome_empresa, usuario, senha, numero, permissao):
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (usuario,))
        count_usuario = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE numero = %s", (numero,))
        count_numero = cursor.fetchone()[0]

        if count_usuario > 0:
            st.error("Nome de usuário já está sendo utilizado.")
            return False

        if count_numero > 0:
            st.error("Número já está sendo utilizado.")
            return False

        cursor.execute(
            "INSERT INTO usuarios (`Nome/Empresa`, usuario, senha, numero, permissao) VALUES (%s, %s, %s, %s, %s)",
            (nome_empresa, usuario, senha, numero, permissao)
        )
        conexao.commit()
        conexao.close()
        return True
    return False

def formularionovousuario():
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("❌ Fechar", key="fecharformulario"):
            st.session_state.novousuario = False
            st.rerun()

    st.subheader("Adicionar Novo Usuário")

    with st.form(key="formnovousuario"):
        nome_empresa = st.text_input("Nome/Empresa")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        numero = st.text_input("Número")
        permissao = st.radio("Permissão", ["adm", "cliente"], horizontal=True)

        submit_button = st.form_submit_button(label="Adicionar Usuário", use_container_width=True)

        if submit_button:
            if novousuario(nome_empresa, usuario, senha, numero, permissao):
                st.session_state.mensagem = "Novo usuário cadastrado com sucesso!"
                st.session_state.novousuario = False
                st.rerun()

def formularioeditarusuario(user):
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("❌ Fechar", key=f"fecharformularioeditar{user[0]}"):
            st.session_state.editar_usuario = None
            st.rerun()

    st.subheader(f"Editar Usuário: {user[1]}")

    with st.form(key=f"editarusuario{user[0]}"):
        nome_empresa = st.text_input("Nome/Empresa", value=user[1])
        usuario = st.text_input("Usuário", value=user[2])
        senha = st.text_input("Senha", value=user[3], type="password")
        numero = st.text_input("Número", value=user[4])
        permissao = st.radio("Permissão", ["adm", "cliente"], 
                           index=0 if user[5] == "adm" else 1,
                           horizontal=True)
        submit_button = st.form_submit_button(label="Atualizar Usuário", use_container_width=True)

        if submit_button:
            if atualizacaousuarios(user[0], nome_empresa, usuario, senha, numero, permissao):
                st.session_state.editar_usuario = None
                st.rerun()

def listarusuarios():
    usuarios = puxarusuarios()
    
    # Verificação simplificada de dispositivo móvel
    try:
        st.columns(6)  # Testa se consegue criar várias colunas
        is_mobile = False
    except:
        is_mobile = True

    if not usuarios:
        st.info("Nenhum usuário cadastrado ainda.")
        return

    if is_mobile:
        # Layout mobile otimizado
        for user in usuarios:
            with st.expander(f"👤 {user[1]}", expanded=False):
                # Organiza as informações em colunas
                col1, col2 = st.columns(2)
                col1.write(f"**ID:** {user[0]}")
                col2.write(f"**Usuário:** {user[2]}")
                
                col1, col2 = st.columns(2)
                col1.write(f"**Número:** {user[4]}")
                col2.write(f"**Permissão:** {user[5]}")
                
                st.write(f"**Senha:** {'*' * len(str(user[3]))}")
                
                # Botões de ação
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button("✏️ Editar", key=f"edit_{user[0]}", use_container_width=True):
                    st.session_state.editar_usuario = user[0]
                    st.rerun()
                
                if btn_col2.button("🗑️ Excluir", key=f"delete_{user[0]}", use_container_width=True):
                    st.session_state.confirmarexclusao = user[0]
                    st.session_state.usuario_a_excluir = user[1]
                    st.rerun()
                
                # Confirmação de exclusão
                if ("confirmarexclusao" in st.session_state and 
                    st.session_state.confirmarexclusao == user[0]):
                    st.warning(f"Confirmar exclusão de {st.session_state.usuario_a_excluir}?")
                    
                    confirm_col1, confirm_col2 = st.columns(2)
                    if confirm_col1.button("✅ Sim", key=f"sim_{user[0]}", use_container_width=True):
                        excluirusuario(user[0])
                        del st.session_state.confirmarexclusao
                        st.rerun()
                    
                    if confirm_col2.button("❌ Não", key=f"nao_{user[0]}", use_container_width=True):
                        del st.session_state.confirmarexclusao
                        st.rerun()
    else:
        # Layout desktop - usando dataframe estilizado
        df_data = []
        for user in usuarios:
            df_data.append({
                "ID": user[0],
                "Nome/Empresa": user[1],
                "Usuário": user[2],
                "Senha": "••••••",
                "Número": user[4],
                "Permissão": user[5],
                "Editar": "✏️",
                "Excluir": "🗑️"
            })
        
        # Mostra a tabela
        for idx, user in enumerate(usuarios):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1,3,2,2,2,2,1,1])
            col1.write(user[0])
            col2.write(user[1])
            col3.write(user[2])
            col4.write("••••••")
            col5.write(user[4])
            col6.write(user[5])
            
            if col7.button("✏️", key=f"edit_{user[0]}"):
                st.session_state.editar_usuario = user[0]
                st.rerun()
            
            if col8.button("🗑️", key=f"delete_{user[0]}"):
                st.session_state.confirmarexclusao = user[0]
                st.session_state.usuario_a_excluir = user[1]
                st.rerun()
        
        # Diálogo de confirmação
        if "confirmarexclusao" in st.session_state:
            st.warning(f"Confirmar exclusão de {st.session_state.usuario_a_excluir}?")
            col1, col2 = st.columns(2)
            if col1.button("✅ Confirmar", use_container_width=True):
                excluirusuario(st.session_state.confirmarexclusao)
                del st.session_state.confirmarexclusao
                st.rerun()
            if col2.button("❌ Cancelar", use_container_width=True):
                del st.session_state.confirmarexclusao
                st.rerun()

def show_admin_page():
    # Verifica permissão antes de mostrar a página
    verificar_permissao()
    
    st.set_page_config(layout="wide", page_title="Admin", page_icon="👨‍💼")
    
    # Barra lateral
    with st.sidebar:
        if 'user_info' in st.session_state:
            st.subheader("Informações do Usuário")
            st.write(f"👤 Nome: {st.session_state.user_info['nome']}")
            st.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.page = None
            st.rerun()
    
    # Conteúdo principal
    st.title("📋 Gerenciamento de Usuários")

    # Barra de ações
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("➕ Adicionar Novo Usuário", use_container_width=True):
            st.session_state.novousuario = True
            st.rerun()
    with action_col2:
        if st.button("📊 Ir para Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    # Mensagens
    if "mensagem" in st.session_state:
        st.success(st.session_state.mensagem)
        del st.session_state.mensagem

    # Mostrar formulários quando necessário
    if "novousuario" in st.session_state and st.session_state.novousuario:
        formularionovousuario()

    listarusuarios()

    if "editar_usuario" in st.session_state and st.session_state.editar_usuario:
        usuario_editar = next(user for user in puxarusuarios() if user[0] == st.session_state.editar_usuario)
        formularioeditarusuario(usuario_editar)