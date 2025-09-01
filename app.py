# -*- coding: utf-8 -*-
"""
이 스크립트는 FastAPI를 사용하여 통합 검색 API를 제공합니다.
- /search 엔드포인트를 통해 검색 기능을 웹 서비스로 노출합니다.
- main.py의 SearchService 클래스를 사용하여 실제 검색 로직을 수행합니다.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from main import SearchService
import json

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# SearchService 인스턴스 생성
# 애플리케이션 시작 시 한 번만 생성하여 재사용합니다.
search_service = SearchService()

@app.get("/search")
def search_api(query: str, use_naver_blog: bool = True, use_naver_news: bool = True, use_google_search: bool = True):
    """
    통합 검색 API 엔드포인트입니다.

    쿼리 파라미터를 통해 검색어와 사용할 검색 엔진을 지정할 수 있습니다.
    - **query**: 검색할 키워드 (필수)
    - **use_naver_blog**: 네이버 블로그 검색 사용 여부 (선택, 기본값: True)
    - **use_naver_news**: 네이버 뉴스 검색 사용 여부 (선택, 기본값: True)
    - **use_google_search**: 구글 검색 사용 여부 (선택, 기본값: True)
    """
    try:
        # SearchService를 사용하여 검색 수행
        results_json_str = search_service.search(
            query=query,
            use_naver_blog=use_naver_blog,
            use_naver_news=use_naver_news,
            use_google_search=use_google_search
        )
        
        # JSON 문자열을 파이썬 객체(리스트)로 변환
        results_list = json.loads(results_json_str)
        
        # 결과를 JSONResponse로 반환
        return JSONResponse(content=results_list)

    except Exception as e:
        # 에러 발생 시 500 상태 코드와 에러 메시지 반환
        return JSONResponse(status_code=500, content={"error": str(e)})

# 서버 실행 가이드 (터미널에서 직접 실행 시)
# uvicorn app:app --reload
