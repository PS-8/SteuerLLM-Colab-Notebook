# 1. Install zstd dependency, Ollama, and Python client
!apt-get update -qq && apt-get install -y zstd -qq
!curl -fsSL https://ollama.com/install.sh | sh
!pip install ollama huggingface_hub -q

import subprocess
import time
import ollama
from huggingface_hub import hf_hub_download

# 2. Start Ollama service in the background
print("Starting Ollama background process...")
subprocess.Popen(["ollama", "serve"])
time.sleep(5)  # Wait for service startup

# 3. Download GGUF file from Hugging Face
REPO_ID = "User954738/open_steuerllm-Q4_K_M-GGUF"
FILENAME = "open_steuerllm-q4_k_m.gguf"

print(f"Downloading {FILENAME} from Hugging Face...")
model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

# 4. Create Ollama Model Definition
modelfile_content = f"""
FROM {model_path}
SYSTEM "Du bist SteuerLLM, ein spezialisierter Assistent für deutsches Steuerrecht. Beantworte Fragen sachlich, präzise und fundiert auf Deutsch."
PARAMETER temperature 0.2
"""

with open("Modelfile", "w") as f:
    f.write(modelfile_content)

print("Importing model into Ollama...")
subprocess.run(["ollama", "create", "steuerllm", "-f", "./Modelfile"], check=True)

# 5. Interactive Chat Loop
print("\n" + "=" * 50)
print(" SteuerLLM Ready! Type 'exit' to quit.")
print("=" * 50 + "\n")

messages = []

while True:
    try:
        user_input = input("User: ")
    except (KeyboardInterrupt, EOFError):
        break

    if user_input.strip().lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    print("SteuerLLM: ", end="", flush=True)
    assistant_response = ""

    stream = ollama.chat(
        model="steuerllm",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        content = chunk["message"]["content"]
        print(content, end="", flush=True)
        assistant_response += content
    print("\n")

    messages.append({"role": "assistant", "content": assistant_response})