"""Content for the games hub and the five game pages. Edit here, then run build.py."""
import html
from guides_auto import faq

def e(s): return html.escape(str(s), quote=True)

COMMON = [("Do I need an account or to install anything?", "No. The game runs in your browser, needs no sign-up and keeps your best scores on your own device."),
          ("Does it work on my phone?", "Yes. It is built for touch screens as well as laptops, and it fits your screen.")]

GAMES = [
 dict(slug="command-sprint", name="Command Sprint", icon="\u2328\uFE0F", genre=["Typing", "Educational"],
  blurb="Type real Linux commands against the clock and earn a rank.",
  title="Command Sprint: Linux Typing Game", desc="Command Sprint is a quick Linux typing game. Type real terminal commands against the clock, pick a level and earn a rank from Rookie to Root Legend.",
  intro="Command Sprint is a typing game built around real Linux commands. A command appears, you type it exactly, and the next one loads straight away. Pick Easy, Normal or Hard, race the timer and finish with a words-per-minute score, an accuracy figure and a rank.",
  how=["Choose a level, then press Start.", "Type the command shown. The box turns blue while you are right and olive when you slip.", "The next command loads on its own when you finish one correctly.", "When the timer ends you see your commands, speed, accuracy and rank."],
  tips=["Do not rush. Mistakes cost accuracy, and fixing them costs time.", "Learn the shape of common commands such as ls, cd, grep and chmod, and the rest follows.", "Hard mode adds pipes and flags that you will meet in real guides."],
  faq=[("Are these real Linux commands?", "Yes. Every command is something you can run in a terminal. Hard mode includes system and network commands."), ("Will playing teach me Linux?", "It builds familiarity with the syntax. For meaning and examples, read our Linux terminal basics guide.")],
  guides=[("guide-how-to-use-the-linux-terminal-basics.html", "Linux terminal basics"), ("guide-linux-ls-command.html", "The ls command explained"), ("guide-linux-grep-command.html", "The grep command explained")]),
 dict(slug="boot-memory", name="Boot Memory", icon="\U0001F9E0", genre=["Puzzle", "Memory"],
  blurb="Match Linux and boot terms in as few moves as you can.",
  title="Boot Memory: Linux Card Matching Game", desc="Boot Memory is a card matching game with Linux names and boot terms. Choose Easy, Normal or Hard and beat your best moves and time.",
  intro="Boot Memory is a classic pairs game with a Linux twist. The cards carry distribution and boot terms such as Ubuntu, Debian, GRUB and Ventoy. Flip two at a time, remember where each one sits and clear the board in as few moves as possible.",
  how=["Pick Easy (6 pairs), Normal (8 pairs) or Hard (10 pairs).", "Tap a card to flip it, then tap a second card.", "Matching cards stay face up. Mismatches flip back after a moment.", "Clear every pair to finish. Your moves and time are recorded against your best."],
  tips=["Work through the board in a set order so you remember what you have seen.", "Say each word out loud as you flip it.", "On Hard, count the cards left to avoid guessing."],
  faq=[("Which words appear on the cards?", "Names such as Ubuntu, Mint, Debian, Fedora, Arch and Zorin, plus terms such as GRUB, Ventoy, Kernel and Shell."), ("How is my score worked out?", "Fewer moves is better. Your best moves for each level are saved on your device.")],
  guides=[("guide-what-is-ubuntu.html", "What is Ubuntu?"), ("guide-what-is-ventoy.html", "What is Ventoy?"), ("guide-what-is-a-bootloader-grub.html", "What is a bootloader (GRUB)?")]),
 dict(slug="usb-catch", name="USB Catch", icon="\U0001F427", genre=["Arcade"],
  blurb="Steer the penguin to catch drives, dodge bugs and build combos.",
  title="USB Catch: Penguin Arcade Game", desc="USB Catch is a fast arcade game. Steer the penguin to catch falling USB drives, dodge bugs, grab shields and hearts, and build combo multipliers.",
  intro="USB Catch is a quick arcade game for a short break. USB drives, bugs, hearts and stars fall from the top of the screen. Move the penguin to catch the drives, avoid the bugs and chase a score that gets harder to beat as the speed builds.",
  how=["Press Start. Drag or tap on a phone, or use the arrow keys or A and D on a laptop.", "Catch drives to score. Every five in a row raises your multiplier, up to times five.", "Avoid bugs. Each one costs a life and resets your combo.", "Grab a heart for an extra life and a star for a six-second shield."],
  tips=["Stay near the middle so you can reach both sides.", "Keep your combo alive. A times-five multiplier is where big scores come from.", "Save the shield for when the screen gets busy."],
  faq=[("What do the stars and hearts do?", "A heart gives you one extra life, up to five. A star gives a six-second shield that blocks bugs."), ("Does the game get harder?", "Yes. Items fall faster and more often as your score climbs.")],
  guides=[("guide-what-is-a-bootable-usb-drive.html", "What is a bootable USB drive?"), ("guide-how-to-create-a-bootable-usb-drive.html", "How to create a bootable USB drive"), ("guide-how-to-pick-the-right-usb-drive-size.html", "How to pick the right USB drive size")]),
 dict(slug="linux-quiz", name="Linux Quiz", icon="\u2753", genre=["Quiz", "Educational"],
  blurb="Ten quick questions on Linux and bootable USB drives.",
  title="Linux Quiz: Test Your Linux Knowledge", desc="Take the Linux Quiz: ten random questions on commands, distributions, boot settings and USB drives, with a short explanation after every answer.",
  intro="The Linux Quiz asks ten random questions drawn from a bank of two dozen, covering commands, distributions, file systems and booting from USB. After each answer you see the correct choice and a one-line explanation, so you learn as you play.",
  how=["Press an answer for each question.", "Read the short explanation, then continue.", "Build a streak for bragging rights.", "At the end you get a score out of ten and a rank from Fresh Install to Kernel Wizard."],
  tips=["Read all four options before you answer.", "If you miss one, the explanation is the lesson. Play again for new questions.", "Use the questions you miss as a reading list in our guides."],
  faq=[("Do the questions change each time?", "Yes. Each game picks ten at random from a larger bank in a new order."), ("Is the quiz suitable for beginners?", "Yes. Most questions cover basics, and every answer comes with an explanation.")],
  guides=[("guide-choosing-a-linux-distribution.html", "How to choose a Linux distribution"), ("guide-what-is-a-linux-distribution.html", "What is a Linux distribution?"), ("guide-boot-menu-keys-by-brand.html", "Boot menu keys by brand")]),
 dict(slug="usb-snake", name="USB Snake", icon="\U0001F40D", genre=["Arcade", "Classic"],
  blurb="Classic Snake where the food is a USB drive.",
  title="USB Snake: Classic Snake in Your Browser", desc="USB Snake is the classic Snake game with a USB drive as food. Swipe on a phone or use the arrow keys on a laptop, and beat your best score.",
  intro="USB Snake is the classic snake game with a USB drive as the food. Steer the snake around a grid, collect drives to grow and speed up, and avoid the walls and your own tail. Swipe on a phone, tap the arrow buttons or use the keyboard.",
  how=["Press Start. The snake moves on its own.", "Swipe in a direction, tap the arrow buttons, or use the arrow keys or WASD.", "Collect drives to grow longer. The snake speeds up as your score rises.", "The game ends if you touch a wall or your own body."],
  tips=["Plan two moves ahead, especially when the snake is long.", "Use the edges and corners to keep room in the middle.", "Slow, tidy loops beat risky shortcuts."],
  faq=[("How do I control it on a phone?", "Swipe on the game area, or tap the four arrow buttons below it."), ("Does the snake speed up?", "Yes. It moves a little faster each time you collect a drive, up to a limit.")],
  guides=[("guide-how-to-safely-eject-and-store-your-usb.html", "How to safely eject and store your USB"), ("guide-usb-3-vs-usb-2-for-live-linux.html", "USB 3 vs USB 2 for live Linux"), ("guide-what-is-persistence-on-a-live-usb.html", "What is persistence on a live USB?")]),
]
BY = {g["slug"]: g for g in GAMES}

