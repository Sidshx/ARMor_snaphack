import win32evtlog
import win32evtlogutil
import win32con
import datetime
import requests
import sys
from typing import List, Dict, Optional

def extract_windows_logs(log_type: str = "System", max_entries: int = 20) -> List[Dict]:
    """
    Extracts Windows Event Logs (System, Application, etc.).
    Filters for recent ERROR, WARNING, and INFO level logs.
    """
    valid_log_types = ["System", "Application", "Security"]
    if log_type not in valid_log_types:
        raise ValueError(f"Invalid log type. Must be one of {valid_log_types}")

    try:
        server = "localhost"  # local machine
        hand = win32evtlog.OpenEventLog(server, log_type)
    except Exception as e:
        print(f"Error opening event log: {e}")
        return []

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    logs = []
    allowed_levels = {
        win32con.EVENTLOG_ERROR_TYPE: "ERROR",
        win32con.EVENTLOG_WARNING_TYPE: "WARNING",
        win32con.EVENTLOG_INFORMATION_TYPE: "INFO"
    }

    try:
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        for i, event in enumerate(events):
            if i >= max_entries:
                break
            event_type = event.EventType
            if event_type not in allowed_levels:
                continue

            try:
                event_time = datetime.datetime.strptime(
                    event.TimeGenerated.Format(), '%a %b %d %H:%M:%S %Y'
                )
                message = win32evtlogutil.SafeFormatMessage(event, log_type) or "No message available"
                logs.append({
                    "timestamp": event_time.isoformat(),
                    "level": allowed_levels[event_type],
                    "source": str(event.SourceName),
                    "message": message.strip()
                })
            except Exception as e:
                print(f"Error processing event {i}: {e}")
                continue
    except Exception as e:
        print(f"Error reading event log: {e}")
    finally:
        win32evtlog.CloseEventLog(hand)

    return logs

def build_prompt(logs: List[Dict], user_question: str) -> str:
    """
    Builds a prompt for the LLM using the provided logs and user question.
    """
    if not user_question.strip():
        raise ValueError("User question cannot be empty")

    log_text = "\n".join(
        f"[{log['timestamp']}] {log['level']} - {log['source']}: {log['message']}"
        for log in logs
    )
    prompt = f"""
You are a Windows on ARM debug assistant. Analyze the following system logs and provide a detailed answer to the user question. Include potential causes and solutions where applicable.

Logs:
{log_text}

User question: {user_question}
"""
    return prompt.strip()

def query_llm(prompt: str, model: str = "mistral", llm_url: str = "http://localhost:11434/api/generate") -> str:
    """
    Queries the local LLM with the provided prompt.
    """
    try:
        response = requests.post(
            url=llm_url,
            headers={"Content-Type": "application/json"},
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "[No response from model]")
    except requests.RequestException as e:
        return f"Error querying LLM: {e}"

def main():
    try:
        print("Reading logs from Windows Event Viewer...")
        logs = extract_windows_logs(log_type="System", max_entries=15)

        if not logs:
            print("No relevant logs found.")
            return

        user_question = input("Ask a question about the logs: ").strip()
        if not user_question:
            print("Error: Question cannot be empty.")
            return

        print("\n[Sending prompt to LLM...]\n")
        prompt = build_prompt(logs, user_question)
        answer = query_llm(prompt)

        print("\nLLM Response:\n")
        print(answer)
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()