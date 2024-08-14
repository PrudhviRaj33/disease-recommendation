from flask import Flask, render_template, request
from gradio_client import Client
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import os

# Ensure consistent results
DetectorFactory.seed = 0

# Initialize Flask app
app = Flask(__name__)

# Initialize Gradio client
client = Client("PrudhviRajGandrothu/llama-3.1")

def is_telugu(text):
    try:
        # Detect the language of the text
        detected_lang = detect(text)
        # Check if the detected language is Telugu ('te')
        return detected_lang == 'te'
    except LangDetectException as e:
        print(f"Error detecting language: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            telugu_text = request.form['disease']
            dummy=telugu_text
            # Sending the Telugu text to the LLM for translation
            prompt = f"Translate the following Telugu text to English: '{telugu_text}'"
            translation = client.predict(
                prompt,  # The prompt to the LLM
                api_name="/chat"  # Replace with the correct API endpoint if necessary
            )
            disease = translation

            # Generate plant suggestions based on the translated disease
            plant_prompt = (
                f"Suggest exactly three Indian plants that can help with curing the following disease: {disease}. "
                "For each plant, provide the following information in HTML format:\n"
                "<h2>Suggested Plants</h2>\n"
                "<ul>\n"
                "<li><b>Plant Title:</b> Provide only the name of the plant.\n"
                "<ul>\n"
                "<li><b>Scientific Name:</b> Provide the scientific name of the plant.</li>\n"
                "<li><b>Benefits:</b> List the benefits of this plant.</li>\n"
                "<li><b>Active Compounds:</b> Key compounds responsible for its medicinal properties.</li>\n"
                "<li><b>Toxic Compounds:</b> Any known toxic compounds and their potential effects.</li>\n"
                "<li><b>Safety and Side Effects:</b> Information on safety, side effects, and interactions.</li>\n"
                "<li><b>Storage Instructions:</b> How to store the plant or its preparations.</li>\n"
                "<li><b>Usage Instructions:</b>\n"
                "<ul>\n"
                "<li>Detail 1</li>\n"
                "<li>Detail 2</li>\n"
                "</ul>\n"
                "</li>\n"
                "<li><b>Alternative Remedies:</b> Other plants or remedies that can be used as alternatives.</li>\n"
                "<li><b>Recipes and Formulations:</b> Specific recipes or ways to prepare the plant for use.</li>\n"
                "</ul>\n"
                "</li>\n"
                "</ul>\n"
                "Ensure that the response includes exactly three plants, each with its own <li> tag, and all sections are detailed and formatted properly within each <li> tag. The <b>Plant Title</b> section should contain only the name of the plant without any additional information."
            )

            result = client.predict(
                message=plant_prompt,
                api_name="/chat"
            )

            if is_telugu(telugu_text):
                # Translate the result to Telugu if the original text was in Telugu
                translate_prompt = f"Translate the following English text to Telugu: '{result}'"
                translation = client.predict(
                    translate_prompt,  # The prompt to the LLM
                    api_name="/chat"  # Replace with the correct API endpoint if necessary
                )
                return render_template('index.html', disease=dummy, plants=translation)
            
            return render_template('index.html', disease=telugu_text, plants=result)
        except Exception as e:
            print(f"Error: {e}")
            return render_template('index.html', disease=None, plants="Error occurred while processing your request.")
    
    return render_template('index.html', disease=None, plants=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port provided by Render
    app.run(host='0.0.0.0', port=port, debug=True)

