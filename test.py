import os
from firecrawl import FirecrawlApp
from utils import llm_call, JSON_llm, system_prompt
from pydantic import BaseModel
from typing import Optional

def test_llm_call_sync():
    """Test synchronous LLM call"""
    client = None # Replace with actual client in real test
    prompt = "Say hello"
    model = "gpt-3.5-turbo"
    
    response = llm_call(prompt, model, client)
    print("\nLLM Call Test Results:")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print(f"Response type: {type(response)}")
    print(f"Response length: {len(response)}")





class TestResponse(BaseModel):
    message: str
    score: Optional[float]


def test_json_llm():
    """Test JSON structured LLM response"""
    client = None # Replace with actual client in real test
    prompt = "Return a greeting message with score"
    
    response = JSON_llm(
        user_prompt=prompt,
        schema=TestResponse,
        client=client,
        system_prompt=system_prompt(),
        model="gpt-4"
    )
    print("\nJSON LLM Test Results:")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print(f"Response type: {type(response)}")
    if response:
        print(f"Message: {response.message}")
        print(f"Score: {response.score}")

def test_firecrawl_search():
    # FirecrawlApp 초기화 (API 키 필요)
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))
    
    # 테스트할 검색어 설정
    query = "아침 운동의 신체적 이점 30대"
    
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
            print(f"설명: {result.get('description', '설명 없음')[:200]}...")
            
        return response
        
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    test_llm_call_sync()
    test_json_llm()
    test_firecrawl_search()
    

