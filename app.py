import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from streamlit_image_coordinates import streamlit_image_coordinates
import streamlit.components.v1 as components

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="JUST-JEE City Exploration", layout="wide", page_icon="🏙️", initial_sidebar_state="collapsed")

# ใส่ API Key ของคุณที่นี่
GEMINI_API_KEY = "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8" 

if GEMINI_API_KEY != "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 2. Navigation Logic & State ---
if 'view' not in st.session_state: st.session_state.view = 'intro'
if 'intro_step' not in st.session_state: st.session_state.intro_step = 1
if 'item' not in st.session_state: st.session_state.item = None

def change_page(v, i=None):
    st.session_state.view = v
    st.session_state.item = i

def next_intro_step():
    st.session_state.intro_step += 1

def start_app():
    st.session_state.view = 'map'

# --- 3. ข้อมูลจำลอง ---
objects_data = {
    "คน": {
        "keyword_default": "อาชีพ",
        "keywords": {"อาชีพ": [], "การจ้างงาน": [], "PDPA": [], "สถานะของบุคคล": []}
    },
    "คนพิการ": {
        "keyword_default": "คนพิการ",
        "keywords": {"ผู้ทุพลภาพ": [], "กลุ่มเปราะบาง": []}
    },
    "ยานพาหนะ": {
        "keyword_default": "จราจร",
        "keywords": {"จราจร": [], "ขนส่ง": [], "รถยนต์": []}
    },
    "ถนน": {
        "keyword_default": "ทางหลวง",
        "keywords": {"ทางหลวง": [], "จราจรทางบก": [], "ขนส่งทางบก": [], "ความปลอดภัยทางถนน": [], "ผังเมือง": [], "ยานพาหนะ": [], "คมนาคม": []}
    },
    "ต้นไม้": {
        "keyword_default": "ป่าไม้",
        "keywords": {"ป่าไม้": [], "ป่าชุมชน": [], "อุทยานแห่งชาติ": [], "ป่าสงวน": [], "ที่ดิน": []}
    },
    "อาหารและเครื่องดื่ม": {
        "keyword_default": "อาหาร",
        "keywords": {"อาหาร": [], "เครื่องดื่ม": [], "โภชนาการ": [], "สุขาภิบาลอาหาร": []}
    },
    "อินเตอร์เน็ต": {
        "keyword_default": "อินเทอร์เน็ต",
        "keywords": {"อินเทอร์เน็ต": [], "ดิจิทัล": [], "โทรคมนาคม": [], "โทรศัพท์": [], "อาชญากรรมทางเทคโนโลยี": []}
    },
    "ยาเสพติด/สุรา": {
        "keyword_default": "สุรา",
        "keywords": {"สุรา": [], "สรรพสามิต": [], "เครื่องดื่มแอลกอฮอล์": [], "อาหารปลอดภัย": [], "ผลิตสุรา": [], "สุราก้าวหน้า": [], "ผู้ผลิตรายย่อย": [], "กัญชา": [], "สารเสพติด": []}
    },
    "สายอาร์ต": {
        "keyword_default": "ลิขสิทธิ์",
        "keywords": {"วัฒนธรรมสร้างสรรค์": [], "ซอฟต์พาวเวอร์": [], "ศิลปะ": [], "ศิลปิน": [], "ภาพยนตร์": [], "ลิขสิทธิ์": [], "ทรัพย์สินทางปัญญา": [], "เศรษฐกิจสร้างสรรค์": []}
    },
    "น้ำ": {
        "keyword_default": "ทรัพยากรน้ำ",
        "keywords": {"ทรัพยากรน้ำ": [], "ชายฝั่ง": [], "ทะเล": [], "น้ำบาดาล": [], "บำบัดน้ำ": [], "การประมง": []}
    },
    "สัตว์เลี้ยง": {
        "keyword_default": "สัตว์เลี้ยง",
        "keywords": {"สัตว์เลี้ยง": [], "ทารุณกรรมสัตว์": [], "สวัสดิภาพสัตว์": []}
    },
    "โรงพยาบาล": {
        "keyword_default": "สถานพยาบาล",
        "keywords": {"สถานพยาบาล": [], "สาธารณสุข": [], "ผู้ป่วย": [], "ยา": []}
    },
    "การศึกษา/โรงเรียน": {
        "keyword_default": "การศึกษา",
        "keywords": {"การศึกษา": [], "กยศ": [], "สิทธิเด็ก": [], "สถานศึกษา": []}
    },
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": {
        "keyword_default": "โรงงาน",
        "keywords": {"โรงงาน": [], "สารมลพิษ": [], "วัตถุอันตราย": [], "ผังเมือง": [], "PRTR": []}
    },
    "พลังงาน/ไฟฟ้า": {
        "keyword_default": "พลังงาน",
        "keywords": {"พลังงาน": [], "ไฟฟ้า": [], "พลังงานหมุนเวียน": [], "พลังงานสะอาด": []}
    },
    "เครื่องสำอางค์": {
        "keyword_default": "เครื่องสำอาง",
        "keywords": {"เครื่องสำอาง": [], "สรรพสามิต": [], "ความปลอดภัยของเครื่องสำอาง": []}
    }
}

