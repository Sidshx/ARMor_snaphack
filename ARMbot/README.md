## ��ARMbot: Windows-on-ARM Troubleshooting Assistant

### 🔍 Overview

**ARMbot** is a local assistant agent designed to troubleshoot issues on Windows-on-ARM systems, specifically targeting devices like the Snapdragon X Elite laptop. It leverages system logs and a locally hosted large language model (LLM) to diagnose problems and provide clear, step-by-step solutions. The project uses the **VSCode AI Toolkit** for LLM setup, but is compatible with other models that support a localhost server.

### 🎯 Key Features

* ✅ **System Log Extraction**: Retrieves recent Windows event logs (System, Application, Security) using `pywin32`.
* ✅ **Local LLM Integration**: Queries a locally hosted LLM (e.g., via VSCode AI Toolkit) for intelligent troubleshooting.
* ✅ **Context Management**: Supports fresh or continued chat contexts via CLI arguments.
* ✅ **Windows-on-ARM Focus**: Tailored for diagnosing issues on ARM-based Windows devices like Snapdragon X Elite laptops.
* ✅ **Privacy-First**: Runs entirely locally, ensuring no data leaves the device.

---

### 🧠 How It Works

1. **Log Extraction**  
   The script uses `pywin32` to extract recent Windows event logs (e.g., System logs) with details like timestamp, event type (ERROR, WARNING, INFO), and message.

2. **CLI Parsing**  
   The `--new-context` flag allows users to start with a fresh in-memory chat history or continue an existing session.

3. **LLM Query**  
   The script sends the user’s question along with relevant system logs to a locally hosted LLM (e.g., `qnn-deepseek-r1-distill-qwen-1.5b`) via the OpenAI-compatible API. The LLM analyzes logs and provides a diagnosis and solution.

4. **Response Delivery**  
   The assistant returns a clear, actionable response in English, focusing only on log entries relevant to the user’s issue.

---

### 💻 File Structure

```text
armbot.py     # Main script for log extraction and LLM querying
```

---

### 📦 Dependencies

Install via pip:

```bash
pip install pywin32 openai
```

Additionally, set up a local LLM server using the **VSCode AI Toolkit**. Follow the setup tutorial here: [VSCode AI Toolkit Getting Started](https://learn.microsoft.com/en-us/windows/ai/toolkit/toolkit-getting-started?tabs=rest).

---

### ▶ How to Run

1. Ensure a local LLM server is running (e.g., via VSCode AI Toolkit) at `http://localhost:5272/v1`.
2. Install dependencies (see above).
3. Run the script:

```bash
python armbot.py
```

4. To start with a fresh context:

```bash
python armbot.py --new-context
```

5. Enter your troubleshooting question when prompted (e.g., "Why is my Snapdragon X Elite laptop crashing?").

The script will extract relevant system logs, query the LLM, and display a diagnosis with step-by-step solutions.

---

### 🧩 Key Code Components

* `pywin32` → Extracts Windows event logs using `win32evtlog` and `win32evtlogutil`.
* `openai` → Communicates with the local LLM server via an OpenAI-compatible API.
* `argparse` → Handles CLI arguments for context management.
* `datetime` → Processes log timestamps for readability.

---

### 📌 Notes

* The script defaults to extracting the 15 most recent System logs. Adjust `max_entries` in `extract_windows_logs` to change this.
* Only System, Application, and Security logs are supported. Modify `valid` in `extract_windows_logs` to extend support.
* The LLM model (`qnn-deepseek-r1-distill-qwen-1.5b`) is an example. Other models compatible with a localhost server can be used by updating the `model` parameter in `query_llm`.
* Ensure the local LLM server is running before executing the script, or it will fail to connect.

---