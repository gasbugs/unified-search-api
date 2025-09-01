# -*- coding: utf-8 -*-
"""
이 스크립트는 FastAPI를 사용하여 통합 검색 API를 제공합니다.
- /search 엔드포인트를 통해 검색 기능을 웹 서비스로 노출합니다.
- main.py의 SearchService 클래스를 사용하여 실제 검색 로직을 수행합니다.
- 모든 엔드포인트는 헤더의 API 키를 통해 보호됩니다.
"""

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from main import SearchService
import json

# --- API 키 검증 의존성 ---
API_KEY = "abcdefg12345"
API_KEY_NAME = "key"

async def verify_api_key(key: str = Header(..., description="API Key")):
    """
    API 키를 검증하는 의존성 함수.
    요청 헤더에 있는 'key' 값을 확인하여 유효하지 않으면 403 Forbidden 에러를 발생시킵니다.
    """
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Request Body 모델 정의 ---
class SearchRequest(BaseModel):
    query: str
    use_naver_blog: bool = True
    use_naver_news: bool = True
    use_google_search: bool = True

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(dependencies=[Depends(verify_api_key)])

# SearchService 인스턴스 생성
search_service = SearchService()

@app.post("/search")
def search_api(request: SearchRequest):
    """
    통합 검색 API 엔드포인트입니다.

    Request Body를 통해 검색어와 사용할 검색 엔진을 지정할 수 있습니다.
    - **query**: 검색할 키워드 (필수)
    - **use_naver_blog**: 네이버 블로그 검색 사용 여부 (선택, 기본값: True)
    - **use_naver_news**: 네이버 뉴스 검색 사용 여부 (선택, 기본값: True)
    - **use_google_search**: 구글 검색 사용 여부 (선택, 기본값: True)
    """
    try:
        results_json_str = search_service.search(
            query=request.query,
            use_naver_blog=request.use_naver_blog,
            use_naver_news=request.use_naver_news,
            use_google_search=request.use_google_search
        )
        
        results_list = json.loads(results_json_str)
        return JSONResponse(content=results_list)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 서버 실행 가이드 (터미널에서 직접 실행 시)
# uvicorn app:app --reload
