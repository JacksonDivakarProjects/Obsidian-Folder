Good question. Here’s how to install **Ollama** and set up models on Linux, step by step. (I’ll also include how to add custom/gguf models.)

---

## 1. Install Ollama on Linux

1. Run the official install script:
    
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
    
    ([ollama.readthedocs.io](https://ollama.readthedocs.io/en/quickstart/?utm_source=chatgpt.com "Quickstart - Ollama English Documentation"))
    
2. (Optional) **Manual install**:
    
    - Download the binary:
        
        ```bash
        curl -fsSL https://ollama.com/download/ollama-linux-amd64.tgz | sudo tar zx -C /usr
        ```
        
        ([docs.ollama.com](https://docs.ollama.com/linux?utm_source=chatgpt.com "Linux - Ollama"))
        
    - If you have an **AMD GPU** (with ROCm), download the ROCm build:
        
        ```bash
        curl -fsSL https://ollama.com/download/ollama-linux-amd64‑rocm.tgz | sudo tar zx -C /usr
        ```
        
        ([docs.ollama.com](https://docs.ollama.com/linux?utm_source=chatgpt.com "Linux - Ollama"))
        
    - Then start the service:
        
        ```bash
        ollama serve
        ```
        
        ([docs.ollama.com](https://docs.ollama.com/linux?utm_source=chatgpt.com "Linux - Ollama"))
        
3. To check version / make sure installation worked:
    
    ```bash
    ollama -v
    ```
    
    ([docs.ollama.com](https://docs.ollama.com/linux?utm_source=chatgpt.com "Linux - Ollama"))
    
4. (Service setup) If you installed via script, Ollama may run as a `systemd` service. You can enable/start it:
    
    ```bash
    systemctl --user start ollama  
    systemctl --user enable ollama  
    ```
    
    ([ibm.com](https://www.ibm.com/granite/docs/run/granite-with-ollama-linux?utm_source=chatgpt.com "Ollama on Linux - IBM Granite"))
    

---

## 2. Download / Install Models (“Install Olaama models”)

Once Ollama is installed:

1. **Pull a model from Ollama’s library**:
    
    ```bash
    ollama pull <model_name>
    ```
    
    Example:
    
    ```bash
    ollama pull llama3.2
    ```
    
    ([Medium](https://medium.com/%40nishith.explorer/run-llama-2-3-locally-a-step-by-step-guide-using-ollama-extended-guide-132527e28cdd?utm_source=chatgpt.com "Run LLaMA 2 & 3 Locally: A Step-by-Step Guide Using Ollama (Extended Guide) | by Nishith Singh | Medium"))
    
2. **List downloaded models**:
    
    ```bash
    ollama list
    ```
    
    ([(Indico)](https://events.grnet.gr/event/147/contributions/606/attachments/422/729/4.%20Using%20LLMs%20on%20%E2%80%9CAristotelis%E2%80%9D%20HPC%20infrastructure%20-%20George%20Vlahavas%2C%20AUTH.pdf?utm_source=chatgpt.com "Using LLMs on “Aristotelis”"))
    
3. **Run a model**:
    
    ```bash
    ollama run <model_name>
    ```
    
    Example:
    
    ```bash
    ollama run llama3.2
    ```
    
    ([ollama.readthedocs.io](https://ollama.readthedocs.io/en/quickstart/?utm_source=chatgpt.com "Quickstart - Ollama English Documentation"))
    

---

## 3. Use Custom Models (GGUF, safetensors, etc.)

If you have a custom model (e.g. from Hugging Face in `.gguf` format):

1. **Download the model file** (let’s say `.gguf`) to your machine. For example:
    
    ```bash
    wget https://huggingface.co/…/model.gguf
    ```
    
    ([GitHub](https://github.com/khmowais/offline_ollama_guide?utm_source=chatgpt.com "GitHub - khmowais/offline_ollama_guide: Running OLLAMA on an Offline Linux System, Fast Guide + Full Walkthrough"))
    
2. **Create a `Modelfile`**:  
    This is a simple text file (no extension) that tells Ollama what to load. Example content:
    
    ```
    FROM ./model.gguf
    ```
    
    ([GitHub](https://github.com/loong64/ollama?utm_source=chatgpt.com "GitHub - loong64/ollama: Get up and running with Llama 3.3, DeepSeek-R1, Phi-4, Gemma 2, and other large language models."))
    
3. **Register the model with Ollama**:
    
    ```bash
    ollama create mymodel -f ./Modelfile
    ```
    
    (Here, `mymodel` is the name you give.) ([GitHub](https://github.com/loong64/ollama?utm_source=chatgpt.com "GitHub - loong64/ollama: Get up and running with Llama 3.3, DeepSeek-R1, Phi-4, Gemma 2, and other large language models."))
    
4. **Run your custom model**:
    
    ```bash
    ollama run mymodel
    ```
    
    ([GitHub](https://github.com/loong64/ollama?utm_source=chatgpt.com "GitHub - loong64/ollama: Get up and running with Llama 3.3, DeepSeek-R1, Phi-4, Gemma 2, and other large language models."))
    

---

## 4. (Optional) Change Where Models Are Stored

- By default, Ollama stores models under `/usr/share/ollama/.ollama/models`. ([Reddit](https://www.reddit.com/r/ollama/comments/1bjuk84?utm_source=chatgpt.com "Moving models from Windows to Linux"))
    
- If you want to move them (e.g., to another SSD), many use a **symlink**:
    
    ```bash
    sudo mv /usr/share/ollama/.ollama/models /path/to/your/bigger/drive/models  
    sudo ln -s /path/to/your/bigger/drive/models /usr/share/ollama/.ollama/models  
    ```
    
    ([Reddit](https://www.reddit.com//r/ollama/comments/1c4zg15?utm_source=chatgpt.com "Does anyone know how to change where your models are saved on linux?"))
    

---

## 5. Verify and Use

After installation and pulling a model:

- Run `ollama list` to check models.
    
- Run `ollama run <model>` to start interacting.
    
- To stop a model, you can usually just exit the REPL or use commands provided by Ollama.
    

---

### ⚠️ Notes / Tips

- Make sure your machine has **enough RAM**: big models (7B, 13B, etc.) need a lot. ([ollama.readthedocs.io](https://ollama.readthedocs.io/en/quickstart/?utm_source=chatgpt.com "Quickstart - Ollama English Documentation"))
    
- If you're using a GPU (especially AMD), install the ROCm version of Ollama for better performance. ([docs.ollama.com](https://docs.ollama.com/linux?utm_source=chatgpt.com "Linux - Ollama"))
    
- When working with custom models, double-check that the `.gguf` file is compatible / correctly downloaded.
    

---

If you like, I can check **which Ollama models are best for low-RAM Linux machines** (or recommend based on your hardware). Do you want me to do that?

## 🔗 Related Notes
- [[Laptop Level Notes/Swap Memory/Swapping Memory|Swapping Memory]]
- [[Laptop Level Notes/Fedora/Fedora Basic Commands|Fedora Linux Cheat Sheet (Essential)]]
- [[Laptop Level Notes/Set Java SDK/Set Java SDK|Set Java SDK]]
