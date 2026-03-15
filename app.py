import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
import os
import ast
import plotly.graph_objects as go

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
<<<<<<< HEAD
st.set_page_config(page_title="POLITILAND Exploration", layout="wide", page_icon="🏙️", initial_sidebar_state="collapsed")
=======
st.set_page_config(page_title="Politiland Exploration", layout="wide", page_icon="🏙️", initial_sidebar_state="collapsed")
>>>>>>> main

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

# 🌟 ดึงค่าจากการคลิกและเปลี่ยนหน้า
if "item" in st.query_params:
    st.session_state.item = st.query_params["item"]
    st.session_state.view = 'dash'
    st.query_params.clear()

def change_page(v, i=None):
    st.session_state.view = v
    st.session_state.item = i
    st.query_params.clear()

def next_intro_step():
    st.session_state.intro_step += 1

def start_app():
    st.session_state.view = 'map'

# --- 3. โหลดข้อมูลจากไฟล์ CSV และ Mapping ---
@st.cache_data
def load_vote_data():
    try:
        df = pd.read_csv('final_classified_qwen_v2.csv')
        # เปลี่ยนเป็นแปลงข้อมูลในคอลัมน์ party_votes_json แทน
        if 'party_votes_json' in df.columns:
            df['party_votes_json'] = df['party_votes_json'].apply(lambda x: ast.literal_eval(str(x)) if pd.notnull(x) and str(x).strip() != '' else {})
        return df
    except Exception as e:
        st.warning(f"ไม่สามารถโหลดไฟล์ final_classified_qwen_v2.csv ได้: {e}")
        return pd.DataFrame()

df_votes_data = load_vote_data()

# Mapping ระหว่าง Object ที่คลิก กับ หมวดหมู่ในไฟล์ CSV
ITEM_TO_CATEGORY = {
    "การศึกษา/โรงเรียน": "หมวดการศึกษาและสังคม",
    "ถนน": "หมวดคมนาคมและการขนส่ง",
    "ยานพาหนะ": "หมวดคมนาคมและการขนส่ง",
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": "หมวดอุตสาหกรรมและพลังงาน",
    "อาหารและเครื่องดื่ม": "หมวดอุตสาหกรรมและพลังงาน",
    "น้ำ": "หมวดทรัพยากรธรรมชาติและสิ่งแวดล้อม",
    "โรงพยาบาล": "หมวดสุขภาพและสาธารณสุข",
    "สัตว์เลี้ยง": "หมวดสุขภาพและสาธารณสุข",
    "สายอาร์ต": "หมวดศิลปะและเศรษฐกิจสร้างสรรค์",
    "อินเตอร์เน็ต": "หมวดเทคโนโลยีและข้อมูล",
    "ต้นไม้": "หมวดทรัพยากรธรรมชาติและสิ่งแวดล้อม",
    "คนพิการ": "หมวดบุคคลและสถานะ",
    "ยาเสพติด/สุรา": "หมวดสิ่งมึนเมาและสารสกัด",
    "เครื่องสำอางค์": "หมวดสิ่งมึนเมาและสารสกัด",
    "พลังงาน/ไฟฟ้า": "หมวดอุตสาหกรรมและพลังงาน",
    "คน": "หมวดบุคคลและสถานะ"
}

