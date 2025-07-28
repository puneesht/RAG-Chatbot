import gradio as gr
from pdf import pdf_engines
import base64
import os

print("Files in current dir:", os.listdir())

# Step 1: Read and encode the background image
def get_base64_bg(path):
    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

background_base64 = get_base64_bg("background.png")

# Step 2: Embed image in CSS
css = f"""
.gradio-container {{
    background-image: url("{background_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
}}
.gradio-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.3);  /* Light overlay for readability */
    z-index: 0;
}}
.gradio-container > * {{
    position: relative;
    z-index: 1;
}}
"""

def answer_question(pdf_name, question):
    engine = pdf_engines[pdf_name]
    result = engine.query(question)
    return str(result)

with gr.Blocks(theme=gr.themes.Soft(), css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Image("logo.png", show_label=False, show_download_button=False, elem_id="company-logo", height=70)
            gr.Markdown(
                """
                # <span style='color:#6966FF;'>  Tachyon HR Chatbot</span>
                <small>
                <span style='color:#444;'>  Ask questions from <b>any PDF</b> in your data folder.<br>
                Select a document, type your question, and get instant answers.</span>
                </small>
                """,
                elem_id="header-md"
            )
            pdf_choice = gr.Dropdown(
                choices=list(pdf_engines.keys()),
                label="📄 Select PDF Document",
                elem_id="pdf-dropdown"
            )
        with gr.Column(scale=2):
            gr.Markdown("<hr>")
            question = gr.Textbox(
                label="Your Question",
                placeholder="Type your question and press 'Ask'...",
                elem_id="question-box"
            )
            answer = gr.Markdown(
                label="Answer",
                elem_id="answer-box"
            )
            ask = gr.Button("Ask", elem_id="ask-btn", variant="primary")

    def submit_question(pdf_name, question):
        if not pdf_name:
            return "Please select a PDF document.", question
        if not question.strip():
            return "", question
        result = answer_question(pdf_name, question)
        return result, question

    ask.click(submit_question, inputs=[pdf_choice, question], outputs=[answer, question])

    gr.Markdown(
        """
        ---
        ### ℹ️ About this Tool
        Powered by AI to answer questions from your documents. 
        """
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
