import os
import uuid
from typing import Dict, List

import gradio as gr
from groq import Groq


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Please add it in Hugging Face Space Secrets."
    )


client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"
MAX_HISTORY_MESSAGES = 10


class Conversation:
    def __init__(self):
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful, friendly, and clear AI assistant. "
                    "Answer users naturally and accurately."
                )
            }
        ]


conversations: Dict[str, Conversation] = {}


def get_or_create_conversation(conversation_id: str) -> Conversation:
    if conversation_id not in conversations:
        conversations[conversation_id] = Conversation()

    return conversations[conversation_id]


def trim_conversation(conversation: Conversation):
    system_message = conversation.messages[0]
    recent_messages = conversation.messages[1:]

    if len(recent_messages) > MAX_HISTORY_MESSAGES:
        recent_messages = recent_messages[-MAX_HISTORY_MESSAGES:]

    conversation.messages = [system_message] + recent_messages


def ask_groq_conversation(user_message: str, conversation_id: str) -> str:
    conversation = get_or_create_conversation(conversation_id)

    conversation.messages.append({
        "role": "user",
        "content": user_message
    })

    trim_conversation(conversation)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=conversation.messages,
        temperature=0.3,
        max_completion_tokens=500,
        top_p=1,
        stream=False
    )

    assistant_response = completion.choices[0].message.content

    conversation.messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    trim_conversation(conversation)

    return assistant_response


def chat(user_message, history, conversation_id):
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    if history is None:
        history = []

    if not user_message or not user_message.strip():
        return history, conversation_id, ""

    try:
        bot_response = ask_groq_conversation(
            user_message=user_message,
            conversation_id=conversation_id
        )

    except Exception as e:
        bot_response = f"Error: {str(e)}"

    history.append({
        "role": "user",
        "content": user_message
    })

    history.append({
        "role": "assistant",
        "content": bot_response
    })

    return history, conversation_id, ""


def reset_chat():
    conversation_id = str(uuid.uuid4())
    return [], conversation_id, ""


with gr.Blocks(title="Groq Memory Chatbot") as demo:
    gr.Markdown("# Groq Memory Chatbot")
    gr.Markdown(
        "A multi-session AI chatbot powered by Groq API and Llama 3.1 8B Instant. "
        "It supports conversation memory and memory trimming."
    )

    conversation_id_state = gr.State(str(uuid.uuid4()))

    chatbot = gr.Chatbot(
        label="Chat",
        height=450
    )

    user_input = gr.Textbox(
        label="Your message",
        placeholder="Type your message here...",
        lines=3
    )

    with gr.Row():
        send_button = gr.Button("Send", variant="primary")
        reset_button = gr.Button("Reset Chat")

    send_button.click(
        fn=chat,
        inputs=[user_input, chatbot, conversation_id_state],
        outputs=[chatbot, conversation_id_state, user_input]
    )

    user_input.submit(
        fn=chat,
        inputs=[user_input, chatbot, conversation_id_state],
        outputs=[chatbot, conversation_id_state, user_input]
    )

    reset_button.click(
        fn=reset_chat,
        inputs=[],
        outputs=[chatbot, conversation_id_state, user_input]
    )


if __name__ == "__main__":
    demo.launch()