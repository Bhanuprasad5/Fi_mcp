# app.py
# This file creates a Flask web server to expose your agent via an API.

import asyncio
import logging

# Import the agent factory function from your other file
from agents import create_retirement_agent
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# --- Basic Server and Logging Setup ---
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
# Enable CORS to allow your web front-end to call this server
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- ADK Setup ---
# 1. Create the agent instance using the factory function
AGENT = create_retirement_agent()
# 2. Create a session service to manage conversation history
SESSION_SERVICE = InMemorySessionService()
# 3. Create a runner to execute the agent's logic
RUNNER = Runner(agent=AGENT, session_service=SESSION_SERVICE)

# --- API Endpoints ---

@app.route("/api/sessions", methods=["POST"])
async def create_session():
    """
    Creates a new conversation session and returns its ID.
    """
    try:
        session_id = await SESSION_SERVICE.create_session()
        logging.info(f"New session created: {session_id}")
        return jsonify({"session_id": session_id}), 201
    except Exception as e:
        logging.error(f"Error creating session: {e}")
        return jsonify({"error": "Failed to create session"}), 500

@app.route("/api/sessions/<session_id>/messages", methods=["POST"])
async def post_message(session_id: str):
    """
    Receives a user message, runs the agent, and streams the response.
    """
    try:
        # Extract user input from the request body
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Message not provided"}), 400
        user_input = data["message"]
        logging.info(f"Received message for session {session_id}: {user_input}")

        # This is the core function that runs the agent logic
        # It returns a generator that yields parts of the response as they are generated
        async def stream_response():
            try:
                # The run_conversation method handles the entire agent interaction
                async for chunk in RUNNER.run_conversation(
                    session_id=session_id, user_input=user_input
                ):
                    # In a streaming response, chunks can be of different types
                    # (e.g., intermediate thoughts, tool output, final answer).
                    # We serialize the chunk to a JSON string to send it over HTTP.
                    yield chunk.to_json() + "\n"
                logging.info(f"Finished streaming for session {session_id}")
            except Exception as e:
                logging.error(f"Error during agent execution for session {session_id}: {e}")
                error_chunk = {"error": str(e)}
                import json
                yield json.dumps(error_chunk) + "\n"

        # Return a streaming HTTP response
        return Response(stream_response(), mimetype="application/x-ndjson")

    except Exception as e:
        logging.error(f"Error in message handler for session {session_id}: {e}")
        return jsonify({"error": "Failed to process message"}), 500

# --- Main Execution ---
if __name__ == "__main__":
    # Use a port that is unlikely to conflict with other services
    PORT = 5001
    print("="*50)
    print("🚀 ADK Agent Server starting...")
    print(f"      Agent: {AGENT.name}")
    print(f"      URL: http://localhost:{PORT}")
    print("      Endpoints:")
    print(f"        - POST /api/sessions (to create a new chat session)")
    print(f"        - POST /api/sessions/<id>/messages (to send a message)")
    print("="*50)
    # Run the Flask app
    app.run(host="0.0.0.0", port=PORT)

