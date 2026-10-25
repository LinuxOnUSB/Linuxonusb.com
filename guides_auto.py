"""Data-driven guides: distro profiles, install guides, comparisons, best-for lists, commands, glossary.
more(plink, seen) returns (slug, title, meta description, html body) tuples. plink(prefix, text) links a product page.
Edit the data blocks below and rebuild; every page is generated from them."""
import html
from itertools import combinations

def e(s): return html.escape(str(s), quote=True)
def trim(t, n):
    if len(t) <= n: return t
    return t[:n].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
def ram_txt(r): return f"{int(r * 1024)} MB" if r < 1 else f"{r:g} GB"

# slug|name|base|desktop|package manager|release|RAM GB|installer|tags|audience|update command|product id prefix
DISTROS = """ubuntu|Ubuntu|Debian|GNOME|apt and Snap|lts|4|Ubuntu's graphical installer|beginner stable dev gnome|people who want the most widely supported desktop, with a new release every six months and a long-term release every two years|sudo apt update && sudo apt upgrade|ubuntu-linux-latest
linux-mint|Linux Mint|Ubuntu|Cinnamon|apt and Flatpak|lts|4|the Mint graphical installer|beginner winlike stable|people moving from Windows who want a familiar, conservative desktop that rarely changes|sudo apt update && sudo apt upgrade|linux-mint-latest
debian|Debian|Independent|GNOME|apt|fixed|2|the Debian installer|stable server dev|people who value stability, long-lived releases and a community-run project|sudo apt update && sudo apt upgrade|debian-linux-latest
fedora|Fedora|Independent|GNOME|dnf and Flatpak|fixed|4|the Anaconda installer|dev gnome|people who want recent software and developer tools with sensible defaults|sudo dnf upgrade|fedora-linux-latest
arch|Arch Linux|Independent|none by default|pacman|rolling|2|the archinstall script or a manual install|advanced rolling dev|experienced users who want to build the system themselves and always run current software|sudo pacman -Syu|arch-linux-latest
manjaro|Manjaro|Arch|Xfce, KDE Plasma or GNOME|pacman|rolling|4|the Calamares installer|rolling kde xfce|people who want Arch's software with an easier installer and curated updates|sudo pacman -Syu|manjaro-linux-latest
endeavouros|EndeavourOS|Arch|Xfce, with other desktops on offer|pacman|rolling|2|the Calamares installer|rolling advanced dev|people who want close-to-pure Arch with a friendly installer|sudo pacman -Syu|endeavour-linux
cachyos|CachyOS|Arch|KDE Plasma, with others on offer|pacman|rolling|4|the Calamares installer|rolling gaming kde|people who want a fast Arch-based system tuned for performance and gaming|sudo pacman -Syu|cachyos
garuda|Garuda Linux|Arch|KDE Plasma|pacman|rolling|8|the Calamares installer|rolling gaming kde|people with a capable computer who want a polished, gaming-friendly Arch-based desktop|sudo pacman -Syu|garuda
opensuse|openSUSE|Independent|KDE Plasma or GNOME|zypper|semi|4|the openSUSE installer|stable kde dev server|people who like a carefully engineered system with strong snapshot rollback, in rolling (Tumbleweed) or fixed (Leap) form|sudo zypper dup (Tumbleweed) or sudo zypper update (Leap)|opensuse-linux-latest
pop-os|Pop!_OS|Ubuntu|COSMIC|apt and Flatpak|lts|4|the Pop!_OS installer|gaming dev beginner|people who want a developer- and gamer-friendly system from hardware maker System76|sudo apt update && sudo apt upgrade|pop-os-linux
zorin|Zorin OS|Ubuntu|a Windows-style GNOME desktop|apt|lts|4|the Zorin installer|beginner winlike stable|people switching from Windows who want a polished layout from day one|sudo apt update && sudo apt upgrade|zorin-os-linux-bootable
elementary|elementary OS|Ubuntu|Pantheon|apt and Flatpak|lts|4|the elementary installer|beginner mac stable|people who like a clean, Mac-style desktop with a curated app store|sudo apt update && sudo apt upgrade|elementary-os
mx-linux|MX Linux|Debian|Xfce, with KDE and Fluxbox editions|apt|fixed|2|the MX installer|light stable beginner xfce|people who want a stable, lightweight system with many handy built-in tools, even on older hardware|sudo apt update && sudo apt upgrade|mx-linux-latest
antix|antiX|Debian|IceWM or Fluxbox|apt|fixed|0.5|the antiX installer|light advanced rescue|people with very old or low-memory computers, since it runs without systemd|sudo apt update && sudo apt upgrade|antix
linux-lite|Linux Lite|Ubuntu|Xfce|apt|lts|2|the Linux Lite installer|light beginner winlike xfce|people moving from Windows who want a simple, light system for modest hardware|sudo apt update && sudo apt upgrade|linux-lite
lubuntu|Lubuntu|Ubuntu|LXQt|apt|lts|2|the Calamares installer|light beginner|people who want an official Ubuntu flavour that runs well on older computers|sudo apt update && sudo apt upgrade|lubuntu
xubuntu|Xubuntu|Ubuntu|Xfce|apt|lts|2|Ubuntu's graphical installer|light stable beginner xfce|people who want Ubuntu's base with a light, traditional desktop|sudo apt update && sudo apt upgrade|xubuntu
kubuntu|Kubuntu|Ubuntu|KDE Plasma|apt|lts|4|the Calamares installer|stable kde beginner|people who want Ubuntu's base with KDE Plasma and plenty of customisation|sudo apt update && sudo apt upgrade|kubuntu
ubuntu-budgie|Ubuntu Budgie|Ubuntu|Budgie|apt|lts|4|Ubuntu's graphical installer|beginner stable|people who like a simple, modern and tidy desktop on Ubuntu's base|sudo apt update && sudo apt upgrade|ubuntu-budgie
ubuntu-studio|Ubuntu Studio|Ubuntu|KDE Plasma|apt|lts|8|the Calamares installer|creative stable kde|people making audio, video, graphics or photos who want the tools preinstalled|sudo apt update && sudo apt upgrade|ubuntu-studio
kde-neon|KDE neon|Ubuntu|KDE Plasma|apt|semi|4|the Calamares installer|kde dev|people who want the newest KDE Plasma on a stable Ubuntu LTS base|sudo apt update && sudo apt full-upgrade|kde-neon
alma|AlmaLinux|RHEL-compatible|GNOME|dnf|lts|2|the Anaconda installer|server stable|people running servers or workstations who want Red Hat Enterprise Linux compatibility and long support|sudo dnf upgrade|alma-linux-latest
rocky|Rocky Linux|RHEL-compatible|GNOME|dnf|lts|2|the Anaconda installer|server stable|people running servers or workstations who want Red Hat Enterprise Linux compatibility and long support|sudo dnf upgrade|rocky-linux
solus|Solus|Independent|Budgie, with GNOME, KDE and Xfce editions|eopkg|semi|4|the Solus installer|beginner|people who want a clean, curated desktop built from scratch rather than on another distribution|sudo eopkg upgrade|solus-linux
void|Void Linux|Independent|none by default|xbps|rolling|1|a text-based installer|advanced rolling light|experienced users who like a fast, independent, runit-based system|sudo xbps-install -Su|void-linux-latest
gentoo|Gentoo|Independent|none by default|Portage|rolling|4|a manual installation|advanced rolling|enthusiasts who want to build and tune the system from source code|sudo emerge --sync && sudo emerge --ask --update --deep --newuse @world|gentoo-linux
slackware|Slackware|Independent|KDE Plasma or Xfce|slackpkg|fixed|2|a text-based setup program|advanced stable|users who value simplicity and a very traditional Unix-like design|slackpkg update && slackpkg upgrade-all|slackware
alpine|Alpine Linux|Independent|none by default|apk|fixed|0.25|the setup-alpine script|advanced light server|people who want a tiny, security-focused system, often for servers and containers|apk update && apk upgrade|alpine-linux-latest
tiny-core|Tiny Core Linux|Independent|a minimal window manager|the Tiny Core extension system|fixed|0.05|a lightweight boot-and-save setup|light advanced rescue|people who want an extremely small system that runs from memory|none needed day to day|tiny-core
puppy|Puppy Linux|Independent|JWM or a similar light desktop|the Puppy Package Manager|fixed|0.5|a frugal install or a save file|light rescue|people reviving old computers or wanting a portable system that runs from RAM|none needed day to day|puppy-linux-latest
slax|Slax|Debian|Fluxbox|apt|fixed|1|a portable USB setup|light rescue|people who want a pocket-sized live system that starts fast|none needed day to day|slax-linux
porteus|Porteus|Slackware|Xfce, KDE or LXQt|modules|fixed|1|a portable USB setup|light rescue|people who want a modular, portable live system|none needed day to day|porteus-linux
qubes|Qubes OS|Fedora and Xen|Xfce|dnf inside templates|fixed|16|its own installer|privacy advanced|people who need strong security through isolation and own a capable computer|the built-in Qubes Update tool|qubes-os
whonix|Whonix|Debian|Xfce|apt|fixed|4|a virtual machine image|privacy advanced|people who want anonymity by routing everything through Tor|sudo apt update && sudo apt upgrade|whonix
vanilla-os|Vanilla OS|Debian|GNOME|apx|fixed|4|its graphical installer|immutable beginner|people who want a system that is hard to break and easy to roll back|the built-in update manager|vanilla-os
nobara|Nobara|Fedora|GNOME or KDE Plasma|dnf|fixed|4|a graphical installer|gaming kde|people who want a Fedora-based system with gaming fixes and media codecs ready to go|the Nobara Update System tool|nobara-linux-latest
deepin|deepin|Independent|DDE|apt|fixed|4|a graphical installer|beginner winlike|people who like a polished, visually rich desktop|sudo apt update && sudo apt upgrade|deepin
bodhi|Bodhi Linux|Ubuntu|Moksha|apt|lts|1|a graphical installer|light advanced|people who want a minimal, highly customisable and light desktop|sudo apt update && sudo apt upgrade|bodhi
bunsenlabs|BunsenLabs|Debian|Openbox|apt|fixed|1|a graphical installer|light advanced|people who like a simple, keyboard-friendly, lightweight desktop|sudo apt update && sudo apt upgrade|bunsen
q4os|Q4OS|Debian|Trinity or KDE Plasma|apt|fixed|1|a graphical installer|light winlike stable|people who want a Windows-like layout that runs well on older computers|sudo apt update && sudo apt upgrade|q4os
sparky|SparkyLinux|Debian|Xfce, LXQt, MATE or KDE Plasma|apt|fixed|2|a graphical installer|light stable|people who want a fast Debian-based system with a choice of lightweight desktops|sudo apt update && sudo apt upgrade|sparky
peppermint|Peppermint OS|Debian|Xfce|apt|fixed|2|a graphical installer|light beginner xfce|people who want a light, simple desktop for everyday web and office use|sudo apt update && sudo apt upgrade|peppermint
nitrux|Nitrux|Debian|NX Desktop|apt and AppImage|fixed|4|a graphical installer|kde|people who like KDE-based design and AppImage software|sudo apt update && sudo apt upgrade|nitrux
mageia|Mageia|Independent|KDE Plasma or GNOME|dnf|fixed|2|the Mageia installer|stable kde|people who want a community-run, rpm-based desktop system|sudo dnf upgrade|mageia
openmandriva|OpenMandriva|Independent|KDE Plasma|dnf|fixed|4|a graphical installer|kde|people who want a KDE-focused, rpm-based system with current software|sudo dnf upgrade|open-mandriva
devuan|Devuan|Debian|Xfce|apt|fixed|1|a Debian-style installer|stable advanced light|people who want Debian without systemd|sudo apt update && sudo apt upgrade|devuan
tuxedo-os|TUXEDO OS|Ubuntu|KDE Plasma|apt|lts|4|a graphical installer|beginner kde stable|people who want a polished KDE system tuned for TUXEDO laptops and other computers|sudo apt update && sudo apt upgrade|tuxedo-os
voyager|Voyager|Ubuntu|Xfce|apt|lts|2|a graphical installer|beginner light xfce|people who want a decorated, ready-to-use Xfce desktop on Ubuntu's base|sudo apt update && sudo apt upgrade|voyager
omarchy|Omarchy|Arch|Hyprland|pacman|rolling|4|a guided installer|dev rolling advanced|developers who like a keyboard-driven tiling desktop that is set up for them|sudo pacman -Syu|omarchy
freebsd|FreeBSD|BSD|none by default|pkg|fixed|1|the bsdinstall text installer|server advanced stable|people running servers, firewalls or storage who like ZFS and a complete, unified base system|pkg update && pkg upgrade|freebsd-latest
openbsd|OpenBSD|BSD|none by default|pkg_add|fixed|1|a text-based installer|privacy advanced stable|people who put security and clean code first|doas pkg_add -u|openbsd-latest"""

