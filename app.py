import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import base64
import os

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="JUST-JEE City Exploration", layout="wide", page_icon="🏙️")

GEMINI_API_KEY = "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8" 

if GEMINI_API_KEY != "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 2. การจัดการ Navigation ด้วย Query Params (เมื่อคลิกรูป) ---
# ถ้ามีการส่งค่า item ผ่าน URL ให้เปลี่ยนไปหน้า Dash ทันที
if "item" in st.query_params:
    item_val = st.query_params["item"]
    st.session_state.view = 'dash'
    st.session_state.item = item_val
    st.query_params.clear() # เคลียร์ URL ให้สะอาด

if 'view' not in st.session_state: st.session_state.view = 'map'
if 'item' not in st.session_state: st.session_state.item = None

def change_page(v, i=None):
    st.session_state.view = v
    st.session_state.item = i
    st.query_params.clear()

# --- 3. Custom CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
    .stApp { background-color: #FDFDFD; }
    h1 { color: #0F172A; font-weight: 600; text-align: center; margin-top: 2rem; }
    
    div.stButton > button:first-child {
        background-color: #FFFFFF; color: #1E293B !important;
        border: 1px solid #E2E8F0; border-radius: 8px; font-weight: 500;
        padding: 0.5rem 1.5rem; transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover { border-color: #0F172A; background-color: #F8FAFC; }
    .data-card { background-color: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 12px; padding: 24px; }
    div[data-testid="metric-container"] { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ข้อมูล 15 วัตถุ ---
# โครงสร้างสำหรับเก็บไฟล์รูปและพิกัดบนหน้าจอ (แก้ % top/left ให้ตรงกับรูปของคุณ)
objects_config = {
    "โรงเรียน": {"img": "school.png", "top": "7%", "left": "5%", "width": "20%"},
    "ถนน": {"img": "road.png", "top": "25%", "left": "25%", "width": "15%"},
    "รถบัส": {"img": "bus.png", "top": "40%", "left": "27%", "width": "10%"},
    "โรงงาน": {"img": "factory.png", "top": "1%", "left": "40%", "width": "20%"},
    "ร้านอาหาร": {"img": "restaurant.png", "top": "1%", "left": "60%", "width": "20%"},
    "ทะเลและเรือ": {"img": "sea.png", "top": "20%", "left": "83%", "width": "18%"},
    "โรงพยาบาล": {"img": "hospital.png", "top": "43%", "left": "60%", "width": "23%"},
    "ร้านสัตว์เลี้ยง": {"img": "petshop.png", "top": "70%", "left": "43%", "width": "18%"},
    "ศิลปะ": {"img": "art.png", "top": "50%", "left": "13%", "width": "15%"},
    "คอมพิวเตอร์": {"img": "computer.png", "top": "80%", "left": "5%", "width": "15%"},
    "สวนสาธารณะ": {"img": "park.png", "top": "25%", "left": "3%", "width": "20%"},
    "คนพิการ": {"img": "wheelchair.png", "top": "45%", "left": "50%", "width": "10%"},
    "สุราก้าวหน้า": {"img": "drunk.png", "top": "75%", "left": "63%", "width": "15%"},
    "ความงาม": {"img": "makeup.png", "top": "73%", "left": "0%", "width": "15%"},
    "พลังงาน": {"img": "power.png", "top": "15%", "left": "65%", "width": "12%"},
    "คน": {"img": "human.png", "top": "45%", "left": "40%", "width": "12%"},
}

# (Mock Data สำหรับ 15 หมวด - ระบบจะใช้ค่านี้เป็น Default ถ้าไม่ได้แก้)
default_vote = {"ก้าวไกล": {"เห็นชอบ": 90, "ไม่เห็นชอบ": 5, "งดออกเสียง": 5}, "เพื่อไทย": {"เห็นชอบ": 80, "ไม่เห็นชอบ": 15, "งดออกเสียง": 5}}
objects_data = {key: {"keyword": f"ร่าง พ.ร.บ. เกี่ยวกับ{key}", "bill_stats": {"total": 5, "passed": 2, "failed": 3}, "vote_details": default_vote} for key in objects_config.keys()}

# ฟังก์ชันแปลงรูปภาพเป็น Base64 เพื่อให้ฝังใน HTML ได้
def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_ai_summary(keyword):
    if model:
        try: return model.generate_content(f"สรุปเนื้อหาสำคัญของ '{keyword}' สำหรับประชาชนทั่วไปใน 3 บรรทัด").text
        except: return "ระบบ AI ไม่สามารถประมวลผลได้"
    return "โปรดตั้งค่า API Key"

# --- 5. หน้าแผนที่หลัก ---
if st.session_state.view == 'map':
    st.markdown("<h1>JUST-JEE City Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 2rem;'>เลือกสำรวจนโยบายโดยชี้และคลิกที่สิ่งของต่างๆ</p>", unsafe_allow_html=True)
    
    # ดึงรูปพื้นหลัง
    bg_b64 = get_image_base64("city_bg.png") 
    
    # สร้าง HTML + CSS สำหรับเอฟเฟกต์ Hover
    html_code = f"""
    <style>
    .map-container {{ position: relative; width: 100%; max-width: 1000px; margin: 0 auto; overflow: hidden; border-radius: 12px; }}
    .map-container img {{ transition: filter 0.3s ease, transform 0.3s ease; }}
    
    /* เมื่อเอาเมาส์ชี้ในพื้นที่ Container -> ให้รูป Background และ Object ทั้งหมดกลายเป็นสีเทา */
    .map-container:hover .bg-img,
    .map-container:hover .obj-img {{ filter: grayscale(100%) opacity(0.8); }}
    
    /* ยกเว้นรูปที่กำลังถูกเอาเมาส์ชี้ (Hover) -> ให้กลับมามีสีปกติและขยายขึ้นนิดหน่อย */
    .map-container .obj-link:hover .obj-img {{ filter: grayscale(0%) opacity(1) !important; transform: scale(1.1); drop-shadow: 0px 10px 15px rgba(0,0,0,0.3); }}
    
    .bg-img {{ width: 100%; height: auto; display: block; }}
    .obj-link {{ position: absolute; display: block; z-index: 10; cursor: pointer; }}
    .obj-img {{ width: 100%; height: auto; object-fit: contain; }}
    </style>
    
    <div class="map-container">
        <img class="bg-img" src="data:image/png;base64,{bg_b64}" alt="Background">
    """
    
    # วนลูปวางรูปวัตถุทั้ง 15 ชิ้นลงบนพิกัด
    for item_name, conf in objects_config.items():
        obj_b64 = get_image_base64(conf["img"])
        # ถ้าหาไฟล์ไม่เจอ จะใช้รูป Placeholder แทน
        img_src = f"data:image/png;base64,{obj_b64}" if obj_b64 else f"https://via.placeholder.com/150?text={item_name}"
        
        # ใส่ Link ?item=ชื่อวัตถุ เพื่อให้ Streamlit รีเฟรชหน้าแล้วจับ Parameter ได้
        html_code += f"""
        <a class="obj-link" href="?item={item_name}" target="_self" style="top: {conf['top']}; left: {conf['left']}; width: {conf['width']};">
            <img class="obj-img" src="{img_src}" alt="{item_name}">
        </a>
        """
        
    html_code += "</div>"
    
    # แสดงผล HTML
    st.components.v1.html(html_code, height=700)

# --- 6. หน้า Dashboard (หน้าข้อมูล) ---
elif st.session_state.view == 'dash':
    item = st.session_state.item
    data = objects_data.get(item, objects_data["โรงเรียน"]) # ถ้าไม่เจอให้แสดงค่า Default
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หัวข้อ: {data['keyword']}</p></div>", unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("📄 สถานะร่าง พ.ร.บ. ที่เกี่ยวข้อง")
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวน พ.ร.บ. ทั้งหมด", f"{data['bill_stats']['total']} ฉบับ")
    c2.metric("ผ่านการเห็นชอบ ✅", f"{data['bill_stats']['passed']} ฉบับ")
    c3.metric("ไม่ผ่านการเห็นชอบ ❌", f"{data['bill_stats']['failed']} ฉบับ")

    st.write("<br>", unsafe_allow_html=True)
    st.subheader("✨ AI Analysis Report")
    with st.spinner("Analyzing data with Gemini 1.5 Flash..."):
        summary = get_ai_summary(data['keyword'])
        st.markdown(f"<div style='background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 1.5rem; border-radius: 4px;'>{summary}</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("🗳️ Vote Distribution by Political Parties (%)")
    
    rows = []
    for party, votes in data['vote_details'].items():
        for vote_type, percentage in votes.items():
            rows.append({'Party': party, 'Vote Type': vote_type, 'Percentage': percentage})
    df_votes = pd.DataFrame(rows)

    party_order = sorted(data['vote_details'].keys(), key=lambda p: data['vote_details'][p].get('เห็นชอบ', 0))
    fig = px.bar(df_votes, x='Percentage', y='Party', color='Vote Type', orientation='h', 
                 color_discrete_map={"เห็นชอบ": "#2ECC71", "ไม่เห็นชอบ": "#E74C3C", "งดออกเสียง": "#94A3B8"}, text_auto=True)
    
    fig.update_layout(xaxis_title="ร้อยละ (%)", yaxis_title="", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      barmode='stack', yaxis={'categoryorder': 'array', 'categoryarray': party_order},
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=450)
    st.plotly_chart(fig, use_container_width=True)