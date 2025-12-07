from flask import Flask, request, jsonify, send_from_directory
import os
import traceback

app = Flask(__name__, static_folder='static')

mace_knowledge = ""
try:
    with open('mace_knowledge.txt', 'r') as f:
        mace_knowledge = f.read()
except:
    pass

groq_api_key = os.environ.get("GROQ_API_KEY")
tavily_api_key = os.environ.get("TAVILY_API_KEY")

groq_client = None
tavily_client = None

if groq_api_key:
    try:
        from groq import Groq
        groq_client = Groq(api_key=groq_api_key)
        print("Groq client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")

if tavily_api_key:
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=tavily_api_key)
        print("Tavily client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Tavily client: {e}")


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/ask', methods=['POST'])
def ask():
    try:
        if not groq_client:
            return jsonify({"error": "API keys not configured. Please contact the site owner."}), 500

        data = request.get_json()
        question = data.get("question", "")

        search_text = ""
        if tavily_client:
            try:
                results = tavily_client.search(query=question, max_results=3)
                search_text = "\n".join([
                    r.get("content", "")
                    for r in results.get("results", [])
                ])
            except Exception as e:
                print(f"Tavily search failed: {e}")
                search_text = ""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "system",
                "content": f"You are MaceGPT, the official assistant for MACE (Mad About Civilisations and Empires). IMPORTANT: When someone asks about MACE, ALWAYS use this official information - MACE is NOT a weapon or spice:\n\n{mace_knowledge}\n\nFor questions about Buddhism, Jainism, or other civilizations/empires, you can also use web search results. Be concise and helpful."
            }, {
                "role": "user",
                "content": f"Question: {question}\n\nAdditional Web Search Results:\n{search_text}"
            }])

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
