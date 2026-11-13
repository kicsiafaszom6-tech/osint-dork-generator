#!/usr/bin/env python3
-- coding: utf-8 --
"""
The OSINT Vault — Google Dork Generator (CLI/TUI) v2.0
Cross-platform: Termux (Android), Windows, Linux, macOS
No external dependencies — only Python 3.7+ stdlib.

Sources:
• Stodelov, D. & Miloslavskaya, N. (2022). Open Source INTeLLigence Tools.
Procedia Computer Science 213, 83-88.
• Khera, V., Prasad, A. R., & Kwanoran, S. (2024).
Open Source Intelligence (OSINT) - A Practical Introduction: A Field Manual.
River Publishers.
• OSINT Vault (Nicole Hurey) — dork methodology.
"""
import sys, os, platform, shutil, subprocess, webbrowser, urllib.parse
from typing import List

try:
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
except Exception:
pass
if os.name == 'nt':
os.system('')

── Colors ─────────────────────────────────────────────
class C:
RESET='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
CYAN='\033[96m'; BLUE='\033[94m'; GREEN='\033[92m'
YELLOW='\033[93m'; RED='\033[91m'; GRAY='\033[90m'

def _colors_ok():
if os.environ.get('NO_COLOR'): return False
if not sys.stdout.isatty(): return False
if os.name == 'nt':
try:
if sys.getwindowsversion().major < 10: return False
except Exception: return False
return True

if not colors_ok():
for k in list(dir(C)):
if not k.startswith(''):
setattr(C, k, '')

══════════════════════════════════════════════════════
DATA: Dork Library (OSINT Vault)
══════════════════════════════════════════════════════
CATEGORIES = [
("Identity", "Személyazonosság", [
('site:facebook.com "email address"', "E-mail címek keresése Facebookon"),
('site:linkedin.com intitle:"at [Company Name]"', "Cégnévhez kötődő LinkedIn-profilok"),
('site:twitter.com "contact me at" email', "Kapcsolatfelvételi e-mail címek Twitteren"),
]),
("Document", "Dokumentumok", [
('filetype:pdf "confidential"', "Bizalmas PDF-ek"),
('site:.gov filetype:xlsx "internal use only"', "Kormányzati belső használatú Excel"),
('filetype:docx "draft" "do not distribute"', "Piszkozat Word-dokumentumok"),
('filetype:pptx intitle:"Q4 report" site:.com', "Negyedéves jelentések"),
('filetype:csv "employee" "salary"', "Alkalmazotti fizetési adatok"),
 ]),
("Infra", "Infrastruktúra", [
('intitle:"index of" "backup" site:example.com', "Biztonsági mentések"),
('inurl:admin intitle:"login" -site:google.com', "Admin bejelentkező panelek"),
('inurl:wp-config.php filetype:txt', "WordPress konfigurációk"),
('intitle:"phpMyAdmin" inurl:phpmyadmin', "phpMyAdmin felületek"),
('inurl:"/wp-content/uploads/" filetype:log', "WP feltöltési naplók"),
('intitle:"dashboard" inurl:8080 OR inurl:8443', "Irányítópultok"),
 ]),
("Exposure", "Kitettség / Kiszivárgás", [
('site:pastebin.com "password" "username"', "Jelszavak Pastebinen"),
('site:github.com "api_key" OR "secret_key" filename:.env', "API-kulcsok GitHubon"),
('filetype:sql "INSERT INTO" "password"', "SQL-dumpok"),
('intext:"BEGIN RSA PRIVATE KEY" filetype:txt', "RSA privát kulcsok"),
('site:trello.com "password" OR "token" "private"', "Trello-táblák"),
('site:.gov filetype:pdf "court order"', "Bírósági végzések"),
 ]),
("Records", "Nyilvántartások", [
('site:.gov "property tax" filetype:csv', "Ingatlanadó-adatok"),
('site:.edu "staff directory" filetype:pdf', "Egyetemi névsorok"),
('site:.gov "annual report" filetype:pdf 2024', "Éves jelentések"),
 ]),
("Cloud", "Felhő", [
('site:s3.amazonaws.com filetype:pdf OR filetype:xlsx', "Nyilvános S3 bucketek"),
('site:storage.googleapis.com "backup"', "Google Cloud mentések"),
('site:blob.core.windows.net filetype:docx', "Azure Blob"),
('inurl:s3.amazonaws.com "AllUsers" OR "public"', "Nyilvános S3"),
('site:digitaloceanspaces.com intitle:"index of"', "DigitalOcean Spaces"),
 ]),
]

OPERATORS = [
("site:", 'site:example.com', "Domainre/aldomainre korlátoz"),
("filetype:", 'filetype:pdf "confidential"', "Fájltípusra szűr"),
("intitle:", 'intitle:"index of"', "Címben keres"),
("inurl:", 'inurl:admin', "URL-ben keres"),
('"exact phrase"', '"internal use only"', "Pontos kifejezés"),
("-", 'password -reset', "Kizárás"),
("OR / |", 'intitle:password OR inurl:login', "VAGY kapcsolat"),
("cache:", 'cache:example.com', "Gyorsítótárazott verzió"),
("related:", 'related:example.com', "Hasonló oldalak"),
("*", '"the * most wanted"', "Helyettesítő karakter"),
]

USECASES = [
"Kitett dokumentumok és fájltárak felderítése.",
"Admin panelek, bejelentkező portálok megtalálása.",
"Infrastruktúra feltérképezése (aldomainek, staging).",
"Nyilvános hivatkozások harmadik féltől származó domaineken.",
"Kitett hitelesítő adatok paste oldalakon, repókban.",
"Törölt/módosított oldalak gyorsítótárazott verziói.",
"Személyzeti hivatkozások, alkalmazotti névsorok.",
"Felhőtárhely-konfigurációs hibák felfedezése.",
]

WORKFLOW = [
("Precíz lekérdezés a Generatorral", "Válaszd ki a célt, az eszköz kezeli a szintaxist."),
("Futtatás a Google-ben", "Illeszd be a generált lekérdezést."),
("Továbbítás Multi-Search Launcherrel", "theosintvault.io/multi-search-launcher.html"),
("Bizonyíték rögzítése Bookmarklet Library-vel", "theosintvault.io/osint-bookmarklet-library.html"),
("Dokumentálás Report Composerben", "theosintvault.io/report-composer.html"),
]

