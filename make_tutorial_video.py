# ╔══════════════════════════════════════════════════════════════╗
# ║  Tutorial Video Generator                                    ║
# ║  Generates a 3-minute tutorial MP4 for the LinkedIn bot      ║
# ║                                                              ║
# ║  Requirements:                                               ║
# ║    brew install ffmpeg                                       ║
# ║    pip install Pillow                                        ║
# ║                                                              ║
# ║  Run: python3 make_tutorial_video.py                         ║
# ║  Output: tutorial.mp4                                        ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import subprocess
import sys
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont

VOICE   = "Samantha"
WIDTH   = 1920
HEIGHT  = 1080
FPS     = 30
OUTPUT  = "tutorial.mp4"

BG     = (10, 10, 10)
WHITE  = (255, 255, 255)
BODY   = (200, 200, 200)
DIM    = (120, 120, 120)
CODE   = (97, 218, 251)
ACCENT = (0, 212, 170)

SLIDES = [
    {
        "title": "LinkedIn Easy Apply Bot",
        "body": [
            ("Applies to jobs automatically", False),
            ("Custom AI cover letter per job", False),
            ("Runs 100% locally — free", False),
        ],
        "narration": "This bot applies to LinkedIn jobs automatically — writing a custom AI cover letter for each one, running locally on your machine for free. Let me show you how to set it up.",
    },
    {
        "title": "What You Need",
        "body": [
            ("Mac, Windows, or Linux", False),
            ("8 GB RAM minimum", False),
            ("5 GB free disk space", False),
            ("Internet connection", False),
        ],
        "narration": "Before we start, make sure you have a computer with at least 8 gigabytes of RAM and 5 gigabytes of free disk space. That's everything — we install the rest right now.",
    },
    {
        "title": "Step 1 — Install Python",
        "body": [
            ("python.org/downloads", True),
            ("Download Python 3.10 or newer", False),
            ("", False),
            ("Windows: check 'Add Python to PATH'", False),
            ("Then verify:  python3 --version", True),
        ],
        "narration": "Go to python dot org slash downloads and grab Python 3 point 10 or newer. Windows users — on the very first screen, check the box that says Add Python to PATH. After installing, open a terminal and type python3 --version to confirm it worked.",
    },
    {
        "title": "Step 2 — Download and Install",
        "body": [
            ("git clone https://github.com/coachpat123/linkedin-bot.git", True),
            ("cd linkedin-bot", True),
            ("python3 -m venv venv", True),
            ("source venv/bin/activate", True),
            ("pip install -r requirements.txt", True),
            ("playwright install chromium", True),
        ],
        "narration": "Clone the repo, step into the folder, create a virtual environment and activate it. Then install the dependencies and the browser Playwright uses. The browser download is about 400 megabytes so give it a minute.",
    },
    {
        "title": "Step 3 — Install Ollama",
        "body": [
            ("ollama.com  →  download and open", False),
            ("", False),
            ("ollama pull llama3.2", True),
            ("", False),
            ("Runs on your machine — no cloud, no API key", False),
        ],
        "narration": "Go to ollama dot com, download it for your OS, and open it. Then run ollama pull llama3 point 2 — this downloads a 2 gigabyte AI model that runs entirely on your computer. Nothing goes to the cloud, and it's completely free.",
    },
    {
        "title": "Step 4 — Fill In Your Info",
        "body": [
            ("Open linkedin_bot.py in VS Code", False),
            ("", False),
            ("PERSONAL_INFO  →  name, email, phone", True),
            ("BASE_RESUME    →  paste plain text resume", True),
            ("COVER_LETTER_EXAMPLES  →  your best openers", True),
        ],
        "narration": "Open linkedin bot dot py in any text editor. Fill in your personal info, paste your resume as plain text with real numbers, and add one or two of your strongest cover letter opening lines. The AI studies your examples and matches your voice — better examples mean better output.",
    },
    {
        "title": "Step 5 — Log In & Run",
        "body": [
            ("python3 linkedin_bot.py", True),
            ("", False),
            ("→ Browser opens  →  log in to LinkedIn", False),
            ("→ Press Enter when on your feed", False),
            ("→ Session saved — never log in again", False),
            ("", False),
            ("Paste a LinkedIn jobs search URL", False),
        ],
        "narration": "Run the bot once to log in. A browser opens on the LinkedIn login page — sign in normally, press Enter when you see your feed, and your session is saved. You'll never have to do that again. Then go to LinkedIn Jobs, search for your role, copy the URL, paste it when prompted, and watch it go.",
    },
    {
        "title": "Watch It Work",
        "body": [
            ("  → Account Executive @ Acme Corp", True),
            ("     ✅ Applied!", False),
            ("", False),
            ("  → Sales Manager @ TechCo", True),
            ("     ⏭  No Easy Apply button", False),
            ("", False),
            ("  📊  12 applied  |  8 skipped", False),
        ],
        "narration": "You'll see it hit each job in real time — applying where there's an Easy Apply button, skipping where there isn't. Every application gets its own folder with a tailored resume and cover letter saved inside.",
    },
    {
        "title": "Done",
        "body": [
            ("github.com/coachpat123/linkedin-bot", True),
            ("", False),
            ("Star the repo if it helped", False),
            ("Open an issue for bugs or broken selectors", False),
        ],
        "narration": "That's it. Link is in the description. Star the repo if this saved you time, and open a GitHub issue if LinkedIn updates their HTML and something breaks.",
    },
]


