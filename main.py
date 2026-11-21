import requests
import json
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import threading

def create_payload_from_prompt(prompt):
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": True,
    }
    return payload

def print_log(*args, **kwargs):
    print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]", *args, **kwargs)


def post_request(prompt):
    try:
        with requests.post(
            "http://localhost:11434/api/generate", json=create_payload_from_prompt(prompt), stream=True
        ) as response:
                
            print_log("Status code:", response.status_code)
            
            if response.status_code // 100 != 2:
                messagebox.showerror("Error", "Llama response error!")
                print_log("Error occured")

            for line in response.iter_lines():
                if line:
                    content = line.decode("utf-8").removeprefix("data: ")
                    try:
                        chunk = json.loads(content)
                        new_text = chunk.get("response", "")
                        text_agent_response.config(state="normal")
                        text_agent_response.insert(END, new_text)
                        text_agent_response.see(END)
                        text_agent_response.config(state="disabled")
                    except Exception as e:
                        print_log(f"\n[Error parsing line]: {content}")
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