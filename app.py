"""
Flask application for "What Would They Say?" Advisor
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from prompts.personalities import get_personality, PERSONALITIES
from utils.rag_pipeline import RAGPipeline
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store RAG pipeline for Steve Jobs (initialized on first use)
steve_jobs_pipeline = None


def get_steve_jobs_pipeline():
    """Get or create RAG pipeline for Steve Jobs"""
    global steve_jobs_pipeline
    if steve_jobs_pipeline is None:
        documents_path = "steve_job_pdf.pdf"
        steve_jobs_pipeline = RAGPipeline("steve_jobs", documents_path)
        steve_jobs_pipeline.setup()
    return steve_jobs_pipeline


def query_with_system_prompt(personality_id, message):
    """
    Query a personality using just the system prompt (no RAG)
    Used for Kobe Bryant and Marcus Aurelius
    """
    personality = get_personality(personality_id)
    if not personality:
        return {"error": "Personality not found"}

    # Format the system prompt with empty context
    prompt = personality['system_prompt'].format(
        context="[No specific source material available, respond based on general knowledge of this person's philosophy and style]",
        question=message
    )

    # Get LLM response
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    response = llm.invoke(prompt)

    return {
        "response": response.content,
        "sources": []
    }


@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')


@app.route('/select')
def select():
    """Personality selection page"""
    # Get only the 3 available personalities
    available_ids = ["steve_jobs", "kobe_bryant", "marcus_aurelius"]
    personalities = []
    for p_id in available_ids:
        p_data = PERSONALITIES[p_id]
        personalities.append({
            "id": p_id,
            "name": p_data["name"],
            "domain": p_data["domain"],
            "quote": p_data["quote"],
            "accent_color": p_data["accent_color"],
            "available": True
        })
    return render_template('select.html', personalities=personalities)


@app.route('/chat')
def chat():
    """Multi-column chat interface (3 personalities at once)"""
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint to send a message and get a response from a personality"""
    data = request.json
    personality_id = data.get('personality_id')
    message = data.get('message')

    if not personality_id or not message:
        return jsonify({"error": "Missing personality_id or message"}), 400

    # Get personality config
    personality = get_personality(personality_id)
    if not personality:
        return jsonify({"error": "Personality not found"}), 404

    try:
        # Handle Steve Jobs with RAG
        if personality_id == "steve_jobs":
            pipeline = get_steve_jobs_pipeline()
            result = pipeline.query(
                question=message,
                system_prompt_template=personality['system_prompt']
            )
        # Handle Kobe and Marcus with system prompt only
        elif personality_id in ["kobe_bryant", "marcus_aurelius"]:
            result = query_with_system_prompt(personality_id, message)
        else:
            return jsonify({"error": "Personality not available"}), 404

        # Check if there was an error
        if 'error' in result:
            return jsonify({"error": result['error']}), 500

        return jsonify({
            "response": result['response'],
            "sources": result.get('sources', [])
        })

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    print("Starting Flask app...")
    print("Available at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
