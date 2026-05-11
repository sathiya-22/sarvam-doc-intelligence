"""Sarvam Document Intelligence — extract, detect, translate Indian documents."""
import os, json, base64, sys
from pathlib import Path
from dotenv import load_dotenv
from sarvamai import SarvamAI
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()
client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

def extract(file_path):
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = Path(file_path).suffix.lstrip(".").lower()
    media = "application/pdf" if ext == "pdf" else f"image/{ext}"
    return client.documents.parse(document={"type":"base64","media_type":media,"data":data}).text

def detect_lang(text):
    r = client.text.identify_language(input=text[:300])
    return r.language_code

def translate(text, src):
    if src == "en-IN": return text
    return client.text.translate(input=text, source_language_code=src, target_language_code="en-IN").translated_text

def process(file_path, output="output.json"):
    raw = extract(file_path)
    lang = detect_lang(raw)
    translated = translate(raw, lang)
    result = {"source": file_path, "language": lang, "original": raw, "english": translated}
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    console.print(Panel(f"Language: {lang}\n\n{translated[:400]}", title="Result"))
    console.print(f"[green]Saved to {output}[/green]")
    return result

if __name__ == "__main__":
    process(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output.json")
