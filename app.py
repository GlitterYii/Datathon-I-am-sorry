import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
import os

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="JUST-JEE City Exploration", layout="wide", page_icon="🏙️", initial_sidebar_state="collapsed")

GEMINI_API_KEY = "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8" 

if GEMINI_API_KEY != "AIzaSyD8dkFu8Si2j9bTr7at9BINy3MCKueCCg8":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 2. Navigation Logic & State ---
if "item" in st.query_params:
    item_val = st.query_params["item"]
    st.session_state.view = 'dash'
    st.session_state.item = item_val
    st.query_params.clear() 

if 'view' not in st.session_state: st.session_state.view = 'intro'
if 'intro_step' not in st.session_state: st.session_state.intro_step = 1
if 'item' not in st.session_state: st.session_state.item = None

def change_page(v, i=None):
    st.session_state.view = v
    st.session_state.item = i
    st.query_params.clear()

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
        "keywords": {"คนพิการ": [],"ผู้ทุพลภาพ": [], "กลุ่มเปราะบาง": []}
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

for key, val in objects_data.items():
    if "bill_stats" not in val:
        val["bill_stats"] = {"total": 12, "passed": 8, "failed": 4}
    if "vote_details" not in val:
        val["vote_details"] = {
            "พรรคก้าวไกล": {"เห็นชอบ": 85, "ไม่เห็นชอบ": 10, "งดออกเสียง": 5},
            "พรรคเพื่อไทย": {"เห็นชอบ": 75, "ไม่เห็นชอบ": 15, "งดออกเสียง": 10},
            "พรรคภูมิใจไทย": {"เห็นชอบ": 40, "ไม่เห็นชอบ": 50, "งดออกเสียง": 10}
        }

