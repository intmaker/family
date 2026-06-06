import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 웹 페이지 기본 설정 및 스타일 정의
st.set_page_config(page_title="FamilySync - Smart Family Dashboard", layout="wide")

# 세련된 카드 디자인을 위한 사용자 정의 CSS 스타일
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

# 담당자별 고유 컬러 패키지 정의
theme_colors = {
    "엄마": {"bg": "#FFF0F1", "fg": "#D63031", "emoji": "👩‍💻"},
    "아빠": {"bg": "#EBF5FF", "fg": "#0984E3", "emoji": "👨‍💼"},
    "아이": {"bg": "#E8F8F0", "fg": "#2ED573", "emoji": "🧒"}
}

# 긴급도 태그별 색상 정의
tag_styles = {
    "Urgent 🚨": "#D63031",     # 레드
    "Priority 📌": "#E67E22",   # 오렌지
    "Normal 📅": "#7F8C8D"      # 그레이
}

# -------------------------------------------------------------
# 🔗 [데이터베이스] 사용자 제공 구글 스프레드시트 실시간 연동
# -------------------------------------------------------------
# 보내주신 스프레드시트의 CSV 변환 주소입니다.
sheet_url = "https://docs.google.com/spreadsheets/d/1vSXiuoYiQM4dxlKGkXbNJRKKWW0ADAJ3ESsxtA-4Hpg/gviz/tq?tqx=out:csv"

def load_data():
    """구글 스프레드시트에서 데이터를 실시간으로 긁어오는 함수 (새로고침 보존의 핵심)"""
    try:
        # 판다스(pandas)를 이용해 온라인 csv 데이터를 딕셔너리 형태로 변환
        # 주소 뒤에 난수를 붙여 브라우저에 구글 데이터가 캐싱(기억)되어 안 바뀌는 현상 방지
        nocache_url = f"{sheet_url}&timestamp={int(datetime.now().timestamp())}"
        df = pd.read_csv(nocache_url)
        return df.to_dict(orient="records")
    except Exception as e:
        # 데이터가 비어있거나 불러오기 실패 시 빈 리스트 반환
        return []

# 2. 실시간 상태 관리를 위한 세션 초기화
if "current_missions" not in st.session_state:
    st.session_state.current_missions = load_data()

# 대시보드 타이틀 헤더
st.title("👨‍👩‍👧‍👦 FamilySync - 워킹맘을 위한 스마트 가족 대시보드")
st.caption("구글 스프레드시트 클라우드 연동 완료 🌐 | 새로고침(F5)을 해도 우리 가족 데이터가 완벽히 보존됩니다.")

# 3. 화면 레이아웃 분할 (좌측: 입력 폼, 우측: 실시간 모니터링 카드 뷰)
col1, col2 = st.columns([1, 1.2])

# --- [왼쪽 영역: 새로운 미션 작성 폼] ---
with col1:
    st.subheader("Create New Family Mission")
    with st.form("mission_form", clear_on_submit=True):
        # 할 일 텍스트 입력창
        task_text = st.text_input("할 일 (일정)", placeholder="예: 효주 음악학원 픽업, 현준이 약 먹이기")
        
        # 라디오 버튼을 이용한 가사/육아 주체 지정
        worker = st.radio("담당자 (Assignee)", ["엄마", "아빠", "아이"], horizontal=True)
        
        # 콤보박스를 활용한 효주/현준이 대상 타겟팅 및 일정 종류 카테고리화
        c_col, t_col = st.columns(2)
        with c_col:
            chosen_child = st.selectbox("대상 자녀", ["효주", "현준", "공통"])
        with t_col:
            chosen_type = st.selectbox("일정 종류", ["학원", "병원", "집안일", "마트", "기타"])
            
        # 긴급도 및 마감일 위젯
        chosen_tag = st.radio("우선순위 / 긴급도 설정", ["Normal 📅", "Priority 📌", "Urgent 🚨"], horizontal=True)
        due_date = st.date_input("마감 일자 (Due Date)", datetime.now())
        
        submit_btn = st.form_submit_button("+ 미션 추가", use_container_width=True)
        
        if submit_btn:
            if not task_text:
                st.error("할 일을 입력해 주세요!")
            else:
                # 임시 새 미션 객체 생성
                new_mission = {
                    "worker": worker,
                    "child": chosen_child,
                    "type": chosen_type,
                    "task": task_text,
                    "tag": chosen_tag,
                    "due": str(due_date)
                }
                # 현재 세션에 데이터 추가 (가시성 확보)
                st.session_state.current_missions.append(new_mission)
                st.success("🎉 대시보드에 임시 등록되었습니다! (구글 시트 원본에 반영하려면 시트에 한 줄 추가해 주세요)")
                st.rerun()

# --- [오른쪽 영역: 클라우드 동기화 대시보드 모니터링] ---
with col2:
    st.subheader("Today's Family Missions")
    
    # 🔄 실시간 원격 새로고침 버튼 (엄마나 아빠가 구글 시트 수정한 내용을 즉시 가져옴)
    if st.button("🔄 구글 스프레드시트 데이터 실시간 원격 동기화", use_container_width=True):
        st.session_state.current_missions = load_data()
        st.toast("구글 클라우드에서 최신 일정을 원격으로 동기화했습니다! 📡")
        st.rerun()
        
    display_missions = st.session_state.current_missions
    
    if not display_missions:
        st.info("🥳 대시보드가 비어있습니다. 구글 시트에 일정을 추가하거나 왼쪽 폼을 이용해 보세요!")
    else:
        # 데이터베이스의 일정을 기반으로 HTML/CSS 입체 카드 동적 조립
        for idx, item in enumerate(display_missions):
            # 예외 처리: 데이터 누락 대비 기본값 세팅
            current_worker = item.get("worker", "엄마")
            theme = theme_colors.get(current_worker, theme_colors["엄마"])
            current_tag = item.get("tag", "Normal 📅")
            tag_color = tag_styles.get(current_tag, "#7F8C8D")
            
            # Urgent🚨 태그의 경우 카드 테두리를 강렬한 빨간색으로 시각적 강조
            border_color = "#E84118" if current_tag == "Urgent 🚨" else theme['fg']
            
            # 부트스트랩 웹 카드 형태로 드로잉
            card_html = f"""
            <div class="family-card" style="background-color: {theme['bg']}; border-left: 6px solid {border_color};">
                <span class="badge" style="background-color: {tag_color};">{current_tag}</span>
                <h4 style="color: #2C3E50; margin: 0;">{theme['emoji']} [{current_worker}] 대상: {item.get('child', '공통')} | 분류: {item.get('type', '일반')}</h4>
                <p style="color: #485460; margin: 6px 0 2px 0; font-size: 1.1rem; font-weight: bold;">{item.get('task', '내용 없음')}</p>
                <div class="due-date">📅 마감기한: <b>{item.get('due', str(datetime.now().date()))}</b></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 개별 미션 완료 처리 버튼 (웹 대시보드 화면상에서 임시 숨김 처리)
            if st.button(f"✔ {idx+1}번 미션 완료 처리 (화면에서 숨기기)", key=f"comp_{idx}"):
                del st.session_state.current_missions[idx]
                st.toast("미션 완료! 화면에서 성공적으로 제거되었습니다. ❤️")
                st.rerun()
                
    st.write("---")
    if st.button("🗑 대시보드 화면 초기화", use_container_width=True):
        st.session_state.current_missions.clear()
        st.rerun()