# 🌟 เติม Mock Data ข้อมูลตัวเลขและกราฟอัตโนมัติ เพื่อป้องกัน Error KeyError
for key, val in objects_data.items():
    if "bill_stats" not in val:
        val["bill_stats"] = {"total": 12, "passed": 8, "failed": 4}
    if "vote_details" not in val:
        val["vote_details"] = {
            "พรรคก้าวไกล": {"เห็นชอบ": 85, "ไม่เห็นชอบ": 10, "งดออกเสียง": 5},
            "พรรคเพื่อไทย": {"เห็นชอบ": 75, "ไม่เห็นชอบ": 15, "งดออกเสียง": 10},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 40, "ไม่เห็นชอบ": 50, "งดออกเสียง": 10}
        }

# --- 4. พิกัดตำแหน่งพิกัด ---
regions = {
    "พลังงาน/ไฟฟ้า": {"x": (50, 160), "y": (50, 310)},
    "โรงพยาบาล": {"x": (180, 340), "y": (50, 250)},
    "ร้านอาหาร": {"x": (370, 520), "y": (50, 350)},
    "เรื่องน้ำ/ทะเล": {"x": (570, 780), "y": (50, 350)},
    "สัตว์เลี้ยง": {"x": (780, 950), "y": (600, 950)},
}

# --- 5. ฟังก์ชันสรุปโดย Gemini ---
def get_ai_summary(keyword):
    if model:
        try:
            prompt = f"สรุปเนื้อหาสำคัญของ '{keyword}' สำหรับประชาชนทั่วไปใน 3 บรรทัด สไตล์มินิมอล"
            return model.generate_content(prompt).text
        except: return "ขออภัย ระบบ AI ไม่สามารถประมวลผลได้ในขณะนี้"
    return "โปรดตั้งค่า API Key เพื่อเปิดใช้งานบทสรุปจาก AI"

