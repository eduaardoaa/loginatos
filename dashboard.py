import streamlit as st
import pandas as pd
import plotly.express as px

def verificar_autenticacao():
    """Verifica se o usuário está autenticado (fez login)"""
    if not st.session_state.get('authenticated', False):
        st.error("Você precisa fazer login para acessar esta página!")
        st.session_state.page = None
        st.rerun()

def dashboardcliente():
    verificar_autenticacao()
    
    # Configuração da agina
    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
    
    # Barra lateral
    if 'user_info' in st.session_state:
        st.sidebar.subheader("Informações do Usuário")
        st.sidebar.write(f"👤 Nome: {st.session_state.user_info['nome']}")
        st.sidebar.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
    
    # Botão sair da conta
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()
    
    # Nome Principal Pagina
    st.title("📊 DASHBOARD")
    
    # Mensagem boas vindas com nome cadastrado na conta (TEMPORARIO)
    if 'user_info' in st.session_state:
        st.write(f"Bem-vindo, {st.session_state.user_info['nome']}!")
