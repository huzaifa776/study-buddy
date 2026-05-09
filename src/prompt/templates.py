from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Generate exactly {count} distinct {difficulty} multiple-choice questions about {topic}.\n\n"
        "Return ONLY a JSON object with this exact shape:\n"
        '{{\n'
        '    "questions": [\n'
        '        {{\n'
        '            "question": "...",\n'
        '            "options": ["...", "...", "...", "..."],\n'
        '            "correct_answer": "..."\n'
        '        }}\n'
        '    ]\n'
        '}}\n\n'
        "Each question must have exactly 4 options and the correct_answer must be one of them.\n\n"
        "Make the questions different from each other and avoid repeating the same facts.\n\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "count"]
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate exactly {count} distinct {difficulty} fill-in-the-blank questions about {topic}.\n\n"
        "Return ONLY a JSON object with this exact shape:\n"
        '{{\n'
        '    "questions": [\n'
        '        {{\n'
        '            "question": "... _____ ...",\n'
        '            "answer": "..."\n'
        '        }}\n'
        '    ]\n'
        '}}\n\n'
        "Each question must contain '___' or '_____' in the sentence and the answer must match the blank.\n\n"
        "Make the questions different from each other and avoid repeating the same facts.\n\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "count"]
)