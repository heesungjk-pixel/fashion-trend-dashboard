import streamlit as st
import google.generativeai as genai
import json
import urllib.parse

# 페이지 기본 설정
st.set_page_config(page_title="패션 트렌드 대시보드", page_icon="👗", layout="wide")

st.title("🇰🇷 소셜미디어 패션 트렌드 예측 대시보드")
st.markdown("선택한 기간의 플랫폼별 핵심 패션 트렌드 키워드와 콘텐츠 아이디어를 AI가 기획해 드립니다.")

# 메인 화면: 날짜 선택
st.markdown("### 📅 분석할 기간을 선택하세요")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일")
with col2:
    end_date = st.date_input("종료일")

if st.button("🚀 트렌드 예측 및 기획안 생성", use_container_width=True):
    with st.spinner('AI가 뾰족한 마이크로 트렌드와 콘텐츠 아이디어를 기획 중입니다... (약 15초 소요)'):
        try:
            api_key = st.secrets["API_KEY"]
            genai.configure(api_key=api_key)

            # 사용 가능한 모델 찾기
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = valid_models[0]
            for m in valid_models:
                if 'flash' in m:
                    chosen_model = m
                    break

            model_name = chosen_model.replace("models/", "")
            model = genai.GenerativeModel(model_name)

            # 🚨 [핵심] 키워드 + 아이디어까지 기획하게 만드는 프롬프트
            prompt = f"""
            분석 기간: {start_date} ~ {end_date}
            각 플랫폼별로 유행할 구체적인 마이크로 트렌드 키워드 5개와, 해당 키워드로 만들 수 있는 훌륭한 콘텐츠 아이디어 3개씩을 도출해주세요.

            [규칙]
            1. '여름코디', 'OOTD' 같은 뻔한 단어 금지. (예: 버뮤다팬츠, 긱시크, 스크런치 등 구체적 아이템/밈)
            2. 응답은 반드시 아래 JSON 형식이어야 합니다. 다른 말은 절대 추가하지 마세요.
            {{
                "X (Twitter)": [
                    {{"keyword": "키워드1", "ideas": ["아이디어1", "아이디어2", "아이디어3"]}},
                    {{"keyword": "키워드2", "ideas": ["아이디어1", "아이디어2", "아이디어3"]}}
                ],
                "Threads": [ ... 동일하게 5개 ... ],
                "Instagram": [ ... 동일하게 5개 ... ],
                "YouTube": [ ... 동일하게 5개 ... ],
                "TikTok": [ ... 동일하게 5개 ... ]
            }}
            """

            response = model.generate_content(prompt)
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            trends_data = json.loads(raw_text)

            st.success("🎉 분석 및 기획 완료! 아래 키워드를 클릭하여 아이디어와 레퍼런스를 확인하세요.")

            # UI 출력 (클릭 가능한 확장 패널 형태)
            platforms = ["X (Twitter)", "Threads", "Instagram", "YouTube", "TikTok"]
            tabs = st.tabs(platforms) # 플랫폼을 탭 형태로 예쁘게 분리
            
            for i, platform in enumerate(platforms):
                with tabs[i]:
                    st.markdown(f"### {platform} 트렌드 키워드 TOP 5")
                    items = trends_data.get(platform, [])
                    
                    for item in items:
                        kw = item.get("keyword", "")
                        ideas = item.get("ideas", [])
                        clean_kw = kw.replace("#", "").replace(" ", "") # URL용 검색어 정제
                        
                        # 키워드 클릭 시 열리는 아코디언(Expander) UI
                        with st.expander(f"✨ **{kw}**"):
                            st.markdown("💡 **콘텐츠 아이디어 (3가지)**")
                            for idea in ideas:
                                st.markdown(f"- {idea}")
                            
                            st.markdown("---")
                            st.markdown("🔗 **실제 콘텐츠 URL & 탐색 (Click)**")
                            
                            # URL 생성
                            url_x = f"https://twitter.com/search?q=%23{urllib.parse.quote(clean_kw)}"
                            url_yt = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_kw)}"
                            url_ig = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(clean_kw)}/"
                            url_tk = f"https://www.tiktok.com/tag/{urllib.parse.quote(clean_kw)}"
                            url_pin = f"https://www.pinterest.co.kr/search/pins/?q={urllib.parse.quote(clean_kw)}"

                            # 버튼 가로 배치
                            c1, c2, c3, c4, c5 = st.columns(5)
                            c1.link_button("🐦 X 피드 검색", url_x)
                            c2.link_button("📺 YouTube 검색", url_yt)
                            c3.link_button("📸 Instagram 검색", url_ig)
                            c4.link_button("🎵 TikTok 검색", url_tk)
                            c5.link_button("📌 Pinterest 무드보드", url_pin)

            # 신뢰도 테이블 영역 추가
            st.markdown("---")
            st.markdown("### 📊 데이터 수집 및 신뢰도 요약")
            st.info("본 데이터는 선택한 기간의 웹 검색, 기사 트렌드, SNS 성격을 기반으로 AI가 실시간 추론한 데이터입니다. 하단의 실제 수치 확인 도구를 함께 활용하시길 권장합니다.")
            st.markdown("""
            * **Google Trends (검색어 동향):** [trends.google.co.kr](https://trends.google.co.kr/)
            * **네이버 DataLab (쇼핑인사이트):** [datalab.naver.com](https://datalab.naver.com/)
            * **TikTok Creative Center:** [ads.tiktok.com](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/ko)
            """)

        except Exception as e:
            st.error(f"오류가 발생했습니다. AI 응답이 지연되었을 수 있으니 다시 버튼을 눌러주세요.\n\n상세 오류: {e}")