D = {}
for row in DISTROS.split("\n"):
    f = row.split("|")
    D[f[0]] = dict(slug=f[0], name=f[1], base=f[2], desk=f[3], pkg=f[4], rel=f[5], ram=float(f[6]), inst=f[7], tags=f[8].split(), aud=f[9], upd=f[10], pre=f[11])

REL = {"lts": "long-term releases that stay supported for years", "fixed": "numbered releases on a fixed schedule", "rolling": "a rolling release, so updates arrive continuously with no big version jumps", "semi": "a curated model where updates are released in tested batches"}
def basep(d):
    b = d["base"]
    if b == "Independent": return "built independently rather than on another distribution"
    if b == "BSD": return "a member of the BSD family of Unix-like systems rather than a Linux distribution"
    if b == "RHEL-compatible": return "built to stay compatible with Red Hat Enterprise Linux"
    return f"built on {b}"

STRENGTH = {"beginner": "A gentle learning curve, with everyday tasks handled through graphical tools.", "winlike": "A layout Windows users recognise quickly, with a taskbar, a start-style menu and familiar window controls.", "mac": "A tidy, Mac-inspired layout with a dock and a curated app store.", "stable": "Changes arrive slowly and are tested first, so the system rarely surprises you.", "light": "Low memory and processor use, which helps older or modest computers feel quick.", "rolling": "Software stays close to the newest versions without waiting for a new release.", "advanced": "Fine control over how the system is built and what it contains.", "dev": "Good tooling for programming, with current compilers, languages and containers available.", "gaming": "Sensible defaults for Steam, Proton and current graphics drivers.", "creative": "Suited to audio, video, graphics and photography work.", "server": "A strong fit for servers and always-on machines, thanks to long support and predictable updates.", "privacy": "Design choices that put privacy and security ahead of convenience.", "rescue": "Small and quick to start, which makes it handy for repair, recovery and portable use.", "immutable": "A protected core that is hard to break and easy to roll back.", "kde": "The KDE Plasma desktop, with a great deal of customisation built in.", "gnome": "The GNOME desktop, with a clean, modern design.", "xfce": "The Xfce desktop, which is light, traditional and easy to tweak."}
CONSIDER = {"advanced": "It expects you to read documentation and solve problems yourself, so it is not the best first Linux system.", "rolling": "Updates never stop arriving, so update often and keep a backup in case an update needs fixing.", "light": "The lighter design means fewer built-in features and a plainer look than the big desktops.", "privacy": "Extra isolation or anonymity can mean slower performance and some programs behaving differently.", "rescue": "It is designed for portable or temporary use, so it suits a live USB drive better than a permanent daily system.", "immutable": "Because the core is protected, installing some traditional software works differently.", "server": "Software versions are conservative, so brand-new desktop applications may arrive later.", "stable": "Stability means some software is not the very newest version.", "gaming": "Newer hardware can need extra driver steps, so check your graphics card before you commit.", "creative": "The full creative toolset takes more disk space and memory than a basic desktop."}

