import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="JUST-JEE City Exploration", layout="wide", page_icon="🏙️")

# ใส่ API Key ของคุณที่นี่
GEMINI_API_KEY = "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8" 

if GEMINI_API_KEY != "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8":
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

    .img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        max-width: 100%;
        overflow: hidden;
    }
    
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

    .data-card {
        background-color: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    /* ตกแต่งกล่อง Metric สำหรับจำนวน พรบ. */
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }

    .ai-note {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 3rem;
        text-align: center;
        border-top: 1px solid #F1F5F9;
        padding-top: 1rem;
    }

    hr { border-top: 1px solid #F1F5F9; margin: 2rem 0; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ข้อมูลจำลอง (เพิ่ม Stat พ.ร.บ. และรายละเอียดการโหวต) ---
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
    
    # 1. ปุ่มย้อนกลับ
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
    # 2. หัวข้อหลัก
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หัวข้อ: {data['keyword']}</p></div>", unsafe_allow_html=True)
    
    # 3. จำนวนสถิติ พ.ร.บ. (เพิ่มใหม่)
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("📄 สถานะร่าง พ.ร.บ. ที่เกี่ยวข้อง")
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวน พ.ร.บ. ทั้งหมด", f"{data['bill_stats']['total']} ฉบับ")
    c2.metric("ผ่านการเห็นชอบ ✅", f"{data['bill_stats']['passed']} ฉบับ")
    c3.metric("ไม่ผ่านการเห็นชอบ ❌", f"{data['bill_stats']['failed']} ฉบับ")

    # 4. AI Analysis (ย้ายมาก่อนกราฟ)
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("✨ AI Analysis Report")
    with st.spinner("Analyzing data with Gemini 1.5 Flash..."):
        summary = get_ai_summary(data['keyword'])
        st.markdown(f"""
            <div style='background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 1.5rem; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 1rem;'>
                <p style='line-height: 1.8; color: #1E293B; font-size: 1.05rem; margin: 0;'>{summary}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # 5. กราฟ Visualization แบบแบ่ง เห็นชอบ / ไม่เห็นชอบ / งดออกเสียง
    st.subheader("🗳️ Vote Distribution by Political Parties (%)")
    
    # แปลงข้อมูลซ้อนให้อยู่ในรูปแบบตาราง (DataFrame)
    rows = []
    for party, votes in data['vote_details'].items():
        for vote_type, percentage in votes.items():
            rows.append({'Party': party, 'Vote Type': vote_type, 'Percentage': percentage})
    df_votes = pd.DataFrame(rows)

    # จัดเรียงพรรคตามเปอร์เซ็นต์ "เห็นชอบ" จากมากไปน้อย
    party_order = sorted(data['vote_details'].keys(), key=lambda p: data['vote_details'][p]['เห็นชอบ'])
    
    # สร้าง Stacked Bar Chart ด้วย Plotly
    fig = px.bar(df_votes, x='Percentage', y='Party', color='Vote Type', orientation='h', 
                 color_discrete_map={
                     "เห็นชอบ": "#2ECC71",     # สีเขียว
                     "ไม่เห็นชอบ": "#E74C3C",   # สีแดง
                     "งดออกเสียง": "#94A3B8"    # สีเทา
                 },
                 text_auto=True)
    
    fig.update_layout(
        xaxis_title="ร้อยละ (%)", yaxis_title="", 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        barmode='stack',  # ให้แท่งกราฟต่อกัน (Stacked)
        yaxis={'categoryorder': 'array', 'categoryarray': party_order},
        legend_title_text="ประเภทการลงมติ",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=10, l=10, r=10),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 6. หมายเหตุ
    st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ แนะนำให้ตรวจสอบกับเอกสารทางการเพิ่มเติม</div>", unsafe_allow_html=True)