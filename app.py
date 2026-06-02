import streamlit as st
import google.generativeai as genai
import json

# 페이지 기본 설정
st.set_page_config(page_title="패션 트렌드 대시보드", page_icon="👗", layout="wide")

st.title("🇰🇷 소셜미디어 패션 트렌드 예측 대시보드")
st.markdown("선택한 기간의 플랫폼별 핵심 패션 트렌드 키워드를 AI가 실시간으로 분석해 드립니다.")

# 메인 화면: 날짜 선택
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일")
with col2:
    end_date = st.date_input("종료일")

# 실행 버튼
if st.button("🚀 트렌드 예측하기", use_container_width=True):
    with st.spinner('AI가 사용 가능한 모델을 찾아 데이터를 분석 중입니다... (약 10초 소요)'):
        try:
            # Streamlit 서버 금고에서 API 키 불러오기
            api_key = st.secrets["API_KEY"]
            genai.configure(api_key=api_key)

            # 🚨 [핵심] 구글 서버에서 현재 사용 가능한 모델 리스트 자동 확인
            valid_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name)
            
            if not valid_models:
                st.error("현재 API 키로 사용할 수 있는 모델이 없습니다. API 키를 다시 확인해주세요.")
                st.stop()

            # 가장 적합한 모델 자동 선택
            chosen_model = valid_models[0]
            for m in valid_models:
                if 'flash' in m:
                    chosen_model = m
                    break
                elif 'pro' in m:
                    chosen_model = m

            # 모델 이름 클렌징 후 세팅
            model_name = chosen_model.replace("models/", "")
            model = genai.GenerativeModel(model_name)

            # AI에게 내릴 프롬프트 명령
            prompt = f"""
            분석 기간: {start_date} ~ {end_date}
            국가: 대한민국
            주제: 패션 (의류/스타일링/브랜드)
            위 기간 동안 예상되는 소셜미디어 플랫폼별 패션 트렌드 키워드를 5개씩 도출해줘.
            결과는 반드시 아래와 같은 순수 JSON 형태로만 출력해 (마크다운 코드블록 금지):
            {{
                "X (Twitter)": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
                "Threads": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
                "Instagram": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
                "YouTube": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
                "TikTok": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
            }}
            """

            response = model.generate_content(prompt)
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            trends_data = json.loads(raw_text)

            st.success(f"🎉 분석 완료! (자동 연결된 AI 모델: {model_name})")

            # UI 출력
            platforms = ["X (Twitter)", "Threads", "Instagram", "YouTube", "TikTok"]
            cols = st.columns(5)
            
            for i, platform in enumerate(platforms):
                with cols[i]:
                    st.subheader(platform)
                    for kw in trends_data.get(platform, []):
                        st.info(f"**{kw}**")

        except Exception as e:
            st.error(f"오류가 발생했습니다.\n\n상세 오류: {e}")
