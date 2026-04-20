import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from factories.component_factory import ComponentFactory

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


if __name__ == "__main__":
    print("⚡️ Oracle Bot is waking up...")
    # Socket Mode handler requires the App Level Token (xapp-...)
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()