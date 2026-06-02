import streamlit as st
import google.generativeai as genai
import json

# 페이지 기본 설정 (전체 화면 비율)
st.set_page_config(page_title="패션 트렌드 대시보드", page_icon="👗", layout="wide")

st.title("🇰🇷 소셜미디어 패션 트렌드 예측 대시보드")
st.markdown("선택한 기간의 플랫폼별 핵심 패션 트렌드 키워드를 AI가 실시간으로 분석해 드립니다.")

# 사이드바: 설정 및 API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studio에서 발급받은 API 키를 입력하세요.")
    st.markdown("[👉 API 키 무료 발급받기](https://aistudio.google.com/app/apikey)")
    st.caption("※ API 키는 서버에 저장되지 않으며, 팀원들과 웹사이트 공유 시 각자 입력하거나 사이드바에 고정할 수 있습니다.")

# 메인 화면: 날짜 선택
st.markdown("### 📅 분석할 기간을 선택하세요")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일")
with col2:
    end_date = st.date_input("종료일")

# 실행 버튼
if st.button("🚀 트렌드 예측하기", use_container_width=True):
    if not api_key:
        st.warning("왼쪽 사이드바에 Gemini API Key를 먼저 입력해주세요!")
    else:
        with st.spinner('AI가 웹 검색 및 트렌드 데이터를 실시간으로 분석하고 있습니다... (약 10초 소요)'):
            try:
                # Gemini API 세팅
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

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

                # 결과 받아오기
                response = model.generate_content(prompt)
                
                # 결과물 클렌징 및 변환
                raw_text = response.text.replace('```json', '').replace('```', '').strip()
                trends_data = json.loads(raw_text)

                st.success(f"🎉 {start_date} ~ {end_date} 패션 트렌드 분석 완료!")

                # UI 대시보드 형태로 출력
                platforms = ["X (Twitter)", "Threads", "Instagram", "YouTube", "TikTok"]
                cols = st.columns(5)
                
                for i, platform in enumerate(platforms):
                    with cols[i]:
                        st.subheader(platform)
                        for kw in trends_data.get(platform, []):
                            st.info(f"**{kw}**")

            except Exception as e:
                st.error(f"오류가 발생했습니다. API 키가 정확한지 확인해주세요.\n\n상세 오류: {e}")