METHODOLOGY = [
("01 · SOURCING", "Forrásolás", "Saját, valós munkában használt, vagy megbízható gyakorló által ajánlott eszközök. Nincs tömeges import."),
("02 · TESTING", "Tesztelés", "Ismert teszt-célon futtatás: visszaadja-e amit állít, nincs-e rejtett fizetés, nem gyűjti-e a lekérdezést."),
("03 · OMERTÀ", "Verdiktek", "Confirmed = pozitív egyezés. Uncertain = valós jelzés, nem elég. Manual = kézi ellenőrzés."),
("04 · OSINT GRID", "Hivatalos források", "Kormányzati és köznyilvántartási források, működő URL ellenőrzéssel."),
("05 · MONEY", "Pénz", "Nincs szponzorált elhelyezés. A rangsor nem eladó."),
("06 · PRIVACY", "Adatvédelem", "Nincs harmadik féltől származó analitika. Minden kliensoldalon fut."),
("07 · CORRECTIONS", "Javítások", "Hibás link/állítás jelezhető. Ellenőrzött javítás a következő körben."),
]

══════════════════════════════════════════════════════
DATA: Stodelov & Miloslavskaya (2022)
══════════════════════════════════════════════════════
PAPER_CITATION = ("Stodelov, D., Miloslavskaya, N. (2022). Open Source INTeLLigence Tools. "
"Procedia Computer Science 213, 83-88. (BICA 2022, MEPhI Moscow)")
PAPER_URL = "https://www.sciencedirect.com/science/article/pii/S187705092201732X"

MITRE_RECON = [
("Active scanning", ["IP addresses blocks' scanning", "Vulnerability search"]),
("Attacked hosts' information collection", ["Hardware", "Software", "Firmware", "Hosts' configuration"]),
("Attacked users' information collection", ["Credentials", "Emails", "Employers' names"]),
("Network infrastructure information collection",
["Domain properties", "DNS", "Trusted networks", "Network topology", "IP addresses", "Network security tools"]),
("Organization's information collection",
["Physical location", "Counterparties", "Production cycle", "Employers' business roles"]),
("Spear phishing", ["via third-party services", "with an attachment", "with a link"]),
("Information collection from closed sources", ["Threat Intelligence", "Purchase of technical data"]),
("Information collection from open sources",
["DNS records", "WHOIS", "Digital certificates", "Content delivery networks", "Open databases with search results"]),
("Search in open web sites/domains", ["Social networks", "Search engines"]),
("Web site search", []),
]

OSINT_FRAMEWORK = [
"Username", "Email Address", "Domain Name", "IP Address", "Images / Videos / Docs",
"Social Networks", "Instant Messaging", "People Search Engines", "Dating",
"Telephone Numbers", "Public Records", "Business Records", "Transportation",
"Geolocation Tools / Maps", "Search Engines", "Forums / Blogs / IRC", "Archives",
"Language Translation", "Metadata", "Mobile Emulation", "Terrorism", "Dark Web",
"Digital Currency", "Classifieds", "Encoding / Decoding", "Tools",
"Malicious File Analysis", "Exploits & Advisories", "Threat Intelligence", "OpSec",
"Documentation", "Training",
]

OSINT_TOOLS = [
("Shodan Search Engine", "https://www.shodan.io", "Infra / Recon",
"Domain, IP, port, device és IT-infrastruktúra részletek."),
("DomainTools WHOIS", "https://whois.domaintools.com", "Infra / Recon",
"Domain és IP részletes adatok (WHOIS, DNS)."),
("ZoomEye", "https://www.zoomeye.org", "Infra / Recon",
"Kívülről elérhető eszközök, OS + verzió, geolokáció."),
("Have I Been Pwned", "https://haveibeenpwned.com", "Credentials",
"Fiókok, jelszavak, telefonszámok ellenőrzése."),
("Dehashed", "https://www.dehashed.com", "Credentials",
"Fiókok, jelszavak, jelszó-hashek."),
("MaxMind", "https://www.maxmind.com", "Reputation",
"E-mail reputáció, IP geolokáció, VPN/proxy."),
("Abuse.ch", "https://abuse.ch", "Threat Intel",
"Botnet-interakció, kompromittálódási azonosítók."),
("AlienVault OTX", "https://otx.alienvault.com", "Threat Intel",
"Kompromittálódási azonosítók, botnet-kapcsolatok."),
("GreyNoise", "https://www.greynoise.io", "Threat Intel",
"Intranet-eszközök botnet-interakciójának detektálása."),
("Wigle", "https://wigle.net", "Wireless",
"Vezeték nélküli hálózatok keresése és lokalizálása."),
("Hunter", "https://hunter.io", "Identity / Email",
"Erőforrások céges e-mail regisztrációval."),
("Master Name", "https://www.mastername.ru", "Domain Defense",
"A célhoz hasonló szabad/foglalt domainek."),
("Website Informer", "https://website.informer.com", "Infra / Recon",
"Webhely-részletek: kapcsolattartók, IP-címek."),
("Cert Spotter", "https://sslmate.com/certspotter", "Certificates",
"Tanúsítvány-ellenőrzés: helyettesítés, visszavonás."),
("VirusTotal", "https://www.virustotal.com", "File / Link",
"Adathalász linkek és fájlok ellenőrzése."),
("SpiderFoot", "https://www.spiderfoot.net", "Automation",
"Cél-domain/IP keresése: szolgáltatások, szoftververziók."),
("Maltego", "https://www.maltego.com", "Automation",
"Automatizált OSINT-gráf építés."),
("theHarvester", "https://www.kali.org/tools/theharvester", "Automation",
"E-mailek, subdomainek, hostok, alkalmazotti nevek."),
]

