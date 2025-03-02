import os
from openai import OpenAI
from step1_feedback.feedback import generate_feedback
from step2_research.research import deep_research
from step3_reporting.reporting import write_final_report
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경 변수를 불러옵니다.

def main():
    # 사용자로부터 초기 연구 질문을 입력받음
    query = input("어떤 주제에 대해 리서치하시겠습니까?: ")

    # LLM 클라이언트를 초기화하고 모델 설정
    model = "gpt-4o-mini"
    client = OpenAI()

    # 추가적인 질문을 생성하여 연구 방향을 구체화
    print("\n추가 질문을 생성하는 중...")
    feedback_questions = generate_feedback(query, client, model, max_feedbacks=3)
    answers = []
    if feedback_questions:
        print("\n다음 질문에 답변해 주세요:")
        for idx, question in enumerate(feedback_questions, start=1):
            answer = input(f"질문 {idx}: {question}\n답변: ")
            answers.append(answer)
    else:
        print("추가 질문이 생성되지 않았습니다.")

    # 초기 질문과 후속 질문 및 답변을 결합
    combined_query = f"초기 질문: {query}\n"
    for i in range(len(feedback_questions)):
        combined_query += f"\n{i+1}. 질문: {feedback_questions[i]}\n"
        combined_query += f"   답변: {answers[i]}\n"
        
    print("---------------------------최종 질문----------------------")
    print(combined_query)

    # 연구 범위 및 깊이를 사용자로부터 입력받음
    try:
        breadth = int(input("연구 범위를 입력하세요 (예: 2): ") or "2")
    except ValueError:
        breadth = 2
    try:
        depth = int(input("연구 깊이를 입력하세요 (예: 2): ") or "2")
    except ValueError:
        depth = 2

    # 심층 연구 수행 (동기적으로 실행)
    print("\n연구를 수행하는 중...")
    research_results = deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        client=client,
        model=model
    )

    # 연구 결과 출력
    print("\n연구 결과:")
    for learning in research_results["learnings"]:
        print(f" - {learning}")

    # 최종 보고서 생성
    print("\n최종 보고서를 생성하는 중...")
    model_for_reporting="o3-mini" ## "o1-mini 또는 gpt-4o-mini"로 변경 가능
    report = write_final_report(
        prompt=combined_query,
        learnings=research_results["learnings"],
        visited_urls=research_results["visited_urls"],
        client=client,
        model=model_for_reporting
    )

    # 최종 보고서 출력 및 파일 저장
    print("\n최종 보고서:\n")
    print(report)
    with open("output/output.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n보고서가 output/output.md 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()
