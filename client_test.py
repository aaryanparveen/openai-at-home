
import sys
import signal

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.theme import Theme

BASE_URL = "http://localhost:13373/v1"
API_KEY = "hiiiiiiiiiii"
MODEL = "openai/gpt-5.3"

theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "error": "bold red",
    "user": "bold green",
    "assistant": "bold cyan",
    "system": "dim white",
})
console = Console(theme=theme)

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
conversation: list[dict] = []

def print_banner():
    console.print()
    console.print(Panel.fit(
        "[bold cyan] OpenAI At Home[/]\n"
        f"[dim]Model: {MODEL}[/]\n"
        f"[dim]Server: {BASE_URL}[/]\n"
        "[dim]Type [bold]/help[/bold] for commands[/]",
        border_style="cyan",
    ))
    console.print()

def print_help():
    console.print(Panel(
        "[bold]/help[/]     - Show this menu\n"
        "[bold]/clear[/]    - Clear conversation history\n"
        "[bold]/history[/]  - Show conversation history\n"
        "[bold]/system[/]   - Set system prompt\n"
        "[bold]/model[/]    - Show current model\n"
        "[bold]/models[/]   - List available models\n"
        "[bold]/exit[/]     - Quit",
        title="[bold]Commands[/]",
        border_style="dim",
    ))

def stream_response():
    full_reply = []

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            stream=True,
        )

        console.print("[assistant]Assistant:[/] ", end="")

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                console.print(delta.content, end="", highlight=False)
                full_reply.append(delta.content)

        console.print()

    except KeyboardInterrupt:
        console.print("\n[warning] Stream interrupted[/]")
    except Exception as e:
        console.print(f"\n[error] Error: {e}[/]")
        return None

    reply_text = "".join(full_reply)
    return reply_text

def non_stream_response():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            stream=False,
        )
        reply = response.choices[0].message.content
        console.print(f"[assistant]Assistant:[/] {reply}")
        return reply
    except Exception as e:
        console.print(f"[error] Error: {e}[/]")
        return None

def main():
    global conversation, MODEL

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    print_banner()

    while True:
        try:
            console.print("[user]You:[/] ", end="")
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[info]Goodbye! [/]")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input.lower().split()[0]

            if cmd == "/exit" or cmd == "/quit" or cmd == "/q":
                console.print("[info]Goodbye! [/]")
                break

            elif cmd == "/help":
                print_help()
                continue

            elif cmd == "/clear":
                conversation = []
                console.print("[info] Conversation cleared[/]")
                continue

            elif cmd == "/history":
                if not conversation:
                    console.print("[info]No messages yet.[/]")
                else:
                    for i, msg in enumerate(conversation):
                        role_style = "user" if msg["role"] == "user" else "assistant" if msg["role"] == "assistant" else "system"
                        console.print(f"  [dim]{i+1}.[/] [{role_style}]{msg['role']}:[/] {msg['content'][:80]}{'...' if len(msg['content']) > 80 else ''}")
                continue

            elif cmd == "/system":
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print("[info]Usage: /system <your system prompt>[/]")
                else:
                    system_msg = parts[1]
                    if conversation and conversation[0]["role"] == "system":
                        conversation[0] = {"role": "system", "content": system_msg}
                    else:
                        conversation.insert(0, {"role": "system", "content": system_msg})
                    console.print(f"[info] System prompt set: {system_msg[:60]}...[/]")
                continue

            elif cmd == "/model":
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print(f"[info]Current model: {MODEL}[/]")
                else:
                    new_model = parts[1]
                    MODEL = new_model
                    console.print(f"[info] Switched active model to: {MODEL}[/]")
                continue

            elif cmd == "/models":
                try:
                    models = client.models.list()
                    for m in models.data:
                        marker = " <- current" if m.id == MODEL else ""
                        console.print(f"  [dim] [/] {m.id}{marker}")
                except Exception as e:
                    console.print(f"[error] {e}[/]")
                continue

            else:
                console.print(f"[warning]Unknown command: {cmd}. Type /help[/]")
                continue

        conversation.append({"role": "user", "content": user_input})

        reply = stream_response()

        if reply:
            conversation.append({"role": "assistant", "content": reply})

        console.print()


if __name__ == "__main__":
    main()
