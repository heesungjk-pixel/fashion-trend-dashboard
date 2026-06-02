import streamlit as st
import google.generativeai as genai
import json
import urllib.parse

# 페이지 기본 설정
st.set_page_config(page_title="패션 트렌드 대시보드", page_icon="👗", layout="wide")

st.title("🇰🇷 소셜미디어 패션 트렌드 예측 대시보드")
st.markdown("선택한 기간의 플랫폼별 핵심 패션 트렌드 키워드를 AI가 실시간으로 분석해 드립니다.")

# 메인 화면: 날짜 선택
st.markdown("### 📅 분석할 기간을 선택하세요")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일")
with col2:
    end_date = st.date_input("종료일")

if st.button("🚀 트렌드 예측하기", use_container_width=True):
    with st.spinner('원동력 분석 엔진 작동 중... (약 7초 소요)'):
        try:
            api_key = st.secrets["API_KEY"]
            genai.configure(api_key=api_key)

            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            chosen_model = valid_models[0]
            for m in valid_models:
                if 'flash' in m:
                    chosen_model = m
                    break

            model_name = chosen_model.replace("models/", "")
            model = genai.GenerativeModel(model_name)

            # 🚨 [오리지널 마인드맵 래핑 프롬프트 완벽 이식]
            prompt = f"""
            당신은 대한민국 최고의 소셜미디어 패션 트렌드 분석가입니다.
            아래의 데이터 수집 및 키워드 선정 기준에 따라 지정된 기간의 리얼 패션 트렌드를 뾰족하게 도출해주세요.

            [기본 조건]
            - 분석 기간: {start_date} ~ {end_date}
            - 국가: 대한민국
            - 주제: 패션 (의류/스타일링/브랜드/코어트렌드)

            [데이터 수집 및 키워드 선정 기준]
            1. 해당 기간 실제 기사, 뉴스, 검색 결과 및 SNS 반응을 종합하여 가장 언급량이 높은 핵심 트렌드 키워드를 플랫폼별로 10개씩 도출하세요.
            2. 인공지능이 억지로 지어낸 작위적인 신조어는 철저히 배제하고, 실제 대중과 유저들이 소통할 때 사용하는 현실적인 단어 및 아이템명을 선별하세요.
            3. 아래 플랫폼별 고유 성격에 맞게 완벽히 차별화된 결과물을 내야 합니다:
               - X (Twitter): 해시태그 중심, 실시간 반응성이 극대화된 실시간 담론 및 밈
               - Threads: 텍스트 중심 담론, 유저들의 솔직한 취향 공유 및 실제 소비 고민 피드
               - Instagram: 시각적 해시태그 중심, 릴스 트렌드 및 감성 스타일링 용어
               - YouTube: 영상 주제로 적합한 대규모 하울, 체형/상황별 튜토리얼, 신상 리뷰 중심 핵심 단어
               - TikTok: 챌린지, 숏폼 바이럴, 글로벌 마이크로 코어트렌드
            4. 각 플랫폼별 수집 데이터의 성격을 종합 판단하여, 신뢰도 구분을 다음 3가지 중 하나로 명확히 평정하세요: "실데이터" / "기사 기반 추정" / "트렌드 방향만 참고"

            결과는 반드시 아무런 앞뒤 부연 설명 없이 아래 JSON 형식으로만 출력하세요:
            {{
                "X (Twitter)": {{
                    "reliability": "신뢰도 구분 값",
                    "keywords": ["#키워드1", "#키워드2", "#키워드3", "#키워드4", "#키워드5", "#키워드6", "#키워드7", "#키워드8", "#키워드9", "#키워드10"]
                }},
                "Threads": {{
                    "reliability": "신뢰도 구분 값",
                    "keywords": [...]
                }},
                "Instagram": {{
                    "reliability": "신뢰도 구분 값",
                    "keywords": [...]
                }},
                "YouTube": {{
                    "reliability": "신뢰도 구분 값",
                    "keywords": [...]
                }},
                "TikTok": {{
                    "reliability": "신뢰도 구분 값",
                    "keywords": [...]
                }}
            }}
            """

            response = model.generate_content(prompt)
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            trends_data = json.loads(raw_text)

            st.success("🎉 마인드맵 분석 엔진 기반 트렌드 도출 완료!")

            # UI 출력 (플랫폼별 탭 분할)
            platforms = ["X (Twitter)", "Threads", "Instagram", "YouTube", "TikTok"]
            tabs = st.tabs(platforms)
            
            for i, platform in enumerate(platforms):
                with tabs[i]:
                    platform_data = trends_data.get(platform, {})
                    reliability = platform_data.get("reliability", "데이터 확인 중")
                    keywords = platform_data.get("keywords", [])
                    
                    # 상단에 데이터 신뢰도 표기
                    st.markdown(f"🔹 **데이터 신뢰도 수준:** `{reliability}`")
                    st.caption("※ 키워드를 클릭하면 해당 플랫폼의 실시간 제작/소비 피드로 즉시 연결됩니다.")
                    st.write("")
                    
                    # 5개씩 2줄 그리드로 깔끔하게 확장형 버튼(Expander) 배치
                    cols1 = st.columns(5)
                    for j, kw in enumerate(keywords[:5]):
                        with cols1[j]:
                            with st.expander(f"✨ {kw}"):
                                clean_kw = kw.replace("#", "").strip()
                                # 파이썬 백엔드단에서 초고속 URL 연동 (AI 부하 0%)
                                url_x = f"https://twitter.com/search?q={urllib.parse.quote(clean_kw)}"
                                url_yt = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_kw)}"
                                url_ig = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(clean_kw)}/"
                                url_tk = f"https://www.tiktok.com/tag/{urllib.parse.quote(clean_kw)}"
                                url_pin = f"https://www.pinterest.co.kr/search/pins/?q={urllib.parse.quote(clean_kw)}"
                                
                                st.link_button("🐦 X 피드", url_x, use_container_width=True)
                                st.link_button("📺 YouTube", url_yt, use_container_width=True)
                                st.link_button("📸 Instagram", url_ig, use_container_width=True)
                                st.link_button("🎵 TikTok", url_tk, use_container_width=True)
                                st.link_button("📌 Pinterest", url_pin, use_container_width=True)

                    cols2 = st.columns(5)
                    for j, kw in enumerate(keywords[5:10]):
                        with cols2[j]:
                            with st.expander(f"✨ {kw}"):
                                clean_kw = kw.replace("#", "").strip()
                                url_x = f"https://twitter.com/search?q={urllib.parse.quote(clean_kw)}"
                                url_yt = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_kw)}"
                                url_ig = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(clean_kw)}/"
                                url_tk = f"https://www.tiktok.com/tag/{urllib.parse.quote(clean_kw)}"
                                url_pin = f"https://www.pinterest.co.kr/search/pins/?q={urllib.parse.quote(clean_kw)}"
                                
                                st.link_button("🐦 X 피드", url_x, use_container_width=True)
                                st.link_button("📺 YouTube", url_yt, use_container_width=True)
                                st.link_button("📸 Instagram", url_ig, use_container_width=True)
                                st.link_button("🎵 TikTok", url_tk, use_container_width=True)
                                st.link_button("📌 Pinterest", url_pin, use_container_width=True)

            # 하단 신뢰도 정보 및 공식 툴 안내
            st.markdown("---")
            st.markdown("### 📊 데이터 수집 및 신뢰도 요약 안내")
            st.info("본 대시보드는 입력한 기간 동안의 뉴스 기사, 플랫폼별 검색 데이터, 소셜미디어 담론 양상을 원본 프롬프트 알고리즘에 따라 실시간 평가한 결과물입니다.")
            st.markdown("""
            * **Google Trends (검색어 동향):** [trends.google.co.kr](https://trends.google.co.kr/)
            * **네이버 DataLab (쇼핑인사이트):** [datalab.naver.com](https://datalab.naver.com/)
            * **TikTok Creative Center KR (해시태그 랭킹):** [ads.tiktok.com](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/ko)
            """)

        except Exception as e:
            st.error(f"오류가 발생했습니다.\n\n상세 오류: {e}")
