import streamlit as st
from datetime import datetime

# 1. 웹 페이지 기본 설정 및 스타일 정의
st.set_page_config(page_title="FamilySync - Smart Family Dashboard", layout="wide")

# 가상 카드를 위한 이쁜 CSS 스타일 적용
st.markdown("""
    <style>
    .family-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
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
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# 담당자별 디자인 정의
theme_colors = {
    "엄마": {"bg": "#FFF0F1", "fg": "#D63031", "emoji": "👩‍💻"},
    "아빠": {"bg": "#EBF5FF", "fg": "#0984E3", "emoji": "👨‍💼"},
    "아이": {"bg": "#E8F8F0", "fg": "#2ED573", "emoji": "🧒"}
}

# 긴급도 태그별 색상 정의
tag_styles = {
    "Urgent 🚨": "#D63031",     # 강렬한 레드
    "Priority 📌": "#E67E22",   # 오렌지
    "Normal 📅": "#7F8C8D"      # 그레이
}

# 2. 웹 세션 상태(데이터 저장소) 초기화 및 초기 예시 데이터 생성
if "missions" not in st.session_state:
    st.session_state.missions = [
        {"worker": "엄마", "child": "효주", "type": "학원", "task": "효주 피아노 학원 하원 픽업 (4시)", "tag": "Urgent 🚨", "due": "2026-06-06"},
        {"worker": "아빠", "child": "현준", "type": "병원", "task": "현준이 소아과 영유아 검진 예약 (5시)", "tag": "Priority 📌", "due": "2026-06-06"},
        {"worker": "아이", "child": "효주", "type": "집안일", "task": "효주 영어 숙제 및 알림장 체크하기", "tag": "Normal 📅", "due": "2026-06-07"},
    ]

st.title("👨‍👩‍👧‍👦 FamilySync - 워킹맘을 위한 스마트 가족 대시보드")
st.caption("회사에서도, 집에서도 온 가족이 실시간으로 확인하는 가사/육아 분담 알림장")

# 3. 화면 좌우 분할 레이아웃
col1, col2 = st.columns([1, 1.2])

# --- [왼쪽: 미션 생성부 (기능 대폭 추가)] ---
with col1:
    st.subheader("Create New Family Mission")
    with st.form("mission_form", clear_on_submit=True):
        # 할 일 입력
        task_text = st.text_input("할 일 (일정)", placeholder="예: 효주 음악학원 픽업, 현준이 약 먹이기")
        
        # 담당자 선택
        worker = st.radio("담당자 (Assignee)", ["엄마", "아빠", "아이"], horizontal=True)
        
        # 대상 자녀 및 일정 종류
        c_col, t_col = st.columns(2)
        with c_col:
            chosen_child = st.selectbox("대상 자녀", ["효주", "현준", "공통"])
        with t_col:
            chosen_type = st.selectbox("일정 종류", ["학원", "병원", "집안일", "마트", "기타"])
            
        # [추가된 기능 1] 긴급도 체크 라디오 버튼
        chosen_tag = st.radio("우선순위 / 긴급도 설정", ["Normal 📅", "Priority 📌", "Urgent 🚨"], index=0, horizontal=True)
        
        # [추가된 기능 2] 마감 일자 선택 캘린더 위젯
        due_date = st.date_input("마감 일자 (Due Date)", datetime.now())
        
        # 제출 버튼
        submit_btn = st.form_submit_button("+ 미션 추가", use_container_width=True)
        
        if submit_btn:
            if not task_text:
                st.error("할 일을 입력해 주세요!")
            else:
                new_mission = {
                    "worker": worker,
                    "child": chosen_child,
                    "type": chosen_type,
                    "task": task_text,
                    "tag": chosen_tag,  # 사용자가 직접 체크한 긴급도 반영
                    "due": str(due_date) # 선택한 날짜 문자열로 저장
                }
                st.session_state.missions.append(new_mission)
                st.success(f"🎉 [{worker}] 담당 미션이 성공적으로 등록되었습니다!")
                st.rerun()

# --- [오른쪽: 대시보드 모니터링 및 완료 처리] ---
with col2:
    st.subheader("Today's Family Missions")
    
    if not st.session_state.missions:
        st.info("🥳 모든 미션이 완료되었습니다! 프리한 하루를 즐기세요!")
    else:
        # 미션을 하나씩 카드로 렌더링
        for idx, item in enumerate(st.session_state.missions):
            theme = theme_colors[item["worker"]]
            tag_color = tag_styles.get(item["tag"], "#7F8C8D")
            
            # 긴급도(Urgent)일 경우 테두리를 더 눈에 띄게 붉은색 계열로 하이라이트
            border_color = "#E84118" if item["tag"] == "Urgent 🚨" else theme['fg']
            
            # HTML/CSS 구조에 마감일 정보(due) 시각화 추가
            card_html = f"""
            <div class="family-card" style="background-color: {theme['bg']}; border-left: 6px solid {border_color};">
                <span class="badge" style="background-color: {tag_color};">{item['tag']}</span>
                <h4 style="color: #2C3E50; margin: 0;">{theme['emoji']} [{item['worker']}] 대상: {item['child']} | 분류: {item['type']}</h4>
                <p style="color: #485460; margin: 5px 0 2px 0; font-size: 1.1rem; font-weight: bold;">{item['task']}</p>
                <div class="due-date">📅 마감기한: <b>{item['due']}</b></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 각 카드 바로 밑에 '완료' 버튼 배치
            if st.button(f"✔ {idx+1}번 미션 완료 처리", key=f"comp_{idx}"):
                del st.session_state.missions[idx]
                st.toast("미션 클리어! 오늘도 힘내는 우리 가족 최고! ❤")
                st.rerun()
                
    st.write("---")
    if st.button("🗑 전체 미션 초기화", use_container_width=True):
        st.session_state.missions.clear()
        st.rerun()
