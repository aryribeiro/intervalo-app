import streamlit as st
import time
import os
import base64

# Configuração da página
st.set_page_config(
    page_title="Intervalo Web App",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo personalizado
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #333333;
    }
    .clock-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
        background-color: #000000;
        border-radius: 15px;
        padding: 20px;
        max-width: 500px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .timer-display {
        font-family: 'Arial', sans-serif;
        font-size: 150px;
        font-weight: bold;
        color: #00ff00;
        text-align: center;
        margin: 20px 0;
        text-shadow: 0 0 10px rgba(0,255,0,0.7);
    }
    .alarm {
        font-family: 'Arial', sans-serif;
        font-size: 90px;
        font-weight: bold;
        color: #ff0000;
        text-align: center;
        margin: 20px 0;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0% {opacity: 1;}
        50% {opacity: 0;}
        100% {opacity: 1;}
    }
    .stButton > button {
        background-color: #00FF00;
        color: black;
        font-weight: bold;
        padding: 7px 14px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 20px;
        transition: all 0.3s;
        width: 70%;
        margin: 5px auto;
        display: block;
    }
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .stButton > button:active {
        background-color: #3e8e41;
        transform: translateY(2px);
    }
    .reset-button button {
        background-color: #f44336 !important;
    }
    .reset-button button:hover {
        background-color: #d32f2f !important;
    }
    .pause-button button {
        background-color: #ff9800 !important;
    }
    .pause-button button:hover {
        background-color: #f57c00 !important;
    }
    .start-button button {
        background-color: #2196F3 !important;
    }
    .start-button button:hover {
        background-color: #1976D2 !important;
    }
    /* Redução de espaço entre os botões */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        padding: 0px !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0px !important;
        padding: 0px !important;
    }
    .column-container {
        padding: 0 !important;
        margin: 0 !important;
    }
    .button-container {
        padding: 0 !important;
        margin: 0 !important;
    }
    button {
        transition: transform 0.1s;
    }
    button:active {
        transform: scale(0.95);
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar o som em base64
def get_sound_base64():
    """Retorna o arquivo de som codificado em base64"""
    sound_file = "som.mp3"
    try:
        with open(sound_file, "rb") as f:
            sound_bytes = f.read()
            encoded_sound = base64.b64encode(sound_bytes).decode("utf-8")
            return encoded_sound
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo de som: {e}")
        return None

# Inicializa o estado da sessão se não existir
if 'remaining_seconds' not in st.session_state:
    st.session_state.remaining_seconds = 1 * 60  # 1 minuto por padrão
    
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
    
if 'alarm_triggered' not in st.session_state:
    st.session_state.alarm_triggered = False
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

if 'sound_loaded' not in st.session_state:
    st.session_state.sound_loaded = False

# Título
st.markdown("<h1 style='text-align: center; color: black; padding-bottom: 10px;'>...⏱️ Intervalo Web App ⏱️...</h1>", unsafe_allow_html=True)

# Exibe o tempo restante formatado
mins, secs = divmod(st.session_state.remaining_seconds, 60)
timer_display = f"{int(mins):02d}:{int(secs):02d}"

# Carrega o som em base64 apenas uma vez e armazena na sessão
if not st.session_state.sound_loaded:
    sound_base64 = get_sound_base64()
    if sound_base64:
        st.session_state.sound_base64 = sound_base64
        st.session_state.sound_loaded = True

# Container do relógio com borda iluminada
if st.session_state.alarm_triggered:
    # Certifique-se de que o som base64 está disponível
    sound_data_uri = ""
    if st.session_state.sound_loaded:
        sound_data_uri = f"data:audio/mp3;base64,{st.session_state.sound_base64}"
    
    st.markdown(f"""
    <div class='clock-container' style='box-shadow: 0 0 20px #ff0000; border: 2px solid #ff0000;'>
        <div class='alarm'>{timer_display}</div>
    </div>
    <audio id="alarmSound" autoplay loop>
        <source src="{sound_data_uri}" type="audio/mpeg">
    </audio>
    <script>
        // Função para garantir que o áudio seja reproduzido
        function playAlarm() {{
            var audio = document.getElementById('alarmSound');
            if (audio) {{
                audio.volume = 1.0;
                
                // Função para tentar tocar o áudio com intervalo
                var playAttempt = function() {{
                    var playPromise = audio.play();
                    
                    if (playPromise !== undefined) {{
                        playPromise.then(_ => {{
                            console.log('Áudio tocando com sucesso');
                        }}).catch(error => {{
                            console.log('Erro ao tocar áudio:', error);
                            // Retenta após um curto período
                            setTimeout(playAttempt, 300);
                        }});
                    }}
                }};
                
                // Inicia a reprodução
                playAttempt();
                
                // Verificação contínua para garantir que o áudio continue tocando
                setInterval(function() {{
                    if (audio.paused) {{
                        console.log('Áudio pausado, reiniciando...');
                        playAttempt();
                    }}
                }}, 500);
            }}
        }}
        
        // Tenta reproduzir o som quando o documento estiver totalmente carregado
        document.addEventListener('DOMContentLoaded', function() {{
            playAlarm();
        }});
        
        // Também tenta reproduzir o som imediatamente
        playAlarm();
        
        // E como backup, tenta novamente após um curto intervalo
        setTimeout(playAlarm, 500);
    </script>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='clock-container'>
        <div class='timer-display'>{timer_display}</div>
    </div>
    """, unsafe_allow_html=True)

# Funções para os botões
def decrease_time():
    st.session_state.remaining_seconds = max(0, st.session_state.remaining_seconds - 300)
    st.session_state.alarm_triggered = False
    st.session_state.last_update = time.time()
    
def increase_time():
    st.session_state.remaining_seconds += 300
    st.session_state.alarm_triggered = False
    st.session_state.last_update = time.time()
    
def toggle_timer():
    if st.session_state.timer_active:
        st.session_state.timer_active = False
    else:
        st.session_state.timer_active = True
        st.session_state.last_update = time.time()
        st.session_state.alarm_triggered = False
        
def reset_timer():
    st.session_state.remaining_seconds = 5 * 60
    st.session_state.timer_active = False
    st.session_state.alarm_triggered = False
    st.session_state.last_update = time.time()

# Botões de controle em colunas - com espaço reduzido
st.markdown('<div style="display: flex; justify-content: center; padding: 0; margin: 0;">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown('<div class="button-container" style="padding: 0; margin: 0;">', unsafe_allow_html=True)
    if st.button("-5 min", key="decrease", on_click=decrease_time):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="button-container '+ ("pause-button" if st.session_state.timer_active else "start-button") + '" style="padding: 0; margin: 0;">', unsafe_allow_html=True)
    if st.button("Pausar" if st.session_state.timer_active else "Iniciar", key="toggle", on_click=toggle_timer):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="button-container" style="padding: 0; margin: 0;">', unsafe_allow_html=True)
    if st.button("+5 min", key="increase", on_click=increase_time):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Botão para resetar o timer
st.markdown('<div class="reset-button" style="padding: 0; max-width: 100px; margin: 5px auto;">', unsafe_allow_html=True)
if st.button("Resetar +5 Min", key="reset", on_click=reset_timer):
    pass
st.markdown('</div>', unsafe_allow_html=True)

# Atualização do cronômetro em tempo real
current_time = time.time()

if st.session_state.timer_active and not st.session_state.alarm_triggered:
    # Calcula o tempo decorrido desde a última atualização
    elapsed = current_time - st.session_state.last_update
    st.session_state.last_update = current_time
    
    # Atualiza o tempo restante
    st.session_state.remaining_seconds -= elapsed
    
    # Verifica se o cronômetro chegou a zero
    if st.session_state.remaining_seconds <= 0:
        st.session_state.remaining_seconds = 0
        st.session_state.timer_active = False
        st.session_state.alarm_triggered = True

# Rodapé com data e hora no formato brasileiro
from datetime import datetime
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass  # Se não conseguir definir o locale, usará o formato padrão

now = datetime.now()
dia_semana = now.strftime('%A').capitalize()
dia = now.strftime('%d')
mes = now.strftime('%B').capitalize()
ano = now.strftime('%Y')
hora = now.strftime('%H:%M:%S')

# Garantir que funcione mesmo sem locale português
dias_semana = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

meses = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

# Tratamento para garantir tradução correta independente do locale
if dia_semana in dias_semana:
    dia_semana = dias_semana[dia_semana]
if mes in meses:
    mes = meses[mes]

data_hora_formatada = f"{dia_semana}, {dia} de {mes} de {ano} - {hora}"

st.markdown(f"""
<div style="text-align: center; opacity: 1.0; margin-top: 50px;">
    <p>{data_hora_formatada}</p>
</div>
""", unsafe_allow_html=True)

# JavaScript para atualizar a página automaticamente
st.markdown("""
<script>
    // Função para atualizar a página
    function refreshPage() {
        // Recarrega a página para atualizar o temporizador
        setTimeout(function() {
            window.location.reload();
        }, 100);
    }
    
    // Inicia o processo de atualização com um pequeno atraso
    setTimeout(refreshPage, 200);
</script>
""", unsafe_allow_html=True)

# Força uma atualização mais rápida quando o timer estiver ativo
if st.session_state.timer_active or st.session_state.alarm_triggered:
    time.sleep(0.05)
    st.rerun()

# Estilo personalizado - Remoção de elementos da interface do Streamlit
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #333333;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    /* Esconde completamente todos os elementos da barra padrão do Streamlit */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}
    /* Remove qualquer espaço em branco adicional */
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove quaisquer margens extras */
    .element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Informações de contato
st.markdown("""
<hr>
<div style="text-align: center;">
    <h4>Intervalo Web App: cronômetro com alarme ⏰</h4>
    <p>Para intervalos ou Método Pomodoro 🍅 | Por Ary Ribeiro. Contato, através do email <a href="mailto:aryribeiro@gmail.com">aryribeiro@gmail.com</a></p>
</div>
""", unsafe_allow_html=True)