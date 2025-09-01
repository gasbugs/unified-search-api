# 통합 검색 API (Unified Search API)

다양한 검색 엔진(네이버 블로그, 네이버 뉴스, 구글 검색)의 API를 하나로 묶어, 단일 엔드포인트로 통합된 검색 결과를 제공하는 FastAPI 기반의 웹 서비스입니다.

## 주요 기능

- **통합 검색**: 여러 검색 엔진의 결과를 하나의 API 호출로 받아볼 수 있습니다.
- **출처 명시**: 각 검색 결과에 출처(`source`) 정보(예: "Naver Blog")가 포함되어 있습니다.
- **동적 파라미터**: 쿼리 파라미터를 통해 특정 검색 엔진을 동적으로 활성화/비활성화할 수 있습니다.
- **객체 지향 설계**: 검색 로직을 `SearchService` 클래스로 캡슐화하여 코드의 재사용성과 유지보수성을 높였습니다.
- **자동 API 문서**: FastAPI를 통해 Swagger UI와 ReDoc API 문서를 자동으로 생성합니다.

## 프로젝트 구조

```
.
├── .env              # API 키 등 환경 변수 설정 파일
├── app.py            # FastAPI 애플리케이션 (API 엔드포인트 정의)
├── main.py           # 핵심 검색 로직 (SearchService 클래스)
├── requirements.txt  # 프로젝트 의존성 패키지 목록
├── test_app.py       # app.py에 대한 단위 테스트
└── test_main.py      # main.py에 대한 단위 테스트
```

## 설치 및 설정

1.  **저장소 복제:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **가상 환경 생성 및 활성화 (권장):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **의존성 패키지 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **`.env` 파일 설정:**
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래와 같이 네이버와 구글에서 발급받은 API 키를 입력합니다.

    ```env
    NAVER_CLIENT_ID="YOUR_NAVER_CLIENT_ID"
    NAVER_CLIENT_SECRET="YOUR_NAVER_CLIENT_SECRET"
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    GOOGLE_CSE_ID="YOUR_GOOGLE_CSE_ID"
    ```

## 로컬 서버 실행

아래 명령어를 사용하여 FastAPI 개발 서버를 실행합니다.

```bash
uvicorn app:app --reload
```

서버가 실행되면 `http://127.0.0.1:8000` 주소로 접속할 수 있습니다.

-   **API 문서 (Swagger UI):** `http://127.0.0.1:8000/docs`
    -   **참고:** API 테스트 전, 우측 상단의 'Authorize' 버튼을 클릭하고 `abcdefg12345`를 입력하여 인증해야 합니다.
-   **API 문서 (ReDoc):** `http://127.0.0.1:8000/redoc`

## API 엔드포인트

### `GET /search`

통합 검색을 수행합니다. **(API 키 인증 필요)**

-   **URL:** `/search`
-   **Method:** `GET`
-   **Headers:**
    -   `key` (str, **필수**): `abcdefg12345`
-   **쿼리 파라미터:**
    -   `query` (str, **필수**): 검색할 키워드.
    -   `use_naver_blog` (bool, 선택, 기본값: `True`): 네이버 블로그 검색 사용 여부.
    -   `use_naver_news` (bool, 선택, 기본값: `True`): 네이버 뉴스 검색 사용 여부.
    -   `use_google_search` (bool, 선택, 기본값: `True`): 구글 검색 사용 여부.

-   **요청 예시 (`curl`):**
    ```bash
    curl -X GET "http://127.0.0.1:8000/search?query=인공지능&use_google_search=false" -H "key: abcdefg12345"
    ```

-   **성공 응답 (200 OK):**
    ```json
    [
      {
        "title": "네이버 블로그 검색 결과",
        "url": "...",
        "content": "...",
        "source": "Naver Blog"
      },
      {
        "title": "네이버 뉴스 검색 결과",
        "url": "...",
        "content": "...",
        "source": "Naver News"
      }
    ]
    ```

## 테스트 실행

프로젝트의 무결성을 확인하기 위해 단위 테스트를 실행할 수 있습니다.

```bash
# 전체 테스트 실행
python -m unittest discover

# 또는 개별 테스트 파일 실행
python -m unittest test_main.py
python -m unittest test_app.py
```