def cards(skip=None):
    return '<ul class="card-grid gm-cards">' + "".join(f'<li><a class="card gm-link" href="game-{g["slug"]}.html"><span class="gm-ico" aria-hidden="true">{g["icon"]}</span><strong>{e(g["name"])}</strong><span>{e(g["blurb"])}</span><span class="gm-play">Play now</span></a></li>' for g in GAMES if g["slug"] != skip) + "</ul>"

def player(asset_v, only=None):
    o = f' data-only="{only}"' if only else ""
    return f'<div id="games" class="games"{o}><div class="gm-tabs" role="tablist" aria-label="Choose a game"></div><div id="gm-host" class="gm-host"></div></div><noscript><p>The games need JavaScript turned on.</p></noscript><script src="assets/games.js?v={asset_v}" defer></script>'

CTA = '<p class="gm-cta"><a class="btn" href="shop.html">Browse bootable USB drives</a> <a class="btn btn--ghost" href="category-linux.html">Linux USB drives</a> <a class="btn btn--ghost" href="guides.html">Read the guides</a></p>'

def hub(asset_v):
    return ('<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> &rsaquo; Games</nav><h1>Linux mini games</h1>'
            '<p>Short browser games for a quick break while you shop. Practise Linux commands, test your memory, catch falling USB drives or try the quiz. They work on phones, tablets and laptops, need no sign-up and keep your best scores on your own device.</p>'
            + player(asset_v) + '<h2>Pick a game</h2>' + cards() +
            '<h2>Why play?</h2><p>The games borrow from what the shop is about. Command Sprint and the Linux Quiz build familiarity with the terminal and with how Linux works, which makes your first live USB session less daunting. The rest are simply a good way to spend a few minutes.</p>'
            + CTA + faq(COMMON + [("What are Linux mini games?", "They are short browser games with a Linux and bootable-USB theme, from typing commands to a classic arcade game."), ("Which game is best for learning Linux?", "Start with the Linux Quiz, then try Command Sprint to get used to typing commands.")]))

def game(g, asset_v):
    li = lambda xs: "<ul>" + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>"
    gl = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in g["guides"])
    return (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> &rsaquo; <a href="games.html">Games</a> &rsaquo; {e(g["name"])}</nav><h1>{e(g["name"])}: play it in your browser</h1>'
            f'<p>{e(g["intro"])}</p>' + player(asset_v, g["slug"]) +
            f'<h2>How to play {e(g["name"])}</h2>{li(g["how"])}<h2>Tips to score higher</h2>{li(g["tips"])}'
            f'<h2>Learn more while you are here</h2><ul>{gl}</ul><h2>More games</h2>' + cards(g["slug"]) + CTA + faq(g["faq"] + COMMON))