def ram_note(d):
    r = d["ram"]
    if r >= 8: return f"It is meant for a capable computer, so plan on at least {ram_txt(r)} of RAM."
    return f"As a rough guide, about {ram_txt(r)} of RAM is a comfortable minimum for a desktop session."

INSTALL_SLUG = {"zorin": "how-to-install-zorin-os-from-usb"}
def inst_slug(d): return INSTALL_SLUG.get(d["slug"], f"how-to-install-{d['slug']}-from-usb")

def profile(d, pairs):
    n = d["name"]
    rel = [p for p in pairs if d["slug"] in p][:6]
    cmp_links = "".join(f'<li><a href="guide-{a}-vs-{b}.html">{e(D[a]["name"])} vs {e(D[b]["name"])}</a></li>' for a, b in rel)
    st = "".join(f"<li>{STRENGTH[t]}</li>" for t in d["tags"] if t in STRENGTH)
    co = "".join(f"<li>{CONSIDER[t]}</li>" for t in d["tags"] if t in CONSIDER) + f"<li>{ram_note(d)}</li>"
    return (f"<p>{e(n)} is {e(basep(d))}. It uses {e(d['desk'])} as its desktop and {e(d['pkg'])} for software, and it follows {REL[d['rel']]}.</p>"
            f"<h2>{e(n)} at a glance</h2><ul><li><strong>Foundation:</strong> {e(basep(d))}</li><li><strong>Desktop:</strong> {e(d['desk'])}</li><li><strong>Software tools:</strong> {e(d['pkg'])}</li><li><strong>Release style:</strong> {e(REL[d['rel']])}</li><li><strong>Installer:</strong> {e(d['inst'])}</li></ul>"
            f"<h2>Who {e(n)} suits</h2><p>{e(n)} suits {e(d['aud'])}.</p>"
            f"<h2>Strengths</h2><ul>{st}</ul><h2>Things to consider</h2><ul>{co}</ul>"
            f"<h2>Try {e(n)} from a USB drive</h2><p>The easiest way to find out is to start it from a USB drive without changing your computer. See the {plink_(d['pre'], n + ' bootable USB drive')}, then follow <a href=\"guide-{inst_slug(d)}.html\">our install guide</a> when you are ready. New to this? Read <a href=\"guide-how-to-try-linux-without-installing.html\">how to try Linux without installing it</a> and <a href=\"guide-how-to-boot-from-usb.html\">how to boot from a USB drive</a>.</p>"
            + (f"<h2>Compare {e(n)}</h2><ul>{cmp_links}</ul>" if cmp_links else ""))