# --- 4. ข้อมูลจำลอง (เก็บไว้สำหรับส่วนของจำนวน พ.ร.บ. ที่ยังไม่มีใน CSV) ---
objects_data = {
<<<<<<< HEAD
    "คน": {"keyword_default": "อาชีพ"},
    "คนพิการ": {"keyword_default": "คนพิการ"},
    "ยานพาหนะ": {"keyword_default": "จราจร"},
    "ถนน": {"keyword_default": "ทางหลวง"},
    "ต้นไม้": {"keyword_default": "ป่าไม้"},
    "อาหารและเครื่องดื่ม": {"keyword_default": "อาหาร"},
    "อินเตอร์เน็ต": {"keyword_default": "อินเทอร์เน็ต"},
    "ยาเสพติด/สุรา": {"keyword_default": "สุรา"},
    "สายอาร์ต": {"keyword_default": "ลิขสิทธิ์"},
    "น้ำ": {"keyword_default": "ทรัพยากรน้ำ"},
    "สัตว์เลี้ยง": {"keyword_default": "สัตว์เลี้ยง"},
    "โรงพยาบาล": {"keyword_default": "สถานพยาบาล"},
    "การศึกษา/โรงเรียน": {"keyword_default": "การศึกษา"},
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": {"keyword_default": "โรงงาน"},
    "พลังงาน/ไฟฟ้า": {"keyword_default": "พลังงาน"},
    "เครื่องสำอางค์": {"keyword_default": "เครื่องสำอาง"}
=======
    "คน": {"keyword_default": "อาชีพ", "keywords": {"อาชีพ": [], "การจ้างงาน": [], "PDPA": [], "สถานะของบุคคล": []}},
    "คนพิการ": {"keyword_default": "คนพิการ", "keywords": {"คนพิการ": [],"ผู้ทุพลภาพ": [], "กลุ่มเปราะบาง": []}},
    "ยานพาหนะ": {"keyword_default": "จราจร", "keywords": {"จราจร": [], "ขนส่ง": [], "รถยนต์": []}},
    "ถนน": {"keyword_default": "ทางหลวง", "keywords": {"ทางหลวง": [], "จราจรทางบก": [], "ขนส่งทางบก": [], "ความปลอดภัยทางถนน": [], "ผังเมือง": [], "ยานพาหนะ": [], "คมนาคม": []}},
    "ต้นไม้": {"keyword_default": "ป่าไม้", "keywords": {"ป่าไม้": [], "ป่าชุมชน": [], "อุทยานแห่งชาติ": [], "ป่าสงวน": [], "ที่ดิน": []}},
    "อาหารและเครื่องดื่ม": {"keyword_default": "อาหาร", "keywords": {"อาหาร": [], "เครื่องดื่ม": [], "โภชนาการ": [], "สุขาภิบาลอาหาร": []}},
    "อินเตอร์เน็ต": {"keyword_default": "อินเทอร์เน็ต", "keywords": {"อินเทอร์เน็ต": [], "ดิจิทัล": [], "โทรคมนาคม": [], "โทรศัพท์": [], "อาชญากรรมทางเทคโนโลยี": []}},
    "ยาเสพติด/สุรา": {"keyword_default": "สุรา", "keywords": {"สุรา": [], "สรรพสามิต": [], "เครื่องดื่มแอลกอฮอล์": [], "อาหารปลอดภัย": [], "ผลิตสุรา": [], "สุราก้าวหน้า": [], "ผู้ผลิตรายย่อย": [], "กัญชา": [], "สารเสพติด": []}},
    "สายอาร์ต": {"keyword_default": "ลิขสิทธิ์", "keywords": {"วัฒนธรรมสร้างสรรค์": [], "ซอฟต์พาวเวอร์": [], "ศิลปะ": [], "ศิลปิน": [], "ภาพยนตร์": [], "ลิขสิทธิ์": [], "ทรัพย์สินทางปัญญา": [], "เศรษฐกิจสร้างสรรค์": []}},
    "น้ำ": {"keyword_default": "ทรัพยากรน้ำ", "keywords": {"ทรัพยากรน้ำ": [], "ชายฝั่ง": [], "ทะเล": [], "น้ำบาดาล": [], "บำบัดน้ำ": [], "การประมง": []}},
    "สัตว์เลี้ยง": {"keyword_default": "สัตว์เลี้ยง", "keywords": {"สัตว์เลี้ยง": [], "ทารุณกรรมสัตว์": [], "สวัสดิภาพสัตว์": []}},
    "โรงพยาบาล": {"keyword_default": "สถานพยาบาล", "keywords": {"สถานพยาบาล": [], "สาธารณสุข": [], "ผู้ป่วย": [], "ยา": []}},
    "การศึกษา/โรงเรียน": {"keyword_default": "การศึกษา", "keywords": {"การศึกษา": [], "กยศ": [], "สิทธิเด็ก": [], "สถานศึกษา": []}},
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": {"keyword_default": "โรงงาน", "keywords": {"โรงงาน": [], "สารมลพิษ": [], "วัตถุอันตราย": [], "ผังเมือง": [], "PRTR": []}},
    "พลังงาน/ไฟฟ้า": {"keyword_default": "พลังงาน", "keywords": {"พลังงาน": [], "ไฟฟ้า": [], "พลังงานหมุนเวียน": [], "พลังงานสะอาด": []}},
    "เครื่องสำอางค์": {"keyword_default": "เครื่องสำอาง", "keywords": {"เครื่องสำอาง": [], "สรรพสามิต": [], "ความปลอดภัยของเครื่องสำอาง": []}}
>>>>>>> main
}