PAPER_RECS = [
"IDPS, firewall, SIEM beállítása intranet-szkennelés detektálására.",
"Rendszeres intranet sebezhetőség-szkennelés.",
"Intranet-topológia és IT-infrastruktúra rendszeres elemzése.",
"Többfaktoros hitelesítés (MFA) + jelszókísérletek korlátozása.",
"E-mail biztonság + URL-validáció (rövidített linkek is).",
"Kívülről elérhető információ minimalizálása.",
"Megtévesztő rendszer üzemeltetése.",
"Social media feltöltések kontrollja/szűrése.",
"A sajáthoz hasonló domainek lefoglalása.",
"Internet-erőforrások reputációjának figyelése.",
"Folyamatos munkatárs-képzés social engineering ellen.",
]

══════════════════════════════════════════════════════
DATA: Khera, Prasad & Kwanoran (2024)
══════════════════════════════════════════════════════
BOOK_INFO = {
"title": "Open Source Intelligence (OSINT) – A Practical Introduction: A Field Manual",
"authors": "Varin Khera, Anand R. Prasad, Suksit Kwanoran",
"publisher": "River Publishers (Routledge/Taylor & Francis)",
"year": 2024,
"isbn": "978-87-7004-717-3 (pb) · 978-87-0004-719-7 (online) · 978-87-9004-718-0 (ebook)",
"chapters": 12,
}
BOOK_CHAPTERS = [
"1. Introduction to Threat",
"2. Introduction to Open Source Intelligence (OSINT)",
"3. Online Tracking and Behavioral Profiling",
"4. Hiding Your Traces When Conducting Online Investigations",
"5. Open Source Intelligence (OSINT): A Practical Example",
"6. Using AI in OSINT Research",
"7. Social Media Intelligence (SOCMINT)",
"8. The Web Layers: Introduction to Surface, Deep and Darknet",
"9. Darkweb and Internet Anonymity: Exploring the Hidden Internet",
"10. Introduction to Digital Forensics",
"11. OSINT for Digital Forensics Investigations",
"12. Data Protection and Cybersecurity Laws for the Asia Pacific Region",
]

TI_TYPES = [
("Strategic", "Board / felső vezetés", "Hosszú távú: fenyegetések, geopolitika, megfelelés (HIPAA, PCI DSS)."),
("Tactical", "Architect / admin", "TTP-k, malware-családok, phishing, exploit-kitek."),
("Operational", "Defenders", "Konkrét támadás: támadóprofil, motiváció, idővonal."),
("Technical", "SOC / IR", "IOC-k: rosszindulatú IP-k, hash-ek, domainek."),
]

TI_LIFECYCLE = [
("1. Planning", "Intelligence requirements, risk profile, védendő assetek."),
("2. Collection", "Logok, ingyenes TI feedek (OTX, Phishtank), kereskedelmi platformok, OSINT, darknet."),
("3. Processing", "Nyers adat → strukturált információ."),
("4. Analysis", "Malware-elemzés, IOC-elemzés, emberi interpretáció."),
("5. Dissemination", "Jelentés stakeholdereknek."),
("6. Feedback", "Hiányosságok azonosítása, következő kör javítása."),
]

PYRAMID_OF_PAIN = [
("Hash value", "Könnyen módosítható — legalacsonyabb érték."),
("IP address", "Geolokáció — VPN/TOR mögé rejthető."),
("Domain name", "C2 / phishing infrastruktúra."),
("Network/host artifacts", "Logok, forgalmi minták, konfig."),
("Tools", "Exploit-kitek, Mimikatz."),
("TTP", "Legnehezebb megkerülni."),
]

KILL_CHAIN = ["Reconnaissance", "Weaponization", "Delivery", "Exploitation",
"Installation", "Command and Control", "Action on Objectives"]

TI_SHARING = [
("STIX", "Structured Threat Information Expression — fenyegetés-adatok strukturált leírása."),
("CybOX", "Cyber Observable Expression — megfigyelhető kiber-adatok leírása."),
("TAXII", "Trusted Automated Exchange of Indicator Information — biztonságos IOC-csere."),
]

TI_FREE_SOURCES = [
("AlienVault OTX", "https://otx.alienvault.com", "Nyílt fenyegetés-csere platform."),
("Phishtank", "https://www.phishtank.com", "Adathalász URL-ek gyűjteménye."),
("OpenCTI", "https://github.com/OpenCTI-Platform/opencti", "TI-vizualizáció (open source)."),
("AbuseIPDB", "https://www.abuseipdb.com", "Rosszindulatú IP-k jelentése."),
("Binary Defense Artillery", "https://www.binarydefense.com/banlist.txt", "Ingyenes TI feed."),
("Mimikatz", "https://github.com/gentilkiwi/mimikatz", "Hitelesítő adat kinyerése (támadói eszköz)."),
]

TRACKING_METHODS = [
("IP Address", "Geolokáció, szolgáltató, szervezeti hovatartozás."),
("Cookies", "Session-, tracking- és third-party cookie-k."),
("ETag", "Cache-alapú követés — cookie-törlés után is működik."),
("Browser Fingerprinting", "User-agent, képernyő, fontok, pluginok, canvas."),
]

TRACKING_COUNTERMEASURES = [
("OS védelem", "Frissítés, full-disk encryption, elkülönített VM."),
("Biztonságos böngészés", "HTTPS-only, privát mód, NoScript, uBlock, DoH."),
("Anti-tracking", "Cookie-törlés, Privacy Badger, Canvas Blocker, UA-switcher."),
("Anonimitás", "TOR Browser, VPN+TOR, Tails / Whonix."),
]

PRACTICAL_STEPS = [
("Technical Investigation", "WHOIS, DNS, IP, headerek, robots.txt, sitemap.xml."),
("Analytics and Tracking", "Google Analytics ID-k, Facebook Pixel (Bellingcat-módszer)."),
("Website History", "Wayback Machine, archive.today, Google cache."),
("Subdomain Discovery", "crt.sh, SecurityTrails, Sublist3r, Amass."),
("Infrastructure Types & Versions", "Shodan, Censys, ZoomEye."),
("Harvest Digital Files", "site:+filetype: dorkok, wget-mirror."),
("File Metadata", "EXIF, PDF, Office-metaadat."),
("Metadata Tools", "ExifTool, FOCA, Metagoofil, PDFinfo, mat2, Metadata2Go."),
]

