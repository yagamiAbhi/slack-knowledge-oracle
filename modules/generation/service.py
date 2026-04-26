import logging
from typing import List, Dict
from interfaces.llm import BaseLLM
from core.entities import Document

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def answer_query(self, query: str, context: List[Document], chat_history: List[Dict]) -> str:
        logger.debug(
            "Generation started (query_chars=%d, context_docs=%d, history_messages=%d)",
            len(query),
            len(context),
            len(chat_history),
        )

        # 1. Format context to INCLUDE metadata so the LLM can cite it
        context_strings = []
        for doc in context:
            author = doc.metadata.get("author", "Unknown Author")
            url = doc.metadata.get("slack_url", "No URL available")
            text = doc.text
            context_strings.append(f"[Source: {url} | Author: {author}]\n{text}")
            
        context_text = "\n\n---\n\n".join(context_strings)

        # 2. Update the System Prompt to enforce the Oracle persona
        system_prompt = (
            "You are the 'Knowledge Oracle', a friendly Amex Slack assistant. Your job is to help team members "
            "by answering their questions. \n"
            "1. IDENTITY: If the user asks 'who are you', respond EXACTLY with: 'I am your Amex Slack assistant, what should I find for you?'\n"
            "2. GENERAL: For general greetings or questions about what you do, respond warmly and explain that you help search through Slack history to unblock engineers.\n"
            "3. TECHNICAL: For technical questions, use the provided context. If the answer is in the context, you MUST include a reference to the author and the Slack URL.\n"
            "4. DATE: Today's date is Monday, April 27, 2026. Use this if asked about the time or date.\n"
            "5. UNKNOWN: If the answer is not in the context and it is not a general greeting/identity question, politely state you do not have that knowledge."
        )
        
        final_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nUser Query: {query}"
        
        response = self.llm.generate(
            prompt=final_prompt, 
            context=context, 
            chat_history=chat_history
        )
        
        logger.debug("Generation completed (response_chars=%d)", len(response))
        return response