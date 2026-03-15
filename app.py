import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
import os
import ast
import json
import plotly.graph_objects as go

# --- 1. ตั้งค่าหน้าเว็บและการเชื่อมต่อ AI ---
st.set_page_config(page_title="POLITILAND Exploration", layout="wide", page_icon="🏙️", initial_sidebar_state="collapsed")

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

# --- 3. โหลดข้อมูลจากไฟล์ CSV (เปลี่ยนชื่อเพื่อล้าง Cache) ---
@st.cache_data
def fetch_final_csv_data_v3():
    try:
        df = pd.read_csv('final_classified_qwen_v2.csv')
        return df
    except Exception as e:
        st.warning(f"ไม่สามารถโหลดไฟล์ final_classified_qwen_v2.csv ได้: {e}")
        return pd.DataFrame()

df_votes_data = fetch_final_csv_data_v3()

ITEM_TO_CATEGORY = {
    "การศึกษา/โรงเรียน": "หมวดการศึกษาและสังคม",
    "ถนน": "หมวดคมนาคมและการขนส่ง",
    "ยานพาหนะ": "หมวดคมนาคมและการขนส่ง",
    "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": "หมวดอุตสาหกรรมและพลังงาน",
    "อาหารและเครื่องดื่ม": "หมวดทรัพยากรธรรมชาติและสิ่งแวดล้อม",
    "น้ำ": "หมวดทรัพยากรธรรมชาติและสิ่งแวดล้อม",
    "โรงพยาบาล": "หมวดสุขภาพและสาธารณสุข",
    "สัตว์เลี้ยง": "หมวดสุขภาพและสาธารณสุข",
    "สายอาร์ต": "หมวดศิลปะและเศรษฐกิจสร้างสรรค์",
    "อินเตอร์เน็ต": "หมวดเทคโนโลยีและข้อมูล",
    "ธรรมชาติ": "หมวดทรัพยากรธรรมชาติและสิ่งแวดล้อม",
    "คนพิการ": "หมวดบุคคลและสถานะ",
    "ยาเสพติด/สุรา": "หมวดสิ่งมึนเมาและสารสกัด",
    "เครื่องสำอางค์": "หมวดสิ่งมึนเมาและสารสกัด",
    "พลังงาน/ไฟฟ้า": "หมวดอุตสาหกรรมและพลังงาน",
    "คน": "หมวดบุคคลและสถานะ"
}