METADATA_TOOLS = [
("ExifTool", "https://exiftool.org", "Legteljesebb metadata-kinyerő."),
("FOCA", "https://github.com/ElevenPaths/FOCA", "Metadata + hálózati topológia."),
("Metagoofil", "https://github.com/laramies/metagoofil", "Domain-ről dokumentum-metaadat."),
("PDFinfo", "https://poppler.freedesktop.org", "PDF-metaadat (poppler-utils)."),
("mat2", "https://0xacab.org/jvoisin/mat2", "Metadata eltávolítása (anonimizálás)."),
("Metadata2Go", "https://www.metadata2go.com", "Online metadata-viewer."),
]

AI_OSINT = [
("Data Collection & Scraping", "Automatizált adatgyűjtés weboldalakról, API-król."),
("Unstructured Text Analysis", "NLP: entitás-kinyerés, kapcsolatok."),
("Multimedia Analysis", "Kép/videóelemzés, AI-generált tartalom detektálása."),
("Content Summarization", "Hosszú szövegek automatikus összefoglalása."),
("Social Network Analysis", "Gráf-alapú kapcsolatfeltárás."),
]

SOCMINT = [
("Privacy issues", "Személyes adatok, GDPR-megfelelés, etikai korlátok."),
("OSINT roadmap", "Platform-specifikus lépések: FB, X, LinkedIn, Instagram, TikTok."),
("Eszközök", "Maltego, Sociallinks, Twint (archivált), Instaloader, Sherlock."),
]

WEB_LAYERS = [
("Surface Web", "Indexelt, keresőmotorokkal elérhető."),
("Deep Web", "Nem indexelt: adatbázisok, portálok, paywall-ok."),
("Darknet", "Csak speciális szoftverrel (TOR, I2P, Freenet)."),
]

TOR_SEARCH_ENGINES = [
("Ahmia", "https://ahmia.fi"),
("Torch", "http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion"),
("Haystack", "https://haystack.deepnet.id"),
("DarkSearch", "https://darksearch.io"),
("OnionLand", "https://onionlandsearchengine.com"),
]

FORENSICS_PROCESS = [
("1. Identification", "Digitális bizonyíték azonosítása."),
("2. Preservation", "Bizonyíték megőrzése — hash, write-blocker, chain of custody."),
("3. Analysis", "Adatok elemzése, idővonal, artefaktumok."),
("4. Reporting", "Szakértői jelentés, bírósági felhasználhatóság."),
]

OSINT_FOR_FORENSICS = [
("Individual Intelligence", "Személyek nyilvános adatainak gyűjtése."),
("Social Networking Sites", "Profilok, kapcsolatok, posztok, geolokáció."),
("File Metadata", "EXIF, PDF, Office — idő, hely, szerző, eszköz."),
("Darknet Credentials", "Szivárgott hitelesítő adatok keresése."),
]

LEGAL_APAC = [
("Singapore", "PDPA — Personal Data Protection Act (2012)."),
("Japan", "APPI — Act on Protection of Personal Information."),
("Vietnam", "Cybersecurity Law (2018) + Personal Data Protection Decree."),
("China", "PIPL — Personal Information Protection Law (2021)."),
("Thailand", "PDPA — Personal Data Protection Act (2019)."),
]

LEGAL_INTL = [
("APEC Privacy Framework", "https://www.apec.org/Publications/2017/08/APEC-Privacy-Framework-(2015)"),
("GDPR (EU)", "https://gdpr-info.eu"),
("UNCTAD adatvédelem", "https://unctad.org/page/data-protection-and-privacy-legislation-worldwide"),
]

══════════════════════════════════════════════════════
CLIPBOARD
══════════════════════════════════════════════════════
def copy_to_clipboard(text: str) -> bool:
try:
import pyperclip
pyperclip.copy(text)
return True
except Exception:
pass
s = platform.system()
try:
if s == "Windows":
try:
import tkinter as tk
r = tk.Tk(); r.withdraw()
r.clipboard_clear(); r.clipboard_append(text); r.update()
r.destroy()
return True
except Exception:
pass
p = subprocess.run("clip", input=text.encode("utf-8"), shell=True)
if p.returncode == 0: return True
elif s == "Darwin":
if subprocess.run("pbcopy", input=text.encode("utf-8")).returncode == 0:
return True
else:
for cmd in (["termux-clipboard-set"], ["wl-copy"],
["xclip", "-selection", "clipboard"],
["xsel", "--clipboard", "--input"]):
if shutil.which(cmd[0]):
try:
if subprocess.run(cmd, input=text.encode("utf-8")).returncode == 0:
return True
except Exception:
pass
except Exception:
pass
try:
import tkinter as tk
r = tk.Tk(); r.withdraw()
r.clipboard_clear(); r.clipboard_append(text); r.update()
r.destroy()
return True
except Exception:
return False

def clipboard_available() -> bool:
try:
import pyperclip; return True
except Exception:
pass
s = platform.system()
if s == "Windows": return True
if s == "Darwin": return shutil.which("pbcopy") is not None
for c in ("termux-clipboard-set", "wl-copy", "xclip", "xsel"):
if shutil.which(c): return True
return False

══════════════════════════════════════════════════════
GOOGLE
══════════════════════════════════════════════════════
def open_google(query: str) -> bool:
if "://" not in query:
query = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
url = query
if shutil.which("termux-open-url"):
try:
subprocess.run(["termux-open-url", url]); return True
except Exception:
pass
try:
return webbrowser.open(url, new=2)
except Exception:
return False

══════════════════════════════════════════════════════
UI
══════════════════════════════════════════════════════
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')
def hr(c='─', w=62, color=C.GRAY): print(f"{color}{c*w}{C.RESET}")
def header():
clear_screen()
hr('═', color=C.CYAN)
print(f"{C.BOLD}{C.CYAN} THE OSINT VAULT {C.RESET}{C.GRAY}—{C.RESET} {C.BOLD}Google Dork Generator v2.0{C.RESET}")
print(f" {C.GRAY}CLI · Helyi futtatás · Khera 2024 + Stodelov 2022{C.RESET}")
hr('═', color=C.CYAN)

def prompt(msg: str) -> str:
try:
return input(f"{C.YELLOW}▸ {msg}{C.RESET} ").strip()
except (EOFError, KeyboardInterrupt):
return "0"

