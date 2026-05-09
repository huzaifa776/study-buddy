from src.models.question_schemas import MCQQuestion,FillBlankQuestion
from src.prompt.templates import mcq_prompt_template,fill_blank_prompt_template
from src.llm.groq_client import get_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
import json
import re


class QuestionGenerator:
    def __init__(self):
        self.llm = get_llm()
        self.logger = get_logger(self.__class__.__name__)

    def _normalize_response_content(self, response_content):
        content = response_content

        if isinstance(content, dict) and 'text' in content:
            content = content['text']
        elif isinstance(content, list):
            content = " ".join([str(item) for item in content])

        content_str = str(content).strip()

        if content_str.startswith("```"):
            content_str = re.sub(r"^```(?:json)?\s*", "", content_str)
            content_str = re.sub(r"\s*```$", "", content_str)

        if content_str.startswith("{'type': 'text', 'text':"):
            match = re.search(r"'text': '(.*?)', 'extras':", content_str, re.DOTALL)
            if match:
                content_str = match.group(1).encode().decode('unicode_escape')

        return content_str

    def _extract_json_payload(self, content_str):
        try:
            return json.loads(content_str)
        except json.JSONDecodeError:
            pass

        object_match = re.search(r"\{.*\}", content_str, re.DOTALL)
        if object_match:
            return json.loads(object_match.group(0))

        array_match = re.search(r"\[.*\]", content_str, re.DOTALL)
        if array_match:
            return json.loads(array_match.group(0))

        raise ValueError("Model response did not contain valid JSON")

    def _retry_and_parse_questions(self, prompt, topic, difficulty, count, model_cls):

        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating {count} question(s) for topic {topic} with difficulty {difficulty}")

                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty, count=count))

                content_str = self._normalize_response_content(response.content)
                payload = self._extract_json_payload(content_str)

                if not isinstance(payload, dict) or "questions" not in payload:
                    raise ValueError("Expected a JSON object with a questions field")

                questions = payload["questions"]
                if not isinstance(questions, list):
                    raise ValueError("questions field must be a list")
                if len(questions) != count:
                    raise ValueError(f"Expected {count} questions but received {len(questions)}")

                parsed_questions = [model_cls(**question) for question in questions]

                self.logger.info("Successfully parsed the questions")

                return parsed_questions
            
            except Exception as e:
                self.logger.error(f"Error coming : {str(e)}")
                if attempt==settings.MAX_RETRIES-1:
                    raise CustomException(f"Generation failed after {settings.MAX_RETRIES} attempts", e)
                
    
    def generate_mcqs(self, topic:str, difficulty:str='medium', count:int=1) -> list[MCQQuestion]:
        try:
            questions = self._retry_and_parse_questions(mcq_prompt_template, topic, difficulty, count, MCQQuestion)

            for question in questions:
                if len(question.options) != 4 or question.correct_answer not in question.options:
                    raise ValueError("Invalid MCQ Structure")
            
            self.logger.info("Generated valid MCQ questions")
            return questions
        
        except Exception as e:
            self.logger.error(f"Failed to generate MCQs : {str(e)}")
            raise CustomException("MCQ generation failed" , e)
        
    
    def generate_fill_blanks(self, topic:str, difficulty:str='medium', count:int=1) -> list[FillBlankQuestion]:
        try:
            questions = self._retry_and_parse_questions(fill_blank_prompt_template, topic, difficulty, count, FillBlankQuestion)

            for question in questions:
                if "___" not in question.question:
                    raise ValueError("Fill in blanks should contain '___'")
            
            self.logger.info("Generated valid Fill in the Blank questions")
            return questions
        
        except Exception as e:
            self.logger.error(f"Failed to generate fill blanks : {str(e)}")
            raise CustomException("Fill in blanks generation failed" , e)