def install(d):
    n = d["name"]; adv = "advanced" in d["tags"]; r = d["rel"]
    heads = []
    if adv: heads.append(f"{n} expects some comfort with documentation. If this is your first Linux system, try a beginner-friendly distribution on a live USB first, then come back.")
    if "light" in d["tags"]: heads.append(f"{n} is light on resources, so it is a good candidate for an older computer. A USB 3.0 drive still makes the live session noticeably quicker.")
    if "rolling" in d["tags"]: heads.append("Because this is a rolling release, run a full update right after installing and keep doing so regularly. Make a backup before large updates.")
    if "rescue" in d["tags"]: heads.append(f"{n} is built for portable use. Many people keep it on a USB drive rather than installing it to the hard disk.")
    if not heads: heads.append("The steps below suit most computers made in the last decade. Screens vary slightly between versions.")
    upd = "" if d["upd"].startswith(("none", "the ")) else f"<pre>{e(d['upd'])}</pre>"
    updline = (f"<p>To update {e(n)} from a terminal, run:</p>{upd}" if upd else f"<p>Updates for {e(n)} are handled by {e(d['upd'])}. See <a href=\"guide-how-to-update-linux.html\">how to update Linux</a> for the general idea.</p>")
    relnote = {"rolling": "Rolling releases never need a big upgrade, but they do need regular updates.", "lts": "Long-term releases mean you can stay on one version for years, receiving security fixes along the way.", "fixed": "Fixed releases are supported for a set period, so plan to move to the next version when this one reaches the end of its life.", "semi": "Updates arrive in tested batches, so you get newer software without the surprises of a pure rolling release."}[r]
    return (f"<p>This guide covers installing {e(n)} from a bootable USB drive. {' '.join(heads)}</p>"
            f"<h2>Before you begin</h2><ul><li>Back up anything you care about. See <a href=\"guide-how-to-back-up-before-installing-linux.html\">how to back up before installing Linux</a>.</li><li>Check you have about {e(ram_txt(d['ram']))} of RAM or more, and a spare 20 GB or more of disk space for a desktop install.</li><li>Plug a laptop into power so it cannot shut down part-way.</li><li>Have your {plink_(d['pre'], n + ' bootable USB drive')} ready.</li></ul>"
            f"<h2>Install steps</h2><ol><li>Insert the USB drive and restart. Open the boot menu (see <a href=\"guide-boot-menu-keys-by-brand.html\">boot menu keys by brand</a>) and choose the USB drive.</li><li>When {e(n)} starts, use {e(d['inst'])} to begin. If it offers a live session, test Wi-Fi, sound and graphics first.</li><li>Choose your language, keyboard layout and time zone.</li><li>Choose where to install. To keep another system, see <a href=\"guide-how-to-dual-boot-linux-and-windows.html\">dual booting</a>. To use the whole disk, pick the erase-disk option and confirm only when you are sure.</li><li>Create your user name and a strong password, then start the installation.</li><li>When it finishes, remove the USB drive and restart into {e(n)}.</li></ol>"
            f"<h2>After installing</h2><p>{e(relnote)}</p>{updline}"
            f"<h2>If it will not start</h2><ul><li>Try <a href=\"guide-secure-boot-and-linux.html\">turning off Secure Boot</a> if the drive is ignored.</li><li>Check <a href=\"guide-uefi-vs-legacy-bios-boot.html\">UEFI vs Legacy</a> settings.</li><li>Read <a href=\"guide-how-to-fix-a-usb-drive-that-will-not-boot.html\">how to fix a USB drive that will not boot</a>.</li></ul>"
            f"<p>Want to know more first? Read <a href=\"guide-what-is-{d['slug']}.html\">what {e(n)} is and who it is for</a>.</p>")

PAIRS = ("ubuntu:debian ubuntu:fedora ubuntu:linux-mint ubuntu:pop-os ubuntu:zorin ubuntu:elementary debian:linux-mint debian:fedora debian:pop-os debian:zorin debian:elementary fedora:linux-mint fedora:pop-os fedora:zorin fedora:elementary linux-mint:pop-os linux-mint:zorin linux-mint:elementary pop-os:zorin pop-os:elementary zorin:elementary "
         "arch:manjaro arch:endeavouros arch:cachyos arch:garuda manjaro:endeavouros manjaro:cachyos manjaro:garuda endeavouros:cachyos endeavouros:garuda cachyos:garuda "
         "antix:lubuntu antix:xubuntu antix:linux-lite antix:mx-linux antix:puppy antix:bodhi lubuntu:xubuntu lubuntu:linux-lite lubuntu:mx-linux lubuntu:puppy lubuntu:bodhi xubuntu:linux-lite xubuntu:mx-linux xubuntu:puppy xubuntu:bodhi linux-lite:mx-linux linux-lite:puppy linux-lite:bodhi mx-linux:puppy mx-linux:bodhi puppy:bodhi "
         "alma:rocky alma:debian rocky:debian alma:fedora rocky:fedora debian:opensuse alma:opensuse rocky:opensuse "
         "gentoo:arch gentoo:void gentoo:alpine gentoo:slackware arch:void arch:alpine arch:slackware void:alpine void:slackware alpine:slackware "
         "freebsd:openbsd freebsd:debian openbsd:debian "
         "ubuntu:kubuntu ubuntu:xubuntu ubuntu:lubuntu ubuntu:ubuntu-budgie ubuntu:ubuntu-studio kubuntu:xubuntu kubuntu:lubuntu kubuntu:ubuntu-budgie kubuntu:ubuntu-studio xubuntu:ubuntu-budgie xubuntu:ubuntu-studio lubuntu:ubuntu-budgie lubuntu:ubuntu-studio ubuntu-budgie:ubuntu-studio "
         "qubes:whonix qubes:debian whonix:debian nobara:cachyos nobara:pop-os nobara:garuda nobara:fedora cachyos:pop-os garuda:pop-os kubuntu:kde-neon kde-neon:opensuse kubuntu:opensuse "
         "arch:fedora opensuse:fedora opensuse:ubuntu linux-mint:manjaro zorin:linux-lite mx-linux:debian vanilla-os:fedora vanilla-os:ubuntu omarchy:arch omarchy:endeavouros devuan:debian").split()
PAIRS = [tuple(p.split(":")) for p in PAIRS]

def compare(a, b):
    A, B = D[a], D[b]; an, bn = A["name"], B["name"]
    L = []
    if A["base"] == B["base"] and A["base"] != "Independent": L.append(f"<strong>Foundation:</strong> both are built on {e(A['base'])}, so much of the help, software and troubleshooting advice for one applies to the other.")
    elif A["base"] == B["base"]: L.append("<strong>Foundation:</strong> both are independent projects with their own repositories and tools, so advice for one rarely carries straight over to the other.")
    else: L.append(f"<strong>Foundation:</strong> {e(an)} is {e(basep(A))}, while {e(bn)} is {e(basep(B))}.")
    L.append(f"<strong>Desktop:</strong> " + (f"both use {e(A['desk'])}." if A["desk"] == B["desk"] else f"{e(an)} uses {e(A['desk'])}; {e(bn)} uses {e(B['desk'])}."))
    L.append(f"<strong>Software tools:</strong> " + (f"both use {e(A['pkg'])}, so install commands are the same." if A["pkg"] == B["pkg"] else f"{e(an)} uses {e(A['pkg'])}; {e(bn)} uses {e(B['pkg'])}, so the commands you learn for one do not carry over."))
    L.append(f"<strong>Releases:</strong> " + (f"both follow {e(REL[A['rel']])}." if A["rel"] == B["rel"] else f"{e(an)} uses {e(REL[A['rel']])}; {e(bn)} uses {e(REL[B['rel']])}."))
    L.append(f"<strong>Memory:</strong> about {e(ram_txt(A['ram']))} for {e(an)} against about {e(ram_txt(B['ram']))} for {e(bn)} is a comfortable minimum for a desktop session.")
    ba, bb = "beginner" in A["tags"], "beginner" in B["tags"]
    easy = (f"Both suit beginners, so choose on look and feel." if ba and bb else f"{e(an)} is generally the easier first step." if ba else f"{e(bn)} is generally the easier first step." if bb else f"Neither is aimed at first-time users. If this is your first Linux system, try <a href=\"guide-choosing-a-linux-distribution.html\">a beginner-friendly distribution</a> first.")
    light = (f"{e(an)} asks for less memory." if A["ram"] < B["ram"] else f"{e(bn)} asks for less memory." if B["ram"] < A["ram"] else "They ask for a similar amount of memory.")
    return (f"<p>{e(an)} and {e(bn)} are often considered side by side. This page compares what each one is built on, how it looks, how software is installed, how updates arrive and what hardware it needs.</p>"
            f"<h2>Key differences</h2><ul>" + "".join(f"<li>{x}</li>" for x in L) + "</ul>"
            f"<h2>Choose {e(an)} if</h2><p>You are among the {e(A['aud'])}.</p><h2>Choose {e(bn)} if</h2><p>You are among the {e(B['aud'])}.</p>"
            f"<h2>Quick answers</h2><ul><li><strong>Which is easier for a beginner?</strong> {easy}</li><li><strong>Which suits older hardware?</strong> {light}</li><li><strong>Can I try both?</strong> Yes. Start each from a live USB drive without installing, or put both on one drive with <a href=\"guide-how-to-use-ventoy-multiboot-usb.html\">Ventoy</a>.</li></ul>"
            f"<p>Browse the {plink_(A['pre'], an + ' USB drive')} or the {plink_(B['pre'], bn + ' USB drive')}. Learn more: <a href=\"guide-what-is-{a}.html\">what is {e(an)}</a> and <a href=\"guide-what-is-{b}.html\">what is {e(bn)}</a>.</p>")

