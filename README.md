# 서초구 상품권 사용처 지도 (Streamlit + GitHub)

티머니와 문화상품권 사용 가능 가맹점을 서초구 지도 위에 예쁘고 고급스럽게 보여주는 스트림릿 앱입니다.

## 빠른 시작 (로컬)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포
1. 이 저장소를 GitHub에 푸시
2. [streamlit.io/cloud](https://streamlit.io/cloud) 에서 새 앱 생성
3. `Secrets`에 다음을 추가하면 더 예쁜 지도가 나옵니다(선택):
```toml
MAPBOX_API_KEY = "여기에_본인_토큰"
```
(토큰은 https://account.mapbox.com/ 에서 무료 생성 가능)

## 데이터 교체하기
- `data/merchants_seocho.csv` 파일의 컬럼을 유지하면서, 실제 가맹점 좌표(lat, lon)를 넣어 교체하세요.
- 컬럼:
  - `name`: 점포 이름
  - `type`: `tmoney` 또는 `culture`
  - `lat`, `lon`: 위도/경도 (WGS84)
  - `address`: 주소
  - `category`: 업종

## 파일 구조
```
.
├─ app.py
├─ requirements.txt
└─ data/
   └─ merchants_seocho.csv
```