for key, val in objects_data.items():
    if "bill_stats" not in val:
        val["bill_stats"] = {"total": 12, "passed": 8, "failed": 4}

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

<<<<<<< HEAD
    if step == 1:
        st.markdown('<div class="intro-hook">กฎหมายไม่ได้อยู่แค่ในรัฐสภา<br>แต่มันอยู่ใน <span class="highlight">ทุกวันของชีวิตคุณ</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">เคยสงสัยไหมว่า...<br><br>ไฟฟ้าที่คุณใช้<br>โรงพยาบาลที่คุณไป<br>หรืออาหารที่คุณกิน<br><br>ทั้งหมดถูกกำหนดโดย <b>การโหวตในรัฐสภา</b></div>', unsafe_allow_html=True)
        st.button("Press Space to continue ➔", on_click=next_intro_step)
    elif step == 2:
        st.markdown('<div class="intro-hook">ทุกพื้นที่ของเมือง<br>ถูกขับเคลื่อนด้วย <span class="warning-highlight">กฎหมาย</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">กฎหมายไม่ใช่เรื่องไกลตัว<br>และไม่ใช่แค่เอกสารในสภา<br><br>แต่มันคือตัวกำหนด <b>คุณภาพชีวิตของคุณ</b></div>', unsafe_allow_html=True)
        st.button("Press Space to continue ➔", on_click=next_intro_step)
    elif step == 3:
        st.markdown('<div class="intro-hook">ยินดีต้อนรับสู่<br><span class="highlight">POLITILAND</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-text">แผนที่ของกฎหมายในชีวิตประจำวัน<br><br>เมืองที่คุณอาศัยอยู่<br>ถูกสร้างขึ้นจาก <b>เสียงโหวตของใคร?</b></div>', unsafe_allow_html=True)
        st.button("🚀 เข้าสู่เมือง (Press Space)", on_click=start_app)
        st.caption("Interactive exploration of parliamentary decisions in everyday life")
=======
        st.markdown(f'<div class="intro-container page-step step-{step}">', unsafe_allow_html=True)
