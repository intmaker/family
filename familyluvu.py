import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. 웹 페이지 기본 설정 및 스타일 정의
st.set_page_config(page_title="FamilySync - Smart Family Dashboard", layout="wide")

st.markdown("""
    <style>
    .family-card { 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 15px; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.06); 
    }
    .badge { 
        float: right; 
        color: white; 
        padding: 4px 10px; 
        border-radius: 5px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .due-date { 
        font-size: 0.85rem; 
        color: #7F8C8D; 
        font-weight: normal; 
        margin-top: 5px; 
    }
    </style>
""", unsafe_allow_html=True)

theme_colors = {
    "엄마": {"bg": "#FFF0F1", "fg": "#D63031", "emoji": "👩‍💻"},
    "아빠": {"bg": "#EBF5FF", "fg": "#0984E3", "emoji": "👨‍💼"},
    "아이": {"bg": "#E8F8F0", "fg": "#2ED573", "emoji": "🧒"}
}
tag_styles = {"Urgent 🚨": "#D63031", "Priority 📌": "#E67E22", "Normal 📅": "#7F8C8D"}

# -------------------------------------------------------------
# 🔗 [양방향 클라우드 주소 연동 - 업데이트 완료 🎯]
# -------------------------------------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1vSXiuoYiQM4dxlKGkXbNJRKKWW0ADAJ3ESsxtA-4Hpg/gviz/tq?tqx=out:csv"

# 보내주신 최신 구글 앱스 스크립트 주소로 교체했습니다!
script_url = "https://script.google.com/macros/s/AKfycbxgOhqUO0iI7V-1nJWLdM6A6V95ikhF2KW9_jQvWISQQooplu80izy7ZVgHovOrj_E0/exec"

def load_data():
    """구글 시트에서 데이터를 실시간으로 읽어오는 함수"""
    try:
        nocache_url = f"{sheet_url}&timestamp={int(datetime.now().timestamp())}"
        df = pd.read_csv(nocache_url)
        df = df.fillna("") 
        
        # 'status' 열의 양쪽 공백을 제거하고, '완료'인 항목은 대시보드에서 보이지 않게 필터링
        if "status" in df.columns:
            df["status"] = df["status"].astype(str).str.strip()
            df = df[df["status"] != "완료"]
            
        return df.to_dict(orient="records")
    except:
        return []

# 실시간 데이터 로드 상태 유지
if "current_missions" not in st.session_state:
    st.session_state.current_missions = load_data()

st.title("👨‍👩‍👧‍👦 FamilySync - 워킹맘을 위한 스마트 가족 대시보드")
st.caption("🌐 클라우드 완벽 연동 | 완료 처리 시 구글 시트 원본의 status 데이터가 '완료'로 즉시 업데이트됩니다.")

col1, col2 = st.columns([1, 1.2])

# --- [왼쪽 영역: 새로운 미션 작성 및 구글 전송 폼] ---
with col1:
    st.subheader("Create New Family Mission")
    with st.form("mission_form", clear_on_submit=True):
        task_text = st.text_input("할 일 (일정)", placeholder="예: 효주 음악학원 픽업, 현준이 약 먹이기")
        worker = st.radio("담당자 (Assignee)", ["엄마", "아빠", "아이"], horizontal=True)
        chosen_child = st.selectbox("대상 자녀", ["효주", "현준", "공통"])
        chosen_tag = st.radio("우선순위 / 긴급도 설정", ["Normal 📅", "Priority 📌", "Urgent 🚨"], horizontal=True)
        due_date = st.date_input("마감 일자 (Due Date)", datetime.now())
        
        submit_btn = st.form_submit_button("+ 미션 추가 및 구글 저장", use_container_width=True)
        
        if submit_btn:
            if not task_text:
                st.error("할 일을 입력해 주세요!")
            else:
                payload = {
                    "worker": worker, 
                    "child": chosen_child, 
                    "task": task_text, 
                    "tag": chosen_tag, 
                    "due": str(due_date)
                }
                
                try:
                    response = requests.post(script_url, json=payload)
                    if response.status_code == 200:
                        st.success("🎯 구글 스프레드시트에 영구 저장되었습니다!")
                        st.session_state.current_missions = load_data()
                        st.rerun()
                    else:
                        st.error("구글 서버 통신에 실패했습니다.")
                except Exception as e:
                    st.error(f"전송 실패 오류: {e}")

# --- [오른쪽 영역: 클라우드 동기화 대시보드] ---
with col2:
    st.subheader("Today's Family Missions")
    
    if st.button("🔄 구글 스프레드시트 데이터 실시간 동기화", use_container_width=True):
        st.session_state.current_missions = load_data()
        st.rerun()
        
    display_missions = st.session_state.current_missions
    
    if not display_missions:
        st.info("🥳 현재 대시보드가 비어있습니다. 새로운 일정을 등록해 보세요!")
    else:
        for idx, item in enumerate(display_missions):
            current_worker = item.get("worker", "엄마")
            if not current_worker or current_worker == "nan": current_worker = "엄마"
                
            theme = theme_colors.get(current_worker, theme_colors["엄마"])
            
            current_tag = item.get("tag", "Normal 📅")
            if not current_tag or current_tag == "nan": current_tag = "Normal 📅"
                
            border_color = "#E84118" if current_tag == "Urgent 🚨" else theme['fg']
            
            task_display = item.get('task', '내용 없음')
            due_display = item.get('due', str(datetime.now().date()))
            
            card_html = f"""
            <div class="family-card" style="background-color: {theme['bg']}; border-left: 6px solid {border_color};">
                <span class="badge" style="background-color: {tag_styles.get(current_tag, '#7F8C8D')};">{current_tag}</span>
                <h4 style="color: #2C3E50; margin: 0;">{theme['emoji']} [{current_worker}] 대상: {item.get('child', '공통')}</h4>
                <p style="color: #485460; margin: 8px 0 2px 0; font-size: 1.1rem; font-weight: bold;">{task_display}</p>
                <div class="due-date">📅 마감기한: <b>{due_display}</b></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 완료 버튼을 누르면 신규 구글 앱스 스크립트 주소로 'action: complete' 신호를 보냅니다.
            if st.button(f"✔ {idx+1}번 미션 완료 처리", key=f"comp_{idx}"):
                complete_payload = {
                    "action": "complete",
                    "worker": str(current_worker),
                    "child": str(item.get('child', '공통')),
                    "task": str(task_display)
                }
                try:
                    res = requests.post(script_url, json=complete_payload)
                    if res.status_code == 200:
                        st.toast("구글 시트와 완료 상태가 성공적으로 동기화되었습니다! ✔")
                        st.session_state.current_missions = load_data()
                        st.rerun()
                    else:
                        st.error("구글 시트 업데이트에 실패했습니다.")
                except Exception as e:
                    st.error(f"통신 오류 발생: {e}")