# --- 6. พื้นที่บีบอัด Padding ของ Streamlit (ทำให้ Fit จอ) ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 7. ฟังก์ชันวาดหน้า Intro ---
def render_intro_view():
    step = st.session_state.intro_step

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"]{ font-family:'Inter','Prompt',sans-serif; }
    .stApp{ background-color:#0F172A; color:#FFFFFF; }
    .block-container{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:100%; max-width:1000px; text-align:center; padding:0; }
    @keyframes pageEnter{
        0%{ opacity:0; transform:translateY(30px) scale(0.98); filter:blur(6px); }
        100%{ opacity:1; transform:translateY(0px) scale(1); filter:blur(0px); }
    }
    .page-step{ animation:pageEnter 0.7s cubic-bezier(0.2,0.8,0.2,1); }
    .intro-container{ display:flex; flex-direction:column; justify-content:center; align-items:center; }
    .intro-hook{ font-size:2.8rem; font-weight:600; color:#F1F5F9; line-height:1.35; letter-spacing:-0.5px; margin-bottom:1rem; }
    .intro-text{ font-size:1.35rem; color:#94A3B8; line-height:1.7; margin-bottom:2rem; }
    .highlight{ color:#3B82F6; font-weight:500; }
    .warning-highlight{ color:#F59E0B; font-weight:500; }
    div.stButton > button:first-child{ background-color:#2563EB; border:none; color:white !important; border-radius:40px; padding:12px 40px; font-size:1.1rem; font-weight:500; transition:all 0.25s ease; }
    div.stButton > button:first-child:hover{ transform:translateY(-2px); box-shadow:0 10px 25px rgba(37,99,235,0.35); }
    .progress{ font-size:1.3rem; color:#64748B; margin-top:20px; }
    </style>
    """, unsafe_allow_html=True)

    components.html("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown',function(e){
        if(e.code === 'Space'){
            e.preventDefault()
            const buttons = doc.querySelectorAll('.stButton button')
            if(buttons.length > 0){ buttons[0].click() }
        }
    })
    </script>
    """,height=0,width=0)

    st.markdown(f'<div class="intro-container page-step step-{step}">', unsafe_allow_html=True)

    if step == 1:
        st.markdown('<div class="intro-hook">กฎหมายไม่ได้อยู่แค่ในรัฐสภา<br>แต่มันอยู่ใน <span class="highlight">ทุกวันของชีวิตคุณ</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">เคยสงสัยไหมว่า...<br><br>ไฟฟ้าที่คุณใช้<br>โรงพยาบาลที่คุณไป<br>หรืออาหารที่คุณกิน<br><br>ทั้งหมดถูกกำหนดโดย <b>การโหวตในรัฐสภา</b></div>', unsafe_allow_html=True)
        st.button("Press Space to continue ➔", on_click=next_intro_step)
    elif step == 2:
        st.markdown('<div class="intro-hook">ทุกพื้นที่ของเมือง<br>ถูกขับเคลื่อนด้วย <span class="warning-highlight">กฎหมาย</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">กฎหมายไม่ใช่เรื่องไกลตัว<br>และไม่ใช่แค่เอกสารในสภา<br><br>แต่มันคือตัวกำหนด <b>คุณภาพชีวิตของคุณ</b></div>', unsafe_allow_html=True)
        st.button("Press Space to continue ➔", on_click=next_intro_step)
    elif step == 3:
        st.markdown('<div class="intro-hook">ยินดีต้อนรับสู่<br><span class="highlight">JUST-JEE CITY</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">แผนที่ของกฎหมายในชีวิตประจำวัน<br><br>เมืองที่คุณอาศัยอยู่<br>ถูกสร้างขึ้นจาก <b>เสียงโหวตของใคร?</b></div>', unsafe_allow_html=True)
        st.button("🚀 เข้าสู่เมือง (Press Space)", on_click=start_app)
        st.caption("Interactive exploration of parliamentary decisions in everyday life")

    dots = ["○","○","○"]
    dots[step-1] = "●"
    st.markdown(f"<div class='progress'>{' '.join(dots)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 8. CSS สำหรับหน้าหลัก (แผนที่และกราฟ) ---
def apply_main_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
        .stApp { background-color: #FDFDFD; color: #000; }
        @keyframes pageTransition {
            0% { opacity: 0; transform: translateY(15px); filter: blur(3px); }
            100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
        }
        .block-container { animation: pageTransition 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        h1 { color: #0F172A; font-weight: 600; text-align: center; letter-spacing: -1px; margin-top: 0; font-size: 2rem; margin-bottom: 0.5rem;}
        h3 { margin-bottom: 0.2rem !important; margin-top: 0.5rem !important; font-size: 1.1rem; color: #1E293B;}
        .img-container { display: flex; justify-content: center; align-items: center; max-height: 70vh; overflow: hidden; }
        div.stButton > button:first-child { background-color: #FFFFFF; color: #1E293B !important; border: 1px solid #E2E8F0; border-radius: 6px; font-weight: 500; padding: 0.3rem 1rem; }
        .data-card { background-color: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 8px; padding: 10px 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        div[data-testid="metric-container"] { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 5px; text-align: center; margin-bottom: 0.5rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; }
        .ai-report-box { background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 10px 15px; border-radius: 4px; margin-bottom: 0.5rem; }
        .ai-report-box p { font-size: 0.95rem; line-height: 1.5; margin: 0; }
        .ai-note { font-size: 0.75rem; color: #94A3B8; text-align: center; margin-top: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

# --- 9. การแสดงผล (Main Controller) ---
if st.session_state.view == 'intro':
    render_intro_view()

elif st.session_state.view == 'map':
    apply_main_css()
    st.markdown("<h1>JUST-JEE City Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1rem; margin-bottom: 0.5rem;'>คลิกเลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
    
    _, col_img, _ = st.columns([1.5, 7, 1.5]) 
    with col_img:
        st.markdown('<div class="img-container">', unsafe_allow_html=True)
        value = streamlit_image_coordinates("city.png", key="map")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if value:
            x, y = value['x'], value['y']
            for item, bounds in regions.items():
                if bounds["x"][0] <= x <= bounds["x"][1] and bounds["y"][0] <= y <= bounds["y"][1]:
                    change_page('dash', item)
                    st.rerun()

elif st.session_state.view == 'dash':
    apply_main_css()
    item = st.session_state.item
    data = objects_data.get(item, list(objects_data.values())[0])
    
    # 🌟 รวบรวม Keyword ทั้งหมดที่มีในหมวดนี้ และตัดคำที่ซ้ำกัน
    all_keywords = [data['keyword_default']] + list(data['keywords'].keys())
    all_keywords = list(dict.fromkeys(all_keywords))
    
    # 1. แถบ Header (ปรับให้เรียบง่ายขึ้น และเอา Dropdown มาไว้ฝั่งซ้าย)
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown(f"<div class='data-card'><div style='font-size: 1.2rem; font-weight: 600;'>ประเด็น: {item}</div></div>", unsafe_allow_html=True)
    with col_btn:
        st.button("← กลับแผนที่", on_click=change_page, args=('map',), use_container_width=True)
    
    # 🌟 Dropdown ให้ผู้ใช้เลือก
    selected_keyword = st.selectbox("📌 เลือกหัวข้อย่อยเพื่อดูสรุป:", all_keywords)
    
    # 2. นำ Metrics พ.ร.บ. และ AI Analysis มาวางคู่กัน
    col_stat, col_ai = st.columns([1, 1.5])
    
    with col_stat:
        st.markdown("<h3>📄 สถานะ พ.ร.บ.</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("ทั้งหมด", f"{data['bill_stats']['total']}")
        c2.metric("ผ่าน ✅", f"{data['bill_stats']['passed']}")
        c3.metric("ตก ❌", f"{data['bill_stats']['failed']}")

    with col_ai:
        st.markdown(f"<h3>✨ AI Analysis: {selected_keyword}</h3>", unsafe_allow_html=True)
        with st.spinner("Analyzing..."):
            # 🌟 โยนคำที่ผู้ใช้เลือกไปให้ Gemini
            summary = get_ai_summary(selected_keyword)
            st.markdown(f"<div class='ai-report-box'><p>{summary}</p></div>", unsafe_allow_html=True)

    # 3. กราฟ Visualization
    st.markdown("<h3>🗳️ Vote Distribution by Political Parties (%)</h3>", unsafe_allow_html=True)
    
    rows = []
    for party, votes in data['vote_details'].items():
        for vote_type, percentage in votes.items():
            rows.append({'Party': party, 'Vote Type': vote_type, 'Percentage': percentage})
    df_votes = pd.DataFrame(rows)

    party_order = sorted(data['vote_details'].keys(), key=lambda p: data['vote_details'][p]['เห็นชอบ'])
    
    fig = px.bar(df_votes, x='Percentage', y='Party', color='Vote Type', orientation='h', 
                 color_discrete_map={"เห็นชอบ": "#2ECC71", "ไม่เห็นชอบ": "#E74C3C", "งดออกเสียง": "#94A3B8"},
                 text_auto=True)
    
    fig.update_layout(
        xaxis_title="", yaxis_title="", 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        barmode='stack',
        yaxis={'categoryorder': 'array', 'categoryarray': party_order},
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(t=0, b=0, l=0, r=0),
        height=240
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. หมายเหตุ
    st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ</div>", unsafe_allow_html=True)