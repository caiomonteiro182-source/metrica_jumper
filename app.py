import datetime
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
fav_icon = "logoj.png" if os.path.exists("logoj.png") else "📚"
st.set_page_config(
    page_title="Gestão de Presença | JUMPER",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS PERSONALIZADA
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #090D12 0%, #111822 50%, #1A2433 100%);
        color: #F8FAFC;
    }
    
    div[data-testid="stSegmentedControl"] {
        display: flex !important;
        justify-content: center !important;
        margin: 0 auto 20px auto !important;
        max-width: 550px !important;
        background: rgba(22, 30, 41, 0.8) !important;
        padding: 4px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(162, 209, 54, 0.2) !important;
    }
    
    div[data-testid="stSegmentedControl"] button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        color: #CBD5E1 !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {
        background-color: #A2D136 !important;
        color: #0B0F14 !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 10px rgba(162, 209, 54, 0.3) !important;
    }

    div[data-baseweb="select"] > div, div[data-baseweb="input"] input {
        background-color: #151D28 !important;
        border: 1.5px solid #2A3648 !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    div[data-baseweb="select"]:hover > div, div[data-baseweb="input"]:hover input {
        border-color: #A2D136 !important;
    }
    
    label {
        color: #A2D136 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A2D136 0%, #8EC328 100%) !important;
        color: #0B0F14 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem 1.8rem !important;
        font-size: 16px !important;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 4px 20px rgba(162, 209, 54, 0.35);
        width: 100%;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #B2E246 0%, #9ED432 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(162, 209, 54, 0.5);
    }
    
    [data-testid="stMetric"] {
        background: rgba(22, 30, 41, 0.8);
        border: 1px solid rgba(162, 209, 54, 0.2);
        padding: 18px 22px;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    
    [data-testid="stMetricValue"] {
        color: #A2D136 !important;
        font-weight: 800 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# DADOS COMPLETOS EXTRAÍDOS DOS ARQUIVOS DE AGOSTO
# ---------------------------------------------------------
DADOS_AGOSTO_COMPLETO = [
    # Centro
    ('Centro', 'ALINE', 'CABELEIREIRO', 'QUINTA 19:00 - 21:00', '2026-08-06', 7, 6),
    ('Centro', 'ALINE', 'CABELEIREIRO', 'QUINTA 19:00 - 21:00', '2026-08-13', 7, 5),
    ('Centro', 'ALINE', 'CABELEIREIRO', 'QUINTA 19:00 - 21:00', '2026-08-20', 4, 2),
    ('Centro', 'CAIO', 'INFORMÁTICA', 'SÁBADO 08:30 ÀS 10:30', '2026-08-15', 75, 9),
    ('Centro', 'SAMUEL', 'ROBÓTICA KIDS', 'SÁBADO 08:30', '2026-08-01', 8, 7),
    ('Centro', 'SAMUEL', 'ROBÓTICA KIDS', 'SÁBADO 08:30', '2026-08-08', 8, 7),
    ('Centro', 'SAMUEL', 'ROBÓTICA KIDS', 'SÁBADO 08:30', '2026-08-15', 8, 8),
    ('Centro', 'JULIA', 'INGLÊS KIDS', 'SÁBADO 10:30 AS 12:30', '2026-08-01', 8, 7),
    ('Centro', 'JULIA', 'INGLÊS KIDS', 'SÁBADO 10:30 AS 12:30', '2026-08-08', 8, 7),
    ('Centro', 'JULIA', 'INGLÊS KIDS', 'SÁBADO 10:30 AS 12:30', '2026-08-15', 8, 8),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-04', 10, 9),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-11', 9, 6),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-18', 8, 8),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-04', 7, 4),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-11', 7, 6),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'TERÇA-FEIRA 14:00 ÀS 16:00', '2026-08-18', 7, 5),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'QUARTA-FEIRA 14:00 ÀS 16:00', '2026-08-05', 9, 9),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'QUARTA-FEIRA 14:00 ÀS 16:00', '2026-08-12', 9, 8),
    ('Centro', 'JURANDIR', 'INFORMÁTICA', 'QUARTA-FEIRA 14:00 ÀS 16:00', '2026-08-19', 10, 10),
    ('Centro', 'KELLY', 'MANICURE', 'SÁBADO 08:30 - 10:30', '2026-08-01', 8, 8),
    ('Centro', 'KELLY', 'MANICURE', 'SÁBADO 08:30 - 10:30', '2026-08-08', 9, 9),
    ('Centro', 'KELLY', 'MANICURE', 'SÁBADO 08:30 - 10:30', '2026-08-15', 8, 6),
    ('Centro', 'KELLY', 'MANICURE', 'SÁBADO 08:30 - 10:30', '2026-08-15', 11, 9),
    ('Centro', 'KELLY', 'MANICURE', 'SÁBADO 10:30 - 12:30', '2026-08-15', 64, 11),
    ('Centro', 'MENUHA', 'INGLÊS KIDS', 'SÁBADO 10:30', '2026-08-02', 10, 8),
    ('Centro', 'MENUHA', 'INGLÊS KIDS', 'SÁBADO 10:30', '2026-08-09', 4, 1),
    ('Centro', 'MENUHA', 'INGLÊS KIDS', 'SÁBADO 10:30', '2026-08-16', 4, 4),
    ('Centro', 'MENUHA', 'INGLÊS KIDS', 'SÁBADO 10:30', '2026-08-23', 3, 1),
    ('Centro', 'MENUHA', 'INGLÊS KIDS', 'SÁBADO 10:30', '2026-08-30', 3, 2),
    ('Centro', 'NAYANE', 'INGLÊS', 'QUARTA FEIRA 09:00-11:00', '2026-08-12', 4, 3),
    ('Centro', 'NAYANE', 'INGLÊS', 'QUARTA FEIRA 09:00-11:00', '2026-08-19', 4, 4),
    ('Centro', 'NAYANE', 'INGLÊS', 'QUARTA FEIRA 09:00-11:00', '2026-08-05', 10, 9),
    ('Centro', 'NAYANE', 'INGLÊS', 'QUARTA FEIRA 09:00-11:00', '2026-08-12', 11, 11),
    ('Centro', 'NAYANE', 'INGLÊS', 'QUARTA FEIRA 09:00-11:00', '2026-08-19', 11, 10),
    ('Centro', 'NAYANE', 'INGLÊS', 'SÁBADO 13:00-15:00', '2026-08-15', 68, 6),
    ('Centro', 'DAVI', 'BARBEIRO', 'SEGUNDA 19:00 - 21:00', '2026-08-03', 7, 7),
    ('Centro', 'DAVI', 'BARBEIRO', 'SEGUNDA 19:00 - 21:00', '2026-08-10', 7, 5),
    ('Centro', 'DAVI', 'BARBEIRO', 'SEGUNDA 19:00 - 21:00', '2026-08-17', 7, 6),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 08:30 - 10:30', '2026-08-01', 25, 22),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 08:30 - 10:30', '2026-08-15', 23, 20),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 08:30 - 10:30', '2026-08-05', 5, 5),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 08:30 - 10:30', '2026-08-12', 6, 6),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 08:30 - 10:30', '2026-08-19', 6, 6),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 10:30 - 12:30', '2026-08-01', 22, 19),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 10:30 - 12:30', '2026-08-08', 16, 13),
    ('Centro', 'TULIO', 'INGLÊS', 'SÁBADO 10:30 - 12:30', '2026-08-15', 20, 17),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'SÁBADO 10:30', '2026-08-01', 6, 6),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'SÁBADO 10:30', '2026-08-08', 16, 15),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'SÁBADO 10:30', '2026-08-15', 18, 14),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'QUINTA-FEIRA  9:00', '2026-08-06', 12, 9),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'QUINTA-FEIRA  9:00', '2026-08-13', 12, 9),
    ('Centro', 'VINICIUS', 'EMPREENDEDORISMO', 'QUINTA-FEIRA  9:00', '2026-08-20', 10, 10),

    # Norte (Saul)
    ('Norte (Saul)', 'ALINE', 'CABELEREIRO', 'SEGUNDA-FEIRA 14:00 - 16:00', '2026-08-03', 9, 7),
    ('Norte (Saul)', 'ALINE', 'CABELEREIRO', 'SEGUNDA-FEIRA 14:00 - 16:00', '2026-08-10', 9, 8),
    ('Norte (Saul)', 'ALINE', 'CABELEREIRO', 'SEGUNDA-FEIRA 14:00 - 16:00', '2026-08-17', 9, 7),
    ('Norte (Saul)', 'ALINE', 'CABELEREIRO', 'SEGUNDA-FEIRA 19:00 - 21:00', '2026-08-17', 60, 7),
    ('Norte (Saul)', 'SAMUEL', 'INFORMÁTICA', 'TERÇA-FEIRA 19:00-21:00', '2026-08-11', 7, 6),
    ('Norte (Saul)', 'SAMUEL', 'INFORMÁTICA', 'TERÇA-FEIRA 19:00-21:00', '2026-08-18', 6, 6),
    ('Norte (Saul)', 'BRUNO', 'MAQUIAGEM', 'QUARTA-FEIRA  19:00 -21:00', '2026-08-19', 21, 7),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-03', 9, 8),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-10', 9, 8),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-17', 9, 8),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-06', 8, 6),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-13', 9, 6),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'SEGUNDA-FEIRA 16:00-18:00', '2026-08-20', 9, 5),
    ('Norte (Saul)', 'JURANDIR', 'JURANDIR', 'QUINTA- FEIRA 14:00 -16:00', '2026-08-20', 83, 9),
    ('Norte (Saul)', 'CAIO', 'INFORMÁTICA', 'QUARTA-FEIRA 19:00-21:00', '2026-08-05', 13, 11),
    ('Norte (Saul)', 'CAIO', 'INFORMÁTICA', 'QUARTA-FEIRA 19:00-21:00', '2026-08-12', 13, 10),
    ('Norte (Saul)', 'CAIO', 'INFORMÁTICA', 'QUARTA-FEIRA 19:00-21:00', '2026-08-19', 13, 12),
    ('Norte (Saul)', 'LEONARDO', 'INFORMÁTICA', 'SÁBADO 08:30-10:30', '2026-08-01', 13, 13),
    ('Norte (Saul)', 'LEONARDO', 'INFORMÁTICA', 'SÁBADO 08:30-10:30', '2026-08-08', 13, 6),
    ('Norte (Saul)', 'LEONARDO', 'INFORMÁTICA', 'SÁBADO 08:30-10:30', '2026-08-15', 13, 12),
    ('Norte (Saul)', 'LEONARDO', 'INFORMÁTICA', 'SÁBADO 08:30-10:30', '2026-08-22', 13, 11),
    ('Norte (Saul)', 'LEONARDO', 'INFORMÁTICA', 'SÁBADO 10:30-12:30', '2026-08-15', 85, 10),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-01', 9, 7),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-08', 8, 4),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-15', 8, 8),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-01', 9, 6),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-08', 9, 7),
    ('Norte (Saul)', 'GABRIEL', 'INGLÊS KIDS', 'SÁBADO 08:30 - 10:30 TURMA 1', '2026-08-15', 9, 9),
    ('Norte (Saul)', 'MENUHA', 'INGLÊS KIDS', 'SEGUNDA-FEIRA 19:00 -21:00', '2026-08-03', 8, 7),
    ('Norte (Saul)', 'MENUHA', 'INGLÊS KIDS', 'SEGUNDA-FEIRA 19:00 -21:00', '2026-08-10', 8, 4),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'SEGUNDA-FEIRA 19:00-21:00', '2026-08-03', 11, 9),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'SEGUNDA-FEIRA 19:00-21:00', '2026-08-10', 10, 7),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'SEGUNDA-FEIRA 19:00-21:00', '2026-08-17', 12, 10),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'SEGUNDA-FEIRA 19:00-21:00', '2026-08-14', 9, 7),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'SEGUNDA-FEIRA 19:00-21:00', '2026-08-21', 9, 6),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'TERÇA-FEIRA 19:00 - 21:00 - ALONGAMENTO', '2026-08-04', 8, 8),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'TERÇA-FEIRA 19:00 - 21:00 - ALONGAMENTO', '2026-08-11', 6, 5),
    ('Norte (Saul)', 'KELLY', 'MANICURE', 'TERÇA-FEIRA 19:00 - 21:00 - ALONGAMENTO', '2026-08-18', 7, 7),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-04', 15, 13),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-11', 15, 14),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-18', 15, 13),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-01', 21, 21),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-08', 21, 15),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 14:00 - 16:00', '2026-08-15', 22, 16),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 19:00-21:00', '2026-08-04', 15, 13),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 19:00-21:00', '2026-08-11', 15, 13),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 19:00-21:00', '2026-08-18', 14, 13),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 19:00-21:00', '2026-08-01', 14, 14),
    ('Norte (Saul)', 'NAYANE', 'INGLÊS', 'TERÇA-FEIRA 19:00-21:00', '2026-08-15', 14, 13),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'TERÇA-FEIRA 19:00 - 21:00', '2026-08-11', 11, 7),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'TERÇA-FEIRA 19:00 - 21:00', '2026-08-18', 10, 9),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'TERÇA-FEIRA 19:00 - 21:00', '2026-08-06', 12, 6),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'TERÇA-FEIRA 19:00 - 21:00', '2026-08-13', 10, 8),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'TERÇA-FEIRA 19:00 - 21:00', '2026-08-20', 9, 7),
    ('Norte (Saul)', 'FULVIO', 'MECÂNICA', 'SÁBADO 13:30 ÀS 15:30', '2026-08-15', 92, 12),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-06', 12, 5),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-13', 12, 10),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-20', 11, 7),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-01', 12, 9),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-08', 12, 9),
    ('Norte (Saul)', 'VICTÓRIA', 'ROBÓTICA', 'QUINTA-FEIRA 19:00-21:00', '2026-08-15', 12, 9),
]

