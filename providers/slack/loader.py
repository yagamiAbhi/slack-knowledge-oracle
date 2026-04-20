import os
import hashlib
import logging
from typing import List
from slack_sdk import WebClient
from interfaces.document_loader import BaseDocumentLoader
from core.entities import Document
from core.registry import ProviderRegistry

logger = logging.getLogger(__name__)

@ProviderRegistry.register_loader("slack")
class SlackDocumentLoader(BaseDocumentLoader):
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.workspace_domain = os.getenv("SLACK_WORKSPACE_DOMAIN", "app")
        # Cache for user IDs to real names to avoid spamming the API
        self.user_cache = {} 

    def _get_real_name(self, user_id: str) -> str:
        if not user_id:
            return "Unknown"
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        try:
            response = self.client.users_info(user=user_id)
            real_name = response["user"]["real_name"]
            self.user_cache[user_id] = real_name
            return real_name
        except Exception as e:
            logger.warning(f"Could not resolve user {user_id}: {e}")
            return user_id

    def load(self, channel_id: str) -> List[Document]:
        """Loads messages and threads from a specific Slack channel."""
        logger.info(f"Fetching messages for channel: {channel_id}")
        documents = []

        try:
            # 1. Fetch channel history
            history = self.client.conversations_history(channel=channel_id, limit=100)
            messages = history.get("messages", [])

            for msg in messages:
                # Skip system messages like "user joined channel"
                if msg.get("subtype"):
                    continue

                text = msg.get("text", "")
                author_id = msg.get("user")
                ts = msg.get("ts")
                
                # 2. If message has a thread, fetch the replies and append them
                if "thread_ts" in msg:
                    replies = self.client.conversations_replies(
                        channel=channel_id, 
                        ts=msg["thread_ts"]
                    )
                    for reply in replies.get("messages", [])[1:]: # Skip the first one (parent)
                        reply_author = self._get_real_name(reply.get("user"))
                        text += f"\n\n[Reply from {reply_author}]: {reply.get('text', '')}"

                # 3. Build Deterministic ID (prevents duplicates)
                doc_id = hashlib.sha256(f"{channel_id}_{ts}".encode()).hexdigest()
                
                # 4. Construct the Slack URL manually to save API calls
                # ts looks like "1713500000.123459", URLs remove the dot
                ts_url_format = ts.replace(".", "")
                slack_url = f"https://{self.workspace_domain}.slack.com/archives/{channel_id}/p{ts_url_format}"

                # 5. Package into Document
                doc = Document(
                    id=doc_id,
                    text=text,
                    metadata={
                        "author": self._get_real_name(author_id),
                        "slack_url": slack_url,
                        "channel_id": channel_id,
                        "timestamp": ts
                    }
                )
                documents.append(doc)

        except Exception as e:
            logger.error(f"Error loading Slack data: {e}")

        logger.info(f"Successfully loaded {len(documents)} conversational threads.")
        return documents