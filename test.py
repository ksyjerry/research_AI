import os
from firecrawl import FirecrawlApp
from openai import OpenAI
from utils import llm_call, JSON_llm, system_prompt
from pydantic import BaseModel
from typing import Optional

def test_llm_call_sync():
    """Test synchronous LLM call"""
    client = OpenAI()
    prompt = "안녕하세요!"
    model = "gpt-4o-mini"
    
    response = llm_call(prompt, model, client)
    print("\nLLM Call Test Results:")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print(f"Response type: {type(response)}")
    print(f"Response length: {len(response)}")



class Evaluation(BaseModel):
    evaluation: str
    score: Optional[float]


def test_json_llm():
    """구조화된 LLM 응답을 받기"""
    client = OpenAI()    
    prompt = "다음 인사가 얼마나 친절한지 1줄로 평가해주고 점수도 0~10점 사이로 알려줘. 인사 : 안녕하십니까!!!"
    model = "gpt-4o-mini"
    
    response = JSON_llm(
        user_prompt=prompt,
        schema=Evaluation,
        client=client,
        system_prompt=system_prompt(),
        model=model
    )
    print("\nJSON LLM Test Results:")
    print(response.model_dump())  

def test_firecrawl_search():
    # FirecrawlApp 초기화 (API 키 필요)
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))
    
    # 테스트할 검색어 설정
    query = "아침 운동의 신체적 이점"
    
    try:
        # 검색 실행
        # timeout: 검색 제한 시간 (밀리초)
        # limit: 최대 결과 수
        # scrapeOptions: 스크래핑 옵션 (마크다운 형식으로 결과 받기)
        response = app.search(
            query=query,
            params={
                "timeout": 15000,
                "limit": 5,
                "scrapeOptions": {"formats": ["markdown"]}
            }
        )
        
        # 검색 결과 출력
        print(f"\n검색어 '{query}'에 대한 결과:\n")
        
        # 각 검색 결과 항목 출력
        for idx, result in enumerate(response["data"], 1):
            print(f"\n결과 {idx}:")
            print(f"제목: {result.get('title', '제목 없음')}")
            print(f"URL: {result.get('url', 'URL 없음')}")
            print(f"본문: {result.get('markdown', 'markdown')[:300]}...")
            print(f"설명: {result.get('description', '설명 없음')[:200]}...")
            
        return response
        
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # test_llm_call_sync()
    # test_json_llm()
    test_firecrawl_search()
    