def get_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Courier New.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_slide(slide: dict) -> Image.Image:
    img  = Image.new("RGB", (WIDTH, HEIGHT), color=BG)
    draw = ImageDraw.Draw(img)

    title_font = get_font(68, bold=True)
    body_font  = get_font(44)
    code_font  = get_font(40, mono=True)
    foot_font  = get_font(26)

    draw.text((WIDTH // 2, 130), slide["title"], font=title_font, fill=WHITE, anchor="mm")
    draw.rectangle([160, 215, WIDTH - 160, 220], fill=ACCENT)

    y = 280
    for text, is_code in slide.get("body", []):
        if not text:
            y += 44
            continue
        font  = code_font if is_code else body_font
        color = CODE if is_code else BODY
        draw.text((180, y), text, font=font, fill=color)
        y += 62

    footer = "linkedin-bot  •  github.com/coachpat123/linkedin-bot"
    draw.text((WIDTH // 2, HEIGHT - 50), footer, font=foot_font, fill=DIM, anchor="mm")

    return img


def generate_voiceover(text: str, output_path: str):
    aiff = output_path.replace(".wav", ".aiff")
    subprocess.run(["say", "-v", VOICE, "-o", aiff, text], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-i", aiff, output_path], check=True, capture_output=True)
    os.remove(aiff)


def get_duration(path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def build_slide_video(img_path: str, audio_path: str, output_path: str, duration: float):
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output_path
    ], check=True, capture_output=True)


def check_deps():
    if sys.platform != "darwin":
        print("This script requires macOS (uses the 'say' command).")
        sys.exit(1)
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found. Install with: brew install ffmpeg")
        sys.exit(1)


def main():
    check_deps()

    workdir     = tempfile.mkdtemp(prefix="tutorial_")
    slide_videos = []

    print(f"Building tutorial video ({len(SLIDES)} slides)...\n")

    for i, slide in enumerate(SLIDES):
        print(f"  [{i+1}/{len(SLIDES)}] {slide['title']}")

        img_path   = os.path.join(workdir, f"slide_{i:02d}.png")
        audio_path = os.path.join(workdir, f"audio_{i:02d}.wav")
        video_path = os.path.join(workdir, f"clip_{i:02d}.mp4")

        render_slide(slide).save(img_path)
        generate_voiceover(slide["narration"], audio_path)
        duration = get_duration(audio_path) + 0.8
        build_slide_video(img_path, audio_path, video_path, duration)
        slide_videos.append(video_path)

    print(f"\nConcatenating...")

    concat_list = os.path.join(workdir, "concat.txt")
    with open(concat_list, "w") as f:
        for v in slide_videos:
            f.write(f"file '{v}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        OUTPUT
    ], check=True, capture_output=True)

    shutil.rmtree(workdir)

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n✅ Done — {OUTPUT} ({size_mb:.1f} MB)")
    print(f"   Open with: open {OUTPUT}")


if __name__ == "__main__":
    main()