def ok(m): print(f"{C.GREEN}[✓]{C.RESET} {m}")
def warn(m): print(f"{C.YELLOW}[!]{C.RESET} {m}")
def err(m): print(f"{C.RED}[✗]{C.RESET} {m}")

══════════════════════════════════════════════════════
ACTIONS — Dork library
══════════════════════════════════════════════════════
def handle_dork(dork: str, desc: str = ""):
print(f"\n{C.BOLD}Dork:{C.RESET} {C.CYAN}{dork}{C.RESET}")
if desc: print(f"{C.GRAY}{desc}{C.RESET}")
print()
if copy_to_clipboard(dork): ok("Vágólapra másolva.")
else: warn("Vágólap nem elérhető — másold kézzel.")
if prompt("Megnyitod a Google-ben? (i/n):").lower() in ("i","igen","y","yes"):
if open_google(dork): ok("Böngésző megnyitva.")
else: warn("Nem sikerült böngészőt nyitni.")
prompt("Enter a folytatáshoz...")

def action_dork_library():
while True:
header()
print(f"{C.BOLD} DORK LIBRARY — 28 példa{C.RESET}\n")
for i, (n, hu, items) in enumerate(CATEGORIES, 1):
print(f" {C.YELLOW}[{i}]{C.RESET} {C.BOLD}{n}{C.RESET} {C.GRAY}({hu}){C.RESET} — {len(items)}")
print(f"\n {C.GRAY}[0]{C.RESET} Vissza")
hr()
ch = prompt("Kategória:")
if ch == "0": return
try:
i = int(ch) - 1
if 0 <= i < len(CATEGORIES): action_category(CATEGORIES[i])
except ValueError: warn("Érvénytelen.")

def action_category(cat):
name, hu, items = cat
while True:
header()
print(f"{C.BOLD} {name}{C.RESET} {C.GRAY}— {hu}{C.RESET}\n")
for i, (dork, desc) in enumerate(items, 1):
print(f" {C.YELLOW}[{i}]{C.RESET} {C.CYAN}{dork}{C.RESET}")
print(f" {C.GRAY}{desc}{C.RESET}\n")
print(f" {C.GRAY}[0]{C.RESET} Vissza")
hr()
ch = prompt(f"Dork (0-{len(items)}):")
if ch == "0": return
try:
i = int(ch) - 1
if 0 <= i < len(items): handle_dork(items[i][0], items[i][1])
except ValueError: warn("Érvénytelen.")

def action_builder():
header()
print(f"{C.BOLD} CUSTOM DORK BUILDER{C.RESET}")
print(f" {C.GRAY}Enter = kihagyás.{C.RESET}\n")
parts: List[str] = []
def ask(label, prefix="", placeholder="", quote=False):
v = prompt(f"{label}" + (f" ({placeholder})" if placeholder else "") + ":").strip()
if not v: return
if quote and " " in v and not (v.startswith('"') and v.endswith('"')):
v = f'"{v}"'
parts.append(f"{prefix}{v}" if prefix else v)
ask("site: domain/aldomain", "site:", "example.com")
ask("filetype: (pdf/xlsx/docx/sql/env/log/txt/pptx/csv)", "filetype:", "pdf")
ask("intitle: címben keresett szó", "intitle:", "index of", quote=True)
ask("inurl: URL-ben keresett szó", "inurl:", "admin", quote=True)
phrase = prompt('"pontos kifejezés" (idézőjel nélkül):').strip()
if phrase: parts.append(f'"{phrase}"')
exc = prompt("kizárandó szavak (-szó, vesszővel):").strip()
if exc:
for w in exc.split(","):
w = w.strip()
if w: parts.append(w if w.startswith("-") else f"-{w}")
orv = prompt("OR alternatíva:").strip()
if orv: parts.append(f"OR {orv}")
extra = prompt("extra szabad szöveg:").strip()
if extra: parts.append(extra)
if not parts:
warn("Üres lekérdezés."); prompt("Enter..."); return
q = " ".join(parts)
print()
hr()
print(f"{C.BOLD}Eredmény:{C.RESET}\n {C.CYAN}{q}{C.RESET}")
hr()
handle_dork(q)

def action_operators():
header()
print(f"{C.BOLD} OPERÁTOR-REFERENCIA{C.RESET}\n")
for op, ex, desc in OPERATORS:
print(f" {C.YELLOW}{op:<22}{C.RESET} {C.GRAY}{desc}{C.RESET}")
print(f" {C.CYAN}{ex}{C.RESET}\n")
prompt("Enter...")

def action_usecases():
header()
print(f"{C.BOLD} HIGH-VALUE USE CASES{C.RESET}\n")
for i, u in enumerate(USECASES, 1):
print(f" {C.YELLOW}[{i:02d}]{C.RESET} {u}\n")
prompt("Enter...")