>>>>>>> main

        if step == 1:
            st.markdown('<div class="intro-hook">กฎหมายไม่ได้อยู่แค่ในรัฐสภา<br>แต่มันอยู่ใน <span class="highlight">ทุกวันของชีวิตคุณ</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="intro-text">เคยสงสัยไหมว่า...<br><br>ไฟฟ้าที่คุณใช้<br>โรงพยาบาลที่คุณไป<br>หรืออาหารที่คุณกิน<br><br>ทั้งหมดถูกกำหนดโดย <b>การโหวตในรัฐสภา</b></div>', unsafe_allow_html=True)
            st.button("Press Space to continue ➔", on_click=next_intro_step)
        elif step == 2:
            st.markdown('<div class="intro-hook">ทุกพื้นที่ของเมือง<br>ถูกขับเคลื่อนด้วย <span class="warning-highlight">กฎหมาย</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="intro-text">กฎหมายไม่ใช่เรื่องไกลตัว<br>และไม่ใช่แค่เอกสารในสภา<br><br>แต่มันคือตัวกำหนด <b>คุณภาพชีวิตของคุณ</b></div>', unsafe_allow_html=True)
            st.button("Press Space to continue ➔", on_click=next_intro_step)
        elif step == 3:
            st.markdown('<div class="intro-hook">ยินดีต้อนรับสู่<br><span class="highlight">Politiland</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="intro-text">แผนที่ของกฎหมายในชีวิตประจำวัน<br><br>เมืองที่คุณอาศัยอยู่<br>ถูกสร้างขึ้นจาก <b>เสียงโหวตของใคร?</b></div>', unsafe_allow_html=True)

            def handle_start():
                intro_placeholder.empty() 
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
#             st.markdown('<div class="intro-hook">ยินดีต้อนรับสู่<br><span class="highlight">Politiland</span></div>', unsafe_allow_html=True)
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
        
        /* 🌟 เปลี่ยนสีพื้นหลังเป็น Dark Mode */
        .stApp { background-color: #0F172A; color: #F8FAFC; } 
        
        @keyframes pageTransition { 0% { opacity: 0; transform: translateY(15px); filter: blur(3px); } 100% { opacity: 1; transform: translateY(0); filter: blur(0px); } }
        
        .block-container { 
            animation: pageTransition 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; 
            padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; 
            max-width: 100%; 
        }
        
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 🌟 ปรับสีข้อความต่างๆ ให้สว่างขึ้น เพื่อให้อ่านได้บนพื้นหลังดำ */
        h1 { color: #FFFFFF; font-weight: 600; text-align: center; letter-spacing: -1px; margin-top: 0; font-size: 2.5rem; margin-bottom: 0.5rem;}
        h2 { color: #FFFFFF; }
        h3 { margin-bottom: 0.2rem !important; margin-top: 0.5rem !important; font-size: 1.1rem; color: #F1F5F9;}
        p { color: #CBD5E1; }
        
        /* 🌟 ปรับสีปุ่ม */
        div.stButton > button:first-child { background-color: #1E293B; color: #F8FAFC !important; border: 1px solid #334155; border-radius: 6px; font-weight: 500; padding: 0.3rem 1rem; }
        div.stButton > button:first-child:hover { background-color: #334155; border-color: #475569; }
        
        /* 🌟 ปรับสีกล่องการ์ดข้อมูลต่างๆ */
        .data-card { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 10px 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        .data-card p { color: #94A3B8; margin: 0; }
        
        div[data-testid="metric-container"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; margin-bottom: 0.5rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #FFFFFF; }
        div[data-testid="stMetricLabel"] { color: #94A3B8; }
        
        .ai-report-box { background-color: #1E293B; border-left: 4px solid #3B82F6; padding: 10px 15px; border-radius: 4px; margin-bottom: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #F1F5F9;}
        .ai-note { font-size: 0.75rem; color: #64748B; text-align: center; margin-top: 0.5rem; }
        
        /* 🌟 เปลี่ยนสีกรอบ Dropdown Selectbox */
        div[data-baseweb="select"] > div { background-color: #1E293B; border-color: #334155; color: #FFFFFF; }
        </style>
    """, unsafe_allow_html=True)

# --- 9. การแสดงผล (Main Controller) ---
if st.session_state.view == 'intro':
    render_intro_view()

elif st.session_state.view == 'map':
    apply_main_css()
<<<<<<< HEAD
    st.markdown("<h1>POLITILAND Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;'>คลิกเลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
=======
    st.markdown("<h1>Politiland Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 1.5rem;'>คลิกเลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
>>>>>>> main
    
    bg_b64 = get_image_base64("city_bg.png") 
    
    html_code = f"""
    <style>
    .map-container {{ position: relative; width: 100%; max-width: 1400px; margin: 0 auto; overflow: hidden; border-radius: 12px; }}
    .map-container img {{ transition: filter 0.3s ease, transform 0.3s ease; }}
    .map-container:hover .bg-img, .map-container:hover .obj-img {{ filter: grayscale(100%) opacity(0.8); }}
    .map-container .obj-link:hover .obj-img {{ filter: grayscale(0%) opacity(1) !important; transform: scale(1.1); drop-shadow: 0px 10px 15px rgba(0,0,0,0.5); }}
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
    
    st.markdown(html_code, unsafe_allow_html=True)

elif st.session_state.view == 'dash':
    apply_main_css()
    item = st.session_state.item
<<<<<<< HEAD
    target_category = ITEM_TO_CATEGORY.get(item, "ไม่พบหมวดหมู่")
    data_mock = objects_data.get(item, objects_data["การศึกษา/โรงเรียน"])
=======
    
    data = objects_data.get(item, objects_data["การศึกษา/โรงเรียน"])
>>>>>>> main
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
<<<<<<< HEAD
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หมวดหมู่ในสภา: {target_category}</p></div>", unsafe_allow_html=True)
=======
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p>หัวข้อหลัก: {data['keyword_default']}</p></div>", unsafe_allow_html=True)
>>>>>>> main
    
    # ------------------ กรองข้อมูลจาก CSV ------------------
    if not df_votes_data.empty and 'category' in df_votes_data.columns:
        df_filtered = df_votes_data[df_votes_data['category'] == target_category]
    else:
        df_filtered = pd.DataFrame()

<<<<<<< HEAD
    if df_filtered.empty:
        st.warning(f"ยังไม่มีข้อมูล พ.ร.บ. สำหรับหมวดหมู่ '{target_category}' ในขณะนี้")
    else:
        # สร้าง Dropdown ด้วยรายชื่อ Title ทั้งหมดในหมวดนี้
        titles_list = df_filtered['title'].unique().tolist()
        selected_title = st.selectbox("📌 เลือกร่าง พ.ร.บ. เพื่อดูผลการลงมติและสรุปจาก AI:", titles_list)
        
        # ดึงข้อมูลแถวของ Title ที่ถูกเลือก
        row_data = df_filtered[df_filtered['title'] == selected_title].iloc[0]
        
        # ดึงข้อมูลคะแนนโหวตจากคอลัมน์ party_votes_json แทน all_votes
        vote_dict = row_data.get('party_votes_json', {})
        
        # แสดง Stat & AI Summary
        col_stat, col_ai = st.columns([1, 1.5])
        
        with col_stat:
            st.markdown("<h3>📄 สถานะ พ.ร.บ. ที่เกี่ยวข้อง</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            # แสดงสถิติจำลองไปก่อน ถ้าในอนาคตมีข้อมูลจริงใน CSV ค่อยปรับแก้ได้
            c1.metric("ทั้งหมด", f"{data_mock['bill_stats']['total']}")
            c2.metric("ผ่าน ✅", f"{data_mock['bill_stats']['passed']}")
            c3.metric("ตก ❌", f"{data_mock['bill_stats']['failed']}")
=======
    with col_ai:
        st.markdown(f"<h3>✨ AI Analysis: {selected_keyword}</h3>", unsafe_allow_html=True)
        with st.spinner("Analyzing..."):
            summary = get_ai_summary(selected_keyword)
            st.markdown(f"<div class='ai-report-box'><p style='color: #F1F5F9;'>{summary}</p></div>", unsafe_allow_html=True)
>>>>>>> main

        with col_ai:
            st.markdown(f"<h3>✨ AI Analysis: สรุปนโยบาย</h3>", unsafe_allow_html=True)
            with st.spinner("Analyzing..."):
                summary = get_ai_summary(selected_title)
                st.markdown(f"<div class='ai-report-box'><p>{summary}</p></div>", unsafe_allow_html=True)

<<<<<<< HEAD
        # ------------------ ส่วนกราฟ Visualization ------------------
        st.write("---")
        st.markdown("<h3>🗳️ Vote Distribution by Political Parties</h3>", unsafe_allow_html=True)
        
        # 2. จัดเตรียมข้อมูลสำหรับพล็อต (ใช้ logic แบ่งสีเหมือนเดิม แต่ Apply กับ vote_dict ที่ดึงมาใหม่)
        processed_data = []
        if isinstance(vote_dict, dict):
            for party, votes in vote_dict.items():
                if isinstance(votes, dict):
                    # รวมคะแนนเห็นด้วย / เห็นชอบ
                    agree = votes.get('เห็นด้วย', 0) + votes.get('เห็นชอบ', 0)
                    # รวมคะแนนที่ไม่เห็นด้วย ลา ขาด งดออกเสียง
                    others = votes.get('ลา/ขาด', 0) + votes.get('งดออกเสียง', 0) + votes.get('ไม่ลงคะแนน', 0) + votes.get('ไม่เห็นชอบ', 0)
                    
                    processed_data.append({
                        'พรรค': party,
                        'เห็นด้วย': agree,
                        'อื่นๆ (ลา/งด/ไม่เห็นชอบ)': others
                    })

        # 3. สร้างกราฟ
        if processed_data:
            df_plot = pd.DataFrame(processed_data)
            # เรียงจากพรรคที่เห็นด้วยน้อยไปมาก เพื่อให้พรรคที่โหวตเห็นด้วยเยอะๆ อยู่ด้านบน
            df_plot = df_plot.sort_values(by='เห็นด้วย', ascending=True)

            # กำหนดสี
            colors_agree = {
                'ประชาชน': '#FF6600',
                'ก้าวไกล': '#F47933',
                'พรรคก้าวไกล': '#F47933',
                'เพื่อไทย': '#DA3731',
                'พรรคเพื่อไทย': '#DA3731',
                'ภูมิใจไทย': '#2C3487',
                'พรรคภูมิใจไทย': '#2C3487',
                'รวมไทยสร้างชาติ': '#224494',
                'พลังประชารัฐ': '#3569BB'
            }
            default_palette = px.colors.qualitative.Safe

            fig = go.Figure()

            # แท่งคะแนน "เห็นด้วย" (ใช้สีแยกตามพรรค)
            for i, party in enumerate(df_plot['พรรค']):
                party_row = df_plot[df_plot['พรรค'] == party]
                color = colors_agree.get(party, default_palette[i % len(default_palette)])
                
                fig.add_trace(go.Bar(
                    y=[party],
                    x=party_row['เห็นด้วย'],
                    name=f"{party} (เห็นด้วย)",
                    orientation='h',
                    marker=dict(color=color),
                    showlegend=False,
                    text=party_row['เห็นด้วย'],
                    textposition='inside'
                ))

            # แท่งคะแนน "กลุ่มอื่นๆ" (ใช้สีเทาเหมือนกันหมด)
            fig.add_trace(go.Bar(
                y=df_plot['พรรค'],
                x=df_plot['อื่นๆ (ลา/งด/ไม่เห็นชอบ)'],
                name="อื่นๆ (ลา/ขาด/งด/ไม่เห็นชอบ)",
                orientation='h',
                marker=dict(color='#B0B0B0'),
                text=df_plot['อื่นๆ (ลา/งด/ไม่เห็นชอบ)'],
                textposition='outside'
            ))

            # ปรับแต่งหน้าตากราฟ
            fig.update_layout(
                xaxis_title="จำนวนคะแนนเสียง", yaxis_title="", 
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                barmode='stack', # ให้แท่งกราฟต่อกันแนวนอน
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50, b=10, l=10, r=10),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูลการโหวตสำหรับ พ.ร.บ. ฉบับนี้")
            
        st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ</div>", unsafe_allow_html=True)
=======
    party_order = sorted(data['vote_details'].keys(), key=lambda p: data['vote_details'][p].get('เห็นชอบ', 0))
    
    fig = px.bar(df_votes, x='Percentage', y='Party', color='Vote Type', orientation='h', 
                 color_discrete_map={"เห็นชอบ": "#2ECC71", "ไม่เห็นชอบ": "#E74C3C", "งดออกเสียง": "#94A3B8"},
                 text_auto=True)
    
    # 🌟 ปรับสีข้อความกราฟ Plotly ให้สว่างเข้ากับธีม
    fig.update_layout(
        xaxis_title="ร้อยละ (%)", yaxis_title="", 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"), # สีข้อความกราฟ
        barmode='stack',
        yaxis={'categoryorder': 'array', 'categoryarray': party_order},
        legend_title_text="ประเภทการลงมติ",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=10, l=10, r=10),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ</div>", unsafe_allow_html=True)
>>>>>>> main
