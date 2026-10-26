/* Linux mini games: Command Sprint, Boot Memory, USB Catch, Linux Quiz, USB Snake. No libraries; scores stay on this device. */
(function () {
  "use strict";
  var root = document.getElementById("games"), host = document.getElementById("gm-host");
  if (!root || !host) return;
  var tabsEl = root.querySelector(".gm-tabs"), only = root.getAttribute("data-only");
  function $(t, c, x) { var n = document.createElement(t); if (c) n.className = c; if (x != null) n.textContent = x; return n; }
  function store(k, v, low) {
    try {
      var o = parseFloat(localStorage.getItem("lou-" + k));
      if (v == null) return isNaN(o) ? null : o;
      if (isNaN(o) || (low ? v < o : v > o)) { localStorage.setItem("lou-" + k, String(v)); return v; }
      return o;
    } catch (e) { return v == null ? null : v; }
  }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function stat(label, v) { var s = $("span", "gm-stat"), b = $("b", "", v == null ? "0" : v); s.appendChild(document.createTextNode(label + " ")); s.appendChild(b); s.set = function (x) { b.textContent = x; }; return s; }
  function row(items, cls) { var d = $("div", cls || "gm-stats"); items.forEach(function (s) { d.appendChild(s); }); return d; }
  var SND = false; try { SND = localStorage.getItem("lou-snd") === "1"; } catch (e) {}
  var AC = null;
  function beep(f, d, t) { if (!SND) return; try { AC = AC || new (window.AudioContext || window.webkitAudioContext)(); var o = AC.createOscillator(), g = AC.createGain(); o.type = t || "sine"; o.frequency.value = f; g.gain.value = 0.05; o.connect(g); g.connect(AC.destination); o.start(); o.stop(AC.currentTime + (d || 0.08)); } catch (e) {} }
  function buzz(ms) { try { if (navigator.vibrate) navigator.vibrate(ms || 12); } catch (e) {} }
  function toolbar(h) {
    var s = $("button", "gm-mini", SND ? "Sound on" : "Sound off"); s.type = "button"; s.setAttribute("aria-pressed", String(SND));
    s.addEventListener("click", function () { SND = !SND; try { localStorage.setItem("lou-snd", SND ? "1" : "0"); } catch (e) {} s.textContent = SND ? "Sound on" : "Sound off"; s.setAttribute("aria-pressed", String(SND)); beep(660); });
    var d = $("div", "gm-tools"); d.appendChild(s); h.appendChild(d);
  }
  function seg(h, label, opts, cur, cb) {
    var d = $("div", "gm-seg"); d.appendChild($("span", "gm-seglabel", label)); var bs = [];
    opts.forEach(function (o) { var b = $("button", "gm-chip", o); b.type = "button"; b.setAttribute("aria-pressed", String(o === cur)); b.addEventListener("click", function () { bs.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); cb(o); }); bs.push(b); d.appendChild(b); });
    h.appendChild(d); return d;
  }
  function share(text) {
    var url = location.href.split("#")[0], b = $("button", "btn btn--ghost gm-btn", "Share my score"); b.type = "button";
    b.addEventListener("click", function () {
      if (navigator.share) navigator.share({ text: text, url: url }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(text + " " + url).then(function () { b.textContent = "Copied!"; });
      else b.textContent = "Copy not supported";
    });
    return b;
  }
  function result(box, title, line, shareText) { box.textContent = ""; box.appendChild($("p", "gm-rank", title)); box.appendChild($("p", "gm-msg", line)); box.appendChild(share(shareText)); }

  /* 1. Command Sprint */
  var TIERS = {
    Easy: { t: 45, c: ["ls", "cd ~", "pwd", "whoami", "df -h", "free -h", "lsblk", "top", "history", "clear", "date", "uname -r", "ls -a", "man ls"] },
    Normal: { t: 30, c: ["ls -la", "sudo apt update", "mkdir projects", "cp a.txt b.txt", "mv old new", "rm -i file", "cat notes.txt", "grep -r usb .", "chmod +x run.sh", "ping -c 4 host", "tar -xzf a.tar.gz", "wget file.iso", "nano notes.txt", "ssh user@host", "sudo dnf upgrade", "sudo pacman -Syu"] },
    Hard: { t: 30, c: ["sudo apt update && sudo apt upgrade", "tar -xzf backup.tar.gz", "grep -rin error /var/log", "chmod 644 notes.txt", "find ~ -name *.iso", "ssh -p 22 user@192.168.1.5", "ls -lah /media", "du -sh * | sort -h", "sudo systemctl status ssh", "ps aux | grep firefox", "scp file.txt user@host:~", "sudo mount /dev/sdb1 /mnt"] }
  };
  function sprint(h) {
    var lvl = "Normal", left, done, timer, cur, bag, keys, bad, chars, t0, run = false;
    toolbar(h);
    h.appendChild($("p", "gm-help", "Type each command exactly. It moves on by itself when it is right. Beat the clock and earn a rank."));
    seg(h, "Level", ["Easy", "Normal", "Hard"], lvl, function (o) { if (!run) { lvl = o; reset(); } });
    var tS = stat("Time"), dS = stat("Done"), aS = stat("Accuracy", "100%"), bS = stat("Best"); h.appendChild(row([tS, dS, aS, bS]));
    var prog = $("div", "gm-prog"), pi = $("i"); prog.appendChild(pi); h.appendChild(prog);
    var pr = $("div", "gm-prompt", "Press Start"), inp = $("input", "gm-input"), btn = $("button", "btn gm-btn", "Start"), res = $("div", "gm-res"); res.setAttribute("aria-live", "polite");
    inp.type = "text"; inp.disabled = true; ["autocapitalize", "autocomplete", "autocorrect"].forEach(function (a) { inp.setAttribute(a, "off"); }); inp.spellcheck = false; inp.setAttribute("aria-label", "Type the command shown");
    [pr, inp, btn, res].forEach(function (x) { h.appendChild(x); });
    function reset() { left = TIERS[lvl].t; tS.set(left); dS.set(0); aS.set("100%"); bS.set(store("sprint-" + lvl) || 0); pi.style.width = "100%"; res.textContent = ""; pr.textContent = "Press Start"; }
    function next() { if (!bag.length) bag = shuffle(TIERS[lvl].c); cur = bag.pop(); pr.textContent = cur; inp.value = ""; inp.className = "gm-input"; }
    function end() {
      clearInterval(timer); run = false; inp.disabled = true; btn.disabled = false; btn.textContent = "Play again";
      var mins = (Date.now() - t0) / 60000, wpm = Math.round(chars / 5 / Math.max(mins, 0.1)), acc = Math.max(0, Math.round(100 * (1 - bad / Math.max(keys, 1)))), b = store("sprint-" + lvl, done); bS.set(b);
      var rank = wpm < 15 ? "Terminal Rookie" : wpm < 30 ? "Shell Apprentice" : wpm < 50 ? "Sysadmin" : "Root Legend";
      pr.textContent = "Time is up"; beep(300, 0.25, "square");
      result(res, rank, done + " commands, about " + wpm + " WPM, " + acc + "% accurate. " + (done >= b && done > 0 ? "New best!" : "Best is " + b + "."), "I reached " + rank + " (" + done + " commands) in Command Sprint on Linuxonusb.com.");
    }
    btn.addEventListener("click", function () {
      reset(); done = 0; keys = 0; bad = 0; chars = 0; bag = []; run = true; t0 = Date.now(); inp.disabled = false; btn.disabled = true; next(); inp.focus();
      var total = TIERS[lvl].t; timer = setInterval(function () { left--; tS.set(left); pi.style.width = (100 * left / total) + "%"; if (left <= 0) end(); }, 1000);
    });
    var prev = 0;
    inp.addEventListener("input", function () {
      if (inp.value.length > prev) { keys++; if (cur.indexOf(inp.value) !== 0) bad++; } prev = inp.value.length;
      if (inp.value === cur) { done++; chars += cur.length; dS.set(done); aS.set(Math.max(0, Math.round(100 * (1 - bad / Math.max(keys, 1)))) + "%"); beep(880, 0.05); buzz(8); prev = 0; next(); }
      else inp.className = "gm-input" + (cur.indexOf(inp.value) === 0 ? " ok" : " bad");
    });
    reset(); return function () { clearInterval(timer); };
  }

  /* 2. Boot Memory */
  var WORDS = ["Ubuntu", "Mint", "Debian", "Fedora", "Arch", "Zorin", "GRUB", "Ventoy", "Kernel", "Shell"], PAIRS = { Easy: 6, Normal: 8, Hard: 10 };
  function memory(h) {
    var lvl = "Normal", moves, found, open, lock, secs, timer, started;
    toolbar(h); h.appendChild($("p", "gm-help", "Flip two cards at a time and match the pairs. Fewer moves and a faster time beat your best."));
    seg(h, "Level", ["Easy", "Normal", "Hard"], lvl, function (o) { lvl = o; deal(); });
    var mS = stat("Moves"), tS = stat("Time", "0s"), bS = stat("Best"); h.appendChild(row([mS, tS, bS]));
    var grid = $("div", "gm-grid"), res = $("div", "gm-res"), btn = $("button", "btn gm-btn", "Shuffle and restart"); res.setAttribute("aria-live", "polite"); [grid, res, btn].forEach(function (x) { h.appendChild(x); });
    function tick() { secs++; tS.set(secs + "s"); }
    function deal() {
      clearInterval(timer); started = false; grid.textContent = ""; moves = 0; found = 0; open = []; lock = false; secs = 0; mS.set(0); tS.set("0s"); res.textContent = ""; var b = store("memory-" + lvl, null); bS.set(b == null ? "-" : b);
      shuffle(WORDS.slice(0, PAIRS[lvl]).concat(WORDS.slice(0, PAIRS[lvl]))).forEach(function (w) {
        var c = $("button", "gm-card", "?"); c.type = "button"; c.setAttribute("aria-label", "Hidden card"); c.dataset.w = w;
        c.addEventListener("click", function () {
          if (lock || c.classList.contains("up") || c.classList.contains("done")) return;
          if (!started) { started = true; timer = setInterval(tick, 1000); }
          c.classList.add("up"); c.textContent = w; c.setAttribute("aria-label", w); open.push(c); beep(520, 0.04);
          if (open.length === 2) {
            moves++; mS.set(moves); lock = true;
            if (open[0].dataset.w === open[1].dataset.w) {
              open.forEach(function (x) { x.classList.remove("up"); x.classList.add("done"); }); open = []; lock = false; found++; beep(880, 0.1); buzz(10);
              if (found === PAIRS[lvl]) { clearInterval(timer); var b2 = store("memory-" + lvl, moves, true); bS.set(b2); result(res, moves <= PAIRS[lvl] + 3 ? "Perfect memory" : moves <= PAIRS[lvl] * 2 ? "Sharp mind" : "Keep practising", moves + " moves in " + secs + "s. " + (moves <= b2 ? "New best!" : "Best is " + b2 + "."), "I cleared Boot Memory (" + lvl + ") in " + moves + " moves on Linuxonusb.com."); }
            } else setTimeout(function () { open.forEach(function (x) { x.classList.remove("up"); x.textContent = "?"; x.setAttribute("aria-label", "Hidden card"); }); open = []; lock = false; }, 750);
          }
        });
        grid.appendChild(c);
      });
    }
    btn.addEventListener("click", deal); deal(); return function () { clearInterval(timer); };
  }

  /* 3. USB Catch */
  function catcher(h) {
    toolbar(h); h.appendChild($("p", "gm-help", "Drag, tap or use the arrow keys. Catch drives, dodge bugs, grab the star for a shield and the heart for a life. Streaks build a score multiplier."));
    var sS = stat("Score"), lS = stat("Lives", 3), cS = stat("Combo", "x1"), bS = stat("Best"); h.appendChild(row([sS, lS, cS, bS]));
    var cv = $("canvas", "gm-canvas"), ctx = cv.getContext("2d"), W = 320, H = 360, dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.setAttribute("role", "img"); cv.setAttribute("aria-label", "USB Catch game area");
    var pad = $("div", "gm-pad"), L = $("button", "btn btn--ghost gm-btn", "\u25C0 Left"), R = $("button", "btn btn--ghost gm-btn", "Right \u25B6"), go = $("button", "btn gm-btn", "Start"), res = $("div", "gm-res"); res.setAttribute("aria-live", "polite");
    pad.appendChild(L); pad.appendChild(go); pad.appendChild(R); [cv, pad, res].forEach(function (x) { h.appendChild(x); });
    var px, items = [], score = 0, lives = 3, combo = 0, shield = 0, run = false, dir = 0, last = 0, spawn = 0, raf = 0, stars = [];
    function size() { var cs = getComputedStyle(h), inner = (h.clientWidth || 352) - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0), w = Math.max(240, Math.min(inner, 560)); W = w; H = Math.round(w * 1.1); cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + "px"; cv.style.height = H + "px"; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); if (px == null || px > W) px = W / 2; stars = []; for (var i = 0; i < 24; i++) stars.push([Math.random() * W, Math.random() * H, Math.random() * 1.6 + 0.4]); }
    function mult() { return Math.min(5, 1 + Math.floor(combo / 5)); }
    function draw() {
      var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#dfe8ff"); g.addColorStop(1, "#ffffff"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "rgba(51,95,255,.18)"; stars.forEach(function (s) { ctx.beginPath(); ctx.arc(s[0], s[1], s[2], 0, 6.3); ctx.fill(); });
      ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.font = "30px serif";
      items.forEach(function (i) { ctx.fillText(i.k === "g" ? "\uD83D\uDCBE" : i.k === "b" ? "\uD83D\uDC1B" : i.k === "h" ? "\u2764\uFE0F" : "\u2B50", i.x, i.y); });
      if (shield > 0) { ctx.strokeStyle = "#FF6200"; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(px, H - 34, 30, 0, 6.3); ctx.stroke(); }
      ctx.font = "40px serif"; ctx.fillText("\uD83D\uDC27", px, H - 34);
    }
    function reset() { size(); px = W / 2; items = []; score = 0; lives = 3; combo = 0; shield = 0; spawn = 0; sS.set(0); lS.set(3); cS.set("x1"); var b = store("catch", null); bS.set(b == null ? 0 : b); res.textContent = ""; draw(); }
    function end() { run = false; cancelAnimationFrame(raf); var b = store("catch", score); bS.set(b); beep(220, 0.3, "sawtooth"); go.textContent = "Play again"; go.disabled = false; draw(); result(res, score >= 60 ? "Boot Master" : score >= 30 ? "Drive Collector" : score >= 12 ? "Bug Dodger" : "Fresh Penguin", "Score " + score + ". " + (score >= b && score > 0 ? "New best!" : "Best is " + b + "."), "I scored " + score + " in USB Catch on Linuxonusb.com."); }
    function tick(t) {
      if (!run) return; var dt = Math.min((t - last) / 1000, 0.05); last = t; if (shield > 0) shield -= dt;
      if (dir) px = Math.max(24, Math.min(W - 24, px + dir * 360 * dt));
      spawn -= dt; if (spawn <= 0) { var r = Math.random(); items.push({ x: 24 + Math.random() * (W - 48), y: -20, k: r < 0.62 ? "g" : r < 0.88 ? "b" : r < 0.94 ? "h" : "s" }); spawn = Math.max(0.3, 0.85 - score * 0.008); }
      var v = 130 + Math.min(score, 80) * 2.6;
      items = items.filter(function (i) {
        i.y += v * dt;
        if (i.y > H - 58 && i.y < H - 10 && Math.abs(i.x - px) < 34) {
          if (i.k === "g") { combo++; score += mult(); sS.set(score); cS.set("x" + mult()); beep(700 + combo * 12, 0.05); buzz(6); }
          else if (i.k === "b") { if (shield <= 0) { lives--; lS.set(lives); combo = 0; cS.set("x1"); beep(180, 0.15, "square"); buzz(40); } }
          else if (i.k === "h") { lives = Math.min(5, lives + 1); lS.set(lives); beep(990, 0.12); }
          else { shield = 6; beep(1200, 0.12); }
          return false;
        }
        return i.y < H + 20;
      });
      draw(); if (lives <= 0) return end(); raf = requestAnimationFrame(tick);
    }
    go.addEventListener("click", function () { reset(); run = true; go.disabled = true; last = performance.now(); raf = requestAnimationFrame(tick); });
    function move(e) { if (!run) return; var r = cv.getBoundingClientRect(); px = Math.max(24, Math.min(W - 24, (e.clientX - r.left) * (W / r.width))); }
    cv.addEventListener("pointerdown", move); cv.addEventListener("pointermove", function (e) { if (e.buttons || e.pointerType === "touch") move(e); });
    function hold(b, d) { b.addEventListener("pointerdown", function (e) { e.preventDefault(); dir = d; }); ["pointerup", "pointerleave", "pointercancel"].forEach(function (n) { b.addEventListener(n, function () { dir = 0; }); }); }
    hold(L, -1); hold(R, 1);
    function key(e) { if (!run) return; if (e.key === "ArrowLeft" || e.key === "a") { dir = -1; e.preventDefault(); } else if (e.key === "ArrowRight" || e.key === "d") { dir = 1; e.preventDefault(); } }
    function keyUp(e) { if (["ArrowLeft", "ArrowRight", "a", "d"].indexOf(e.key) > -1) dir = 0; }
    document.addEventListener("keydown", key); document.addEventListener("keyup", keyUp);
    var onResize = function () { if (!run) { size(); draw(); } }; window.addEventListener("resize", onResize); reset();
    return function () { run = false; cancelAnimationFrame(raf); document.removeEventListener("keydown", key); document.removeEventListener("keyup", keyUp); window.removeEventListener("resize", onResize); };
  }

  /* 4. Linux Quiz */
  var QS = [
    ["In most Linux terminals, which shortcut copies selected text?", "Ctrl+Shift+C", "Ctrl+C", "Ctrl+V", "Alt+C", "Ctrl+C stops a running program, so copying uses Ctrl+Shift+C."],
    ["What does the pwd command print?", "The folder you are in", "Your password", "Running processes", "Disk space", "pwd stands for print working directory."],
    ["What is a live USB drive?", "A drive that runs a system without installing it", "A drive that only stores photos", "A charger for laptops", "A faster hard disk", "It lets you test a system with no changes to your disk."],
    ["Which kind of file do you usually write to a USB drive to make it bootable?", "An ISO file", "An MP3 file", "A PDF file", "A DOCX file", "An ISO is a complete copy of an installer disc."],
    ["What does sudo do?", "Runs a command with administrator rights", "Deletes a user", "Shuts the computer down", "Opens the browser", "sudo lets a normal user run one command as an administrator."],
    ["Which package manager do Debian and Ubuntu use?", "apt", "pacman", "dnf", "zypper", "apt installs and updates software on Debian-based systems."],
    ["Which distribution uses the pacman package manager?", "Arch Linux", "Ubuntu", "Fedora", "Debian", "pacman is the Arch Linux package manager."],
    ["UEFI is the modern replacement for what?", "Legacy BIOS", "The kernel", "The file system", "The desktop", "UEFI is the newer firmware that starts the computer."],
    ["What is GRUB?", "A bootloader", "A text editor", "A web browser", "A firewall", "GRUB loads the operating system after the firmware starts."],
    ["Which command lists the files in a folder?", "ls", "ps", "cd", "mv", "ls lists directory contents."],
    ["Which command shows how much memory is used?", "free -h", "df -h", "ls -h", "uname -h", "free reports memory use. df reports disk space."],
    ["What does rm -r do?", "Deletes a folder and everything in it", "Renames a file", "Reads a file", "Restarts the computer", "rm -r removes recursively, with no recycle bin."],
    ["Which desktop is the default on Linux Mint?", "Cinnamon", "GNOME", "LXQt", "Budgie", "Mint's flagship edition uses Cinnamon."],
    ["What is Ventoy used for?", "Putting many ISO files on one USB drive", "Editing photos", "Playing music", "Compressing files", "Ventoy makes a multiboot USB drive."],
    ["Which file system cannot store a single file larger than 4 GB?", "FAT32", "ext4", "Btrfs", "exFAT", "FAT32 has a 4 GB per-file limit."],
    ["Which key opens the boot menu on most Dell computers?", "F12", "F1", "Delete", "Tab", "Dell commonly uses F12 for the one-time boot menu."],
    ["Which of these is a rolling release?", "Arch Linux", "Debian stable", "Ubuntu LTS", "Linux Mint", "Rolling releases update continuously."],
    ["What does chmod +x script.sh do?", "Makes the script runnable", "Deletes the script", "Copies the script", "Hides the script", "+x adds execute permission."],
    ["Which command prints the kernel version?", "uname -r", "whoami", "pwd", "top", "uname -r shows the running kernel release."],
    ["What is Wayland?", "A modern display protocol", "A package manager", "A file system", "A web server", "Wayland is the modern alternative to X11."],
    ["What is swap space?", "Disk space used as memory overflow", "A kind of USB port", "A backup folder", "A network card", "Swap helps when RAM runs short."],
    ["What does LTS stand for?", "Long-term support", "Linux test system", "Light terminal shell", "Large temporary storage", "LTS releases are supported for years."],
    ["Which command downloads a file from a web address?", "wget", "mkdir", "touch", "less", "wget (or curl) fetches files from URLs."],
    ["What does the ~ symbol stand for in a path?", "Your home folder", "The root of the disk", "The trash", "The network", "~ is a shortcut to your home directory."]
  ];
  function quiz(h) {
    var qs, n, score, streak, locked; toolbar(h); h.appendChild($("p", "gm-help", "Ten random questions about Linux and bootable USB drives. Answer to see why, then move on."));
    var qS = stat("Question", "0/10"), sS = stat("Score"), kS = stat("Streak"), bS = stat("Best"); h.appendChild(row([qS, sS, kS, bS]));
    var card = $("div", "gm-quiz"), res = $("div", "gm-res"); res.setAttribute("aria-live", "polite"); h.appendChild(card); h.appendChild(res); bS.set(store("quiz") || 0);
    function begin() { qs = shuffle(QS).slice(0, 10); n = 0; score = 0; streak = 0; res.textContent = ""; sS.set(0); kS.set(0); show(); }
    function show() {
      card.textContent = ""; locked = false; qS.set((n + 1) + "/10"); var q = qs[n]; card.appendChild($("p", "gm-q", q[0]));
      shuffle([q[1], q[2], q[3], q[4]]).forEach(function (o) {
        var b = $("button", "gm-opt", o); b.type = "button";
        b.addEventListener("click", function () {
          if (locked) return; locked = true; var ok = o === q[1];
          [].forEach.call(card.querySelectorAll(".gm-opt"), function (x) { if (x.textContent === q[1]) x.classList.add("right"); });
          if (ok) { score++; streak++; beep(880, 0.08); buzz(8); } else { streak = 0; b.classList.add("wrong"); beep(200, 0.15, "square"); }
          sS.set(score); kS.set(streak); card.appendChild($("p", "gm-why", (ok ? "Correct. " : "Not quite. ") + q[5]));
          var nx = $("button", "btn gm-btn", n === 9 ? "See result" : "Next question"); nx.type = "button"; nx.addEventListener("click", function () { n++; if (n >= 10) finish(); else show(); }); card.appendChild(nx); nx.focus();
        });
        card.appendChild(b);
      });
    }
    function finish() {
      card.textContent = ""; var b = store("quiz", score); bS.set(b);
      var rank = score >= 9 ? "Kernel Wizard" : score >= 7 ? "Power User" : score >= 4 ? "Getting There" : "Fresh Install";
      result(res, rank, score + " out of 10. " + (score >= b && score > 0 ? "New best!" : "Best is " + b + ". ") , "I scored " + score + "/10 on the Linux Quiz at Linuxonusb.com.");
      var again = $("button", "btn gm-btn", "Play again"); again.type = "button"; again.addEventListener("click", begin); res.appendChild(again);
    }
    begin(); return function () {};
  }

  /* 5. USB Snake */
  function snake(h) {
    toolbar(h); h.appendChild($("p", "gm-help", "Guide the snake to the USB drives. Swipe, use the arrow keys or WASD, or tap the buttons. Do not hit the walls or yourself."));
    var sS = stat("Score"), bS = stat("Best"); h.appendChild(row([sS, bS]));
    var cv = $("canvas", "gm-canvas"), ctx = cv.getContext("2d"), G = 16, S = 320, dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.setAttribute("role", "img"); cv.setAttribute("aria-label", "USB Snake game area");
    var dp = $("div", "gm-dpad"), mk = function (t, a) { var b = $("button", "btn btn--ghost gm-btn gm-d", t); b.type = "button"; b.setAttribute("aria-label", a); return b; };
    var U = mk("\u25B2", "Up"), Lf = mk("\u25C0", "Left"), Dn = mk("\u25BC", "Down"), Rt = mk("\u25B6", "Right"); [U, Lf, Dn, Rt].forEach(function (b) { dp.appendChild(b); });
    var go = $("button", "btn gm-btn", "Start"), res = $("div", "gm-res"); res.setAttribute("aria-live", "polite"); [cv, dp, go, res].forEach(function (x) { h.appendChild(x); });
    var body, dir, queue, food, score, run = false, timer = null;
    function size() { var cs = getComputedStyle(h), inner = (h.clientWidth || 352) - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0); S = Math.floor(Math.max(240, Math.min(inner, 480)) / G) * G; cv.width = S * dpr; cv.height = S * dpr; cv.style.width = S + "px"; cv.style.height = S + "px"; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    function place() { do { food = [Math.floor(Math.random() * G), Math.floor(Math.random() * G)]; } while (body.some(function (p) { return p[0] === food[0] && p[1] === food[1]; })); }
    function draw() {
      var c = S / G; ctx.fillStyle = "#f4f6ff"; ctx.fillRect(0, 0, S, S); ctx.fillStyle = "#e6ebff";
      for (var x = 0; x < G; x++) for (var y = 0; y < G; y++) if ((x + y) % 2) ctx.fillRect(x * c, y * c, c, c);
      ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.font = Math.round(c * 0.8) + "px serif"; if (food) ctx.fillText("\uD83D\uDCBE", food[0] * c + c / 2, food[1] * c + c / 2 + 1);
      (body || []).forEach(function (p, i) { ctx.fillStyle = i === 0 ? "#FF6200" : "#335FFF"; var r = c * 0.12; ctx.beginPath(); ctx.roundRect ? ctx.roundRect(p[0] * c + 1, p[1] * c + 1, c - 2, c - 2, r * 2) : ctx.rect(p[0] * c + 1, p[1] * c + 1, c - 2, c - 2); ctx.fill(); });
    }
    function reset() { size(); body = [[8, 8], [7, 8], [6, 8]]; dir = [1, 0]; queue = []; score = 0; sS.set(0); var b = store("snake", null); bS.set(b == null ? 0 : b); res.textContent = ""; place(); draw(); }
    function turn(d) { if (!run) return; var ref = queue.length ? queue[queue.length - 1] : dir; if (d[0] === -ref[0] && d[1] === -ref[1]) return; if (queue.length < 2) queue.push(d); }
    function end() { run = false; clearInterval(timer); var b = store("snake", score); bS.set(b); beep(200, 0.3, "sawtooth"); buzz(60); go.textContent = "Play again"; go.disabled = false; result(res, score >= 25 ? "Snake Charmer" : score >= 12 ? "Drive Hunter" : score >= 5 ? "Getting Longer" : "Hatchling", "Score " + score + ". " + (score >= b && score > 0 ? "New best!" : "Best is " + b + "."), "I scored " + score + " in USB Snake on Linuxonusb.com."); }
    function step() {
      if (document.hidden) return; if (queue.length) dir = queue.shift();
      var hd = [body[0][0] + dir[0], body[0][1] + dir[1]];
      if (hd[0] < 0 || hd[1] < 0 || hd[0] >= G || hd[1] >= G || body.some(function (p) { return p[0] === hd[0] && p[1] === hd[1]; })) return end();
      body.unshift(hd);
      if (hd[0] === food[0] && hd[1] === food[1]) { score++; sS.set(score); beep(760, 0.06); buzz(8); place(); clearInterval(timer); timer = setInterval(step, Math.max(60, 150 - score * 4)); } else body.pop();
      draw();
    }
    go.addEventListener("click", function () { reset(); run = true; go.disabled = true; timer = setInterval(step, 150); });
    U.addEventListener("click", function () { turn([0, -1]); }); Dn.addEventListener("click", function () { turn([0, 1]); }); Lf.addEventListener("click", function () { turn([-1, 0]); }); Rt.addEventListener("click", function () { turn([1, 0]); });
    var map = { ArrowUp: [0, -1], w: [0, -1], ArrowDown: [0, 1], s: [0, 1], ArrowLeft: [-1, 0], a: [-1, 0], ArrowRight: [1, 0], d: [1, 0] };
    function key(e) { if (run && map[e.key]) { e.preventDefault(); turn(map[e.key]); } } document.addEventListener("keydown", key);
    var sx, sy; cv.addEventListener("touchstart", function (e) { var t = e.changedTouches[0]; sx = t.clientX; sy = t.clientY; }, { passive: true });
    cv.addEventListener("touchend", function (e) { var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy; if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return; if (Math.abs(dx) > Math.abs(dy)) turn([dx > 0 ? 1 : -1, 0]); else turn([0, dy > 0 ? 1 : -1]); }, { passive: true });
    reset(); return function () { run = false; clearInterval(timer); document.removeEventListener("keydown", key); };
  }

  var GAMES = [["command-sprint", "Command Sprint", sprint], ["boot-memory", "Boot Memory", memory], ["usb-catch", "USB Catch", catcher], ["linux-quiz", "Linux Quiz", quiz], ["usb-snake", "USB Snake", snake]], btns = [], stop = null;
  function pick(i) {
    if (stop) { stop(); stop = null; }
    btns.forEach(function (b, n) { b.setAttribute("aria-selected", String(n === i)); });
    host.textContent = ""; stop = GAMES[i][2](host) || null;
  }
  var start = 0; GAMES.forEach(function (g, i) { if (only === g[0] || location.hash === "#" + g[0]) start = i; });
  if (only) { if (tabsEl) tabsEl.hidden = true; }
  else GAMES.forEach(function (g, i) { var b = $("button", "gm-tab", g[1]); b.type = "button"; b.setAttribute("role", "tab"); b.addEventListener("click", function () { pick(i); try { history.replaceState(null, "", "#" + g[0]); } catch (e) {} }); tabsEl.appendChild(b); btns.push(b); });
  pick(start);
})();
