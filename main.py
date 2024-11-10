import streamlit as st
import pandas as pd
import pywhatkit
import time
from datetime import datetime
import io

st.set_page_config(page_title="WhatsApp Sender", page_icon="📱", layout="wide")

def download_template():
    """Cria um arquivo Excel template para download"""
    df = pd.DataFrame({
        'telefone': ['+5511999999999', '11999999999'],
        'mensagem': ['Exemplo de mensagem 1', 'Exemplo de mensagem 2']
    })
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def enviar_mensagens_whatsapp(df, progress_bar, status_text, config):
    """
    Envia mensagens do WhatsApp para contatos no DataFrame
    """
    total_mensagens = len(df)
    mensagens_enviadas = 0
    
    # Adicionando prints de diagnóstico
    st.write("Total de mensagens a enviar:", total_mensagens)
    st.write("Conteúdo do DataFrame:")
    st.write(df)
    
    for index, row in df.iterrows():
        telefone = str(row['telefone'])
        mensagem = str(row['mensagem'])
        
        # Print para debug
        st.write(f"Tentando enviar para: {telefone}")
        st.write(f"Mensagem: {mensagem}")
        
        # Remove caracteres especiais do telefone
        telefone = ''.join(filter(str.isdigit, telefone))
        
        # Adiciona prefixo conforme configuração
        if config['adicionar_prefixo'] and len(telefone) == 11:
            telefone = '+55' + telefone
            
        st.write(f"Número formatado: {telefone}")
        
        try:
            status_text.text(f"Enviando mensagem para {telefone}...")
            
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                wait_time=config['tempo_espera'],
                tab_close=config['fechar_aba']
            )
            
            mensagens_enviadas += 1
            progress_bar.progress(mensagens_enviadas / total_mensagens)
            status_text.text(f"✅ Mensagem enviada com sucesso para {telefone}")
            
            time.sleep(config['intervalo_mensagens'])  # Intervalo entre mensagens
            
        except Exception as e:
            st.write(f"Erro detalhado: {str(e)}")
            status_text.text(f"❌ Erro ao enviar mensagem para {telefone}: {str(e)}")
            time.sleep(5)
            continue
    
    return mensagens_enviadas

def main():
    st.title("📱 WhatsApp Sender")
    st.write("Envie mensagens em massa pelo WhatsApp de forma automatizada")
    
    # Configurações na sidebar
    st.sidebar.header("⚙️ Configurações")
    
    # Tempo de espera para carregar o WhatsApp
    tempo_espera = st.sidebar.number_input(
        "Tempo de espera para carregar WhatsApp (segundos)",
        min_value=5,
        max_value=30,
        value=10,
        help="Tempo de espera para o WhatsApp Web carregar antes de enviar a mensagem"
    )
    
    # Intervalo entre mensagens
    intervalo_mensagens = st.sidebar.number_input(
        "Intervalo entre mensagens (segundos)",
        min_value=10,
        max_value=120,
        value=30,
        help="Tempo de espera entre o envio de uma mensagem e outra"
    )
    
    # Opções avançadas em um expander
    with st.sidebar.expander("🔧 Opções Avançadas"):
        adicionar_prefixo = st.checkbox(
            "Adicionar prefixo +55",
            value=True,
            help="Adiciona automaticamente o prefixo +55 para números brasileiros"
        )
        
        fechar_aba = st.checkbox(
            "Fechar aba após envio",
            value=True,
            help="Fecha automaticamente a aba do navegador após enviar a mensagem"
        )
        
        mostrar_preview = st.checkbox(
            "Mostrar preview de mensagens",
            value=True,
            help="Mostra prévia das mensagens antes de enviar"
        )

    # Configurações agrupadas em um dicionário
    config = {
        'tempo_espera': tempo_espera,
        'intervalo_mensagens': intervalo_mensagens,
        'adicionar_prefixo': adicionar_prefixo,
        'fechar_aba': fechar_aba,
        'mostrar_preview': mostrar_preview
    }

    # Sidebar com instruções
    st.sidebar.header("Instruções")
    st.sidebar.write("""
    1. Faça download do template Excel
    2. Preencha com os números e mensagens
    3. Faça upload do arquivo preenchido
    4. Configure as opções desejadas
    5. Clique em 'Enviar Mensagens'
    """)
    
    st.sidebar.warning("""
    ⚠️ Atenção:
    - Mantenha o WhatsApp Web aberto
    - Evite enviar muitas mensagens seguidas
    - Na primeira vez, faça login no WhatsApp Web
    """)
    
    st.sidebar.header("Creditos", divider=True)
    st.sidebar.markdown("""
    💜 Gostou do projeto? Me pague um café!
    
    **PIX:** hugorogerio522@gmail.com""")
    
    # Download do template
    st.subheader("1. Baixe o Template")
    template_file = download_template()
    st.download_button(
        label="📥 Download Template Excel",
        data=template_file,
        file_name="template_whatsapp.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Upload do arquivo
    st.subheader("2. Faça Upload do Arquivo")
    uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Verifica as colunas
            if 'telefone' not in df.columns or 'mensagem' not in df.columns:
                st.error("❌ Erro: O arquivo deve conter as colunas 'telefone' e 'mensagem'")
                return
            
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Mostra preview dos dados se configurado
            if config['mostrar_preview']:
                st.subheader("Preview dos Dados")
                st.dataframe(df)
            
            # Botão de envio
            if st.button("📤 Enviar Mensagens"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner('Enviando mensagens...'):
                    mensagens_enviadas = enviar_mensagens_whatsapp(df, progress_bar, status_text, config)
                
                if mensagens_enviadas > 0:
                    st.success(f"✨ Processo concluído! {mensagens_enviadas} mensagens enviadas.")
                else:
                    st.error("❌ Nenhuma mensagem foi enviada com sucesso.")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {str(e)}")

if __name__ == "__main__":
    main()