import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(
    page_title="PhysiQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# API KEY
# ============================================================
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None

model = None
IA_DISPONIBLE = False

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        IA_DISPONIBLE = True
    except Exception:
        IA_DISPONIBLE = False

# ============================================================
# BANCO DE PREGUNTAS
# ============================================================
TOPICS = [
    "📐  Movimiento 1D y 2D",
    "⚖️  Fuerzas y leyes de Newton",
    "🔄  Torque y equilibrio",
    "💼  Trabajo y potencia",
    "⚡  Energía y conservación",
]

QUESTIONS = {
    "📐  Movimiento 1D y 2D": [
        {"t": "Un auto parte del reposo y alcanza 20 m/s en 5 s con aceleración constante. ¿Cuál es su aceleración?",
         "f": "a = (vf - vi) / t", "o": ["2 m/s²", "4 m/s²", "10 m/s²", "100 m/s²"], "c": 1,
         "e": "a = (20 - 0) / 5 = 4 m/s². En MRUV la aceleración es constante e igual al cambio de velocidad entre el tiempo."},
        {"t": "Un objeto en MRU recorre 150 m en 30 s. ¿Cuál es su velocidad?",
         "f": "v = d / t", "o": ["0.2 m/s", "5 m/s", "450 m/s", "30 m/s"], "c": 1,
         "e": "v = 150 / 30 = 5 m/s. En MRU la velocidad es constante e igual a la distancia entre el tiempo."},
        {"t": "En caída libre desde el reposo, ¿cuánto cae un objeto en los primeros 3 s? (g = 9.8 m/s²)",
         "f": "y = ½ g t²", "o": ["9.8 m", "29.4 m", "44.1 m", "88.2 m"], "c": 2,
         "e": "y = ½ × 9.8 × 9 = 44.1 m. La distancia en caída libre crece con el cuadrado del tiempo."},
        {"t": "Un proyectil se lanza horizontalmente a 15 m/s. ¿Cuál es su velocidad horizontal a los 3 s?",
         "f": None, "o": ["45 m/s", "9.8 m/s", "15 m/s", "29.4 m/s"], "c": 2,
         "e": "La componente horizontal es constante en movimiento parabólico. No hay aceleración horizontal, siempre vale 15 m/s."},
        {"t": "Movimiento circular uniforme: ω = 2π rad/s y r = 3 m. ¿Cuál es la velocidad lineal?",
         "f": "v = ω · r", "o": ["6π m/s", "2π m/s", "3 m/s", "π m/s"], "c": 0,
         "e": "v = 2π × 3 = 6π ≈ 18.85 m/s. La velocidad lineal es el producto de la velocidad angular por el radio."},
    ],
    "⚖️  Fuerzas y leyes de Newton": [
        {"t": "Un bloque de 8 kg en reposo sobre superficie horizontal. ¿Cuál es la fuerza normal? (g = 9.8 m/s²)",
         "f": "N = m · g", "o": ["9.8 N", "78.4 N", "8 N", "0 N"], "c": 1,
         "e": "N = 8 × 9.8 = 78.4 N. La normal equilibra el peso del objeto en reposo sobre superficie horizontal."},
        {"t": "Se aplica 40 N a un bloque de 5 kg con fricción cinética de 15 N. ¿Cuál es la aceleración?",
         "f": "ΣF = F - f = ma", "o": ["8 m/s²", "3 m/s²", "5 m/s²", "11 m/s²"], "c": 2,
         "e": "ΣF = 40 - 15 = 25 N → a = 25/5 = 5 m/s². La fricción se resta a la fuerza aplicada."},
        {"t": "Bloques A (3 kg) y B (5 kg) reciben 24 N. ¿Fuerza de contacto entre ellos?",
         "f": "F = m_B · a", "o": ["24 N", "15 N", "9 N", "3 N"], "c": 1,
         "e": "a = 24/8 = 3 m/s². F sobre B = 5 × 3 = 15 N. Se aplica la 2ª ley sobre B solo."},
        {"t": "μe = 0.4 y N = 50 N. ¿Máxima fricción estática?",
         "f": "fs = μe · N", "o": ["125 N", "20 N", "0.4 N", "50 N"], "c": 1,
         "e": "fs_max = 0.4 × 50 = 20 N. Si la fuerza aplicada supera 20 N el objeto comienza a moverse."},
        {"t": "ΣFx = 0, ΣFy = 0 y Στ = 0. ¿Qué tipo de equilibrio es?",
         "f": None, "o": ["Dinámico", "Inestable", "Estático", "Neutral"], "c": 2,
         "e": "Equilibrio estático: el objeto no se traslada ni rota. Requiere las tres condiciones simultáneamente."},
    ],
    "🔄  Torque y equilibrio": [
        {"t": "Fuerza de 30 N perpendicular a 0.5 m del pivote. ¿Cuál es el torque?",
         "f": "τ = F · d", "o": ["60 N·m", "15 N·m", "0.5 N·m", "30 N·m"], "c": 1,
         "e": "τ = 30 × 0.5 = 15 N·m. Cuando la fuerza es perpendicular al brazo, el torque es su producto directo."},
        {"t": "20 N a 0.8 m del eje formando 30° con el brazo. ¿Cuál es el torque?",
         "f": "τ = F · d · sen(θ)", "o": ["16 N·m", "8 N·m", "13.9 N·m", "20 N·m"], "c": 1,
         "e": "τ = 20 × 0.8 × sen(30°) = 8 N·m. Solo la componente perpendicular a r genera torque."},
        {"t": "Varilla uniforme 4 m, 10 kg apoyada en sus extremos. ¿Reacción en cada apoyo? (g = 10)",
         "f": "R = mg / 2", "o": ["100 N", "50 N", "25 N", "200 N"], "c": 1,
         "e": "Por simetría R1 = R2 = mg/2 = 100/2 = 50 N cada apoyo."},
        {"t": "¿Cuál es la condición de equilibrio rotacional?",
         "f": None, "o": ["ΣF = 0", "Στ = 0", "v = 0", "a = 0"], "c": 1,
         "e": "Equilibrio rotacional exige Στ = 0. Para equilibrio completo también se necesita ΣF = 0."},
        {"t": "Στ = 0 y ΣF ≠ 0. ¿Qué movimiento tiene el cuerpo rígido?",
         "f": None, "o": ["Solo rotación", "Solo traslación", "Traslación y rotación", "Reposo"], "c": 1,
         "e": "ΣF ≠ 0 implica aceleración traslacional. Στ = 0 implica sin aceleración angular. Resultado: solo traslación."},
    ],
    "💼  Trabajo y potencia": [
        {"t": "Fuerza de 50 N desplaza un objeto 8 m en la misma dirección. ¿Cuánto trabajo realiza?",
         "f": "W = F · d", "o": ["6.25 J", "400 J", "58 J", "42 J"], "c": 1,
         "e": "W = 50 × 8 = 400 J. Fuerza y desplazamiento paralelos: el trabajo es su producto directo."},
        {"t": "60 N con 60° respecto al desplazamiento de 5 m. ¿Cuál es el trabajo?",
         "f": "W = F · d · cos(θ)", "o": ["300 J", "150 J", "259.8 J", "75 J"], "c": 1,
         "e": "W = 60 × 5 × cos(60°) = 150 J. Solo la componente paralela al desplazamiento hace trabajo."},
        {"t": "Resorte k = 500 N/m comprimido 0.2 m. ¿Trabajo realizado?",
         "f": "W = ½ k x²", "o": ["100 J", "10 J", "50 J", "0.02 J"], "c": 1,
         "e": "W = ½ × 500 × 0.04 = 10 J. La fuerza del resorte es variable, se usa ½kx²."},
        {"t": "Máquina realiza 3000 J en 60 s. ¿Cuál es su potencia?",
         "f": "P = W / t", "o": ["180 000 W", "0.02 W", "50 W", "3060 W"], "c": 2,
         "e": "P = 3000/60 = 50 W. La potencia mide qué tan rápido se realiza trabajo (W = J/s)."},
        {"t": "¿Trabajo de la fuerza normal sobre un objeto que se desliza horizontalmente?",
         "f": None, "o": ["= peso × distancia", "Positivo", "Cero", "Negativo"], "c": 2,
         "e": "La normal es perpendicular al desplazamiento. cos(90°) = 0, el trabajo de la normal es siempre cero."},
    ],
    "⚡  Energía y conservación": [
        {"t": "Objeto de 4 kg cae 10 m libremente. ¿Energía potencial que pierde? (g = 10)",
         "f": "Ep = m · g · h", "o": ["40 J", "4 J", "400 J", "14 J"], "c": 2,
         "e": "ΔEp = 4 × 10 × 10 = 400 J. Esa energía se transforma en energía cinética durante la caída."},
        {"t": "Objeto de 2 kg a 10 m/s. ¿Cuál es su energía cinética?",
         "f": "Ec = ½ m v²", "o": ["10 J", "20 J", "100 J", "200 J"], "c": 2,
         "e": "Ec = ½ × 2 × 100 = 100 J. La energía cinética depende del cuadrado de la velocidad."},
        {"t": "Bloque cae sin fricción desde h = 5 m. ¿Velocidad al llegar al suelo? (g = 10)",
         "f": "v = √(2gh)", "o": ["5 m/s", "10 m/s", "7.07 m/s", "50 m/s"], "c": 1,
         "e": "v = √(2×10×5) = √100 = 10 m/s. Sin fricción toda la energía potencial se convierte en cinética."},
        {"t": "¿Cuál de estas fuerzas NO es conservativa?",
         "f": None, "o": ["Gravitatoria", "Elástica", "Fricción cinética", "Eléctrica"], "c": 2,
         "e": "La fricción cinética disipa energía como calor. Las fuerzas conservativas tienen trabajo independiente de la trayectoria."},
        {"t": "Sistema conservativo: Ec = 80 J, Ep = 20 J. Si Ep sube a 50 J, ¿cuánto vale Ec?",
         "f": "Em = Ec + Ep = constante", "o": ["80 J", "130 J", "50 J", "30 J"], "c": 2,
         "e": "Em = 80 + 20 = 100 J (constante). Si Ep = 50 J → Ec = 100 - 50 = 50 J."},
    ],
}

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
def init_state():
    defaults = {
        "topic": TOPICS[0],
        "q_idx": 0,
        "xp": 0,
        "lives": 5,
        "rounds": 0,
        "round_correct": 0,
        "round_xp": 0,
        "answered": False,
        "selected_option": None,
        "current_q": None,
        "ai_question_active": False,
        "chat_history": [],
        "last_wrong_q": None,
        "show_results": False,
        "topic_xp": {t: 0 for t in TOPICS},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.current_q is None:
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]

init_state()

# ============================================================
# ESTILOS DARK MODE
# ============================================================
st.markdown("""
<style>
/* Fondo oscuro general */
.stApp {
    background-color: #0D0F14;
    color: #E8EAF0;
}

/* Sidebar oscura */
[data-testid="stSidebar"] {
    background-color: #141720 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * {
    color: #E8EAF0 !important;
}

/* Inputs y widgets oscuros */
[data-testid="stTextInput"] input,
[data-testid="stChatInput"] textarea,
.stTextInput input {
    background-color: #1C2030 !important;
    color: #E8EAF0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    background-color: #1C2030;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 16px;
    margin: 4px 0;
    display: block;
    cursor: pointer;
    transition: border-color .15s;
    color: #8B90A0 !important;
    font-size: 14px;
}
[data-testid="stRadio"] label:hover {
    border-color: #4C8EF7;
    color: #E8EAF0 !important;
}

/* Botones primarios */
.stButton > button[kind="primary"] {
    background: #4C8EF7 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}

/* Botones secundarios */
.stButton > button {
    background: #1C2030 !important;
    color: #8B90A0 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
.stButton > button:hover {
    border-color: #4C8EF7 !important;
    color: #E8EAF0 !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #4C8EF7, #A78BFA) !important;
    border-radius: 3px !important;
}
.stProgress > div {
    background: #1C2030 !important;
    border-radius: 3px !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #1C2030;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #8B90A0 !important; }
[data-testid="stMetricValue"] { color: #E8EAF0 !important; }

/* Alertas */
.stSuccess { background: rgba(52,211,153,0.1) !important; border-color: rgba(52,211,153,0.3) !important; color: #34D399 !important; border-radius: 10px !important; }
.stError   { background: rgba(248,113,113,0.1) !important; border-color: rgba(248,113,113,0.3) !important; color: #F87171 !important; border-radius: 10px !important; }
.stInfo    { background: rgba(76,142,247,0.1)  !important; border-color: rgba(76,142,247,0.3)  !important; color: #4C8EF7  !important; border-radius: 10px !important; }
.stWarning { background: rgba(251,191,36,0.1)  !important; border-color: rgba(251,191,36,0.3)  !important; color: #FBBF24  !important; border-radius: 10px !important; }

/* Chat */
[data-testid="stChatMessage"] {
    background: #1C2030 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

/* Cajas de código / fórmulas */
.formula-box {
    background: #1C2030;
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #4C8EF7;
    border-radius: 8px;
    padding: 10px 16px;
    font-family: monospace;
    font-size: 15px;
    color: #4C8EF7;
    text-align: center;
    margin: 8px 0 16px;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Expandir sidebar */
section[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* Tarjeta de stats */
.stat-card {
    background: #1C2030;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
    margin-bottom: 8px;
}
.stat-val { font-size: 20px; font-weight: 700; color: #E8EAF0; }
.stat-lbl { font-size: 11px; color: #555A70; margin-top: 2px; }

/* Resultado card */
.res-card {
    background: #1C2030;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px 8px;
    text-align: center;
}
.res-num { font-size: 26px; font-weight: 700; margin-bottom: 3px; }
.res-lbl { font-size: 12px; color: #555A70; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# PANTALLA DE BIENVENIDA — pide API key
# ============================================================
if not st.session_state.gemini_api_key:
    st.markdown("## ⚡ PhysiQ")
    st.caption("Aprende física universitaria como si fuera un juego, con un tutor de IA")
    st.divider()
    st.markdown("### 🔑 Ingresa tu API key de Gemini para empezar")
    st.write(
        "PhysiQ usa Google Gemini como tutor de IA. Necesitas tu propia API key gratuita. "
        "No se guarda en ningún servidor ni se comparte — solo existe durante tu sesión."
    )
    with st.expander("¿No tienes una API key? Consíguela gratis en 1 minuto"):
        st.markdown("""
1. Ve a **[aistudio.google.com](https://aistudio.google.com)** e inicia sesión con tu cuenta de Google
2. En el menú izquierdo, clic en **"Get API key"**
3. Clic en **"Create API key"**
4. Copia la clave (empieza con `AIza...`) y pégala abajo

No necesitas tarjeta de crédito. El plan gratuito es más que suficiente.
        """)
    key_input = st.text_input("Tu API key de Gemini", type="password", placeholder="AIza...")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("Entrar →", type="primary", use_container_width=True):
            if not key_input.strip():
                st.error("Por favor ingresa una API key válida.")
            else:
                with st.spinner("Verificando tu API key..."):
                    try:
                        genai.configure(api_key=key_input.strip())
                        test_model = genai.GenerativeModel("gemini-2.5-flash")
                        test_model.generate_content("Responde solo con: OK")
                        st.session_state.gemini_api_key = key_input.strip()
                        st.rerun()
                    except Exception as e:
                        st.error(f"API key no válida o error de conexión: {e}")
    st.stop()

# ============================================================
# FUNCIONES DE IA
# ============================================================
def generar_pregunta_ia(topic):
    prompt = f"""Eres un generador de preguntas de física universitaria básica.
Genera UNA pregunta de examen sobre el tema: {topic}.
Responde SOLO con JSON válido sin backticks ni texto extra:
{{"t":"pregunta","f":"formula o null","o":["A","B","C","D"],"c":0,"e":"explicacion 2-3 oraciones"}}
El campo "c" es el índice (0-3) de la opción correcta. Usa valores numéricos concretos. En español."""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        st.error(f"No se pudo generar la pregunta: {e}")
        return None

def preguntar_tutor(mensaje, topic, pregunta_actual, wrong_q=None):
    ctx = f'El estudiante falló: "{wrong_q["t"]}". Ayúdalo a entenderla sin revelar la respuesta.' if wrong_q else ""
    prompt = f"""Eres PhysiQ, tutor de física universitaria. Amigable y conciso.
Tema: {topic}. Pregunta activa: "{pregunta_actual['t']}" {ctx}
Responde en español, máximo 3-4 oraciones, con analogías cotidianas.
Pregunta: {mensaje}"""
    try:
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"Error al conectar con el tutor: {e}"

# ============================================================
# SIDEBAR: logo + temas + stats
# ============================================================
with st.sidebar:
    st.markdown("## ⚡ PhysiQ")
    st.caption("Física universitaria con IA")
    st.divider()

    st.markdown("**Temas del curso**")
    for t in TOPICS:
        xp_t = st.session_state.topic_xp.get(t, 0)
        is_active = st.session_state.topic == t
        label = f"{'→ ' if is_active else ''}{t}  ·  {xp_t} XP"
        if st.button(label, key=f"btn_{t}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            if t != st.session_state.topic:
                st.session_state.topic = t
                st.session_state.q_idx = 0
                st.session_state.round_correct = 0
                st.session_state.round_xp = 0
                st.session_state.answered = False
                st.session_state.ai_question_active = False
                st.session_state.show_results = False
                st.session_state.current_q = QUESTIONS[t][0]
                st.rerun()

    st.divider()
    st.markdown("**Estadísticas**")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='stat-card'><div class='stat-val'>⭐ {st.session_state.xp}</div><div class='stat-lbl'>XP Total</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='stat-card'><div class='stat-val'>❤️ {st.session_state.lives}</div><div class='stat-lbl'>Vidas</div></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='stat-card'><div class='stat-val'>🔄 {st.session_state.rounds}</div><div class='stat-lbl'>Rondas completadas</div></div>", unsafe_allow_html=True)

    st.divider()
    if st.button("🔑 Cambiar API key", use_container_width=True):
        st.session_state.gemini_api_key = None
        st.rerun()

# ============================================================
# ÁREA PRINCIPAL
# ============================================================
topic_clean = st.session_state.topic.split("  ", 1)[-1].strip()
st.markdown(f"## {st.session_state.topic}")

total_qs = len(QUESTIONS[st.session_state.topic])
st.progress(
    st.session_state.q_idx / total_qs,
    text=f"Pregunta {st.session_state.q_idx + 1} de {total_qs}  ·  XP este tema: {st.session_state.topic_xp.get(st.session_state.topic, 0)}"
)

st.divider()

# ============================================================
# PANTALLA DE RESULTADOS
# ============================================================
if st.session_state.show_results:
    total = len(QUESTIONS[st.session_state.topic])
    pct = st.session_state.round_correct / total

    if pct == 1.0:
        st.success("🎉 ¡Perfecto! Respondiste todas correctamente")
    elif pct >= 0.6:
        st.success("👍 ¡Buen trabajo!")
    else:
        st.info("📘 Sigue practicando, vas mejorando")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"<div class='res-card'><div class='res-num' style='color:#34D399'>{st.session_state.round_correct}/{total}</div><div class='res-lbl'>Correctas</div></div>", unsafe_allow_html=True)
    with r2:
        st.markdown(f"<div class='res-card'><div class='res-num' style='color:#FBBF24'>+{st.session_state.round_xp}</div><div class='res-lbl'>XP ganados</div></div>", unsafe_allow_html=True)
    with r3:
        st.markdown(f"<div class='res-card'><div class='res-num' style='color:#4C8EF7'>{st.session_state.rounds}</div><div class='res-lbl'>Rondas totales</div></div>", unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 Jugar otra ronda", type="primary", use_container_width=True):
        st.session_state.q_idx = 0
        st.session_state.round_correct = 0
        st.session_state.round_xp = 0
        st.session_state.answered = False
        st.session_state.ai_question_active = False
        st.session_state.show_results = False
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]
        st.rerun()

else:
    # ============================================================
    # PREGUNTA
    # ============================================================
    col_q, col_chat = st.columns([3, 2])

    with col_q:
        if st.button("✨ Generar pregunta con IA", use_container_width=False):
            with st.spinner("Generando pregunta con IA..."):
                nueva = generar_pregunta_ia(st.session_state.topic)
                if nueva:
                    st.session_state.current_q = nueva
                    st.session_state.answered = False
                    st.session_state.selected_option = None
                    st.session_state.ai_question_active = True
                    st.rerun()

        q = st.session_state.current_q
        st.markdown(f"#### {q['t']}")

        if q.get("f"):
            st.markdown(f"<div class='formula-box'>{q['f']}</div>", unsafe_allow_html=True)

        if not st.session_state.answered:
            choice = st.radio(
                "Opciones",
                q["o"],
                index=None,
                label_visibility="collapsed",
                key=f"radio_{st.session_state.q_idx}_{st.session_state.ai_question_active}"
            )
            if st.button("Responder ✓", type="primary", disabled=(choice is None), use_container_width=True):
                sel = q["o"].index(choice)
                st.session_state.selected_option = sel
                st.session_state.answered = True
                if sel == q["c"]:
                    st.session_state.xp += 20
                    st.session_state.round_correct += 1
                    st.session_state.round_xp += 20
                    st.session_state.topic_xp[st.session_state.topic] = min(
                        100, st.session_state.topic_xp.get(st.session_state.topic, 0) + 20)
                    st.session_state.last_wrong_q = None
                else:
                    st.session_state.lives = max(0, st.session_state.lives - 1)
                    st.session_state.last_wrong_q = q
                st.rerun()
        else:
            if st.session_state.selected_option == q["c"]:
                st.success(f"✅ **¡Correcto!**\n\n{q['e']}")
            else:
                st.error(f"❌ **Incorrecto.** La respuesta correcta era: **{q['o'][q['c']]}**\n\n{q['e']}")

            if st.button("Siguiente →", type="primary", use_container_width=True):
                st.session_state.q_idx += 1
                st.session_state.answered = False
                st.session_state.selected_option = None
                st.session_state.ai_question_active = False
                if st.session_state.q_idx >= total_qs:
                    st.session_state.rounds += 1
                    st.session_state.show_results = True
                else:
                    st.session_state.current_q = QUESTIONS[st.session_state.topic][st.session_state.q_idx]
                st.rerun()

    # ============================================================
    # CHAT (columna derecha)
    # ============================================================
    with col_chat:
        st.markdown("#### 🤖 Tutor IA")
        st.caption("Pregúntame cualquier duda del tema")

        chat_container = st.container(height=380)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        user_msg = st.chat_input("Escribe tu duda...")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            with st.spinner(""):
                respuesta = preguntar_tutor(
                    user_msg,
                    st.session_state.topic,
                    st.session_state.current_q,
                    st.session_state.last_wrong_q,
                )
            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
            st.rerun()
