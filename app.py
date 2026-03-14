import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="JUST-JEE City Exploration", layout="wide", page_icon="🏙️")

# ใส่ API Key ของคุณที่นี่
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" 

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 2. Custom CSS (Minimal Modern & Image Responsive) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }
    
    .stApp {
        background-color: #FDFDFD;
    }

    h1 {
        color: #0F172A;
        font-weight: 600;
        text-align: center;
        letter-spacing: -1px;
        margin-top: 2rem;
        font-size: 2.5rem;
    }

    /* จำกัดขนาดรูปภาพให้พอดีเฟรม ไม่ล้นจอ */
    .img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        max-width: 100%;
        overflow: hidden;
    }
    
    /* ปรับแต่งปุ่มให้ดูแพง */
    div.stButton > button:first-child {
        background-color: #FFFFFF;
        color: #1E293B !important;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    div.stButton > button:first-child:hover {
        border-color: #0F172A;
        background-color: #F8FAFC;
        transform: translateY(-1px);
    }

    /* กล่องข้อมูล (Card Style) */
    .data-card {
        background-color: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    .ai-note {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 3rem;
        text-align: center;
        border-top: 1px solid #F1F5F9;
        padding-top: 1rem;
    }

    hr { border-top: 1px solid #F1F5F9; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ข้อมูลรายพรรคการเมือง ---
objects_data = {
    "พลังงาน/ไฟฟ้า": {
        "keyword": "ร่าง พ.ร.บ. การประกอบกิจการพลังงาน (ฉบับแก้ไข)",
        "votes": {"พรรคก้าวไกล": 95, "พรรคเพื่อไทย": 88, "พรรคภูมิใจไทย": 40, "พรรครวมไทยสร้างชาติ": 15, "พรรคประชาธิปัตย์": 30}
    },
    "โรงพยาบาล": {
        "keyword": "ร่าง พ.ร.บ. สถานพยาบาล และสิทธิผู้ป่วย",
        "votes": {"พรรคก้าวไกล": 85, "พรรคเพื่อไทย": 95, "พรรคภูมิใจไทย": 90, "พรรครวมไทยสร้างชาติ": 70, "พรรคประชาธิปัตย์": 65}
    },
    "ร้านอาหาร": {
        "keyword": "ร่าง พ.ร.บ. การสาธารณสุข และความปลอดภัยด้านอาหาร",
        "votes": {"พรรคเพื่อไทย": 90, "พรรคภูมิใจไทย": 85, "พรรคประชาธิปัตย์": 60, "พรรคก้าวไกล": 55, "พรรครวมไทยสร้างชาติ": 40}
    },
    "เรื่องน้ำ/ทะเล": {
        "keyword": "ร่าง พ.ร.บ. การเดินเรือในน่านน้ำไทย และการจัดการทรัพยากรทางทะเล",
        "votes": {"พรรคก้าวไกล": 85, "พรรคประชาธิปัตย์": 75, "พรรคเพื่อไทย": 40, "พรรคภูมิใจไทย": 30, "พรรครวมไทยสร้างชาติ": 20}
    },
    "สัตว์เลี้ยง": {
        "keyword": "ร่าง พ.ร.บ. คุ้มครองและสวัสดิภาพสัตว์เลี้ยง",
        "votes": {"พรรคก้าวไกล": 92, "พรรคเพื่อไทย": 80, "พรรคภูมิใจไทย": 75, "พรรคประชาธิปัตย์": 60, "พรรครวมไทยสร้างชาติ": 45}
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

# --- 5. Navigation Logic ---
if 'view' not in st.session_state: st.session_state.view = 'map'
if 'item' not in st.session_state: st.session_state.item = None

def change_page(v, i=None):
    st.session_state.view = v
    st.session_state.item = i

# --- 6. ฟังก์ชันสรุปโดย Gemini ---
def get_ai_summary(keyword):
    if model:
        try:
            prompt = f"สรุปเนื้อหาสำคัญของ '{keyword}' สำหรับประชาชนทั่วไปใน 3 บรรทัด สไตล์มินิมอลและดูน่าเชื่อถือ"
            return model.generate_content(prompt).text
        except: return "ขออภัย ระบบ AI ไม่สามารถประมวลผลได้ในขณะนี้"
    return "โปรดตั้งค่า API Key เพื่อเปิดใช้งานบทสรุปจาก AI"

# --- 7. การแสดงผล ---
if st.session_state.view == 'map':
    st.markdown("<h1>JUST-JEE City Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;'>เลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
    
    # ใช้ Column และ CSS Container เพื่อคุมขนาดรูปภาพ
    _, col_img, _ = st.columns([0.5, 9, 0.5])
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
    item = st.session_state.item
    data = objects_data.get(item, list(objects_data.values())[0])
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หัวข้อ: {data['keyword']}</p></div>", unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("🗳️ Approval Rate by Political Parties (%)")
    
    df_votes = pd.DataFrame(list(data['votes'].items()), columns=['Party', 'Approval']).sort_values(by='Approval', ascending=True)
    
    fig = px.bar(df_votes, x='Approval', y='Party', orientation='h', 
                 color='Approval', color_continuous_scale='Blues',
                 text_auto=True)
    
    fig.update_layout(
        xaxis_title="", yaxis_title="", 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("<br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 1])
    with col_btn:
        st.button("🔍 ANALYZE WITH AI", on_click=change_page, args=('detail', item))

elif st.session_state.view == 'detail':
    item = st.session_state.item
    keyword = objects_data[item]['keyword']
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO DASHBOARD", on_click=change_page, args=('dash', item))
    
    st.markdown(f"<div class='data-card'><h2 style='margin-bottom:0;'>AI Analysis Report</h2><p style='color: #64748B;'>Issue: {item}</p></div>", unsafe_allow_html=True)
    
    with st.spinner("Analyzing data with Gemini 1.5 Flash..."):
        summary = get_ai_summary(keyword)
        st.markdown(f"""
            <div style='background-color: #FFFFFF; border-left: 4px solid #0F172A; padding: 2rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                <p style='line-height: 1.8; color: #1E293B; font-size: 1.15rem;'>{summary}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='ai-note'>* ข้อมูลนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ แนะนำให้ตรวจสอบกับเอกสารทางการเพิ่มเติม</div>", unsafe_allow_html=True)