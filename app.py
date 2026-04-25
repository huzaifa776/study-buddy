import os

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager

load_dotenv()

MAX_QUESTIONS = 10
APP_THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="cyan")



def build_question_updates(questions):
    card_updates = []
    question_updates = []
    mcq_updates = []
    fill_updates = []

    for index in range(MAX_QUESTIONS):
        if index < len(questions):
            question = questions[index]
            card_updates.append(gr.update(visible=True))
            question_updates.append(
                gr.update(value=f"### Question {index + 1}\n{question['question']}", visible=True)
            )

            if question["type"] == "MCQ":
                mcq_updates.append(
                    gr.update(choices=question["options"], value=None, visible=True)
                )
                fill_updates.append(gr.update(value="", visible=False))
            else:
                mcq_updates.append(gr.update(choices=[], value=None, visible=False))
                fill_updates.append(gr.update(value="", visible=True))
        else:
            card_updates.append(gr.update(visible=False))
            question_updates.append(gr.update(value="", visible=False))
            mcq_updates.append(gr.update(choices=[], value=None, visible=False))
            fill_updates.append(gr.update(value="", visible=False))

    return card_updates, question_updates, mcq_updates, fill_updates


def reset_question_updates():
    empty_cards = [gr.update(visible=False) for _ in range(MAX_QUESTIONS)]
    empty_questions = [gr.update(value="", visible=False) for _ in range(MAX_QUESTIONS)]
    empty_mcqs = [gr.update(choices=[], value=None, visible=False) for _ in range(MAX_QUESTIONS)]
    empty_fills = [gr.update(value="", visible=False) for _ in range(MAX_QUESTIONS)]
    return empty_cards, empty_questions, empty_mcqs, empty_fills


def generate_quiz(model_provider, question_type, topic, difficulty, num_questions, quiz_manager):
    topic = (topic or "").strip()
    if not topic:
        empty_cards, empty_questions, empty_mcqs, empty_fills = reset_question_updates()
        return (
            quiz_manager,
            "Enter a topic before generating a quiz.",
            "",
            pd.DataFrame(),
            gr.update(value=None, visible=False),
            *empty_cards,
            *empty_questions,
            *empty_mcqs,
            *empty_fills,
            gr.update(visible=False),
        )

    generator = QuestionGenerator(model_provider)
    success = quiz_manager.generate_questions(
        generator,
        topic,
        question_type,
        difficulty,
        int(num_questions),
    )

    if not success:
        empty_cards, empty_questions, empty_mcqs, empty_fills = reset_question_updates()
        return (
            quiz_manager,
            "Quiz generation failed. Check the logs and try again.",
            "",
            pd.DataFrame(),
            gr.update(value=None, visible=False),
            *empty_cards,
            *empty_questions,
            *empty_mcqs,
            *empty_fills,
            gr.update(visible=False),
        )

    card_updates, question_updates, mcq_updates, fill_updates = build_question_updates(quiz_manager.questions)
    return (
        quiz_manager,
        f"Generated {len(quiz_manager.questions)} question(s).",
        "",
        pd.DataFrame(),
        gr.update(value=None, visible=False),
        *card_updates,
        *question_updates,
        *mcq_updates,
        *fill_updates,
        gr.update(visible=False),
    )


def submit_quiz(quiz_manager, question_type, *answer_values):
    if not quiz_manager.questions:
        return (
            quiz_manager,
            "Generate a quiz before submitting answers.",
            "",
            pd.DataFrame(),
            gr.update(value=None, visible=False),
            gr.update(visible=False),
        )

    count = len(quiz_manager.questions)
    mcq_answers = list(answer_values[:MAX_QUESTIONS])
    fill_answers = list(answer_values[MAX_QUESTIONS:MAX_QUESTIONS * 2])

    if question_type == "Multiple Choice":
        quiz_manager.user_answers = mcq_answers[:count]
    else:
        quiz_manager.user_answers = fill_answers[:count]

    quiz_manager.evaluate_quiz()
    results_df = quiz_manager.generate_result_dataframe()

    if results_df.empty:
        return (
            quiz_manager,
            "No results were generated.",
            "",
            pd.DataFrame(),
            gr.update(value=None, visible=False),
            gr.update(visible=False),
        )

    correct_count = int(results_df["is_correct"].sum())
    total_questions = len(results_df)
    score_percentage = (correct_count / total_questions) * 100
    
    # Determine performance emoji and color
    if score_percentage >= 90:
        emoji = "🌟"
        message = "Outstanding!"
    elif score_percentage >= 75:
        emoji = "🎉"
        message = "Great job!"
    elif score_percentage >= 60:
        emoji = "👍"
        message = "Good effort!"
    else:
        emoji = "💪"
        message = "Keep practicing!"
    
    summary = f"""
    <div class='score-display'>
        <h3>{emoji} {message}</h3>
        <h2>{correct_count}/{total_questions}</h2>
        <p style='font-size: 1.2rem; font-weight: 600;'>{score_percentage:.1f}% Correct</p>
    </div>
    """

    return (
        quiz_manager,
        "Quiz evaluated successfully.",
        summary,
        results_df,
        gr.update(value=None, visible=True),
        gr.update(visible=True),
    )