objects_data = {
    "คน": {"keyword_default": "อาชีพ"}, "คนพิการ": {"keyword_default": "คนพิการ"},
    "ยานพาหนะ": {"keyword_default": "จราจร"}, "ถนน": {"keyword_default": "ทางหลวง"},
    "ธรรมชาติ": {"keyword_default": "ป่าไม้"}, "อาหารและเครื่องดื่ม": {"keyword_default": "อาหาร"},
    "อินเตอร์เน็ต": {"keyword_default": "อินเทอร์เน็ต"}, "ยาเสพติด/สุรา": {"keyword_default": "สุรา"},
    "สายอาร์ต": {"keyword_default": "ลิขสิทธิ์"}, "น้ำ": {"keyword_default": "ทรัพยากรน้ำ"},
    "สัตว์เลี้ยง": {"keyword_default": "สัตว์เลี้ยง"}, "โรงพยาบาล": {"keyword_default": "สถานพยาบาล"},
    "การศึกษา/โรงเรียน": {"keyword_default": "การศึกษา"}, "โรงงาน/อุตสาหกรรม/นิคมอุตสาหกรรม": {"keyword_default": "โรงงาน"},
    "พลังงาน/ไฟฟ้า": {"keyword_default": "พลังงาน"}, "เครื่องสำอางค์": {"keyword_default": "เครื่องสำอาง"}
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
    "ธรรมชาติ": {"img": "park.png", "top": "25%", "left": "2%", "width": "20%"},
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
        @keyframes pageEnter{ 0%{ opacity:0; transform:translateY(30px) scale(0.98); filter:blur(6px); } 100%{ opacity:1; transform:translateY(0px) scale(1); filter:blur(0px); } }
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
                e.preventDefault(); const buttons = doc.querySelectorAll('.stButton button');
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

def apply_main_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
        .stApp { background-color: #0F172A; color: #F8FAFC; } 
        @keyframes pageTransition { 0% { opacity: 0; transform: translateY(15px); filter: blur(3px); } 100% { opacity: 1; transform: translateY(0); filter: blur(0px); } }
        .block-container { animation: pageTransition 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
        header {visibility: hidden;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        h1 { color: #FFFFFF; font-weight: 600; text-align: center; letter-spacing: -1px; margin-top: 0; font-size: 2.5rem; margin-bottom: 0.5rem;}
        h2 { color: #FFFFFF; } h3 { margin-bottom: 0.2rem !important; margin-top: 0.5rem !important; font-size: 1.1rem; color: #F1F5F9;}
        p { color: #CBD5E1; }
        div.stButton > button:first-child { background-color: #1E293B; color: #F8FAFC !important; border: 1px solid #334155; border-radius: 6px; font-weight: 500; padding: 0.3rem 1rem; }
        div.stButton > button:first-child:hover { background-color: #334155; border-color: #475569; }
        .data-card { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 10px 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        .data-card p { color: #94A3B8; margin: 0; }
        div[data-testid="metric-container"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; margin-bottom: 0.5rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #FFFFFF; } div[data-testid="stMetricLabel"] { color: #94A3B8; }
        .ai-report-box { background-color: #1E293B; border-left: 4px solid #3B82F6; padding: 10px 15px; border-radius: 4px; margin-bottom: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #F1F5F9;}
        .ai-note { font-size: 0.75rem; color: #64748B; text-align: center; margin-top: 0.5rem; }
        div[data-baseweb="select"] > div { background-color: #1E293B; border-color: #334155; color: #FFFFFF; }
        
        /* สไตล์สำหรับกล่อง Expander ของ Streamlit */
        .streamlit-expanderHeader { background-color: #1E293B; color: #F8FAFC; border-radius: 8px; }
        .streamlit-expanderContent { background-color: #0F172A; color: #CBD5E1; border: 1px solid #334155; border-top: none; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)

# --- 9. การแสดงผล (Main Controller) ---
if st.session_state.view == 'intro':
    render_intro_view()

elif st.session_state.view == 'map':
    apply_main_css()
    st.markdown("<h1>POLITILAND Exploration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;'>คลิกเลือกสำรวจนโยบายในแต่ละพื้นที่ของเมือง</p>", unsafe_allow_html=True)
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
    <div class="map-container"><img class="bg-img" src="data:image/png;base64,{bg_b64}" alt="Background">
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
    target_category = ITEM_TO_CATEGORY.get(item, "ไม่พบหมวดหมู่")
    
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        st.button("← BACK TO MAP", on_click=change_page, args=('map',))
    
    st.markdown(f"<div class='data-card'><h2>{item}</h2><p style='color: #64748B;'>หมวดหมู่ในสภา: {target_category}</p></div>", unsafe_allow_html=True)
    
    if not df_votes_data.empty and 'category' in df_votes_data.columns:
        df_filtered = df_votes_data[df_votes_data['category'] == target_category]
    else:
        df_filtered = pd.DataFrame()

    if df_filtered.empty:
        st.warning(f"ยังไม่มีข้อมูล พ.ร.บ. สำหรับหมวดหมู่ '{target_category}' ในขณะนี้")
    else:
        titles_list = df_filtered['title'].unique().tolist()
        selected_title = st.selectbox("📌 เลือกร่าง พ.ร.บ. เพื่อดูผลการลงมติและสรุปจาก AI:", titles_list)
        
        row_data = df_filtered[df_filtered['title'] == selected_title].iloc[0]
        
        col_stat, col_ai = st.columns([1, 1.5])
        with col_stat:
            st.markdown("<h3>📄 สถานะ พ.ร.บ. ที่เกี่ยวข้อง</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            
            total_bills = len(df_filtered)
            passed_bills = len(df_filtered[df_filtered['status'].astype(str).str.contains('ENACTED|บังคับใช้|ออกเป็นกฎหมาย', case=False, na=False)])
            failed_bills = len(df_filtered[df_filtered['status'].astype(str).str.contains('REJECTED|ตกไป', case=False, na=False)])
            
            c1.metric("ทั้งหมด", f"{total_bills} ฉบับ")
            c2.metric("ผ่าน ✅", f"{passed_bills} ฉบับ")
            c3.metric("ตก ❌", f"{failed_bills} ฉบับ")

        with col_ai:
            st.markdown(f"<h3>✨ AI Analysis: สรุปนโยบาย</h3>", unsafe_allow_html=True)
            with st.spinner("Analyzing..."):
                summary = get_ai_summary(selected_title)
                st.markdown(f"<div class='ai-report-box'><p>{summary}</p></div>", unsafe_allow_html=True)

        # 🌟 เพิ่มการแสดงผล Rationale (แก้ให้โชว์เลยและตัวใหญ่ขึ้น)
        rationale_text = row_data.get('rationale', '')
        if pd.isna(rationale_text) or str(rationale_text).strip() in ["", "nan", "None"]:
            rationale_text = "ไม่มีข้อมูลเหตุผลสำหรับ พ.ร.บ. ฉบับนี้ในระบบ"
            
        # เพิ่มหัวข้อ
        st.markdown("<h3 style='margin-top: 15px;'>📖 คำอธิบาย</h3>", unsafe_allow_html=True)
        
        # แสดงกล่องข้อความทันที พร้อมปรับขนาดตัวอักษร (font-size) ให้ใหญ่ขึ้น
        st.markdown(f"""
            <div style='
                font-size: 1.2rem; 
                line-height: 1.8; 
                color: #F8FAFC; 
                background-color: #1E293B; 
                padding: 20px; 
                border-radius: 8px; 
                border-left: 5px solid #F59E0B;
                margin-bottom: 20px;
            '>
                {rationale_text}
            </div>
        """, unsafe_allow_html=True)

        # ------------------ ส่วนกราฟ Visualization ------------------
        st.write("---")
        st.markdown("<h3>🗳️ Vote Distribution by Political Parties</h3>", unsafe_allow_html=True)

        # 1. ระบบแปลงข้อความให้กลายเป็น Dictionary
        raw_val = row_data.get('party_votes_json', "{}")
        vote_dict = {}

        if isinstance(raw_val, dict):
            vote_dict = raw_val
        elif isinstance(raw_val, str) and raw_val.strip() not in ["", "nan", "None", "{}"]:
            try: vote_dict = ast.literal_eval(raw_val.strip())
            except:
                try: vote_dict = json.loads(raw_val.replace("'", '"'))
                except: pass

        with st.expander("🛠️ หากกราฟไม่ขึ้น กดที่นี่เพื่อดูข้อมูลดิบ"):
            st.write(f"ข้อมูลต้นฉบับ: {raw_val}")
            st.write(f"แปลงค่าสำเร็จไหม: {vote_dict}")

        import re
        def to_int(val):
            if pd.isna(val) or val is None: return 0
            if isinstance(val, (int, float)): return int(val)
            try:
                nums = re.findall(r'\d+', str(val).replace(',', ''))
                if nums: return int(nums[0])
                return 0
            except:
                return 0

        # 2. จัดเตรียมข้อมูลสำหรับพล็อตแยกเป็น 3 ส่วน
        processed_data = []
        if vote_dict and isinstance(vote_dict, dict):
            for party, votes in vote_dict.items():
                
                if isinstance(votes, str):
                    try: votes = ast.literal_eval(votes)
                    except:
                        try: votes = json.loads(votes.replace("'", '"'))
                        except: pass
                
                agree, disagree, abstain = 0, 0, 0
                
                if isinstance(votes, dict):
                    for k, v in votes.items():
                        k_str = str(k).strip().lower() 
                        val = to_int(v)
                        
                        if k_str in ['เห็นด้วย', 'เห็นชอบ', 'agree']: agree += val
                        elif k_str in ['ไม่เห็นด้วย', 'ไม่เห็นชอบ', 'disagree']: disagree += val
                        elif k_str in ['งดออกเสียง', 'ลา/ขาด', 'ไม่ลงคะแนน', 'ลา', 'ขาด', 'abstain', 'absent', 'no_vote']: abstain += val
                        else:
                            if 'ไม่เห็น' in k_str or 'disagree' in k_str: disagree += val
                            elif 'เห็น' in k_str or 'agree' in k_str: agree += val
                            elif 'งด' in k_str or 'ลา' in k_str or 'ขาด' in k_str or 'abstain' in k_str or 'absent' in k_str: abstain += val
                
                processed_data.append({
                    'พรรค': str(party).strip(),
                    'เห็นด้วย': agree,
                    'ไม่เห็นด้วย': disagree,
                    'งดออกเสียง/ลา/ขาด': abstain
                })

        # 3. สร้างกราฟ
        if processed_data:
            df_plot = pd.DataFrame(processed_data)
            
            df_plot['total'] = df_plot['เห็นด้วย'] + df_plot['ไม่เห็นด้วย'] + df_plot['งดออกเสียง/ลา/ขาด']
            df_plot = df_plot[df_plot['total'] > 0]
            
            df_plot = df_plot.sort_values(by='เห็นด้วย', ascending=True)

            colors_agree = {
                'ประชาชน': '#FF6600', 'ก้าวไกล': '#F47933', 'พรรคก้าวไกล': '#F47933',
                'เพื่อไทย': '#DA3731', 'พรรคเพื่อไทย': '#DA3731', 'ภูมิใจไทย': '#2C3487',
                'พรรคภูมิใจไทย': '#2C3487', 'รวมไทยสร้างชาติ': '#224494', 'พลังประชารัฐ': '#3569BB',
                'ประชาธิปัตย์': '#00AEEF', 'ชาติไทยพัฒนา': '#FFC0CB', 'ชาติพัฒนา': '#FF8C00'
            }
            default_palette = px.colors.qualitative.Safe

            agree_colors_list = []
            for i, party in enumerate(df_plot['พรรค']):
                base_color = default_palette[i % len(default_palette)]
                for p_key, color in colors_agree.items():
                    if p_key in party:
                        base_color = color
                        break
                agree_colors_list.append(base_color)

            if not df_plot.empty:
                fig = go.Figure()

                text_agree = [val if val > 0 else "" for val in df_plot['เห็นด้วย']]
                fig.add_trace(go.Bar(
                    y=df_plot['พรรค'], x=df_plot['เห็นด้วย'], name="เห็นด้วย",
                    orientation='h', marker_color=agree_colors_list, 
                    text=text_agree, textposition='inside'
                ))

                text_disagree = [val if val > 0 else "" for val in df_plot['ไม่เห็นด้วย']]
                fig.add_trace(go.Bar(
                    y=df_plot['พรรค'], x=df_plot['ไม่เห็นด้วย'], name="ไม่เห็นด้วย",
                    orientation='h', marker_color='#000000', 
                    text=text_disagree, textposition='inside'
                ))

                text_abstain = [val if val > 0 else "" for val in df_plot['งดออกเสียง/ลา/ขาด']]
                fig.add_trace(go.Bar(
                    y=df_plot['พรรค'], x=df_plot['งดออกเสียง/ลา/ขาด'], name="งดออกเสียง/ลา/ขาด",
                    orientation='h', marker_color='#B0B0B0', 
                    text=text_abstain, textposition='inside'
                ))

                graph_height = max(350, len(df_plot) * 45)

                fig.update_layout(
                    xaxis_title="จำนวนคะแนนเสียง", yaxis_title="", 
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    barmode='stack', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=50, b=10, l=10, r=10), height=graph_height, font=dict(color="#F1F5F9")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ไม่พบจำนวนคะแนนเสียง (ผลโหวตเป็น 0 ทั้งหมด) สำหรับ พ.ร.บ. ฉบับนี้")
        else:
            st.info("ไม่พบข้อมูลการโหวต หรือ ข้อมูลไม่พร้อมแสดงผล สำหรับ พ.ร.บ. ฉบับนี้")
            
        st.markdown("<div class='ai-note'>* ข้อมูลและบทสรุปนี้ประมวลผลโดย AI เพื่อการวิเคราะห์เบื้องต้น ทีม I am sorry จั๊กจี้หัวใจ</div>", unsafe_allow_html=True)