# slug|title|tag|intro|what to look for (;; separated)
USES = """windows-switchers|Windows switchers|winlike|Moving from Windows is easier when the new desktop looks and behaves in a familiar way. The systems below put a taskbar, a menu and window buttons where you expect them.|A desktop layout you recognise;;Good support for common hardware and drivers;;Simple software installation through a graphical store
mac-style-desktops|a Mac-style desktop|mac|Some people want the tidy, dock-based look of a Mac without buying one. These systems lean towards that clean, simple style.|A dock and a simple app launcher;;A curated app store;;Consistent, polished design across built-in apps
creators|video, audio and photo work|creative|Creative work needs good tools and enough memory. These systems are built or well suited for audio, video, graphics and photography.|Plenty of RAM and a fast drive;;Support for the graphics card you own;;Access to the editing programs you rely on
home-servers|a home server|server|A home server runs for months at a time, so long support and predictable updates matter more than new features.|Long support periods;;Small, steady updates;;Good documentation and a large community
advanced-users|advanced users|advanced|If you enjoy understanding every part of your system, these distributions give you control and expect you to use it.|Clear documentation, such as a detailed wiki;;Willingness to fix problems yourself;;A backup habit before big changes
stability|stability|stable|Some people want a computer that simply works for years. Choose a system with tested updates and a calm release schedule.|Long support periods;;Conservative software updates;;A large community for help
rolling-releases|rolling releases|rolling|A rolling release keeps software close to the latest versions without big upgrades. The trade-off is that you update often.|Regular, small updates;;A good rollback or snapshot plan;;Backups before large updates
kde-plasma|KDE Plasma|kde|KDE Plasma is known for its customisation. The systems below ship it as their main desktop or as a leading option.|A screen big enough to use the settings;;Enough RAM for a comfortable session;;A taste for adjusting things
gnome-desktop|the GNOME desktop|gnome|GNOME has a clean, focused design built around the Activities view. These systems ship it by default.|Comfort with a workflow that differs from Windows;;Optional extensions for extra features;;Reasonable RAM and a modern graphics chip
xfce-desktop|the Xfce desktop|xfce|Xfce is light, traditional and easy to adjust, which is why it is a favourite for older and modest computers.|A taskbar-style layout;;Low memory use;;Simple settings
rescue-and-repair|rescue and repair work|rescue|When a computer will not start, a small, quick live system on a USB drive lets you rescue files and fix problems.|Fast boot from USB;;Small downloads;;Tools for disks and files
immutable-systems|immutable systems|immutable|An immutable system keeps its core read-only so it is hard to break and simple to roll back.|Comfort with containers or Flatpak for extra software;;A rollback feature;;Clear update steps
2gb-ram-computers|computers with 2 GB of RAM|light|Two gigabytes is tight for a modern desktop, so lightweight systems make a big difference. A USB 3.0 drive also helps.|A light desktop such as Xfce or LXQt;;Few background services;;A browser that is not too heavy
low-end-hardware|slow or ageing hardware|light|Older processors and slow disks struggle with heavy desktops. The systems below keep the load small so the computer feels quicker.|A light desktop;;Low memory use;;Regular security updates"""
USE = [r.split("|") for r in USES.split("\n")]

def usecase(u, seen_names=None):
    slug, what, tag, intro, look = u
    picks = [d for d in D.values() if tag in d["tags"]][:8]
    li = "".join(f"<li><strong><a href=\"guide-what-is-{d['slug']}.html\">{e(d['name'])}</a></strong>: suits {e(d['aud'])}. {plink_(d['pre'], 'See the USB drive')}.</li>" for d in picks)
    lk = "".join(f"<li>{e(x)}</li>" for x in look.split(";;"))
    return (f"<p>{e(intro)}</p><h2>What to look for</h2><ul>{lk}</ul><h2>Good choices</h2><ol>{li}</ol>"
            f"<h2>How to decide</h2><p>Start two or three of these from a live USB drive and use each for twenty minutes. See <a href=\"guide-how-to-try-linux-without-installing.html\">how to try Linux without installing</a>, then read <a href=\"guide-choosing-a-linux-distribution.html\">how to choose a Linux distribution</a>.</p>"), f"Best Linux for {what}", f"Which Linux systems suit {what}? A short list of good choices with what to look for, who each suits, and how to try them from a USB drive."

