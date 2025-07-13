import win32evtlog
import win32evtlogutil
import win32con
import datetime
import sys
import argparse
from typing import List, Dict
from openai import OpenAI

# --- CLI parsing for fresh context ---
parser = argparse.ArgumentParser()
parser.add_argument(
    "--new-context",
    action="store_true",
    help="Start with a fresh in-memory history"
)
args = parser.parse_args()

# --- Extract recent system logs ---
def extract_windows_logs(log_type: str = "System", max_entries: int = 20) -> List[str]:
    valid = ["System", "Application", "Security"]
    if log_type not in valid:
        raise ValueError(f"Invalid log type. Must be one of {valid}")
    try:
        hand = win32evtlog.OpenEventLog("localhost", log_type)
    except Exception as e:
        print(f"Error opening event log: {e}")
        return []
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    levels = {
        win32con.EVENTLOG_ERROR_TYPE: "ERROR",
        win32con.EVENTLOG_WARNING_TYPE: "WARNING",
        win32con.EVENTLOG_INFORMATION_TYPE: "INFO"
    }
    logs = []
    try:
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        for i, ev in enumerate(events):
            if i >= max_entries:
                break
            lvl = ev.EventType
            if lvl not in levels:
                continue
            ts = datetime.datetime.strptime(
                ev.TimeGenerated.Format(), '%a %b %d %H:%M:%S %Y'
            ).isoformat()
            msg = win32evtlogutil.SafeFormatMessage(ev, log_type) or "No message available"
            logs.append(f"[{ts}] {levels[lvl]} - {ev.SourceName}: {msg.strip()}")
    except Exception as e:
        print(f"Error reading event log: {e}")
    finally:
        win32evtlog.CloseEventLog(hand)
    return logs

logs = extract_windows_logs("System", max_entries=15)
log_block = "\n".join(logs) if logs else ""

# --- In-memory chat buffer ---
messages: List[Dict] = []
if args.new_context:
    messages.clear()
    print("Context cleared — starting fresh.")

# Minimal system prompt
messages = []
if args.new_context:
    messages.clear()

messages.append({
    "role": "system",
    "content": """\
You are a Windows-on-ARM troubleshooting assistant. Always respond in English.
Use the system logs provided and your knowledge of Windows internals to:
  1. Diagnose the root cause of the user’s problem.
  2. Propose clear, step-by-step solutions.
Only reference log entries that are directly relevant to the issue."""
})


# Instantiate local OpenAI client
client = OpenAI(
    base_url="http://localhost:5272/v1",
    api_key="unused"
)

def query_llm(user_question: str) -> str:
    # Build the user message with logs
    user_content = f"Ignore chat history if not relevant. New User question: {user_question}\n\n"
    if log_block:
        user_content += f"System Logs:\n{log_block}\n"
    else:
        user_content += "No system logs available.\n"

    messages.append({"role": "user", "content": user_content})
    resp = client.chat.completions.create(
        model="qnn-deepseek-r1-distill-qwen-1.5b",
        messages=messages,
        max_tokens=2048,
        temperature=0.6,
        top_p=0.9,
    )
    answer = resp.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer

def main():
    print(f"[{'fresh' if args.new_context else 'continued'} context]")
    question = input("How can I help with your system?\n").strip()
    if not question:
        print("Error: Question cannot be empty.")
        return

    print("\n[Thinking...]\n")
    print(query_llm(question))

if __name__ == "__main__":
    main()
