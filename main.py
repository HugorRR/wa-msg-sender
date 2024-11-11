import streamlit as st
import pandas as pd
import time
from datetime import datetime
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.parse

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

def setup_driver():
    """Configura o driver do Chrome com as opções necessárias"""
    chrome_options = Options()
    # Add these options to help with common issues
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument('--disable-features=VizDisplay')
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--ignore-certificate-errors')
    return webdriver.Chrome(options=chrome_options)

def enviar_mensagem_whatsapp(driver, telefone, mensagem):
    """
    Envia uma mensagem do WhatsApp usando Selenium
    """
    # Formata o número de telefone
    telefone = ''.join(filter(str.isdigit, telefone))
    if len(telefone) == 11:
        telefone = '55' + telefone
    
    # Codifica a mensagem para URL
    mensagem_encoded = urllib.parse.quote(mensagem)
    
    # Cria o link do WhatsApp
    url = f'https://web.whatsapp.com/send?phone={telefone}&text={mensagem_encoded}'
    
    try:
        # Abre o WhatsApp Web
        driver.get(url)
        
        # Aguarda até que o campo de mensagem esteja presente (30 segundos de timeout)
        campo_mensagem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-placeholder="Digite uma mensagem"]'))
        )
        
        # Envia a mensagem
        campo_mensagem.send_keys(Keys.ENTER)
        
        # Aguarda um pouco para a mensagem ser enviada
        time.sleep(3)
        
        return True
    except Exception as e:
        st.error(f"Erro ao enviar mensagem: {str(e)}")
        return False

def enviar_mensagens_whatsapp(df, progress_bar, status_text, config):
    """
    Envia mensagens do WhatsApp para contatos no DataFrame usando Selenium
    """
    driver = setup_driver()
    total_mensagens = len(df)
    mensagens_enviadas = 0
    
    try:
        for index, row in df.iterrows():
            telefone = str(row['telefone'])
            mensagem = str(row['mensagem'])
            
            status_text.text(f"Enviando mensagem para {telefone}...")
            
            if enviar_mensagem_whatsapp(driver, telefone, mensagem):
                mensagens_enviadas += 1
                progress_bar.progress(mensagens_enviadas / total_mensagens)
                status_text.text(f"✅ Mensagem enviada com sucesso para {telefone}")
            else:
                status_text.text(f"❌ Erro ao enviar mensagem para {telefone}")
            
            time.sleep(config['intervalo_mensagens'])
    
    finally:
        driver.quit()
    
    return mensagens_enviadas

def main():
    st.title("📱 WhatsApp Sender")
    st.write("Envie mensagens em massa pelo WhatsApp de forma automatizada")
    
    # Configurações na sidebar
    st.sidebar.header("⚙️ Configurações")
    
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
        mostrar_preview = st.checkbox(
            "Mostrar preview de mensagens",
            value=True,
            help="Mostra prévia das mensagens antes de enviar"
        )

    # Configurações agrupadas em um dicionário
    config = {
        'intervalo_mensagens': intervalo_mensagens,
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
    - Você precisará escanear o QR Code do WhatsApp Web
    - Evite enviar muitas mensagens seguidas
    - Mantenha sua sessão do WhatsApp Web ativa
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
