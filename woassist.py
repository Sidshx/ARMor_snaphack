import win32evtlog
import win32evtlogutil
import win32con
import datetime
import requests


def extract_windows_logs(log_type="System", max_entries=20):
    """
    Extracts real Windows Event Logs (System, Application, etc.).
    Filters for recent ERROR and WARNING level logs.
    """
    server = "localhost"  # local machine
    log = log_type
    hand = win32evtlog.OpenEventLog(server, log)

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand, flags, 0)

    logs = []
    for i, event in enumerate(events):
        if i >= max_entries:
            break
        event_time = event.TimeGenerated.Format()
        event_type = event.EventType
        level = {
            win32con.EVENTLOG_ERROR_TYPE: "ERROR",
            win32con.EVENTLOG_WARNING_TYPE: "WARNING",
            win32con.EVENTLOG_INFORMATION_TYPE: "INFO",
        }.get(event_type, "UNKNOWN")

        source = str(event.SourceName)
        message = win32evtlogutil.SafeFormatMessage(event, log)

        logs.append(
            {
                "timestamp": event_time,
                "level": level,
                "source": source,
                "message": message.strip(),
            }
        )

    return logs


def build_prompt(logs, user_question):
    log_text = "\n".join(
        f"[{log['timestamp']}] {log['level']} - {log['source']}: {log['message']}"
        for log in logs
    )
    prompt = f"""
        You are a Windows on ARM debug assistant. Analyze the following system logs and answer the user question.

        Logs:
        {log_text}

        User question: {user_question}
        """
    return prompt.strip()


def query_llm(prompt, model="mistral"):
    response = requests.post(
        url=f"http://localhost:11434/api/generate",  # localhost port that runs LLM agent
        headers={"Content-Type": "application/json"},
        json={"model": model, "prompt": prompt, "stream": False},
    )
    result = response.json()
    return result.get("response", "[No response from model]")


def main():
    print("Reading logs from Windows Event Viewer...")
    logs = extract_windows_logs("System", max_entries=15)

    if not logs:
        print("No logs found.")
        return

    user_question = input("Ask a question about the logs: ")
    prompt = build_prompt(logs, user_question)

    print("\n[Sending prompt to LLM...]\n")
    answer = query_llm(prompt)

    print("\nLLM Response:\n")
    print(answer)


if __name__ == "__main__":
    main()
