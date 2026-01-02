import streamlit as st
import pandas as pd
import random
from collections import Counter

# ==========================================================
# 1. 페이지 설정 및 디자인 (세련된 UI 적용)
# ==========================================================
st.set_page_config(page_title="인생역전 로또 추천기", page_icon="🍀", layout="wide")

# 로또 공 디자인 및 서약서 스타일링 CSS
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 로또 공 공통 스타일 */
    .lotto-ball {
        display: inline-block;
        width: 45px;
        height: 45px;
        line-height: 45px;
        border-radius: 50%;
        text-align: center;
        font-weight: bold;
        color: white;
        margin-right: 8px;
        font-size: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    /* 번호대별 색상 (한국 로또 기준) */
    .ball-1-10 { background-color: #fbc400; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-11-20 { background-color: #69c8f2; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-21-30 { background-color: #ff7272; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-31-40 { background-color: #aaaaaa; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .ball-41-45 { background-color: #b0d840; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    
    /* 서약서 박스 스타일 */
    .pledge-box {
        background-color: #fffdf5;
        padding: 20px;
        border-radius: 15px;
        border: 2px dashed #ff9900;
        margin-bottom: 25px;
        text-align: center;
        color: #444;
    }
    .pledge-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #d35400;
        margin-bottom: 10px;
    }
    
    /* 게임 결과 카드 스타일 */
    .game-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 6px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
    }
    .game-label {
        font-weight: bold; 
        font-size: 1.1em; 
        margin-right: 20px; 
        color: #333;
        min-width: 80px;
    }
</style>
""", unsafe_allow_html=True)

# 로또 공 HTML 생성 함수
def get_ball_html(num):
    if 1 <= num <= 10: color_class = "ball-1-10"
    elif 11 <= num <= 20: color_class = "ball-11-20"
    elif 21 <= num <= 30: color_class = "ball-21-30"
    elif 31 <= num <= 40: color_class = "ball-31-40"
    else: color_class = "ball-41-45"
    return f'<div class="lotto-ball {color_class}">{num}</div>'

# ==========================================================
# 2. 데이터 로드
# ==========================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('1st_lotto_bonus.xlsx', header=1)
        return df
    except FileNotFoundError:
        return None

df = load_data()

# ==========================================================
# 3. 사이드바 설정 (옵션 기능)
# ==========================================================
st.title("🎰 정진실의 데이터 기반 로또")
st.markdown("##### 🍀 과거 데이터를 분석하여 **당신의 꿈**을 현실로 만들어 드립니다.")

if df is None:
    st.error("❌ '1st_lotto_bonus.xlsx' 파일을 찾을 수 없습니다. 파일을 업로드하거나 경로를 확인해주세요.")
    st.stop()

# --- 데이터 전처리 ---
winning_numbers = df.values.tolist()
past_history = set()
all_past_nums = []

for row in winning_numbers:
    cleaned_row = [int(n) for n in row if pd.notna(n)]
    all_past_nums.extend(cleaned_row)
    if len(cleaned_row) >= 6:
        main_nums = tuple(sorted(cleaned_row[:6]))
        past_history.add(main_nums)

# --- 사이드바: 기능 제어 ---
with st.sidebar:
    st.header("⚙️ 생성 옵션")
    
    # [기능 2] 게임 수 조절 (1~10개)
    game_count = st.slider("생성할 게임 수", min_value=1, max_value=10, value=5)
    
    # [기능 3] 고정수(꿈 번호) 선택
    st.markdown("---")
    st.write("**💤 꿈에서 본 번호가 있나요?**")
    fixed_numbers = st.multiselect(
        "포함할 번호 선택 (최대 5개)",
        options=range(1, 46),
        max_selections=5,
        help="선택한 번호는 무조건 포함하고, 나머지를 추천해줍니다."
    )
    
    st.info(f"📂 분석된 1등 데이터: **{len(past_history)}회**")
    st.caption("Created by 정진실")

# ==========================================================
# 4. 메인 기능: 서약서 및 생성
# ==========================================================

# [기능 1] 재미있는 서약서 섹션
st.markdown("""
<div class="pledge-box">
    <div class="pledge-title">📜 대국민(?) 당첨 서약서</div>
    <p>본인은 이 로또 생성기를 통해 <b>1등에 당첨</b>되더라도,</p>
    <p>개발자 <b>'정진실'</b>에게 어떠한 금전적 보상도 요구받지 않으며,</p>
    <p>단지 <b>"내 인생에 끝내주는 에피소드 하나 생겼다"</b>는 사실 하나로 만족할 것을 굳게 맹세합니다.</p>