# ---------------------------------------------------------
# 1. BANCO DE DADOS EM CACHE COM CARGA DOS DADOS COMPLETOS
# ---------------------------------------------------------
@st.cache_resource
def iniciar_banco_de_dados():
    conn = sqlite3.connect("jumper_presenca.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(turmas)")
    colunas_turmas = [row[1] for row in cursor.fetchall()]

    if colunas_turmas and "unidade" not in colunas_turmas:
        cursor.execute("DROP TABLE IF EXISTS turmas")
        cursor.execute("DROP TABLE IF EXISTS presencas")
        conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turmas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unidade TEXT NOT NULL,
        professor TEXT NOT NULL,
        nome_turma TEXT NOT NULL,
        horario TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presencas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turma_id INTEGER NOT NULL,
        data_aula DATE NOT NULL,
        qtd_alunos INTEGER NOT NULL,
        qtd_presentes INTEGER NOT NULL,
        FOREIGN KEY(turma_id) REFERENCES turmas(id)
    )
    """)
    conn.commit()

    # Recarrega se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM turmas")
    if cursor.fetchone()[0] == 0:
        turmas_unicas = set((item[0], item[1], item[2], item[3]) for item in DADOS_AGOSTO_COMPLETO)
        for unidade, prof, nome_turma, horario in turmas_unicas:
            cursor.execute(
                "INSERT INTO turmas (unidade, professor, nome_turma, horario) VALUES (?, ?, ?, ?)",
                (unidade, prof, nome_turma, horario)
            )
        conn.commit()
        
        for unidade, prof, nome_turma, horario, data_aula, qtd_alunos, qtd_presentes in DADOS_AGOSTO_COMPLETO:
            cursor.execute(
                "SELECT id FROM turmas WHERE unidade = ? AND professor = ? AND nome_turma = ? AND horario = ?",
                (unidade, prof, nome_turma, horario)
            )
            res = cursor.fetchone()
            if res:
                t_id = res[0]
                cursor.execute(
                    "INSERT INTO presencas (turma_id, data_aula, qtd_alunos, qtd_presentes) VALUES (?, ?, ?, ?)",
                    (t_id, data_aula, qtd_alunos, qtd_presentes)
                )
        conn.commit()
        
    return conn

CONN = iniciar_banco_de_dados()
CURSOR = CONN.cursor()

def resetar_turmas_base():
    CURSOR.execute("DELETE FROM presencas")
    CURSOR.execute("DELETE FROM turmas")
    turmas_unicas = set((item[0], item[1], item[2], item[3]) for item in DADOS_AGOSTO_COMPLETO)
    for unidade, prof, nome_turma, horario in turmas_unicas:
        CURSOR.execute(
            "INSERT INTO turmas (unidade, professor, nome_turma, horario) VALUES (?, ?, ?, ?)",
            (unidade, prof, nome_turma, horario)
        )
    CONN.commit()
    for unidade, prof, nome_turma, horario, data_aula, qtd_alunos, qtd_presentes in DADOS_AGOSTO_COMPLETO:
        CURSOR.execute(
            "SELECT id FROM turmas WHERE unidade = ? AND professor = ? AND nome_turma = ? AND horario = ?",
            (unidade, prof, nome_turma, horario)
        )
        res = CURSOR.fetchone()
        if res:
            t_id = res[0]
            CURSOR.execute(
                "INSERT INTO presencas (turma_id, data_aula, qtd_alunos, qtd_presentes) VALUES (?, ?, ?, ?)",
                (t_id, data_aula, qtd_alunos, qtd_presentes)
            )
    CONN.commit()

# ---------------------------------------------------------
# CABEÇALHO CENTRALIZADO
# ---------------------------------------------------------
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown(
            "<h1 style='text-align: center; color:#A2D136; font-weight:800; margin:0;'>JUMPER!</h1>",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# NAVEGAÇÃO AGRUPADA POR BOTÕES
# ---------------------------------------------------------
opcoes_menu = ["📝 Lançamento", "🗑️ Corrigir", "📊 Dashboard", "⚙️ Gerenciar"]
aba_ativa = st.segmented_control("", opcoes_menu, default="📝 Lançamento", label_visibility="collapsed")
st.markdown("---")

# ---------------------------------------------------------
# SELEÇÃO DA UNIDADE (CENTRO / NORTE)
# ---------------------------------------------------------
col_unid1, col_unid2 = st.columns([1, 2])
with col_unid1:
    unidade_selecionada = st.selectbox("🏢 SELECIONE A UNIDADE", ["Centro", "Norte (Saul)"])
st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MÓDULO 1: LANÇAMENTO DE PRESENÇA
# ---------------------------------------------------------
if aba_ativa == "📝 Lançamento":
    df_profs = pd.read_sql_query(
        "SELECT DISTINCT professor FROM turmas WHERE unidade = ? ORDER BY professor",
        CONN, params=(unidade_selecionada,),
    )
    professores = df_profs["professor"].tolist()

    if not professores:
        st.warning(f"Nenhum professor cadastrado para a Unidade {unidade_selecionada}.")
    else:
        prof_selecionado = st.selectbox("👤 Selecione o Professor", professores)

        df_turmas_prof = pd.read_sql_query(
            """
            SELECT MIN(id) as id, nome_turma || ' - ' || horario AS descricao 
            FROM turmas 
            WHERE unidade = ? AND professor = ?
            GROUP BY nome_turma, horario
            ORDER BY id
            """,
            CONN, params=(unidade_selecionada, prof_selecionado),
        )

        if df_turmas_prof.empty:
            st.info("Nenhuma turma encontrada para este professor.")
        else:
            opcoes_turmas = dict(zip(df_turmas_prof["descricao"], df_turmas_prof["id"]))
            turma_desc = st.selectbox("📚 Selecione a Turma", list(opcoes_turmas.keys()))
            turma_id = opcoes_turmas[turma_desc]

            data_aula = st.date_input("📅 Data da Aula", value=datetime.date.today(), format="DD/MM/YYYY")

            col1, col2 = st.columns(2)
            with col1:
                total_alunos = st.number_input("👥 Total de Alunos da Turma", min_value=1, value=20, step=1)
            with col2:
                total_presentes = st.number_input("✅ Quantidade de Presentes", min_value=0, max_value=int(total_alunos), value=min(16, int(total_alunos)), step=1)

            if total_presentes > total_alunos:
                st.error(f"❌ Erro: O número de presentes ({total_presentes}) não pode ser maior do que o total de alunos na turma ({total_alunos}).")
            else:
                porcentagem_presenca = (total_presentes / total_alunos) * 100 if total_alunos > 0 else 0
                cor_texto, bg_box, border_color = ("#FF4B4B", "rgba(255, 75, 75, 0.15)", "#FF4B4B") if porcentagem_presenca < 80.0 else ("#A2D136", "rgba(162, 209, 54, 0.15)", "#A2D136")

                st.markdown(
                    f"""
                    <div style="background-color: {bg_box}; border-left: 5px solid {border_color}; padding: 16px 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 25px;">
                        <span style="font-size: 18px; font-weight: 700; color: {cor_texto};">📊 Resumo: Frequência: {porcentagem_presenca:.1f}%</span>
                        <span style="font-size: 15px; color: #CBD5E1; margin-left: 10px;">(Total da turma: {total_alunos} alunos)</span>
                    </div>
                    """, unsafe_allow_html=True
                )

                if st.button("💾 Salvar Chamada", type="primary"):
                    CURSOR.execute(
                        "INSERT INTO presencas (turma_id, data_aula, qtd_alunos, qtd_presentes) VALUES (?, ?, ?, ?)",
                        (turma_id, data_aula.strftime("%Y-%m-%d"), total_alunos, total_presentes),
                    )
                    CONN.commit()
                    st.success("✅ Chamada salva com sucesso!")

# ---------------------------------------------------------
# MÓDULO 2: EXCLUIR / CORRIGIR CHAMADA
# ---------------------------------------------------------
elif aba_ativa == "🗑️ Corrigir":
    st.subheader(f"🗑️ Gerenciar Chamadas - Unidade {unidade_selecionada}")

    query_ultimos = """
        SELECT p.id, strftime('%d/%m/%Y', p.data_aula) as Data, t.professor as Professor, t.nome_turma as Turma, 
               p.qtd_alunos as "Alunos Esperados", p.qtd_presentes as Presentes, (p.qtd_alunos - p.qtd_presentes) as Faltas
        FROM presencas p JOIN turmas t ON p.turma_id = t.id
        WHERE t.unidade = ? ORDER BY p.id DESC LIMIT 50
    """
    df_chamadas = pd.read_sql_query(query_ultimos, CONN, params=(unidade_selecionada,))

    if df_chamadas.empty:
        st.info("Nenhuma chamada registrada no histórico para esta unidade para exclusão.")
    else:
        st.dataframe(df_chamadas, use_container_width=True, hide_index=True)
        st.markdown("---")
        st.subheader("Apagar Lançamento Incorreto")

        opcoes_deletar = {f"ID: {row['id']} | Data: {row['Data']} | Prof: {row['Professor']} - {row['Turma']} ({row['Presentes']}/{row['Alunos Esperados']} presentes)": row["id"] for idx, row in df_chamadas.iterrows()}
        chamada_selecionada = st.selectbox("Selecione a chamada que deseja APAGAR:", list(opcoes_deletar.keys()))
        id_para_deletar = opcoes_deletar[chamada_selecionada]

        if st.button("❌ Confirmar Exclusão da Chamada", type="primary"):
            CURSOR.execute("DELETE FROM presencas WHERE id = ?", (id_para_deletar,))
            CONN.commit()
            st.success("✅ Chamada apagada com sucesso!")
            st.rerun()

# ---------------------------------------------------------
# MÓDULO 3: DASHBOARD DA GESTÃO (Com formato de mês MM/AAAA)
# ---------------------------------------------------------
elif aba_ativa == "📊 Dashboard":
    query = """
        SELECT p.id, t.professor, t.nome_turma, strftime('%d/%m/%Y', p.data_aula) as data_aula_br, p.data_aula, 
               p.qtd_alunos, p.qtd_presentes, (p.qtd_alunos - p.qtd_presentes) as qtd_faltas, 
               strftime('%m/%Y', p.data_aula) as mes_ano
        FROM presencas p JOIN turmas t ON p.turma_id = t.id
        WHERE t.unidade = ? ORDER BY p.data_aula DESC
    """
    df_dados = pd.read_sql_query(query, CONN, params=(unidade_selecionada,))

    if df_dados.empty:
        st.info(f"Nenhum lançamento registrado até o momento para a Unidade {unidade_selecionada}.")
    else:
        meses_disponiveis = sorted(df_dados["mes_ano"].unique(), reverse=True)
        mes_selecionado = st.selectbox("Filtrar por Mês/Ano", meses_disponiveis)

        df_mes = df_dados[df_dados["mes_ano"] == mes_selecionado].copy()
        total_aulas = len(df_mes)
        total_alunos_acum = df_mes["qtd_alunos"].sum()
        total_presentes_acum = df_mes["qtd_presentes"].sum()
        total_faltas_acum = df_mes["qtd_faltas"].sum()
        freq_media_geral = (total_presentes_acum / total_alunos_acum * 100) if total_alunos_acum > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Frequência Média ({unidade_selecionada})", f"{freq_media_geral:.1f}%")
        c2.metric("Aulas Ministradas", total_aulas)
        c3.metric("Total Alunos Esperados", total_alunos_acum)
        c4.metric("Total Faltas no Mês", total_faltas_acum)

        st.markdown("<br>", unsafe_allow_html=True)

        df_prof = df_mes.groupby("professor").agg(total_esperado=("qtd_alunos", "sum"), total_presencas=("qtd_presentes", "sum"), aulas=("id", "count")).reset_index()
        df_prof["Frequencia_%"] = round((df_prof["total_presencas"] / df_prof["total_esperado"]) * 100, 1)

        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig = px.bar(df_prof, x="professor", y="Frequencia_%", text="Frequencia_%", title=f"Taxa de Frequência - {unidade_selecionada} ({mes_selecionado})", color_discrete_sequence=["#A2D136"])
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_color="#A2D136")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F1F5F9", yaxis_range=[0, 105], margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.subheader("Resumo por Professor")
            st.dataframe(df_prof[["professor", "aulas", "Frequencia_%"]].rename(columns={"professor": "Prof.", "aulas": "Aulas"}), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📋 Registros Detalhados do Mês")
        st.dataframe(df_mes[["id", "data_aula_br", "professor", "nome_turma", "qtd_alunos", "qtd_presentes", "qtd_faltas"]].rename(columns={"data_aula_br": "Data da Aula"}), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# MÓDULO 4: GERENCIAR TURMAS
# ---------------------------------------------------------
elif aba_ativa == "⚙️ Gerenciar":
    st.subheader(f"⚙️ Cadastro e Gestão de Turmas - Unidade {unidade_selecionada}")

    with st.expander(f"➕ Cadastrar Nova Turma na Unidade {unidade_selecionada}"):
        with st.form("form_nova_turma", clear_on_submit=True):
            novo_prof = st.text_input("Nome do Professor").strip().upper()
            nome_turma = st.text_input("Nome/Curso da Turma (Ex: INFORMÁTICA)")
            horario = st.text_input("Dia e Horário (Ex: SÁBADO 08:30 - 10:30)")
            btn_cadastrar = st.form_submit_button("Cadastrar Turma", type="primary")

            if btn_cadastrar:
                if novo_prof and nome_turma and horario:
                    CURSOR.execute("INSERT INTO turmas (unidade, professor, nome_turma, horario) VALUES (?, ?, ?, ?)", (unidade_selecionada, novo_prof, nome_turma, horario))
                    CONN.commit()
                    st.success(f"Nova turma cadastrada na Unidade {unidade_selecionada} para o professor {novo_prof}!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"Turmas Cadastradas - Unidade {unidade_selecionada}")
    df_todas_turmas = pd.read_sql_query("SELECT id, unidade, professor, nome_turma, horario FROM turmas WHERE unidade = ? ORDER BY professor, id", CONN, params=(unidade_selecionada,))

    if df_todas_turmas.empty:
        st.info(f"Nenhuma turma cadastrada para a Unidade {unidade_selecionada}.")
    else:
        st.dataframe(df_todas_turmas, use_container_width=True, hide_index=True)
        st.markdown("---")
        col_ed1, col_ed2 = st.columns(2)

        with col_ed1:
            with st.expander("✏️ Alterar Professor da Turma"):
                dict_turmas_edit = {f"ID {row['id']} | {row['professor']} - {row['nome_turma']} ({row['horario']})": (row["id"], row["professor"]) for idx, row in df_todas_turmas.iterrows()}
                turma_para_editar = st.selectbox("Selecione a turma:", list(dict_turmas_edit.keys()), key="select_edit_prof")
                id_turma_edit, prof_atual = dict_turmas_edit[turma_para_editar]
                novo_prof_nome = st.text_input("Novo Nome do Professor", value=prof_atual).strip().upper()

                if st.button("💾 Salvar Alteração", type="primary"):
                    if novo_prof_nome:
                        CURSOR.execute("UPDATE turmas SET professor = ? WHERE id = ?", (novo_prof_nome, id_turma_edit))
                        CONN.commit()
                        st.success("✅ Professor alterado!")
                        st.rerun()

        with col_ed2:
            with st.expander("🗑️ Excluir Turma Cadastrada"):
                dict_turmas_del = {f"ID {row['id']} | {row['professor']} - {row['nome_turma']} ({row['horario']})": row["id"] for idx, row in df_todas_turmas.iterrows()}
                turma_para_deletar = st.selectbox("Selecione a turma:", list(dict_turmas_del.keys()), key="select_del_turma")
                id_turma_del = dict_turmas_del[turma_para_deletar]
                
                st.warning("⚠️ Ao excluir uma turma, essa ação não poderá ser desfeita.")
                confirmacao = st.checkbox("Tenho certeza que desejo EXCLUIR permanentemente", key="check_confirm_del")

                if st.button("❌ Confirmar Exclusão", type="primary"):
                    if confirmacao:
                        CURSOR.execute("DELETE FROM turmas WHERE id = ?", (id_turma_del,))
                        CONN.commit()
                        st.success("✅ Turma excluída!")
                        st.rerun()
                    else:
                        st.error("Marque a caixa de confirmação.")

    st.markdown("---")
    st.with_expander = st.expander("🛠️ Ferramentas de Manutenção")
    with st.expander("🛠️ Ferramentas de Manutenção"):
        st.caption("Restaura a lista inicial de turmas e dados completos de Agosto.")
        if st.button("🔄 Resetar Banco e Recarregar Dados Completos"):
            resetar_turmas_base()
            st.success("Banco de dados recarregado com sucesso!")
            st.rerun()
