import os

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager

load_dotenv()

MAX_QUESTIONS = 10
APP_THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="cyan")
APP_CSS = """
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body, #root {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    min-height: 100vh;
}

.gradio-container {
    max-width: 1600px !important;
    margin: 0 auto !important;
    padding: 32px 24px !important;
}

/* HEADER SECTION */
.header-banner {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #4f46e5 100%);
    border-radius: 24px;
    padding: 48px 40px;
    margin-bottom: 48px;
    color: white;
    box-shadow: 0 20px 60px rgba(79, 70, 229, 0.3), 0 0 80px rgba(124, 58, 237, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
}

.header-banner h1 {
    margin: 0 0 12px 0 !important;
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    line-height: 1 !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.header-banner p {
    margin: 0 !important;
    font-size: 1.2rem !important;
    opacity: 0.92 !important;
    font-weight: 300;
    letter-spacing: 0.5px;
}

/* CONFIG SECTION */
.config-panel {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(249, 250, 251, 0.95) 100%);
    border-radius: 20px;
    padding: 32px;
    border: 1px solid rgba(79, 70, 229, 0.15);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.config-title {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-bottom: 24px !important;
    display: flex;
    align-items: center;
    gap: 12px;
}

.control-group {
    margin-bottom: 20px;
}

.control-group label {
    display: block;
    font-weight: 600 !important;
    color: #1e293b !important;
    font-size: 0.95rem !important;
    margin-bottom: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.85rem !important;
}

.action-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 32px;
}

.btn-primary, .btn-secondary, .btn-success {
    padding: 14px 28px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    transition: all 0.3s ease;
    border: none !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.btn-primary {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px rgba(79, 70, 229, 0.3);
}

.btn-secondary {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
    color: white !important;
}

.btn-secondary:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px rgba(6, 182, 212, 0.3);
}

.btn-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
}

/* RESULTS PANEL */
.results-panel {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(249, 250, 251, 0.95) 100%);
    border-radius: 20px;
    padding: 32px;
    border: 1px solid rgba(79, 70, 229, 0.15);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.results-title {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-bottom: 24px !important;
}

.status-message {
    padding: 16px 20px;
    border-radius: 12px;
    background: rgba(79, 70, 229, 0.08);
    border-left: 4px solid #4f46e5;
    color: #1e293b;
    font-weight: 500;
    margin-bottom: 20px;
    line-height: 1.6;
}

.status-message.success {
    background: rgba(16, 185, 129, 0.08);
    border-left-color: #10b981;
    color: #065f46;
}

.status-message.error {
    background: rgba(239, 68, 68, 0.08);
    border-left-color: #ef4444;
    color: #7f1d1d;
}

/* SCORE DISPLAY */
.score-display {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 36px 28px;
    border-radius: 16px;
    text-align: center;
    margin: 24px 0;
    box-shadow: 0 20px 50px rgba(79, 70, 229, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.score-display h3 {
    margin: 0 0 16px 0 !important;
    font-size: 1.3rem !important;
    opacity: 0.95;
}

.score-display h2 {
    margin: 0 !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

.score-display p {
    margin: 12px 0 0 0 !important;
    font-size: 1.15rem !important;
    opacity: 0.88;
    font-weight: 500;
}

/* QUESTION CARDS */
.questions-container {
    padding: 32px 0;
}

.quiz-section-title {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: white !important;
    margin-bottom: 32px !important;
    padding: 0 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.question-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(249, 250, 251, 0.94) 100%);
    border: 2px solid rgba(79, 70, 229, 0.2);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.question-card:hover {
    border-color: rgba(79, 70, 229, 0.35);
    box-shadow: 0 20px 50px rgba(79, 70, 229, 0.15);
    transform: translateY(-4px);
}

.question-number {
    display: inline-block;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 12px;
}

.question-card h3 {
    margin: 0 0 20px 0 !important;
    font-size: 1.15rem !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    line-height: 1.6;
}

.answer-input {
    margin-top: 16px;
}

.answer-input label {
    font-weight: 600 !important;
    color: #1e293b !important;
    font-size: 0.9rem !important;
    margin-bottom: 12px !important;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    font-size: 0.8rem !important;
}

.answer-input input, .answer-input textarea, .answer-input select {
    border: 2px solid rgba(79, 70, 229, 0.2) !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    transition: all 0.3s ease !important;
}

.answer-input input:focus, .answer-input textarea:focus, .answer-input select:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}

/* TABLE STYLING */
.dataframe-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.dataframe-container table {
    border-collapse: collapse;
}

.dataframe-container th {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 14px 16px !important;
    font-weight: 700;
    text-align: left;
}

.dataframe-container td {
    padding: 12px 16px !important;
    border-bottom: 1px solid rgba(79, 70, 229, 0.1);
}

.dataframe-container tr:hover {
    background: rgba(79, 70, 229, 0.03);
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .action-buttons {
        grid-template-columns: 1fr;
    }
    
    .header-banner h1 {
        font-size: 2.5rem !important;
    }
    
    .config-panel, .results-panel {
        padding: 24px;
    }
}
"""


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
    with gr.Blocks(title="Study Buddy AI", theme=APP_THEME, css=APP_CSS) as demo:
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
    create_app().launch(theme=APP_THEME, css=APP_CSS)

        
