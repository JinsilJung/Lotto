import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timedelta
from collections import Counter

# ==========================================================
# 1. 페이지 설정 및 디자인 (세련된 UI 적용)
# ==========================================================
st.set_page_config(page_title="인생역전 로또 추천기", page_icon="🍀", layout="wide")

# 로또 공 디자인 및 서약서 스타일링 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .lotto-ball {
        display: inline-block;
        width: 45px; height: 45px; line-height: 45px;
        border-radius: 50%; text-align: center;
        font-weight: bold; color: white;
        margin-right: 8px; font-size: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .ball-1-10 { background-color: #fbc400; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-11-20 { background-color: #69c8f2; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-21-30 { background-color: #ff7272; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-31-40 { background-color: #aaaaaa; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-41-45 { background-color: #b0d840; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    
    .pledge-box {
        background-color: #fffdf5; padding: 20px; border-radius: 15px;
        border: 2px dashed #ff9900; margin-bottom: 25px;
        text-align: center; color: #444;
    }
    .pledge-title {
        font-size: 1.3rem; font-weight: bold; color: #d35400; margin-bottom: 10px;
    }
    .game-card {
        background-color: white; padding: 15px; border-radius: 10px;
        margin-bottom: 12px; border-left: 6px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center;
    }
    .game-label {
        font-weight: bold; font-size: 1.1em; margin-right: 20px; color: #333; min-width: 80px;
    }
</style>
""", unsafe_allow_html=True)

def get_ball_html(num):
    if 1 <= num <= 10: color_class = "ball-1-10"
    elif 11 <= num <= 20: color_class = "ball-11-20"
    elif 21 <= num <= 30: color_class = "ball-21-30"
    elif 31 <= num <= 40: color_class = "ball-31-40"
    else: color_class = "ball-41-45"
    return f'<div class="lotto-ball {color_class}">{num}</div>'

# ==========================================================
# 2. 데이터 로드 및 자동 업데이트 로직 (핵심 변경점)
# ==========================================================

# (1) 오늘 날짜 기준 최신 회차 계산
def get_latest_round():
    # 로또 1회차: 2002년 12월 7일 (토)
    start_date = datetime(2002, 12, 7, 20, 0, 0)
    now = datetime.now()
    
    # 아직 이번 주 추첨 시간(토요일 20시) 전이라면 지난주까지만 계산
    if now.weekday() == 5 and now.hour < 20: 
        now = now - timedelta(days=1)
        
    diff = now - start_date
    return (diff.days // 7) + 1

# (2) 동행복권 API 호출 함수
def fetch_lotto_round(drwNo):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drwNo}"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get("returnValue") == "success":
            # 당첨 번호 6개 + 보너스 번호 리스트로 반환
            return [
                data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                data["drwtNo4"], data["drwtNo5"], data["drwtNo6"],
                data["bnusNo"]
            ]
    except:
        pass
    return None

@st.cache_data(ttl=3600)  # 1시간마다 캐시 갱신 (서버 부하 방지)
def load_and_update_data():
    # A. 엑셀 파일 읽기 (기존 데이터)
    try:
        df = pd.read_excel('1st_lotto_bonus.xlsx', header=1)
        # 엑셀 데이터가 있으면 행 개수로 마지막 회차 추정
        last_saved_index = len(df)
        existing_data = df.values.tolist()
    except FileNotFoundError:
        existing_data = [] 
        last_saved_index = 0

    # B. 업데이트해야 할 회차 계산
    current_round = get_latest_round()
    new_data = []
    
    # C. 데이터가 부족하다면 부족한 만큼 API 호출
    if last_saved_index < current_round:
        start_drwNo = last_saved_index + 1
        
        # 순차적으로 API 호출 (최대 50주치만 자동 업데이트 - 속도 고려)
        for drwNo in range(start_drwNo, current_round + 2):
            if drwNo > start_drwNo + 50: break # 너무 많으면 중단
            
            lotto_nums = fetch_lotto_round(drwNo)
            if lotto_nums:
                new_data.append(lotto_nums)
            else:
                # API 호출 실패 시(아직 발표 전 등) 중단
                break

    # D. 데이터 합치기
    # 기존 데이터(List) + 새 데이터(List)
    total_data = existing_data + new_data
    final_df = pd.DataFrame(total_data)
    
    return final_df, len(new_data)

df, updated_count = load_and_update_data()

# ==========================================================
# 3. 사이드바 설정
# ==========================================================
st.title("🎰 정진실의 데이터 기반 로또")
st.markdown("##### 🍀 과거 데이터를 분석하여 **당신의 꿈**을 현실로 만들어 드립니다.")

if updated_count > 0:
    st.toast(f"📢 최신 {updated_count}주차 당첨 정보를 자동으로 가져왔습니다!", icon="✅")

if df is None or df.empty:
    st.error("❌ 데이터를 불러올 수 없습니다. 인터넷 연결을 확인해주세요.")
    st.stop()

# --- 데이터 전처리 ---
winning_numbers = df.values.tolist()
past_history = set()
all_past_nums = []

for row in winning_numbers:
    # 데이터 정제: API 데이터(숫자)와 엑셀 데이터(문자 등 포함 가능성) 혼합 방지
    # 1~45 사이의 정수만 확실하게 추출
    cleaned_row = []
    for n in row:
        try:
            val = int(n)
            if 1 <= val <= 45:
                cleaned_row.append(val)
        except:
            pass
            
    all_past_nums.extend(cleaned_row)
    if len(cleaned_row) >= 6:
        main_nums = tuple(sorted(cleaned_row[:6]))
        past_history.add(main_nums)

# --- 사이드바: 기능 제어 ---
with st.sidebar:
    st.header("⚙️ 생성 옵션")
    game_count = st.slider("생성할 게임 수", min_value=1, max_value=10, value=5)
    
    st.markdown("---")
    st.write("**💤 꿈에서 본 번호가 있나요?**")
    fixed_numbers = st.multiselect(
        "포함할 번호 선택 (최대 5개)",
        options=range(1, 46),
        max_selections=5,
        help="선택한 번호는 무조건 포함하고, 나머지를 추천해줍니다."
    )
    
    st.info(f"📂 분석된 1등 데이터: **{len(past_history)}회**")
    if updated_count > 0:
        st.caption(f"(+최신 {updated_count}회 자동 반영됨)")
    st.caption("Created by 정진실")

# ==========================================================
# 4. 메인 기능: 서약서 및 생성
# ==========================================================

# [기능 1] 서약서
st.markdown("""
<div class="pledge-box">
    <div class="pledge-title">📜 대국민(?) 당첨 서약서</div>
    <p>본인은 이 로또 생성기를 통해 <b>1등에 당첨</b>되더라도,</p>
    <p>개발자 <b>'정진실'</b>에게 어떠한 금전적 보상도 요구받지 않으며,</p>
    <p>정진실은 <b>"내 인생에 재미있는 에피소드 하나 생겼다"</b>는 사실 하나로 만족할 것을 굳게 맹세합니다.</p>
</div>
""", unsafe_allow_html=True)

pledge_check = st.checkbox("네, 개발자님 마음 편하시게 서명합니다. ✍️ (체크해야 번호가 나옵니다)")

# [기능 2] 번호 생성
if st.button("🎲 행운의 번호 생성하기", type="primary", use_container_width=True):
    if not pledge_check:
        st.warning("⚠️ 서약서에 동의(체크)해주셔야 번호를 드릴 수 있습니다!")
    else:
        # --- 분석 로직 ---
        counts = Counter(all_past_nums)
        ranked_candidates = sorted(range(1, 46), key=lambda x: (counts.get(x, 0), x))

        CUTOFF = 40        
        BOOST_LIMIT = 30   
        survivors = ranked_candidates[:CUTOFF]
        dropped = ranked_candidates[CUTOFF:]   

        max_freq = max(counts.values()) if counts else 100
        my_games = []
        attempt_limit = 0
        
        while len(my_games) < game_count:
            attempt_limit += 1
            if attempt_limit > 1000: break 
            
            selected_set = set(fixed_numbers)
            current_pool = [n for n in survivors if n not in selected_set]
            
            current_weights = []
            for num in current_pool:
                freq = counts.get(num, 0)
                w = (max_freq - freq) + 1
                try:
                    if survivors.index(num) < BOOST_LIMIT:
                        w = int(w * 2.0)
                except ValueError: pass
                current_weights.append(w)
            
            while len(selected_set) < 6:
                if not current_pool: break 
                pick = random.choices(current_pool, weights=current_weights, k=1)[0]
                selected_set.add(pick)
            
            if len(selected_set) == 6:
                guess = sorted(list(selected_set))
                guess_tuple = tuple(guess)
                if guess_tuple not in past_history and guess not in my_games:
                    my_games.append(guess)

        # --- 결과 출력 ---
        st.divider()
        st.subheader(f"🎉 {game_count}개의 행운 조합이 생성되었습니다!")
        
        for i, game in enumerate(my_games):
            ball_htmls = "".join([get_ball_html(num) for num in game])
            st.markdown(f"""
            <div class="game-card">
                <div class="game-label">GAME {i+1}</div>
                {ball_htmls}
            </div>
            """, unsafe_allow_html=True)
            
        st.balloons() 
        
        with st.expander("📊 분석 상세 정보 보기"):
            if fixed_numbers:
                st.info(f"**💡 적용된 고정수:** {fixed_numbers}")
            st.write(f"**🚫 제외된 과열 번호 (Top 5):** {dropped[:5]}")
            st.caption("※ 고정수로 선택한 번호는 과열 번호여도 무조건 포함됩니다.")