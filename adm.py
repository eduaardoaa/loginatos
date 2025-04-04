import mysql.connector
import streamlit as st

def verificar_permissao():
    if not st.session_state.get('authenticated', False):
        st.error("Você não está autenticado!")
        st.session_state.page = None
        st.rerun()
    
    if st.session_state.user_info.get('permissao') != 'adm':
        st.error("Acesso negado: Você não tem permissão para acessar essa pagina!")
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.page = None
        st.rerun()

def conectarbanco():
    try:
        conn = mysql.connector.connect(
            host="crossover.proxy.rlwy.net",
             port=17025,
             user="root",
             password="nwiMDSsxmcmDXWChimBQOIswEFlTUMms",
             database="railway"
         )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def puxarusuarios():
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, `NomeEmpresa`, usuario, senha, numero, permissao FROM usuarios ORDER BY id ASC")
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
            "UPDATE usuarios SET `NomeEmpresa` = %s, usuario = %s, senha = %s, numero = %s, permissao = %s WHERE id = %s",
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
            "INSERT INTO usuarios (`NomeEmpresa`, usuario, senha, numero, permissao) VALUES (%s, %s, %s, %s, %s)",
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
        nome_empresa = st.text_input("NomeEmpresa", max_chars=50)
        usuario = st.text_input("Usuário", max_chars=20)
        senha = st.text_input("Senha", type="password", max_chars=30)
        numero = st.text_input("Número", max_chars=15)
        permissao = st.radio("Permissão", ["adm", "cliente"], horizontal=True)

        submit_button = st.form_submit_button(label="Adicionar Usuário", use_container_width=True)

        if submit_button:
            if not all([nome_empresa, usuario, senha, numero]):
                st.error("Todos os campos são obrigatórios!")
            elif novousuario(nome_empresa, usuario, senha, numero, permissao):
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
        nome_empresa = st.text_input("NomeEmpresa", value=user[1], max_chars=50)
        usuario = st.text_input("Usuário", value=user[2], max_chars=20)
        senha = st.text_input("Senha", value=user[3], type="password", max_chars=30)
        numero = st.text_input("Número", value=user[4], max_chars=15)
        permissao = st.radio("Permissão", ["adm", "cliente"], 
                           index=0 if user[5] == "adm" else 1,
                           horizontal=True)
        
        submit_button = st.form_submit_button(label="Atualizar Usuário", use_container_width=True)

        if submit_button:
            if not all([nome_empresa, usuario, senha, numero]):
                st.error("Todos os campos são obrigatórios!")
            elif atualizacaousuarios(user[0], nome_empresa, usuario, senha, numero, permissao):
                st.session_state.mensagem = "Usuário atualizado com sucesso!"
                st.session_state.editar_usuario = None
                st.rerun()

def listarusuarios():
    usuarios = puxarusuarios()
    
    if not usuarios:
        st.info("Nenhum usuário cadastrado ainda.")
        return
    
    st.subheader("📋 Lista de Usuários")
    
    for user in usuarios:
        with st.container():
            st.markdown(f"### {user[1]}")
            
            col1, col2 = st.columns(2)
            col1.markdown(f"**ID:** `{user[0]}`")
            col2.markdown(f"**Usuário:** `{user[2]}`")
            
            col1, col2 = st.columns(2)
            col1.markdown(f"**Número:** `{user[4]}`")
            col2.markdown(f"**Permissão:** `{user[5]}`")
            
            btn_col1, btn_col2 = st.columns(2)
            
            if btn_col1.button("✏️ Editar", key=f"edit_{user[0]}", use_container_width=True):
                st.session_state.editar_usuario = user[0]
                st.rerun()
            
            if btn_col2.button("🗑️ Excluir", key=f"delete_{user[0]}", use_container_width=True):
                st.session_state.confirmarexclusao = user[0]
                st.session_state.usuario_a_excluir = user[1]
                st.rerun()
            
            if st.session_state.get('editar_usuario') == user[0]:
                formularioeditarusuario(user) 
            
            if ("confirmarexclusao" in st.session_state and 
                st.session_state.confirmarexclusao == user[0]):
                st.warning(f"Confirmar exclusão de {st.session_state.usuario_a_excluir}?")
                
                confirm_col1, confirm_col2 = st.columns(2)
                if confirm_col1.button("✅ Confirmar", key=f"sim_{user[0]}", use_container_width=True):
                    excluirusuario(user[0])
                    del st.session_state.confirmarexclusao
                    st.rerun()
                
                if confirm_col2.button("❌ Cancelar", key=f"nao_{user[0]}", use_container_width=True):
                    del st.session_state.confirmarexclusao
                    st.rerun()
            
            st.divider()

def paginaadm():
    verificar_permissao()
    
    st.set_page_config(layout="wide", page_title="Admin - Gerenciamento de Usuários", page_icon="👨‍💼")
    
    # Barra lateral
    with st.sidebar:
        st.subheader("👤 Painel Administrativo")
        
        if 'user_info' in st.session_state:
            st.markdown(f"""
            **Nome:** {st.session_state.user_info['nome']}  
            **Permissão:** `{st.session_state.user_info['permissao']}`
            """)
        
        st.divider()
        
        if st.button("🚪 Sair", use_container_width=True, type="primary", help="Encerrar sessão"):
            st.session_state.authenticated = False
            st.session_state.page = None
            st.rerun()
    
    st.title("👨🏽‍💼 Gerenciamento de Usuários")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ Adicionar Novo Usuário", use_container_width=True, 
                        help="Cadastrar novo usuário no sistema"):
                st.session_state.novousuario = True
                st.rerun()
        with col2:
            if st.button("📊 Ir para Dashboard", use_container_width=True, 
                        help="Voltar ao painel principal"):
                st.session_state.page = "dashboard"
                st.rerun()
    
    if "mensagem" in st.session_state:
        st.success(st.session_state.mensagem)
        del st.session_state.mensagem
    
    if st.session_state.get("novousuario", False):
        formularionovousuario()
    
    listarusuarios()

if __name__ == "__main__":
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {'nome': 'Admin Teste', 'permissao': 'adm'}
    if 'page' not in st.session_state:
        st.session_state.page = None
    
    st.session_state.authenticated = True
    paginaadm()
