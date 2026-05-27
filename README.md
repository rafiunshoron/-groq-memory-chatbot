---
---
title: Groq Memory Chatbot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
app_file: app.py
pinned: false
---

# Groq Memory Chatbot

This is a multi-session AI chatbot built using **Groq API**, **Llama 3.1 8B Instant**, **Python**, and **Gradio**.

## Features

- Groq API integration
- Llama 3.1 8B Instant model
- Conversation memory
- Multiple chat sessions using conversation IDs
- Memory trimming to control context size
- Interactive Gradio web interface
- Secure API key handling using Hugging Face Secrets

## Required Secret

This Space requires one secret:

```text
GROQ_API_KEY