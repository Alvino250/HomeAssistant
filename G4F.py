import requests

def g4fReply(user_input):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "deepseek-coder:6.7b-instruct",
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        content = response.json()['message']['content']
        return content.strip()
    else:
        return f"Error: {response.status_code} - {response.text}"


