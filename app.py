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
    "พลังงาน/ไฟฟ้า": {
        "keyword": "ร่าง พ.ร.บ. การประกอบกิจการพลังงาน (ฉบับแก้ไข)",
        "bill_stats": {"total": 5, "passed": 2, "failed": 3},
        "vote_details": {
            "พรรคก้าวไกล": {"เห็นชอบ": 95, "ไม่เห็นชอบ": 3, "งดออกเสียง": 2},
            "พรรคเพื่อไทย": {"เห็นชอบ": 88, "ไม่เห็นชอบ": 10, "งดออกเสียง": 2},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 40, "ไม่เห็นชอบ": 55, "งดออกเสียง": 5},
            "พรรครวมไทยสร้างชาติ": {"เห็นชอบ": 15, "ไม่เห็นชอบ": 80, "งดออกเสียง": 5},
            "พรรคประชาธิปัตย์": {"เห็นชอบ": 30, "ไม่เห็นชอบ": 60, "งดออกเสียง": 10}
        }
    },
    "โรงพยาบาล": {
        "keyword": "ร่าง พ.ร.บ. สถานพยาบาล และสิทธิผู้ป่วย",
        "bill_stats": {"total": 8, "passed": 6, "failed": 2},
        "vote_details": {
            "พรรคก้าวไกล": {"เห็นชอบ": 85, "ไม่เห็นชอบ": 10, "งดออกเสียง": 5},
            "พรรคเพื่อไทย": {"เห็นชอบ": 95, "ไม่เห็นชอบ": 2, "งดออกเสียง": 3},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 90, "ไม่เห็นชอบ": 5, "งดออกเสียง": 5},
            "พรรครวมไทยสร้างชาติ": {"เห็นชอบ": 70, "ไม่เห็นชอบ": 20, "งดออกเสียง": 10},
            "พรรคประชาธิปัตย์": {"เห็นชอบ": 65, "ไม่เห็นชอบ": 25, "งดออกเสียง": 10}
        }
    },
    "ร้านอาหาร": {
        "keyword": "ร่าง พ.ร.บ. การสาธารณสุข และความปลอดภัยด้านอาหาร",
        "bill_stats": {"total": 3, "passed": 1, "failed": 2},
        "vote_details": {
            "พรรคก้าวไกล": {"เห็นชอบ": 55, "ไม่เห็นชอบ": 40, "งดออกเสียง": 5},
            "พรรคเพื่อไทย": {"เห็นชอบ": 90, "ไม่เห็นชอบ": 5, "งดออกเสียง": 5},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 85, "ไม่เห็นชอบ": 10, "งดออกเสียง": 5},
            "พรรครวมไทยสร้างชาติ": {"เห็นชอบ": 40, "ไม่เห็นชอบ": 50, "งดออกเสียง": 10},
            "พรรคประชาธิปัตย์": {"เห็นชอบ": 60, "ไม่เห็นชอบ": 30, "งดออกเสียง": 10}
        }
    },
    "เรื่องน้ำ/ทะเล": {
        "keyword": "ร่าง พ.ร.บ. การเดินเรือในน่านน้ำไทย และการจัดการทรัพยากรทางทะเล",
        "bill_stats": {"total": 4, "passed": 2, "failed": 2},
        "vote_details": {
            "พรรคก้าวไกล": {"เห็นชอบ": 85, "ไม่เห็นชอบ": 10, "งดออกเสียง": 5},
            "พรรคเพื่อไทย": {"เห็นชอบ": 40, "ไม่เห็นชอบ": 50, "งดออกเสียง": 10},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 30, "ไม่เห็นชอบ": 60, "งดออกเสียง": 10},
            "พรรครวมไทยสร้างชาติ": {"เห็นชอบ": 20, "ไม่เห็นชอบ": 70, "งดออกเสียง": 10},
            "พรรคประชาธิปัตย์": {"เห็นชอบ": 75, "ไม่เห็นชอบ": 20, "งดออกเสียง": 5}
        }
    },
    "สัตว์เลี้ยง": {
        "keyword": "ร่าง พ.ร.บ. คุ้มครองและสวัสดิภาพสัตว์เลี้ยง",
        "bill_stats": {"total": 2, "passed": 1, "failed": 1},
        "vote_details": {
            "พรรคก้าวไกล": {"เห็นชอบ": 92, "ไม่เห็นชอบ": 5, "งดออกเสียง": 3},
            "พรรคเพื่อไทย": {"เห็นชอบ": 80, "ไม่เห็นชอบ": 15, "งดออกเสียง": 5},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 75, "ไม่เห็นชอบ": 20, "งดออกเสียง": 5},
            "พรรครวมไทยสร้างชาติ": {"เห็นชอบ": 45, "ไม่เห็นชอบ": 50, "งดออกเสียง": 5},
            "พรรคประชาธิปัตย์": {"เห็นชอบ": 60, "ไม่เห็นชอบ": 35, "งดออกเสียง": 5}
        }
    }
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
        /* ลบขอบและระยะห่างเริ่มต้นของ Streamlit ออกให้หมด */
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
# --- 7. ฟังก์ชันวาดหน้า Intro ---
def render_intro_view():
    step = st.session_state.intro_step
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
        .stApp { background-color: #0F172A; color: #FFFFFF; }
        
        /* ซ่อน Header/Footer และบังคับให้คอนเทนเนอร์หลักของ Streamlit อยู่ตรงกลางจอ 100% */
        [data-testid="stHeader"], footer { visibility: hidden; }
        .block-container {
            height: 100vh !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 50px 100px;
            max-width: 100% !important;
            overflow: hidden !important; /* ปิดการ Scroll */
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .intro-container {
            display: flex; flex-direction: column; justify-content: center; 
            align-items: center; text-align: center; width: 100%; padding: 0 10%;
            animation: fadeIn 1s ease-out forwards;
        }
        
        /* ปรับขนาดตัวอักษรให้พอดีกับหน้าจอ */
        .intro-hook { font-size: 2.5rem; font-weight: 600; color: #E2E8F0; margin-bottom: 1rem; line-height: 1.4; }
        .intro-text { font-size: 1.4rem; color: #94A3B8; line-height: 1.6; margin-bottom: 2rem; font-weight: 300; }
        .highlight { color: #3B82F6; font-weight: 500; }
        .warning-highlight { color: #F59E0B; font-weight: 500; }
        
        div.stButton > button:first-child {
            background-color: transparent; border: 1px solid #475569; color: #E2E8F0 !important;
            border-radius: 50px; padding: 10px 35px; font-size: 1.1rem; transition: 0.3s;
        }
        div.stButton > button:first-child:hover { background-color: #3B82F6; border-color: #3B82F6; color: white !important; }
        
        .btn-start div.stButton > button:first-child {
            background-color: #3B82F6; border: none; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

    components.html("""
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            if (e.code === 'Space') {
                e.preventDefault(); 
                const buttons = doc.querySelectorAll('.stButton button');
                if (buttons.length > 0) { buttons[0].click(); }
            }
        });
        </script>
    """, height=0, width=0)

    st.markdown('<div class="intro-container">', unsafe_allow_html=True)
    
    if step == 1:
        st.markdown('<div class="intro-hook">"กฎหมายไม่ได้อยู่แค่ในรัฐสภา...<br>แต่มันซ่อนอยู่ใน <span class="highlight">ทุกวันของชีวิตคุณ</span>"</div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">เคยสงสัยไหมว่า... แสงสว่างจากหลอดไฟ ถนนที่คุณเดิน<br>หรือแม้แต่อาหารจานโปรด มีกฎหมายอะไรควบคุมอยู่?</div>', unsafe_allow_html=True)
        st.button("กด Spacebar เพื่อไปต่อ ➔", on_click=next_intro_step)
        
    elif step == 2:
        st.markdown('<div class="intro-hook">ทุกตารางเมตรที่คุณเหยียบ<br>ล้วนถูกขับเคลื่อนด้วย <span class="warning-highlight">"กฎหมาย"</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">กฎหมายไม่ใช่เรื่องไกลตัว และไม่ใช่แค่กระดาษในสภา<br>แต่มันคือตัวกำหนดคุณภาพชีวิต ที่ถูกชี้ชะตาด้วย <b>"คะแนนโหวต"</b></div>', unsafe_allow_html=True)
        st.button("กด Spacebar เพื่อไปต่อ ➔", on_click=next_intro_step, key="step2")
        
    elif step == 3:
        st.markdown('<div class="intro-hook">ทีม I am sorry จั๊กจี้หัวใจ<br>ขอพาคุณทำความเข้าใจกฎหมายผ่านชีวิตจริง</div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">ยินดีต้อนรับสู่ <b>JUST-JEE CITY</b> แผนที่กฎหมายในชีวิตประจำวัน...<br><br><span style="color:white; font-size:1.8rem; font-weight:500;">เมืองที่คุณอยู่ ถูกสร้างขึ้นมาจากเสียงโหวตของใคร?</span></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-start">', unsafe_allow_html=True)
        st.button("🚀 เข้าสู่เมือง (Press Space)", on_click=start_app, key="start")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. CSS สำหรับหน้าหลัก (แผนที่และกราฟ) ---
def apply_main_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
        .stApp { background-color: #FDFDFD; color: #000; }
        
        h1 { color: #0F172A; font-weight: 600; text-align: center; letter-spacing: -1px; margin-top: 0; font-size: 2rem; margin-bottom: 0.5rem;}
        h3 { margin-bottom: 0.2rem !important; margin-top: 0.5rem !important; font-size: 1.1rem; color: #1E293B;}
        
        .img-container { display: flex; justify-content: center; align-items: center; max-height: 70vh; overflow: hidden; }
        
        div.stButton > button:first-child {
            background-color: #FFFFFF; color: #1E293B !important; border: 1px solid #E2E8F0;
            border-radius: 6px; font-weight: 500; padding: 0.3rem 1rem;
        }
        
        /* กระชับการ์ดข้อมูล */
        .data-card {
            background-color: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 8px;
            padding: 10px 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02); margin-bottom: 0.5rem;
            display: flex; justify-content: space-between; align-items: center;
        }
        
        /* กระชับ Metrics */
        div[data-testid="metric-container"] {
            background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 5px; text-align: center; margin-bottom: 0.5rem;
        }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; }
        
        /* กระชับ AI Report */
        .ai-report-box {
            background-color: #F8FAFC; border-left: 4px solid #3B82F6; 
            padding: 10px 15px; border-radius: 4px; margin-bottom: 0.5rem;
        }
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
    
    # ปรับสัดส่วน Columns บีบรูปให้เล็กลง เพื่อไม่ให้รูปสูงล้นจอ
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
    
    # 1. แถบ Header: นำปุ่มย้อนกลับ และ ชื่อหัวข้อมาไว้บรรทัดเดียวกัน เพื่อประหยัดพื้นที่
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown(f"<div class='data-card'><div style='font-size: 1.2rem; font-weight: 600;'>ประเด็น: {item}</div><div style='font-size: 0.9rem; color: #64748B;'>{data['keyword']}</div></div>", unsafe_allow_html=True)
    with col_btn:
        st.button("← กลับแผนที่", on_click=change_page, args=('map',), use_container_width=True)
    
    # 2. นำ Metrics พ.ร.บ. และ AI Analysis มาวางคู่กัน ซ้าย-ขวา เพื่อประหยัดพื้นที่แนวตั้ง
    col_stat, col_ai = st.columns([1, 1.5])
    
    with col_stat:
        st.markdown("<h3>📄 สถานะ พ.ร.บ.</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("ทั้งหมด", f"{data['bill_stats']['total']}")
        c2.metric("ผ่าน ✅", f"{data['bill_stats']['passed']}")
        c3.metric("ตก ❌", f"{data['bill_stats']['failed']}")

    with col_ai:
        st.markdown("<h3>✨ AI Analysis</h3>", unsafe_allow_html=True)
        with st.spinner("Analyzing..."):
            summary = get_ai_summary(data['keyword'])
            st.markdown(f"<div class='ai-report-box'><p>{summary}</p></div>", unsafe_allow_html=True)

    # 3. กราฟ Visualization (ลดความสูงลง)
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
    
    # ลดความสูงกราฟลงเหลือ 250 (height=250) และบีบ Margin
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