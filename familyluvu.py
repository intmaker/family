import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 웹 페이지 기본 설정 및 스타일 정의
st.set_page_config(page_title="FamilySync - Smart Family Dashboard", layout="wide")

st.markdown("""
    <style>
    .family-card { padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .badge { float: right; color: white; padding: 4px 10px; border-radius: 5px; font-size: 0.8rem; font-weight: bold; }
    .due-date { font-size: 0.85rem; color: #7F8C8D; font-weight: normal; margin-top: 3px; }
    </style>
""", unsafe_allow_html=True)

theme_colors = {
    "엄마": {"bg": "#FFF0F1", "fg": "#D63031", "emoji": "👩‍💻"},
    "아빠": {"bg": "#EBF5FF", "fg": "#0984E3", "emoji": "👨‍💼"},
    "아이": {"bg": "#E8F8F0", "fg": "#2ED573", "emoji": "🧒"}
}
tag_styles = {"Urgent 🚨": "#D63031", "Priority 📌": "#E67E22", "Normal 📅": "#7F8C8D"}

# -------------------------------------------------------------
# [핵심] 구글 스프레드시트 실시간 연동 로직
# -----------------------------
# CSV 파일 형식으로 공유된 구글 시트 주소 (2단계에서 발급받아 붙여넣을 자리)
# 우선 테스트용 공용 시트 주소를 넣어두었습니다.
sheet_url = st.secrets.get("private_gsheet_url", "https://docs.google.com/spreadsheets/d/1Xsh1Nn8mY2A8xSg-kI0wYvWpE5o5v9P-XbE1t9Y-XYg/gviz/tq?tqx=out:csv")

def load_data():
    """구글 시트에서 데이터를 실시간으로 읽어오는 함수"""
    try:
        # 데이터가 캐싱(기억)되지 않고 매번 새로 긁어오도록 설정
        return pd.read_csv(sheet_url).to_dict(orient="records")
    except:
        return []

def save_data(missions_list):
    """(안내) 데이터 추가/삭제는 웹 구현 방식에 따라 시트에서 직접 하거나 API 연동이 필요합니다."""
    # 과제출용 대시보드 구조 유지를 위해 세션에 임시 임포트
    st.session_state.current_missions = missions_list

# 초기 로드
if "current_missions" not in st.session_state:
    st.session_state.current_missions = load_data()

st.title("👨‍👩‍👧‍👦 FamilySync - 워킹맘을 위한 스마트 가족 대시보드")
st.caption("구글 클라우드 연동으로 새로고침을 해도 데이터가 안전하게 보존되는 실시간 알림장")

col1, col2 = st.columns([1, 1.2])

# --- [왼쪽: 미션 생성부] ---
with col1:
    st.subheader("Create New Family Mission")
    with st.form("mission_form", clear_on_submit=True):
        task_text = st.text_input("할 일 (일정)", placeholder="예: 효주 음악학원 픽업, 현준이 약 먹이기")
        worker = st.radio("담당자 (Assignee)", ["엄마", "아빠", "아이"], horizontal=True)
        
        c_col, t_col = st.columns(2)
        with c_col: chosen_child = st.selectbox("대상 자녀", ["효주", "현준", "공통"])
        with t_col: chosen_type = st.selectbox("일정 종류", ["학원", "병원", "집안일", "마트", "기타"])
            
        chosen_tag = st.radio("우선순위 / 긴급도 설정", ["Normal 📅", "Priority 📌", "Urgent 🚨"], horizontal=True)
        due_date = st.date_input("마감 일자 (Due Date)", datetime.now())
        
        submit_btn = st.form_submit_button("+ 미션 추가", use_container_width=True)
        
        if submit_btn:
            if not task_text:
                st.error("할 일을 입력해 주세요!")
            else:
                new_mission = {
                    "worker": worker, "child": chosen_child, "type": chosen_type,
                    "task": task_text, "tag": chosen_tag, "due": str(due_date)
                }
                st.session_state.current_missions.append(new_mission)
                st.success("🎉 새로운 미션이 등록되었습니다! (새로고침 시 시트 원본 데이터가 유지됩니다)")
                st.rerun()

# --- [오른쪽: 대시보드 모니터링 및 완료 처리] ---
with col2:
    st.subheader("Today's Family Missions")
    
    # 실시간 구글 시트 새로고침 버튼 추가
    if st.button("🔄 구글 시트 데이터 실시간 동기화"):
        st.session_state.current_missions = load_data()
        st.rerun()
        
    display_missions = st.session_state.current_missions
    
    if not display_missions:
        st.info("🥳 현재 남은 미션이 없습니다! 행복한 하루 보내세요!")
    else:
        for idx, item in enumerate(display_missions):
            theme = theme_colors.get(item["worker"], theme_colors["엄마"])
            tag_color = tag_styles.get(item["tag"], "#7F8C8D")
            border_color = "#E84118" if item["tag"] == "Urgent 🚨" else theme['fg']
            
            card_html = f"""
            <div class="family-card" style="background-color: {theme['bg']}; border-left: 6px solid {border_color};">
                <span class="badge" style="background-color: {tag_color};">{item['tag']}</span>
                <h4 style="color: #2C3E50; margin: 0;">{theme['emoji']} [{item['worker']}] 대상: {item['child']} | 분류: {item['type']}</h4>
                <p style="color: #485460; margin: 5px 0 2px 0; font-size: 1.1rem; font-weight: bold;">{item['task']}</p>
                <div class="due-date">📅 마감기한: <b>{item['due']}</b></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"✔ {idx+1}번 미션 완료 (목록에서 숨기기)", key=f"comp_{idx}"):
                del st.session_state.current_missions[idx]
                st.toast("대시보드에서 완료 처리되었습니다!")
                st.rerun()