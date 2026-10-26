/* Linux mini games: Command Sprint, Boot Memory, USB Catch. No libraries; scores stay in this browser only. */
(function () {
  "use strict";
  var tabsEl = document.querySelector(".gm-tabs"), host = document.getElementById("gm-host");
  if (!tabsEl || !host) return;
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
  function stat(label) { var s = $("span", "gm-stat"), b = $("b", "", "0"); s.appendChild(document.createTextNode(label + " ")); s.appendChild(b); s.set = function (v) { b.textContent = v; }; return s; }

  /* 1. Command Sprint: type as many commands as you can in 30 seconds */
  var CMDS = ["ls -la", "cd ~", "pwd", "sudo apt update", "mkdir projects", "cp a.txt b.txt", "mv old new", "rm -i file", "cat notes.txt", "grep -r usb .", "chmod +x run.sh", "df -h", "free -h", "lsblk", "uname -r", "ping -c 4 host", "man ls", "tar -xzf a.tar.gz", "wget file.iso", "nano notes.txt", "whoami", "history", "top", "ssh user@host", "sudo dnf upgrade", "sudo pacman -Syu"];
  function sprint(h) {
    var left = 30, done = 0, timer = null, cur = "", bag = [];
    h.appendChild($("p", "gm-help", "Type each command exactly. It moves on by itself when it is right. You have 30 seconds."));
    var st = $("div", "gm-stats"), tS = stat("Time"), dS = stat("Done"), bS = stat("Best");
    [tS, dS, bS].forEach(function (s) { st.appendChild(s); }); h.appendChild(st);
    var pr = $("div", "gm-prompt", "Press Start"), inp = $("input", "gm-input"), btn = $("button", "btn gm-btn", "Start");
    inp.type = "text"; inp.disabled = true; inp.setAttribute("autocapitalize", "off"); inp.setAttribute("autocomplete", "off"); inp.setAttribute("autocorrect", "off"); inp.spellcheck = false; inp.setAttribute("aria-label", "Type the command shown");
    h.appendChild(pr); h.appendChild(inp); h.appendChild(btn);
    var msg = $("p", "gm-msg"); msg.setAttribute("aria-live", "polite"); h.appendChild(msg);
    tS.set(left); dS.set(0); bS.set(store("sprint") || 0);
    function next() { if (!bag.length) bag = shuffle(CMDS); cur = bag.pop(); pr.textContent = cur; inp.value = ""; inp.className = "gm-input"; }
    function end() {
      clearInterval(timer); timer = null; inp.disabled = true; var b = store("sprint", done); bS.set(b);
      pr.textContent = "Time is up"; msg.textContent = done + " commands. " + (done >= b && done > 0 ? "New best!" : "Best is " + b + ".") + " Press Start to go again."; btn.textContent = "Play again"; btn.disabled = false;
    }
    btn.addEventListener("click", function () {
      left = 30; done = 0; tS.set(left); dS.set(0); msg.textContent = ""; inp.disabled = false; btn.disabled = true; next(); inp.focus();
      timer = setInterval(function () { left--; tS.set(left); if (left <= 0) end(); }, 1000);
    });
    inp.addEventListener("input", function () {
      if (inp.value === cur) { done++; dS.set(done); next(); }
      else inp.className = "gm-input" + (cur.indexOf(inp.value) === 0 ? " ok" : " bad");
    });
    return function () { clearInterval(timer); };
  }

  /* 2. Boot Memory: match the pairs in as few moves as you can */
  var WORDS = ["Ubuntu", "Mint", "Debian", "Fedora", "Arch", "Zorin", "GRUB", "Ventoy"];
  function memory(h) {
    var moves = 0, found = 0, open = [], lock = false;
    h.appendChild($("p", "gm-help", "Flip two cards at a time and find the matching pairs. Fewer moves is better."));
    var st = $("div", "gm-stats"), mS = stat("Moves"), bS = stat("Best"); st.appendChild(mS); st.appendChild(bS); h.appendChild(st);
    var grid = $("div", "gm-grid"), msg = $("p", "gm-msg"), btn = $("button", "btn gm-btn", "Shuffle and restart"); msg.setAttribute("aria-live", "polite");
    h.appendChild(grid); h.appendChild(msg); h.appendChild(btn);
    function deal() {
      grid.textContent = ""; moves = 0; found = 0; open = []; lock = false; mS.set(0); msg.textContent = ""; var b = store("memory", null); bS.set(b == null ? "-" : b);
      shuffle(WORDS.concat(WORDS)).forEach(function (w) {
        var c = $("button", "gm-card", "?"); c.type = "button"; c.setAttribute("aria-label", "Hidden card"); c.dataset.w = w;
        c.addEventListener("click", function () {
          if (lock || c.classList.contains("up") || c.classList.contains("done")) return;
          c.classList.add("up"); c.textContent = w; c.setAttribute("aria-label", w); open.push(c);
          if (open.length === 2) {
            moves++; mS.set(moves); lock = true;
            if (open[0].dataset.w === open[1].dataset.w) {
              open.forEach(function (x) { x.classList.remove("up"); x.classList.add("done"); }); open = []; lock = false; found++;
              if (found === WORDS.length) { var b2 = store("memory", moves, true); bS.set(b2); msg.textContent = "Done in " + moves + " moves. " + (moves <= b2 ? "New best!" : "Best is " + b2 + "."); }
            } else setTimeout(function () { open.forEach(function (x) { x.classList.remove("up"); x.textContent = "?"; x.setAttribute("aria-label", "Hidden card"); }); open = []; lock = false; }, 800);
          }
        });
        grid.appendChild(c);
      });
    }
    btn.addEventListener("click", deal); deal();
  }

  /* 3. USB Catch: catch the drives, dodge the bugs */
  function catcher(h) {
    h.appendChild($("p", "gm-help", "Drag, tap or use the arrow keys to move the penguin. Catch the drives, dodge the bugs. Three lives."));
    var st = $("div", "gm-stats"), sS = stat("Score"), lS = stat("Lives"), bS = stat("Best"); [sS, lS, bS].forEach(function (s) { st.appendChild(s); }); h.appendChild(st);
    var cv = $("canvas", "gm-canvas"), ctx = cv.getContext("2d"), W = 320, H = 360, dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.setAttribute("role", "img"); cv.setAttribute("aria-label", "USB Catch game area");
    var pad = $("div", "gm-pad"), L = $("button", "btn btn--ghost gm-btn", "\u25C0 Left"), R = $("button", "btn btn--ghost gm-btn", "Right \u25B6"), go = $("button", "btn gm-btn", "Start");
    pad.appendChild(L); pad.appendChild(go); pad.appendChild(R);
    var msg = $("p", "gm-msg"); msg.setAttribute("aria-live", "polite");
    h.appendChild(cv); h.appendChild(pad); h.appendChild(msg);
    var px, items, score, lives, run = false, dir = 0, last = 0, spawn = 0, raf = 0;
    function size() { var cs = getComputedStyle(h), inner = (h.clientWidth || 352) - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0), w = Math.max(240, Math.min(inner, 560)); W = w; H = Math.round(w * 1.1); cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + "px"; cv.style.height = H + "px"; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); if (px == null || px > W) px = W / 2; }
    function draw() {
      var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, "#eaf0ff"); g.addColorStop(1, "#ffffff"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.font = "30px serif"; items && items.forEach(function (i) { ctx.fillText(i.good ? "\uD83D\uDCBE" : "\uD83D\uDC1B", i.x, i.y); });
      ctx.font = "40px serif"; ctx.fillText("\uD83D\uDC27", px, H - 34);
    }
    function reset() { size(); px = W / 2; items = []; score = 0; lives = 3; spawn = 0; sS.set(0); lS.set(3); var b = store("catch", null); bS.set(b == null ? 0 : b); msg.textContent = ""; draw(); }
    function end() { run = false; cancelAnimationFrame(raf); var b = store("catch", score); bS.set(b); msg.textContent = "Game over. Score " + score + ". " + (score >= b && score > 0 ? "New best!" : "Best is " + b + "."); go.textContent = "Play again"; go.disabled = false; draw(); }
    function tick(t) {
      if (!run) return; var dt = Math.min((t - last) / 1000, 0.05); last = t;
      if (dir) px = Math.max(24, Math.min(W - 24, px + dir * 340 * dt));
      spawn -= dt; if (spawn <= 0) { items.push({ x: 24 + Math.random() * (W - 48), y: -20, good: Math.random() < 0.72 }); spawn = Math.max(0.35, 0.9 - score * 0.012); }
      var v = 130 + Math.min(score, 60) * 3.2;
      items = items.filter(function (i) {
        i.y += v * dt;
        if (i.y > H - 56 && i.y < H - 12 && Math.abs(i.x - px) < 32) { if (i.good) { score++; sS.set(score); } else { lives--; lS.set(lives); } return false; }
        return i.y < H + 20;
      });
      draw(); if (lives <= 0) return end(); raf = requestAnimationFrame(tick);
    }
    go.addEventListener("click", function () { reset(); run = true; go.disabled = true; last = performance.now(); raf = requestAnimationFrame(tick); });
    function move(e) { if (!run) return; var r = cv.getBoundingClientRect(); px = Math.max(24, Math.min(W - 24, (e.clientX - r.left) * (W / r.width))); }
    cv.addEventListener("pointerdown", move); cv.addEventListener("pointermove", function (e) { if (e.buttons || e.pointerType === "touch") move(e); });
    function hold(b, d) { b.addEventListener("pointerdown", function (e) { e.preventDefault(); dir = d; }); ["pointerup", "pointerleave", "pointercancel"].forEach(function (n) { b.addEventListener(n, function () { dir = 0; }); }); }
    hold(L, -1); hold(R, 1);
    function key(e) { if (!run) return; if (e.key === "ArrowLeft") { dir = -1; e.preventDefault(); } else if (e.key === "ArrowRight") { dir = 1; e.preventDefault(); } }
    function keyUp(e) { if (e.key === "ArrowLeft" || e.key === "ArrowRight") dir = 0; }
    document.addEventListener("keydown", key); document.addEventListener("keyup", keyUp);
    var onResize = function () { if (!run) { size(); draw(); } }; window.addEventListener("resize", onResize);
    reset();
    return function () { run = false; cancelAnimationFrame(raf); document.removeEventListener("keydown", key); document.removeEventListener("keyup", keyUp); window.removeEventListener("resize", onResize); };
  }

  var GAMES = [["sprint", "Command Sprint", sprint], ["memory", "Boot Memory", memory], ["catch", "USB Catch", catcher]], btns = [], stop = null;
  function pick(i) {
    if (stop) { stop(); stop = null; }
    btns.forEach(function (b, n) { b.setAttribute("aria-selected", n === i ? "true" : "false"); });
    host.textContent = ""; stop = GAMES[i][2](host) || null;
    try { history.replaceState(null, "", "#" + GAMES[i][0]); } catch (e) {}
  }
  GAMES.forEach(function (g, i) { var b = $("button", "gm-tab", g[1]); b.type = "button"; b.setAttribute("role", "tab"); b.addEventListener("click", function () { pick(i); }); tabsEl.appendChild(b); btns.push(b); });
  var start = 0; GAMES.forEach(function (g, i) { if (location.hash === "#" + g[0]) start = i; }); pick(start);
})();
