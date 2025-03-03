from typing import List
from utils import JSON_llm, system_prompt
from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    questions: List[str]


"""연구 방향을 명확히 하기 위한 후속 질문을 생성합니다."""
def generate_feedback(query: str, client, model: str, max_feedbacks: int = 3) -> List[str]:
    
    prompt = f"""
    Given the following query from the user, ask some follow up questions to clarify the research direction. Return a maximum of ${max_feedbacks} questions, but feel free to return less if the original query is clear.
    ask the follow up questions in korean
    <query>${query}</query>`
    """
    # 프롬프트 의미
    # prompt = (
    #     f"사용자가 다음과 같은 연구 주제에 대해: {query}, 최대 {max_feedbacks}개의 후속 질문을 생성하세요. "
    #     "사용자의 연구 방향을 더 정확히 파악할 수 있도록 구체적이고 명확한 질문을 작성하세요. "
    #     "원래 쿼리가 충분히 명확하다면 질문을 반환하지 않아도 됩니다. "
    #     "응답은 'questions' 배열 필드를 포함하는 JSON 객체로 반환하세요."
    # )

    response = JSON_llm(prompt, FeedbackResponse, client, system_prompt=system_prompt(), model=model)

    try:
        if response is None:
            print("오류: JSON_llm이 None을 반환했습니다.")
            return []
        questions = response.questions
        print(f"주제 '{query}'에 대한 후속 질문 {len(questions)}개 생성됨")
        print(f"생성된 후속 질문: {questions}")
        return questions
    except Exception as e:
        print(f"오류: JSON 응답 처리 중 문제 발생: {e}")
        print(f"원시 응답: {response}")
        print(f"오류: 쿼리 '{query}'에 대한 JSON 응답 처리 실패")
        return []