# cmd|summary|syntax|examples (;; separated, ' => ' splits command from meaning)|tip
CMDS = """ls|lists the files and folders in a directory|ls [options] [folder]|ls -l => long list with sizes and dates;;ls -a => include hidden files that start with a dot;;ls -lh /media => readable sizes for a folder|Add -R to list subfolders as well.
cd|changes the folder you are working in|cd [folder]|cd Documents => move into Documents;;cd .. => go up one level;;cd ~ => jump to your home folder|Press Tab to complete folder names so you type less.
pwd|prints the full path of the folder you are in|pwd|pwd => shows something like /home/yourname/Documents|Use it whenever you are unsure where you are.
cp|copies files and folders|cp [options] source destination|cp notes.txt backup.txt => copy a file;;cp -r photos photos-backup => copy a folder and its contents|Add -i to be asked before overwriting an existing file.
mv|moves or renames files and folders|mv source destination|mv old.txt new.txt => rename a file;;mv report.pdf ~/Documents => move a file|There is no separate rename command, because moving to a new name is renaming.
rm|deletes files and folders permanently|rm [options] file|rm old.txt => delete one file;;rm -r oldfolder => delete a folder and everything in it|rm has no recycle bin. Check the name twice, and avoid running rm -rf with sudo unless you are certain of the path.
mkdir|creates a new folder|mkdir [options] name|mkdir projects => make a folder;;mkdir -p projects/2026/notes => make nested folders in one go|The -p option also stops an error if the folder already exists.
touch|creates an empty file or updates a file's timestamp|touch filename|touch notes.txt => create an empty file|It is a quick way to make files for testing other commands.
cat|prints the contents of a file|cat file|cat /etc/os-release => shows which distribution you are running;;cat a.txt b.txt > all.txt => join two files|For long files, use less so the text does not scroll past.
less|lets you read a long file one screen at a time|less file|less /var/log/syslog => scroll with the arrow keys and search with /|Press q to quit.
head|shows the first lines of a file|head [-n count] file|head -n 5 notes.txt => the first five lines|Its partner is tail, which shows the end of a file.
tail|shows the last lines of a file and can follow it live|tail [-n count] file|tail -n 20 log.txt => the last 20 lines;;tail -f log.txt => watch new lines as they arrive|Press Ctrl+C to stop following.
grep|searches text for lines that match a pattern|grep [options] pattern file|grep error log.txt => lines containing the word error;;grep -i -r "usb" /etc => case-insensitive search through a folder|You can pipe other commands into it, for example lsusb | grep SanDisk.
find|searches for files by name, type, size or date|find folder [tests]|find ~ -name "*.iso" => find ISO files in your home folder;;find . -size +1G => files larger than 1 GB|Searching from / can be slow, so start from a narrower folder.
chmod|changes who can read, write or run a file|chmod [mode] file|chmod +x script.sh => make a script runnable;;chmod 644 notes.txt => owner reads and writes, others read|In numeric modes, read is 4, write is 2 and execute is 1.
chown|changes the owner of a file or folder|sudo chown user:group file|sudo chown alex:alex notes.txt => give the file to alex|It needs sudo because only an administrator can hand files to another user.
sudo|runs one command with administrator rights|sudo command|sudo apt update => run a package update as administrator|Only use it for commands you understand, because it can change anything on the system.
df|shows how much space is used on each mounted drive|df [-h]|df -h => sizes in readable units|Look at the Use% column to spot a drive that is filling up.
du|shows how much space files and folders use|du [options] folder|du -sh ~/Downloads => total size of a folder;;du -h --max-depth=1 ~ => size of each folder in your home folder|Pipe the output into sort -h to find the largest folders.
free|shows memory (RAM) use|free -h|free -h => totals in readable units|The available column is the best guide to what programs can still use.
top|shows running processes and processor and memory use live|top|top => a live list that refreshes every few seconds|Press q to quit, M to sort by memory and P to sort by processor use.
ps|lists running processes at one moment|ps aux|ps aux | grep firefox => find a program's process|The second column is the process ID you give to kill.
kill|stops a process by its ID|kill [signal] pid|kill 1234 => ask the process to stop politely;;kill -9 1234 => force it to stop|Try it without -9 first, so the program gets a chance to save its work.
ping|tests whether another computer can be reached|ping host|ping -c 4 example.com => send four test packets|If ping works by IP address but not by name, the problem is usually DNS.
ssh|opens a secure session on another computer|ssh user@host|ssh alex@192.168.1.20 => log in to a machine on your network|The first connection asks you to confirm the other computer's fingerprint.
scp|copies files securely between computers over SSH|scp source destination|scp notes.txt alex@192.168.1.20:/home/alex/ => send a file to another computer|Add -r to copy whole folders.
tar|packs and unpacks archive files|tar [options] archive|tar -czf backup.tar.gz Documents => create a compressed archive;;tar -xzf backup.tar.gz => extract it|Remember the letters: c create, x extract, z gzip and f file name.
curl|transfers data from or to a web address|curl [options] url|curl -I https://example.com => show the response headers;;curl -O https://example.com/file.zip => download a file|Add -L to follow redirects.
wget|downloads files from the web and can resume them|wget [options] url|wget https://example.com/file.iso => download a file;;wget -c https://example.com/file.iso => continue an interrupted download|The -c option is handy for large ISO downloads on a weak connection.
nano|is a beginner-friendly text editor for the terminal|nano file|nano notes.txt => edit a file; Ctrl+O saves and Ctrl+X exits|The shortcuts are listed along the bottom of the screen.
man|shows the manual page for a command|man command|man ls => read about ls, then press q to leave|Type /word inside a manual to search for a word.
history|lists the commands you have run|history|history | grep apt => find earlier apt commands|Press Ctrl+R to search previous commands as you type.
uname|prints details about the running kernel and system|uname [-a]|uname -r => the kernel version;;uname -m => the architecture, such as x86_64|It is useful when you are choosing the right ISO or driver.
lsblk|lists disks and partitions as a tree|lsblk|lsblk => shows drives such as sda and sdb with sizes and mount points|Run it before writing to a USB drive to be sure you pick the right device.
dd|copies raw data between files and devices, and is often used to write an ISO to USB|sudo dd if=input of=output bs=4M status=progress|sudo dd if=linux.iso of=/dev/sdX bs=4M status=progress => write an ISO to a USB device|dd overwrites whatever device you name without asking. Check with lsblk first, and use a graphical tool if you are unsure.
mount|attaches a drive or partition to a folder so you can use it|sudo mount device folder|sudo mount /dev/sdb1 /mnt => open a USB partition at /mnt|Desktop systems mount USB drives for you. Manual mounting is for minimal systems.
umount|detaches a mounted drive safely (the command is spelled umount)|sudo umount folder-or-device|sudo umount /mnt => detach the drive so it is safe to remove|Always unmount before unplugging to avoid losing data.
lsusb|lists the USB devices connected to the computer|lsusb|lsusb => shows attached USB devices with their IDs|It helps you check whether the system can see your drive or adapter.
lspci|lists PCI devices such as graphics and network cards|lspci|lspci -k => shows which driver each device is using|It is handy for Wi-Fi and graphics driver troubleshooting.
whoami|prints the user name you are logged in as|whoami|whoami => prints your user name|It is useful in scripts and when checking sudo.
echo|prints text or the value of a variable|echo text|echo $HOME => print the path of your home folder;;echo hello > hi.txt => write text to a file|A single > replaces a file's contents, while >> adds to the end."""