</div>
""", unsafe_allow_html=True)

# 서약 체크박스
pledge_check = st.checkbox("네, 개발자님 마음 편하시게 서명합니다. ✍️ (체크해야 번호가 나옵니다)")

# 버튼 클릭 로직
if st.button("🎲 행운의 번호 생성하기", type="primary", use_container_width=True):
    
    if not pledge_check:
        st.warning("⚠️ 서약서에 동의(체크)해주셔야 번호를 드릴 수 있습니다! (돈 달라고 안 할게요 😂)")
    else:
        # --- 분석 로직 ---
        counts = Counter(all_past_nums)
        ranked_candidates = sorted(range(1, 46), key=lambda x: (counts.get(x, 0), x))

        CUTOFF = 40        
        BOOST_LIMIT = 30   

        survivors = ranked_candidates[:CUTOFF]
        dropped = ranked_candidates[CUTOFF:]   

        # 가중치 계산 준비
        max_freq = max(counts.values()) if counts else 100
        
        my_games = []
        attempt_limit = 0
        
        while len(my_games) < game_count:
            attempt_limit += 1
            if attempt_limit > 1000: break # 무한루프 방지
            
            # 1. 고정수(꿈 번호) 먼저 넣기
            selected_set = set(fixed_numbers)
            
            # 2. 남은 자리 채우기 (가중치 적용)
            # 고정수는 후보군에서 제외 (이미 뽑았으니까)
            current_pool = [n for n in survivors if n not in selected_set]
            
            current_weights = []
            for num in current_pool:
                freq = counts.get(num, 0)
                w = (max_freq - freq) + 1
                try:
                    # 원래 순위에서의 인덱스로 가중치 부스트 적용
                    if survivors.index(num) < BOOST_LIMIT:
                        w = int(w * 2.0)
                except ValueError:
                    pass
                current_weights.append(w)
            
            # 부족한 개수만큼 뽑기
            while len(selected_set) < 6:
                if not current_pool: break # 만약 뽑을 풀이 없으면 중단
                pick = random.choices(current_pool, weights=current_weights, k=1)[0]
                selected_set.add(pick)
            
            # 6개 완성 확인
            if len(selected_set) == 6:
                guess = sorted(list(selected_set))
                guess_tuple = tuple(guess)
                
                # 과거 1등 번호와 겹치지 않고, 이번 생성 목록에도 없으면 추가
                if guess_tuple not in past_history and guess not in my_games:
                    my_games.append(guess)

        # --- [기능 4] 세련된 결과 출력 ---
        st.divider()
        st.subheader(f"🎉 {game_count}개의 행운 조합이 생성되었습니다!")
        
        for i, game in enumerate(my_games):
            # HTML 생성
            ball_htmls = "".join([get_ball_html(num) for num in game])
            
            st.markdown(f"""
            <div class="game-card">
                <div class="game-label">GAME {i+1}</div>
                {ball_htmls}
            </div>
            """, unsafe_allow_html=True)
            
        st.balloons() # 축하 효과
        
        # 분석 정보 표시
        with st.expander("📊 분석 상세 정보 보기"):
            if fixed_numbers:
                st.info(f"**💡 적용된 고정수:** {fixed_numbers}")
            st.write(f"**🚫 제외된 과열 번호 (Top 5):** {dropped[:5]}")
            st.caption("※ 고정수로 선택한 번호는 과열 번호여도 무조건 포함됩니다.")