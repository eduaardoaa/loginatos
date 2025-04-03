# main.py
import mysql.connector
import streamlit as st
from adm import show_admin_page
from dashboard import show_dashboard_page

def conexaobanco():
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

def validacao(usr, passw):
    conn = conexaobanco()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
    cursor.execute(query, (usr, passw))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        st.session_state.authenticated = True  
        st.session_state.user_info = {
            'id': user['id'],
            'nome': user['Nome/Empresa'],
            'permissao': user['permissao']
        }
        st.success('Login feito com sucesso!')

        if user['permissao'] == 'adm':
            st.session_state.page = "adm"
            st.rerun()
        elif user['permissao'] == 'cliente':
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error('Permissão desconhecida. Não foi possível redirecionar.')
    else:
        st.error('Usuário ou senha incorretos, tente novamente.')

def show_login_page():
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")
    
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logoatos.png", width=150)

    with st.form('sign_in'):
        st.caption('Por favor, insira seu usuário e senha.')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')

        botaoentrar = st.form_submit_button(label="Entrar", type="primary", use_container_width=True)

    if botaoentrar:
        validacao(username, password)

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        if "page" in st.session_state:
            if st.session_state.page == "adm":
                show_admin_page()
            elif st.session_state.page == "dashboard":
                show_dashboard_page()

if __name__ == "__main__":
    main()