def command(row):
    cmd, summ, syn, ex, tip = [x.replace("\x00", "|") for x in row.replace(" | ", " \x00 ").split("|")]
    exl = "".join(f"<li><code>{e(x.split(' => ')[0])}</code>: {e(x.split(' => ')[1])}</li>" for x in ex.split(";;"))
    return (f"<p>The <code>{e(cmd)}</code> command {e(summ)}. It is one of the most useful commands for anyone using a live USB drive or a fresh Linux install.</p>"
            f"<h2>Syntax</h2><pre>{e(syn)}</pre><h2>Examples</h2><ul>{exl}</ul><h2>Tip</h2><p>{e(tip)}</p>"
            f"<h2>Keep learning</h2><p>New to the terminal? Start with <a href=\"guide-how-to-use-the-linux-terminal-basics.html\">Linux terminal basics</a>. You can try every command safely from a live session: see <a href=\"guide-how-to-try-linux-without-installing.html\">how to try Linux without installing it</a>. Run <code>man {e(cmd)}</code> in a terminal for the full manual.</p>")

# slug|title|what it is|why it matters when using a bootable USB|related page
TERMS = """what-is-an-iso-file|What is an ISO file?|An ISO file is a single file that holds an exact copy of a disc's contents, including its file system. Operating system downloads usually come in this form.|Most tools write the ISO to a USB drive to make it bootable. With Ventoy, you copy the ISO onto a drive that Ventoy has prepared. Either way, check the download first with a checksum.|guide-how-to-create-a-bootable-usb-drive.html
what-is-a-live-usb|What is a live USB drive?|A live USB drive holds a complete operating system that starts from the drive instead of your hard disk. Your installed system is not touched.|It lets you test a system, repair a computer or recover files with no commitment. Changes usually disappear on shutdown unless the drive has persistence.|guide-what-is-persistence-on-a-live-usb.html
what-is-a-bootloader-grub|What is a bootloader (GRUB)?|A bootloader is the small program that runs after the firmware starts and loads the operating system. GRUB is the one most Linux systems use.|If you dual boot or reinstall Windows, the bootloader can be replaced or overwritten, which is a common reason a computer stops showing its boot menu.|guide-how-to-dual-boot-linux-and-windows.html
what-is-the-efi-system-partition|What is the EFI System Partition?|The EFI System Partition (ESP) is a small FAT32 partition on UEFI computers that stores bootloader files for the systems installed on the disk.|When you install Linux next to Windows, the installer usually reuses the existing ESP. Deleting it by mistake can stop every system on that disk from starting.|guide-how-to-partition-a-disk-for-linux.html
what-is-gpt-vs-mbr|GPT vs MBR: what is the difference?|GPT and MBR are two ways of storing a disk's partition table. MBR is older and limited to four main partitions and 2 TB disks; GPT supports far larger disks and many more partitions.|UEFI computers normally boot from GPT disks, while older BIOS computers use MBR. A mismatch is a common reason a USB drive will not boot.|guide-uefi-vs-legacy-bios-boot.html
what-is-swap-space|What is swap space?|Swap is disk space the system can use as overflow when it runs short of memory. It can be a partition or a file.|A small swap area gives older computers a safety net, and hibernation needs swap at least as large as your RAM. Installers usually offer to create it for you.|guide-how-to-partition-a-disk-for-linux.html
what-is-the-ext4-file-system|What is the ext4 file system?|ext4 is the default file system on many Linux distributions. It is mature, fast and reliable, with journaling that protects against corruption after a crash.|When an installer asks how to format the Linux partition, ext4 is the safe default choice unless you have a specific reason to pick something else.|guide-how-to-partition-a-disk-for-linux.html
what-is-btrfs|What is Btrfs?|Btrfs is a modern Linux file system with snapshots, compression and built-in checks for data errors.|Snapshots let you roll back after a bad update, which is why some distributions such as openSUSE use it by default. It is a good option if you want easy rollbacks.|guide-how-to-update-linux.html
what-is-zfs|What is ZFS?|ZFS is a file system and volume manager known for data integrity, snapshots and easy storage pooling. It is common on FreeBSD and used by some Linux users.|It needs more memory than ext4 and is usually chosen for servers and storage rather than a basic desktop. Some installers offer it as an advanced option.|guide-how-to-make-a-linux-home-server.html
what-is-fat32-exfat-and-ntfs|FAT32, exFAT and NTFS compared|These are three file systems you meet on USB drives. FAT32 works almost everywhere but cannot store a single file larger than 4 GB. exFAT removes that limit. NTFS is the main Windows file system.|A UEFI boot drive normally uses FAT32. A large ISO may not fit on it, which is why many tools split files or use a different layout.|guide-how-to-create-a-bootable-usb-drive.html
what-is-flatpak|What is Flatpak?|Flatpak is a way of packaging desktop applications so they run the same on many distributions. Each app is kept in a sandbox with its own set of libraries.|It gives you newer apps on a stable system and works well on immutable distributions. Flathub is the main place to find Flatpak apps.|guide-how-to-install-software-on-linux.html
what-is-snap|What is a Snap package?|A Snap is a self-contained software package developed by Canonical, the company behind Ubuntu. It bundles an app with what it needs and updates itself.|Ubuntu uses Snap for some apps such as its browser. Snaps can start slower than traditional packages, but they update automatically.|guide-how-to-install-software-on-linux.html
what-is-an-appimage|What is an AppImage?|An AppImage is a single file that contains an application. You make it executable and run it, with no installation.|It is useful on a live USB drive because you can keep the app file beside your documents and run it on many distributions.|guide-how-to-install-software-on-linux.html
what-is-a-package-manager|What is a package manager?|A package manager installs, updates and removes software for you, and takes care of the other pieces each program depends on. Examples include apt, dnf and pacman.|Knowing which package manager your distribution uses tells you which commands to run, and which guides apply to you.|guide-how-to-install-software-on-linux.html
what-is-a-software-repository|What is a software repository?|A repository is an online library of software packages that your package manager downloads from. Packages are signed so the system can check they are genuine.|Using the official repositories is the safest way to get software, because the packages are tested and updated for your system.|guide-is-linux-safe-to-use.html
what-is-the-linux-kernel|What is the Linux kernel?|The kernel is the core of the operating system. It talks to your hardware and manages memory, processes and drivers.|Newer kernels support newer hardware. If your Wi-Fi or graphics card is not working on a live USB drive, a distribution with a newer kernel may help.|guide-how-to-set-up-wifi-and-drivers-on-linux.html
what-is-a-window-manager|What is a window manager?|A window manager draws and controls the windows on your screen, including their borders, movement and layout. A full desktop environment adds a panel, settings and apps on top.|Light systems often use a window manager alone, such as Openbox or IceWM, which saves memory on older computers.|guide-what-is-gnome-kde-xfce-cinnamon.html
what-is-wayland-vs-x11|Wayland vs X11: what is the difference?|X11 is the long-standing system that draws graphics on Linux desktops. Wayland is its modern replacement, with a simpler design and better handling of modern screens.|Most big desktops now default to Wayland. If a program misbehaves, many systems let you pick an X11 session at the login screen.|guide-what-is-gnome-kde-xfce-cinnamon.html
what-is-systemd|What is systemd?|systemd is the service manager that starts and supervises programs when the system boots on most Linux distributions. Some systems, such as Devuan and antiX, use alternatives.|If you see commands like systemctl, they control services under systemd. Knowing this helps you follow troubleshooting guides.|guide-how-to-use-the-linux-terminal-basics.html
what-is-a-rolling-release|What is a rolling release?|A rolling release distribution updates software continuously instead of waiting for big version releases. Arch Linux and openSUSE Tumbleweed are examples.|You never need a major upgrade, but you do need to update regularly and keep backups.|guide-lts-vs-regular-releases.html
what-is-an-immutable-distribution|What is an immutable distribution?|An immutable distribution keeps its core system read-only. Updates are applied as a whole and can be rolled back if something goes wrong.|It is harder to break and works well for people who want a stable, low-maintenance system.|guide-what-is-a-linux-distribution.html
what-is-a-sha256-checksum|What is a SHA-256 checksum?|A SHA-256 checksum is a short fingerprint calculated from a file. If even one byte changes, the fingerprint changes completely.|Compare the checksum of your downloaded ISO with the one published by the project to confirm that the download is complete and unchanged. Run sha256sum file.iso to calculate it.|guide-is-linux-safe-to-use.html
what-is-sudo-and-root|What are sudo and root?|Root is the administrator account that can change anything on the system. sudo lets a normal user run one command with root rights after typing their own password.|Installing software and changing system settings needs sudo. Avoid logging in as root for daily use.|guide-how-to-use-the-linux-terminal-basics.html
what-is-the-home-directory|What is the home directory?|Your home directory, usually /home/yourname, is where your documents, downloads, pictures and settings live. The shortcut ~ stands for it.|Keeping /home on its own partition makes it easier to reinstall without losing files. Back it up before you install.|guide-how-to-back-up-before-installing-linux.html
what-is-file-permissions|How Linux file permissions work|Each file has permissions for its owner, its group and everyone else. Each group can be allowed to read, write or execute.|If you see Permission denied, the file is probably owned by another user. Use ls -l to look, and chmod or sudo to fix it.|guide-how-to-use-the-linux-terminal-basics.html
what-is-bash-and-the-shell|What is Bash and the shell?|The shell is the program that reads the commands you type in a terminal. Bash is the most common shell on Linux.|Knowing a little Bash lets you follow most guides and fix problems quickly, even from a live USB drive.|guide-how-to-use-the-linux-terminal-basics.html
what-are-hidden-files-and-dotfiles|What are hidden files and dotfiles?|Files whose names start with a dot, such as .bashrc, are hidden by default. They store settings for your programs and your desktop.|Back up your dotfiles to keep your settings across reinstalls. In a file manager, press Ctrl+H to show or hide them.|guide-how-to-back-up-before-installing-linux.html
what-is-mounting|What does mounting a drive mean?|Mounting attaches a drive or partition to a folder so its files appear in the file system. Unmounting detaches it safely.|Desktop systems mount USB drives automatically. Always eject before unplugging to prevent data loss.|guide-how-to-safely-eject-and-store-your-usb.html"""

