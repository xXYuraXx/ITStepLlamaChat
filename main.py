import requests
import json
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import threading
from dotenv import load_dotenv
import os

def create_payload_from_prompt(prompt):
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": True,
    }
    return payload

def print_log(*args, **kwargs):
    print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]", *args, **kwargs)

def get_ai_response(user_text):
    """
    Sends user text to the Groq server and returns the AI response.
    """

    # Request headers
    # Authorization proves we have access using the API key
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Request body data
    data = {
        # Using the Llama 3 model
        "model": "openai/gpt-oss-120b",

        "messages": [
            # System message: defines assistant behavior
            {
                "role": "system",
                "content": "You are a helpful assistant that answers in Ukrainian. Be concise."
            },

            # User message
            {
                "role": "user",
                "content": user_text
            }
        ],

        # Creativity level
        # 0 = more strict/deterministic
        # 1 = more creative/random
        "temperature": 0.7
    }

    try:
        # SEND REQUEST (POST)
        response = requests.post(GROQ_URL, headers=headers, json=data)

        # Check if request was successful
        # Status code 200 means OK
        if response.status_code == 200:
            result = response.json()

            # --- PARSE RESPONSE ---
            # Response structure:
            # result -> choices -> first item [0] -> message -> content
            bot_text = result['choices'][0]['message']['content']

            return bot_text

        else:
            return f"Server error: {response.status_code}. Check your API key!"

    except Exception as e:
        return f"No internet connection or code error: {e}"

def post_request(prompt):
    try:
        text_response = get_ai_response(prompt)
        text_agent_response.config(state="normal")
        text_agent_response.insert(END, text_response)
        text_agent_response.see(END)
        text_agent_response.config(state="disabled")
    except Exception as e:
        print_log(f"\n[Error parsing line]: {prompt}\nError: {e}")
    finally:
        button_send.config(state="normal")
                    
def send_pressed():
    prompt = entry_user_input.get().strip()
    if not prompt:
        print_log("No text in entry")
        return
    else:
        print_log("Start sending...")
        entry_user_input.delete(0, END)
        text_agent_response.config(state="normal")
        text_agent_response.delete("1.0", END)
        text_agent_response.config(state="disabled")
        button_send.config(state="disabled")
        
    
    thread = threading.Thread(target=post_request, args=(prompt,), daemon=True)
    thread.start()
    
                    
                    
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_KEY")
GROQ_URL = r"https://api.groq.com/openai/v1/chat/completions"

root = Tk()

root.title("Chat llama")
root.geometry("800x500")

frame_bottom = Frame(root)
frame_bottom.pack(side="bottom", fill="x", padx=10, pady=10)

button_send = Button(frame_bottom, text="Send")
button_send.pack(side="right", padx=(10, 0))

entry_user_input = Entry(frame_bottom)
entry_user_input.pack(side="left", fill="x", expand=True)




frame_top = Frame(root)
frame_top.pack(side="top", fill="both", expand=True, padx=10, pady=10)

scrollbar = Scrollbar(frame_top)
scrollbar.pack(side="right", fill="y")



text_agent_response = Text(frame_top,
                           wrap="word",
                           yscrollcommand=scrollbar.set)
text_agent_response.insert("1.0", "Please enter your first message and click send.")
text_agent_response.config(state="disabled")
text_agent_response.pack(side="left", fill="both", expand=True)
scrollbar.config(command=text_agent_response.yview)

button_send.config(command=send_pressed)

mainloop()