def save_results(quiz_manager):
    saved_file = quiz_manager.save_to_csv()
    if not saved_file:
        return gr.update(value=None, visible=False), "No results available to save."

    return gr.update(value=saved_file, visible=True), f"Saved results to {os.path.basename(saved_file)}."


def create_app():
    with gr.Blocks(title="Study Buddy AI", theme=APP_THEME, css="assets/style.css") as demo:
        quiz_manager = gr.State(QuizManager())

        # HEADER
        gr.HTML(
            """
            <div class="header-banner">
                <h1>📚 Study Buddy AI</h1>
                <p>Intelligent Quiz Generation & AI-Powered Learning</p>
            </div>
            """
        )

        with gr.Column():
            # STEP 1: CONFIGURATION
            with gr.Group(elem_classes=["config-panel"]):
                gr.HTML("<div class='config-title'>⚙️ Step 1: Configure Your Quiz</div>")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        with gr.Group(elem_classes=["control-group"]):
                            topic = gr.Textbox(
                                label="🎯 Topic",
                                placeholder="E.g: Photosynthesis, World War 2, Python Basics",
                                lines=2
                            )
                    with gr.Column(scale=1):
                        with gr.Group(elem_classes=["control-group"]):
                            question_type = gr.Dropdown(
                                choices=["Multiple Choice", "Fill in the Blank"],
                                value="Multiple Choice",
                                label="❓ Question Format"
                            )
                        with gr.Group(elem_classes=["control-group"]):
                            difficulty = gr.Dropdown(
                                choices=["Easy", "Medium", "Hard"],
                                value="Medium",
                                label="📊 Difficulty"
                            )
                    with gr.Column(scale=1):
                        with gr.Group(elem_classes=["control-group"]):
                            model_provider = gr.Dropdown(
                                choices=["Llama 80B powered by Groq", "Gemini 3 Flash"],
                                value="Llama 80B powered by Groq",
                                label="🤖 AI Model",
                                info="Groq=Speed, Gemini=Depth"
                            )
                        with gr.Group(elem_classes=["control-group"]):
                            num_questions = gr.Slider(
                                minimum=1,
                                maximum=10,
                                step=1,
                                value=5,
                                label="📝 Questions"
                            )
                
                generate_btn = gr.Button(
                    "🎲 Generate Quiz",
                    variant="primary",
                    elem_classes=["btn-primary"],
                    size="lg"
                )
                
                status = gr.Markdown("✨ Ready to start? Configure your quiz above and generate questions!")

            # STEP 2: QUESTIONS SECTION
            gr.HTML("<div class='questions-container'><div class='quiz-section-title' style='color: #0f172a; margin-top: 20px;'>🧠 Step 2: Take the Quiz</div></div>")
            
            question_markdowns = []
            mcq_inputs = []
            fill_inputs = []
            question_cards = []

            for index in range(MAX_QUESTIONS):
                with gr.Group(visible=False, elem_classes=["question-card"]) as question_card:
                    question_cards.append(question_card)
                    
                    # Question number and text
                    gr.HTML(f"<div class='question-number'>{index + 1}</div>")
                    markdown_comp = gr.Markdown()
                    question_markdowns.append(markdown_comp)
                    
                    # MCQ Answer
                    with gr.Group(visible=True, elem_classes=["answer-input"]):
                        mcq_input = gr.Radio(
                            choices=[],
                            label="Select your answer",
                            visible=False,
                        )
                        mcq_inputs.append(mcq_input)
                    
                    # Fill-in-the-Blank Answer
                    with gr.Group(visible=True, elem_classes=["answer-input"]):
                        fill_input = gr.Textbox(
                            label="Type your answer",
                            placeholder="Enter your response...",
                            lines=1,
                            visible=False
                        )
                        fill_inputs.append(fill_input)
            
            submit_btn = gr.Button(
                "✅ Submit Answers",
                variant="secondary",
                elem_classes=["btn-secondary"],
                size="lg"
            )

            # STEP 3: RESULTS SECTION
            gr.HTML("<div class='results-title' style='margin-top: 40px;'>📊 Step 3: Your Results & Score</div>")
            
            with gr.Group(elem_classes=["results-panel"]):
                score = gr.HTML("")
                
                results_table = gr.Dataframe(
                    value=pd.DataFrame(),
                    interactive=False,
                    wrap=True,
                    min_width=400
                )
                
                with gr.Row():
                    save_btn = gr.Button(
                        "💾 Save Results",
                        visible=False,
                        elem_classes=["btn-success"]
                    )
                    saved_file = gr.File(
                        label="📥 Downloaded Results",
                        visible=False
                    )

        # EVENT HANDLERS
        generate_btn.click(
            fn=generate_quiz,
            inputs=[model_provider, question_type, topic, difficulty, num_questions, quiz_manager],
            outputs=[
                quiz_manager,
                status,
                score,
                results_table,
                saved_file,
                *question_cards,
                *question_markdowns,
                *mcq_inputs,
                *fill_inputs,
                save_btn,
            ],
        )

        submit_btn.click(
            fn=submit_quiz,
            inputs=[quiz_manager, question_type, *mcq_inputs, *fill_inputs],
            outputs=[quiz_manager, status, score, results_table, saved_file, save_btn],
        )

        save_btn.click(
            fn=save_results,
            inputs=[quiz_manager],
            outputs=[saved_file, status],
        )

    return demo


if __name__ == "__main__":
    create_app().launch()

        