def term(row):
    slug, title, what, why, rel = row.split("|")
    rel_title = "Read more"
    return (f"<p>{e(what)}</p><h2>Why it matters when you use a bootable USB drive</h2><p>{e(why)}</p>"
            f"<h2>Related</h2><ul><li><a href=\"{rel}\">{rel_title} on this topic</a></li><li><a href=\"guide-what-is-a-bootable-usb-drive.html\">What is a bootable USB drive?</a></li><li><a href=\"guide-choosing-a-linux-distribution.html\">How to choose a Linux distribution</a></li></ul>")

def plink_(prefix, text):
    return _plink(prefix, text)
_plink = lambda p, t: e(t)

def more(plink, seen):
    global _plink
    _plink = plink
    out, used = [], set(seen)
    def add(slug, title, desc, body):
        if slug in used: return
        used.add(slug); out.append((slug, title, trim(desc, 158), body))
    pairs, sp = [], set()
    for p in PAIRS:
        if p[0] in D and p[1] in D and p[0] != p[1] and frozenset(p) not in sp: sp.add(frozenset(p)); pairs.append(p)
    for d in D.values():
        n = d["name"]; t = f"What is {n}? Who it is for"
        add(f"what-is-{d['slug']}", t if len(t) <= 48 else f"What is {n}?", f"What {n} is, what it is built on, which desktop and tools it uses, who it suits and what to consider before you try it from a USB drive.", profile(d, pairs))
    for d in D.values():
        n = d["name"]; t = f"How to install {n} from a USB drive"
        add(inst_slug(d), t if len(t) <= 48 else f"Install {n} from USB", f"Step-by-step help to install {n} from a bootable USB drive: before you begin, install steps, updating afterwards and fixes if it will not start.", install(d))
    for a, b in pairs:
        t = f"{D[a]['name']} vs {D[b]['name']}: how they differ"
        add(f"{a}-vs-{b}", t if len(t) <= 48 else f"{D[a]['name']} vs {D[b]['name']}", f"{D[a]['name']} vs {D[b]['name']} side by side: foundation, desktop, software tools, updates and memory needs, plus who should choose each.", compare(a, b))
    for u in USE:
        body, title, desc = usecase(u)
        add(f"best-linux-for-{u[0]}", title if len(title) <= 48 else title[:48].rsplit(" ", 1)[0], desc, body)
    for row in CMDS.split("\n"):
        c = row.split("|")[0]
        add(f"linux-{c}-command", f"The {c} command in Linux explained", f"What the {c} command does in Linux, its syntax, practical examples and a tip, written in plain English for people using a live USB drive.", command(row))
    for row in TERMS.split("\n"):
        f = row.split("|")
        add(f[0], f[1], f"{f[1]} A plain-English explanation and why it matters when you create or use a bootable USB drive.", term(row))
    return out
