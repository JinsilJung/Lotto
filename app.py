import streamlit as st
import pandas as pd
import random
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="로또 번호 추천기", page_icon="🍀")

st.title("🎰 데이터 기반 로또 번호 생성기")
st.markdown("과거 데이터를 분석하여 **미출현 번호 가중치** 전략으로 추천합니다.")

# ==========================================================
# 1. 데이터 로드 (캐싱 적용으로 속도 향상)
# ==========================================================
@st.cache_data
def load_data():
    try:
        # 파일이 같은 폴더에 있다고 가정
        df = pd.read_excel('1st_lotto_bonus.xlsx', header=1)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("❌ '1st_lotto_bonus.xlsx' 파일을 찾을 수 없습니다. 파일을 업로드하거나 경로를 확인해주세요.")
    st.stop()

# 데이터 전처리 로직 (기존 코드 유지)
winning_numbers = df.values.tolist()
past_history = set()
all_past_nums = []

for row in winning_numbers:
    cleaned_row = [int(n) for n in row if pd.notna(n)]
    all_past_nums.extend(cleaned_row)
    if len(cleaned_row) >= 6:
        main_nums = tuple(sorted(cleaned_row[:6]))
        past_history.add(main_nums)

st.success(f"📂 과거 1등 데이터 **{len(past_history)}개** 분석 완료!")

# ==========================================================
# 2. 버튼 클릭 시 번호 생성
# ==========================================================
if st.button("🎲 번호 생성하기", type="primary"):
    
    # --- 분석 로직 (기존 코드 유지) ---
    counts = Counter(all_past_nums)
    ranked_candidates = sorted(range(1, 46), key=lambda x: (counts.get(x, 0), x))

    CUTOFF = 40        
    BOOST_LIMIT = 30   

    survivors = ranked_candidates[:CUTOFF]
    dropped = ranked_candidates[CUTOFF:]   

    # 가중치 계산
    max_freq = max(counts.values()) if counts else 100
    weights = []
    for idx, num in enumerate(survivors):
        freq = counts.get(num, 0)
        w = (max_freq - freq) + 1
        if idx < BOOST_LIMIT:
            w = int(w * 2.0)
        weights.append(w)

    # --- 5게임 추천 로직 ---
    my_games = []
    
    while len(my_games) < 5:
        selected_set = set()
        while len(selected_set) < 6:
            pick = random.choices(survivors, weights=weights, k=1)[0]
            selected_set.add(pick)
        
        guess = sorted(list(selected_set))
        guess_tuple = tuple(guess)
        
        if guess_tuple not in past_history and guess not in my_games:
            my_games.append(guess)

    # --- 결과 출력 ---
    st.divider()
    st.subheader("이번 주 추천 번호")
    
    for i, game in enumerate(my_games):
        # 보기 좋게 카드 형태로 출력
        st.info(f"**{i+1}번째 게임:** {game}")
    
    st.balloons() # 축하 효과
    
    # 분석 정보 표시 (Expandable)
    with st.expander("📊 분석 상세 정보 보기"):
        st.write(f"**제외된 과열 번호 (Top 5):** {dropped}")
        st.write("상위 30개 미출현 번호에 가중치 2배가 적용되었습니다.")