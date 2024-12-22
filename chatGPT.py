from flask import Flask, request, jsonify, render_template, stream_with_context, Response
import json
import requests

app = Flask(__name__)

model = "llama3.2"  # TODO: update this for whatever model you wish to use

# Function to interact with the chat model
def chat_stream(messages):
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    r.raise_for_status()

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            yield json.dumps({"error": body["error"]})
            return
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            yield json.dumps({"content": content})
        if body.get("done", False):
            return

# Route for the main chat interface
@app.route('/')
def index():
    return render_template("index.html")

# API route to handle user messages
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid input"}), 400

    messages = data["messages"]
    return Response(stream_with_context(chat_stream(messages)), content_type='application/json')

if __name__ == "__main__":
    app.run(debug=True)
