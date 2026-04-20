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
            "You are the organizational 'Knowledge Oracle' Slack bot. Your job is to unblock team members "
            "by answering their questions based ONLY on the provided context.\n"
            "CRITICAL INSTRUCTION: You MUST include a reference to the original author and the Slack URL "
            "at the end of your response so the user knows exactly who to contact for more details.\n"
            "If the answer is not in the context, politely state that you do not have that knowledge."
        )
        
        final_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nUser Query: {query}"
        
        response = self.llm.generate(
            prompt=final_prompt, 
            context=context, 
            chat_history=chat_history
        )
        
        logger.debug("Generation completed (response_chars=%d)", len(response))
        return response