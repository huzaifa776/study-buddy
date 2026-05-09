from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Create {count} distinct {difficulty} multiple-choice questions about {topic}.\n"
        "Return JSON only in this format: {{\"questions\":[{{\"question\":\"...\",\"options\":[\"...\",\"...\",\"...\",\"...\"],\"correct_answer\":\"...\"}}]}}\n"
        "Use exactly 4 options per question, keep questions different, and keep the response concise.\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "count"]
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Create {count} distinct {difficulty} fill-in-the-blank questions about {topic}.\n"
        "Return JSON only in this format: {{\"questions\":[{{\"question\":\"... ___ ...\",\"answer\":\"...\"}}]}}\n"
        "Each question must contain a blank marker, keep questions different, and keep the response concise.\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "count"]
)