def action_workflow():
header()
print(f"{C.BOLD} NYOMOZÁSI LÁNC{C.RESET}\n")
for i, (t, d) in enumerate(WORKFLOW, 1):
print(f" {C.CYAN}({i}){C.RESET} {C.BOLD}{t}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_methodology():
header()
print(f"{C.BOLD} METODOLÓGIA — „vetted"{C.RESET}\n")
for n, t, d in METHODOLOGY:
print(f" {C.CYAN}{n}{C.RESET} {C.BOLD}{t}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
print(f" {C.BOLD}Nicole Hurey{C.RESET} {C.GRAY}— Licensed Investigator · OSINT Researcher{C.RESET}")
print(f" {C.CYAN}nicole@paradoxindex.com{C.RESET} · {C.CYAN}theosintvault@gmail.com{C.RESET}")
prompt("\nEnter...")

def action_help():
header()
print(f"{C.BOLD} SÚGÓ{C.RESET}\n")
b = os.path.basename(sys.argv[0])
py = "python" if os.name == "nt" else "python3"
print(f"{C.CYAN}▸ Interaktív:{C.RESET} {py} {b}\n")
print(f"{C.CYAN}▸ CLI flagek:{C.RESET}")
rows = [
("--list", "28 dork listázása"),
("--category <Név>", "egy kategória (Identity/Document/Infra/Exposure/Records/Cloud)"),
("--build", "interaktív dork builder"),
("--search <dork>", "vágólapra másol + Google megnyit"),
("--copy <dork>", "csak vágólap"),
("--open <dork>", "csak böngésző"),
("--operators", "operátor-referencia"),
("--examples", "példák"),
("--selftest", "környezet-ellenőrzés"),
("--tools", "18 OSINT eszköz (Stodelov)"),
("--mitre", "MITRE ATT&CK Recon (10)"),
("--framework", "OSINT Framework (32)"),
("--recs", "11 ajánlás"),
("--paper", "Stodelov 2022 info"),
("--ti", "Threat Intelligence (Khera)"),
("--tracking", "Online tracking + counter"),
("--practical", "8 gyakorlati OSINT lépés"),
("--metadata", "6 metadata tool"),
("--ai", "AI in OSINT"),
("--socmint", "SOCMINT"),
("--weblayers", "Surface/Deep/Dark + TOR"),
("--forensics", "Digital Forensics"),
("--legal", "Legal APAC"),
("--book", "Khera 2024 info"),
("--version", "verzió"),
("-h, --help", "ez a súgó"),
 ]
for flag, desc in rows:
print(f" {C.YELLOW}{flag:<22}{C.RESET} {C.GRAY}{desc}{C.RESET}")
print(f"\n{C.CYAN}▸ Platform:{C.RESET} {platform.system()} {platform.release()}")
print(f"{C.CYAN}▸ Python:{C.RESET} {sys.version.split()[0]}")
print(f"{C.CYAN}▸ Vágólap:{C.RESET} {'elérhető' if clipboard_available() else 'NEM'}")
prompt("\nEnter...")

def action_examples():
header()
print(f"{C.BOLD} PÉLDÁK{C.RESET}\n")
ex = [
("Összes dork", "python dork.py --list"),
("Exposure kategória", "python dork.py --category Exposure"),
("Keresés + másolás", 'python dork.py --search 'site:example.com filetype:pdf intitle:confidential''),
("Builder", "python dork.py --build"),
("Önteszt", "python dork.py --selftest"),
("OSINT tools", "python dork.py --tools"),
("TI (Khera)", "python dork.py --ti"),
("Forensics", "python dork.py --forensics"),
 ]
for t, cmd in ex:
print(f" {C.BOLD}{t}{C.RESET}")
print(f" {C.CYAN}{cmd}{C.RESET}\n")
prompt("Enter...")

def action_selftest():
header()
print(f"{C.BOLD} ÖNTESZT{C.RESET}\n")
print(f" {C.GRAY}Python:{C.RESET} {sys.version.split()[0]}", end=" ")
print("(OK)" if sys.version_info >= (3, 7) else "(3.7+ kell)")
print(f" {C.GRAY}Platform:{C.RESET} {platform.system()} {platform.release()}")
print(f" {C.GRAY}Vágólap:{C.RESET} ", end="")
if clipboard_available(): ok("elérhető")
else: warn("NEM elérhető")
print(f" {C.GRAY}Vágólap teszt:{C.RESET} ", end="")
ok("működik") if copy_to_clipboard("osint_selftest") else warn("nem működik")
prompt("\nEnter...")

══════════════════════════════════════════════════════
ACTIONS — Stodelov 2022
══════════════════════════════════════════════════════
def action_tools():
header()
print(f"{C.BOLD} OSINT TOOLSET{C.RESET} {C.GRAY}(Stodelov & Miloslavskaya, 2022){C.RESET}\n")
for i, (name, url, cat, desc) in enumerate(OSINT_TOOLS, 1):
print(f" {C.YELLOW}[{i:02d}]{C.RESET} {C.BOLD}{name}{C.RESET} {C.GRAY}— {cat}{C.RESET}")
print(f" {C.CYAN}{url}{C.RESET}")
print(f" {C.GRAY}{desc}{C.RESET}\n")
print(f" {C.GRAY}[0]{C.RESET} Vissza")
hr()
ch = prompt(f"Eszköz megnyitása (0-{len(OSINT_TOOLS)}):")
if ch in ("", "0"): return
try:
i = int(ch) - 1
if 0 <= i < len(OSINT_TOOLS):
_, url, _, _ = OSINT_TOOLS[i]
copy_to_clipboard(url); ok("URL vágólapra.")
if open_google(url): ok("Megnyitva.")
prompt("Enter...")
except ValueError: warn("Érvénytelen.")

def action_mitre():
header()
print(f"{C.BOLD} MITRE ATT&CK RECONNAISSANCE{C.RESET} {C.GRAY}(TA0043){C.RESET}\n")
for i, (tactic, items) in enumerate(MITRE_RECON, 1):
print(f" {C.YELLOW}[{i:02d}]{C.RESET} {C.BOLD}{tactic}{C.RESET}")
for it in items:
print(f" {C.GRAY}• {it}{C.RESET}")
print()
prompt("Enter...")

def action_framework():
header()
print(f"{C.BOLD} OSINT FRAMEWORK — 32 objektum{C.RESET}\n")
for i, name in enumerate(OSINT_FRAMEWORK, 1):
print(f" {C.YELLOW}[{i:02d}]{C.RESET} {name}")
print(f"\n {C.GRAY}Forrás: osintframework.com{C.RESET}")
prompt("Enter...")

def action_recs():
header()
print(f"{C.BOLD} 11 AJÁNLÁS — KISZIVÁRGÁS ELLEN{C.RESET}\n")
for i, r in enumerate(PAPER_RECS, 1):
print(f" {C.YELLOW}[{i:02d}]{C.RESET} {r}\n")
prompt("Enter...")

def action_paper():
header()
print(f"{C.BOLD} FORRÁS TANULMÁNY{C.RESET}\n")
print(f" {C.CYAN}{PAPER_CITATION}{C.RESET}\n")
print(f" {C.GRAY}URL: {PAPER_URL}{C.RESET}")
print(f" {C.GRAY}Open Access — CC BY-NC-ND 4.0 · BICA 2022{C.RESET}\n")
if prompt("Megnyitás? (i/n):").lower() in ("i","igen","y","yes"):
if open_google(PAPER_URL): ok("Megnyitva.")
prompt("Enter...")

══════════════════════════════════════════════════════
ACTIONS — Khera 2024
══════════════════════════════════════════════════════
def action_ti():
header()
print(f"{C.BOLD} THREAT INTELLIGENCE{C.RESET} {C.GRAY}(Khera–Prasad–Kwanoran 2024, 1. fej.){C.RESET}\n")
print(f"{C.BOLD}TI típusok:{C.RESET}")
for n, who, d in TI_TYPES:
print(f" {C.YELLOW}{n:<12}{C.RESET} {C.GRAY}({who}){C.RESET}")
print(f" {d}\n")
print(f"{C.BOLD}Életciklus:{C.RESET}")
for n, d in TI_LIFECYCLE: print(f" {C.CYAN}{n}{C.RESET} — {d}")
print(f"\n{C.BOLD}Pyramid of Pain:{C.RESET}")
for n, d in PYRAMID_OF_PAIN: print(f" {C.YELLOW}{n:<24}{C.RESET} {C.GRAY}{d}{C.RESET}")
print(f"\n{C.BOLD}Kill Chain:{C.RESET} " + f" {C.GRAY}→{C.RESET} ".join(KILL_CHAIN))
print(f"\n{C.BOLD}IOC-csere:{C.RESET}")
for n, d in TI_SHARING: print(f" {C.CYAN}{n:<8}{C.RESET} {d}")
print(f"\n{C.BOLD}Ingyenes TI források:{C.RESET}")
for n, url, d in TI_FREE_SOURCES:
print(f" {C.YELLOW}•{C.RESET} {C.BOLD}{n}{C.RESET} — {C.CYAN}{url}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}")
prompt("\nEnter...")

def action_tracking():
header()
print(f"{C.BOLD} ONLINE TRACKING & COUNTERMEASURES{C.RESET} {C.GRAY}(3–4. fej.){C.RESET}\n")
print(f"{C.BOLD}Követési módszerek:{C.RESET}")
for n, d in TRACKING_METHODS: print(f" {C.YELLOW}{n:<22}{C.RESET} {C.GRAY}{d}{C.RESET}")
print(f"\n{C.BOLD}Ellenintézkedések:{C.RESET}")
for n, d in TRACKING_COUNTERMEASURES: print(f" {C.CYAN}{n:<18}{C.RESET} {d}")
prompt("\nEnter...")

def action_practical():
header()
print(f"{C.BOLD} GYAKORLATI OSINT-LÉPÉSEK{C.RESET} {C.GRAY}(5. fej.){C.RESET}\n")
for i, (step, d) in enumerate(PRACTICAL_STEPS, 1):
print(f" {C.YELLOW}[{i}]{C.RESET} {C.BOLD}{step}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_metadata():
header()
print(f"{C.BOLD} METADATA TOOLS{C.RESET} {C.GRAY}(5.8){C.RESET}\n")
for n, url, d in METADATA_TOOLS:
print(f" {C.BOLD}{n}{C.RESET}")
print(f" {C.CYAN}{url}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_ai():
header()
print(f"{C.BOLD} AI AZ OSINT-BAN{C.RESET} {C.GRAY}(6. fej.){C.RESET}\n")
for n, d in AI_OSINT:
print(f" {C.YELLOW}{n}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_socmint():
header()
print(f"{C.BOLD} SOCMINT{C.RESET} {C.GRAY}(7. fej.){C.RESET}\n")
for n, d in SOCMINT:
print(f" {C.YELLOW}{n}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_weblayers():
header()
print(f"{C.BOLD} WEB LAYERS + TOR{C.RESET} {C.GRAY}(8–9. fej.){C.RESET}\n")
for n, d in WEB_LAYERS:
print(f" {C.YELLOW}{n:<18}{C.RESET} {C.GRAY}{d}{C.RESET}\n")
print(f"{C.BOLD}TOR keresők:{C.RESET}")
for n, url in TOR_SEARCH_ENGINES:
print(f" {C.CYAN}• {n}{C.RESET} — {url}")
print(f"\n {C.GRAY}TOR Browser: https://www.torproject.org{C.RESET}")
prompt("\nEnter...")

def action_forensics():
header()
print(f"{C.BOLD} DIGITAL FORENSICS{C.RESET} {C.GRAY}(10–11. fej.){C.RESET}\n")
print(f"{C.BOLD}Folyamat:{C.RESET}")
for n, d in FORENSICS_PROCESS: print(f" {C.YELLOW}{n}{C.RESET} — {d}")
print(f"\n{C.BOLD}OSINT forensics-hez:{C.RESET}")
for n, d in OSINT_FOR_FORENSICS:
print(f" {C.CYAN}{n}{C.RESET}")
print(f" {C.GRAY}{d}{C.RESET}\n")
prompt("Enter...")

def action_legal():
header()
print(f"{C.BOLD} LEGAL — APAC{C.RESET} {C.GRAY}(12. fej.){C.RESET}\n")
for n, d in LEGAL_APAC: print(f" {C.YELLOW}{n:<12}{C.RESET} {d}")
print(f"\n{C.BOLD}Nemzetközi keretek:{C.RESET}")
for n, url in LEGAL_INTL:
print(f" {C.CYAN}{n}{C.RESET}")
print(f" {C.GRAY}{url}{C.RESET}")
prompt("\nEnter...")

def action_book():
header()
print(f"{C.BOLD} FORRÁSKÖNYV{C.RESET}\n")
b = BOOK_INFO
print(f" {C.CYAN}{b['title']}{C.RESET}")
print(f" {C.BOLD}{b['authors']}{C.RESET}")
print(f" {C.GRAY}{b['publisher']}, {b['year']}{C.RESET}")
print(f" {C.GRAY}ISBN: {b['isbn']}{C.RESET}")
print(f" {C.GRAY}Fejezetek: {b['chapters']}{C.RESET}\n")
print(f" {C.BOLD}Fejezetek:{C.RESET}")
for ch in BOOK_CHAPTERS: print(f" {C.GRAY}• {ch}{C.RESET}")
prompt("\nEnter...")

══════════════════════════════════════════════════════
CLI
══════════════════════════════════════════════════════
def find_category(name: str):
name = name.lower()
for c in CATEGORIES:
if name == c[0].lower() or name == c[1].lower(): return c
return None

def cli_main():
args = sys.argv[1:]
if not args: return None
cmd = args[0]
if cmd in ("-h", "--help"): action_help(); return 0
if cmd == "--version":
print("The OSINT Vault — Google Dork Generator v2.0 (CLI)"); return 0
if cmd == "--list":
for n, hu, items in CATEGORIES:
print(f"\n{C.BOLD}{n}{C.RESET} {C.GRAY}({hu}){C.RESET}")
for d, desc in items: print(f" {C.CYAN}{d}{C.RESET}\n {C.GRAY}{desc}{C.RESET}")
return 0
if cmd == "--category" and len(args) > 1:
cat = find_category(args[1])
if not cat: err(f"Nincs ilyen: {args[1]}"); return 1
print(f"\n{C.BOLD}{cat[0]}{C.RESET} {C.GRAY}({cat[1]}){C.RESET}")
for d, desc in cat[2]: print(f" {C.CYAN}{d}{C.RESET}\n {C.GRAY}{desc}{C.RESET}")
return 0
if cmd in ("--copy", "--open", "--search") and len(args) > 1:
dork = " ".join(args[1:])
if cmd in ("--copy", "--search"):
if copy_to_clipboard(dork): ok("Vágólapra másolva.")
else: warn("Vágólap nem elérhető.")
if cmd in ("--open", "--search"):
if open_google(dork): ok("Megnyitva.")
else: warn("Nem sikerült.")
return 0
if cmd == "--operators": action_operators(); return 0
if cmd == "--build": action_builder(); return 0
if cmd == "--examples": action_examples(); return 0
if cmd == "--selftest": action_selftest(); return 0
if cmd == "--tools": action_tools(); return 0
if cmd == "--mitre": action_mitre(); return 0
if cmd == "--framework": action_framework(); return 0
if cmd == "--recs": action_recs(); return 0
if cmd == "--paper": action_paper(); return 0
if cmd == "--ti": action_ti(); return 0
if cmd == "--tracking": action_tracking(); return 0
if cmd == "--practical": action_practical(); return 0
if cmd == "--metadata": action_metadata(); return 0
if cmd == "--ai": action_ai(); return 0
if cmd == "--socmint": action_socmint(); return 0
if cmd in ("--weblayers", "--tor"): action_weblayers(); return 0
if cmd == "--forensics": action_forensics(); return 0
if cmd == "--legal": action_legal(); return 0
if cmd == "--book": action_book(); return 0
err(f"Ismeretlen parancs: {cmd}. Használd: --help")
return 1

══════════════════════════════════════════════════════
MAIN
══════════════════════════════════════════════════════
def main():
r = cli_main()
if r is not None: sys.exit(r)
while True:
header()
print(f" {C.YELLOW}[1]{C.RESET} Dork Library (28)")
print(f" {C.YELLOW}[2]{C.RESET} Custom Dork Builder")
print(f" {C.YELLOW}[3]{C.RESET} Operator Reference")
print(f" {C.YELLOW}[4]{C.RESET} Use Cases")
print(f" {C.YELLOW}[5]{C.RESET} Workflow")
print(f" {C.YELLOW}[6]{C.RESET} Methodology & Author")
print(f" {C.YELLOW}[7]{C.RESET} Súgó")
print(f" {C.YELLOW}[8]{C.RESET} Példák")
print(f" {C.YELLOW}[9]{C.RESET} Önteszt")
hr('-', 40)
print(f" {C.CYAN}[10]{C.RESET} OSINT Toolset (Stodelov, 18)")
print(f" {C.CYAN}[11]{C.RESET} MITRE ATT&CK Recon")
print(f" {C.CYAN}[12]{C.RESET} OSINT Framework (32)")
print(f" {C.CYAN}[13]{C.RESET} 11 Recommendations")
print(f" {C.CYAN}[14]{C.RESET} Paper info (Stodelov)")
hr('-', 40)
print(f" {C.GREEN}[15]{C.RESET} Threat Intelligence (Khera)")
print(f" {C.GREEN}[16]{C.RESET} Tracking + Counter")
print(f" {C.GREEN}[17]{C.RESET} Practical OSINT Steps")
print(f" {C.GREEN}[18]{C.RESET} Metadata Tools")
print(f" {C.GREEN}[19]{C.RESET} AI in OSINT")
print(f" {C.GREEN}[20]{C.RESET} SOCMINT")
print(f" {C.GREEN}[21]{C.RESET} Web Layers + TOR")
print(f" {C.GREEN}[22]{C.RESET} Digital Forensics")
print(f" {C.GREEN}[23]{C.RESET} Legal (APAC)")
print(f" {C.GREEN}[24]{C.RESET} Book info (Khera)")
print(f" {C.GRAY}[0]{C.RESET} Kilépés")
hr()
ch = prompt("Válassz:")
if ch == "0":
print(f"\n{C.CYAN}The OSINT Vault{C.RESET} {C.GRAY}— nyomozás, nem találgatás.{C.RESET}\n")
return
elif ch == "1": action_dork_library()
elif ch == "2": action_builder()
elif ch == "3": action_operators()
elif ch == "4": action_usecases()
elif ch == "5": action_workflow()
elif ch == "6": action_methodology()
elif ch == "7": action_help()
elif ch == "8": action_examples()
elif ch == "9": action_selftest()
elif ch == "10": action_tools()
elif ch == "11": action_mitre()
elif ch == "12": action_framework()
elif ch == "13": action_recs()
elif ch == "14": action_paper()
elif ch == "15": action_ti()
elif ch == "16": action_tracking()
elif ch == "17": action_practical()
elif ch == "18": action_metadata()
elif ch == "19": action_ai()
elif ch == "20": action_socmint()
elif ch == "21": action_weblayers()
elif ch == "22": action_forensics()
elif ch == "23": action_legal()
elif ch == "24": action_book()
else: warn("Érvénytelen választás.")

if name == "main":
try:
main()
except KeyboardInterrupt:
print(f"\n{C.GRAY}Kilépés.{C.RESET}")
sys.exit(0)