import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from factories.component_factory import ComponentFactory

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Initialize Slack App
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# 2. Initialize RAG Architecture
factory = ComponentFactory(config_path="config.yaml")
retrieval_service = factory.get_retrieval_service()
generation_service = factory.get_generation_service()

# Memory Dictionary to hold thread contexts (Simple dict for Phase 1)
# In V2, this should be moved to a Redis cache
session_memory = {}

@app.event("app_mention")
def handle_app_mention_events(body, say):
    """Listens for @OracleBot in Slack channels."""
    event = body.get("event", {})
    user_query = event.get("text", "").strip()
    thread_ts = event.get("thread_ts", event.get("ts")) # Reply in the same thread
    channel_id = event.get("channel")

    logger.info(f"Received query: {user_query}")

    # Remove the bot mention (e.g., "<@U12345> how do I...") from the text
    if ">" in user_query:
        user_query = user_query.split(">", 1)[1].strip()

    # Get or create chat history for this thread
    if thread_ts not in session_memory:
        session_memory[thread_ts] = []
    chat_history = session_memory[thread_ts]

    # Process through RAG Pipeline
    try:
        retrieved_docs = retrieval_service.retrieve(user_query)
        
        response = generation_service.answer_query(
            query=user_query, 
            context=retrieved_docs, 
            chat_history=chat_history
        )

        # Update memory
        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": response})

        # Post answer back to Slack
        say(text=response, thread_ts=thread_ts)
        
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        say(text="I encountered an error while consulting the archives.", thread_ts=thread_ts)

@app.event("message")
def handle_direct_messages(body, say):
    """Listens for direct 1-on-1 messages to the bot in its App tab."""
    event = body.get("event", {})
    channel_type = event.get("channel_type")
    
    if channel_type == "im":
        # Ignore the bot's own messages
        if event.get("bot_id"):
            return

        user_query = event.get("text", "").strip()
        logger.info(f"Received DM query: {user_query}")

        # --- FIX 1: Proper Threading ---
        # Only use thread_ts if the user actually clicked "Reply in thread" in the DM
        thread_ts = event.get("thread_ts")

        # --- FIX 2: Handle Greetings & Small Talk ---
        small_talk = ["hi", "hello", "hey", "help", "morning", "ping"]
        if user_query.lower() in small_talk:
            greeting_text = (
                "Hello! 👋 I am your **Knowledge Oracle**.\n\n"
                "I am wired into the organization's public Slack channels. "
                "Ask me a question, and I'll find the answer, unblock you, and give you the link to the original discussion.\n\n"
                "*What would you like to know?*"
            )
            # Send greeting properly (in thread if threaded, else in main DM)
            if thread_ts:
                say(text=greeting_text, thread_ts=thread_ts)
            else:
                say(text=greeting_text)
            return  # Stop here! Don't waste an LLM call on "hi"

        # --- RAG Pipeline (Runs only for real questions) ---
        
        # Memory key: If threaded, use the thread ID. If top-level DM, use the User's ID.
        user_id = event.get("user")
        session_key = thread_ts if thread_ts else user_id

        if session_key not in session_memory:
            session_memory[session_key] = []
        chat_history = session_memory[session_key]

        try:
            retrieved_docs = retrieval_service.retrieve(user_query)
            
            response = generation_service.answer_query(
                query=user_query, 
                context=retrieved_docs, 
                chat_history=chat_history
            )

            # Update memory
            chat_history.append({"role": "user", "content": user_query})
            chat_history.append({"role": "assistant", "content": response})

            # Send response properly
            if thread_ts:
                say(text=response, thread_ts=thread_ts)
            else:
                say(text=response)
            
        except Exception as e:
            logger.error(f"Failed to generate response in DM: {e}")
            error_msg = "I encountered an error while consulting the archives."
            if thread_ts:
                say(text=error_msg, thread_ts=thread_ts)
            else:
                say(text=error_msg)

if __name__ == "__main__":
    print("⚡️ Oracle Bot is waking up...")
    # Socket Mode handler requires the App Level Token (xapp-...)
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()