objects_config = {
    "การศึกษา/โรงเรียน": {"img": "school.png", "top": "7%", "left": "5%", "width": "20%"},
    "ถนน": {"img": "road.png", "top": "25%", "left": "25%", "width": "15%"},
    "ยานพาหนะ": {"img": "bus.png", "top": "50%", "left": "27%", "width": "10%"},
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": {"img": "factory.png", "top": "1%", "left": "40%", "width": "20%"},
    "อาหารและเครื่องดื่ม": {"img": "restaurant.png", "top": "1%", "left": "60%", "width": "20%"},
    "น้ำ": {"img": "sea.png", "top": "20%", "left": "83%", "width": "18%"},
    "โรงพยาบาล": {"img": "hospital.png", "top": "43%", "left": "60%", "width": "23%"},
    "สัตว์เลี้ยง": {"img": "petshop.png", "top": "70%", "left": "43%", "width": "18%"},
    "สายอาร์ต": {"img": "art.png", "top": "50%", "left": "13%", "width": "15%"},
    "อินเตอร์เน็ต": {"img": "computer.png", "top": "80%", "left": "15%", "width": "15%"},
    "ต้นไม้": {"img": "park.png", "top": "25%", "left": "2%", "width": "20%"},
    "คนพิการ": {"img": "wheelchair.png", "top": "45%", "left": "50%", "width": "10%"},
    "ยาเสพติด/สุรา": {"img": "drunk.png", "top": "75%", "left": "63%", "width": "15%"},
    "เครื่องสำอางค์": {"img": "makeup.png", "top": "75%", "left": "0%", "width": "15%"},
    "พลังงาน/ไฟฟ้า": {"img": "power.png", "top": "25%", "left": "20%", "width": "12%"},
    "คน": {"img": "human.png", "top": "45%", "left": "40%", "width": "12%"},
}

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

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; max-width: 100%; }
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def render_intro_view():
    intro_placeholder = st.empty()

    with intro_placeholder.container():
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


            # 3. หุ้มฟังก์ชัน start_app เพื่อสั่งล้างหน้าจอก่อน
            def handle_start():
                intro_placeholder.empty() # สั่งลบ UI ของ Intro ทันทีที่กดปุ่ม
                start_app()  

            st.button("🚀 เข้าสู่เมือง (Press Space)", on_click=handle_start)
            st.caption("Interactive exploration of parliamentary decisions in everyday life")

        dots = ["○","○","○"]
        dots[step-1] = "●"
        st.markdown(f"<div class='progress'>{' '.join(dots)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 7. ฟังก์ชันวาดหน้า Intro ---

# def render_intro_view():
#     # 1. สร้าง Placeholder คลุมไว้ตั้งแต่เริ่ม
#     intro_placeholder = st.empty()
    
#     # 2. เอาเนื้อหาทั้งหมดไปใส่ไว้ใน container ของ placeholder
#     with intro_placeholder.container():
#         step = st.session_state.intro_step

#         st.markdown("""
#         <style>
#         /* ... ใส่ CSS เดิมของคุณทั้งหมดที่นี่ ... */
#         </style>
#         """, unsafe_allow_html=True)

#         components.html("""
#         <script>
#         /* ... ใส่ JS เดิมของคุณที่นี่ ... */
#         </script>
#         """, height=0, width=0)

#         st.markdown(f'<div class="intro-container page-step step-{step}">', unsafe_allow_html=True)

#         if step == 1:
#             # ... โค้ดเดิม ...
#             st.button("Press Space to continue ➔", on_click=next_intro_step)
#         elif step == 2:
#             # ... โค้ดเดิม ...
#             st.button("Press Space to continue ➔", on_click=next_intro_step)
#         elif step == 3:
#             st.markdown('<div class="intro-hook">ยินดีต้อนรับสู่<br><span class="highlight">JUST-JEE CITY</span></div>', unsafe_allow_html=True)
#             st.markdown('<div class="intro-text">แผนที่ของกฎหมายในชีวิตประจำวัน<br><br>เมืองที่คุณอาศัยอยู่<br>ถูกสร้างขึ้นจาก <b>เสียงโหวตของใคร?</b></div>', unsafe_allow_html=True)
            
#             # 3. หุ้มฟังก์ชัน start_app เพื่อสั่งล้างหน้าจอก่อน
#             def handle_start():
#                 intro_placeholder.empty() # สั่งลบ UI ของ Intro ทันทีที่กดปุ่ม
#                 start_app()               # แล้วค่อยเปลี่ยน State ไปหน้า Map
                
#             st.button("🚀 เข้าสู่เมือง (Press Space)", on_click=handle_start)
#             st.caption("Interactive exploration of parliamentary decisions in everyday life")

#         dots = ["○","○","○"]
#         dots[step-1] = "●"
#         st.markdown(f"<div class='progress'>{' '.join(dots)}</div>", unsafe_allow_html=True)
#         st.markdown("</div>", unsafe_allow_html=True)

def apply_main_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
        .stApp { background-color: #FDFDFD; color: #000; }
        @keyframes pageTransition { 0% { opacity: 0; transform: translateY(15px); filter: blur(3px); } 100% { opacity: 1; transform: translateY(0); filter: blur(0px); } }
        .block-container { animation: pageTransition 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        h1 { color: #0F172A; font-weight: 600; text-align: center; letter-spacing: -1px; margin-top: 0; font-size: 2.5rem; margin-bottom: 0.5rem;}
        h3 { margin-bottom: 0.2rem !important; margin-top: 0.5rem !important; font-size: 1.1rem; color: #1E293B;}
        div.stButton > button:first-child { background-color: #FFFFFF; color: #1E293B !important; border: 1px solid #E2E8F0; border-radius: 6px; font-weight: 500; padding: 0.3rem 1rem; }
        .data-card { background-color: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 8px; padding: 10px 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        div[data-testid="metric-container"] { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 5px; text-align: center; margin-bottom: 0.5rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; }
        .ai-report-box { background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 10px 15px; border-radius: 4px; margin-bottom: 0.5rem; }
        .ai-note { font-size: 0.75rem; color: #94A3B8; text-align: center; margin-top: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

# --- 9. การแสดงผล (Main Controller) ---
if st.session_state.view == 'intro':
    render_intro_view()

elif st.session_state.view == 'map':
    apply_main_css()
    st.markdown("<h1>JUST-JEE City Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;'>คลิกเลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
    
    bg_b64 = get_image_base64("city_bg.png") 
    
    html_code = f"""
    <style>
    .map-container {{ position: relative; width: 100%; max-width: 1000px; margin: 0 auto; overflow: hidden; border-radius: 12px; }}
    .map-container img {{ transition: filter 0.3s ease, transform 0.3s ease; }}
    .map-container:hover .bg-img, .map-container:hover .obj-img {{ filter: grayscale(100%) opacity(0.8); }}
    .map-container .obj-link:hover .obj-img {{ filter: grayscale(0%) opacity(1) !important; transform: scale(1.1); drop-shadow: 0px 10px 15px rgba(0,0,0,0.3); }}
    .bg-img {{ width: 100%; height: auto; display: block; }}
    .obj-link {{ position: absolute; display: block; z-index: 10; cursor: pointer; }}
    .obj-img {{ width: 100%; height: auto; object-fit: contain; }}
    </style>
    <div class="map-container">
        <img class="bg-img" src="data:image/png;base64,{bg_b64}" alt="Background">
    """
    
    for item_name, conf in objects_config.items():
        obj_b64 = get_image_base64(conf["img"])
        img_src = f"data:image/png;base64,{obj_b64}" if obj_b64 else f"https://via.placeholder.com/150?text={item_name}"
        html_code += f'<a class="obj-link" href="?item={item_name}" target="_self" style="top: {conf["top"]}; left: {conf["left"]}; width: {conf["width"]};"><img class="obj-img" src="{img_src}" alt="{item_name}"></a>'
        
    html_code += "</div>"
    st.components.v1.html(html_code, height=700)

elif st.session_state.view == 'dash':
    apply_main_css()
    item = st.session_state.item
    # Fallback to defaults if not found
    data = objects_data.get(item, objects_data["การศึกษา/โรงเรียน"])
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หัวข้อหลัก: {data['keyword_default']}</p></div>", unsafe_allow_html=True)
    
    all_keywords = [data['keyword_default']] + list(data['keywords'].keys())
    all_keywords = list(dict.fromkeys(all_keywords))
    selected_keyword = st.selectbox("📌 เลือกหัวข้อย่อยเพื่อดูสรุปจาก AI:", all_keywords)
    
    col_stat, col_ai = st.columns([1, 1.5])
    
    with col_stat:
        st.markdown("<h3>📄 สถานะ พ.ร.บ. ที่เกี่ยวข้อง</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("ทั้งหมด", f"{data['bill_stats']['total']}")
        c2.metric("ผ่าน ✅", f"{data['bill_stats']['passed']}")
        c3.metric("ตก ❌", f"{data['bill_stats']['failed']}")

    with col_ai:
        st.markdown(f"<h3>✨ AI Analysis: {selected_keyword}</h3>", unsafe_allow_html=True)
        with st.spinner("Analyzing..."):
            summary = get_ai_summary(selected_keyword)
            st.markdown(f"<div class='ai-report-box'><p>{summary}</p></div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("<h3>🗳️ Vote Distribution by Political Parties (%)</h3>", unsafe_allow_html=True)
    
    rows = []
    for party, votes in data['vote_details'].items():
        for vote_type, percentage in votes.items():
            rows.append({'Party': party, 'Vote Type': vote_type, 'Percentage': percentage})
    df_votes = pd.DataFrame(rows)

    party_order = sorted(data['vote_details'].keys(), key=lambda p: data['vote_details'][p].get('เห็นชอบ', 0))
    
    fig = px.bar(df_votes, x='Percentage', y='Party', color='Vote Type', orientation='h', 
                 color_discrete_map={"เห็นชอบ": "#2ECC71", "ไม่เห็นชอบ": "#E74C3C", "งดออกเสียง": "#94A3B8"},
                 text_auto=True)
    
    fig.update_layout(
        xaxis_title="ร้อยละ (%)", yaxis_title="", 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        barmode='stack',
        yaxis={'categoryorder': 'array', 'categoryarray': party_order},
        legend_title_text="ประเภทการลงมติ",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=10, l=10, r=10),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ</div>", unsafe_allow_html=True)