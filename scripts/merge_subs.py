import base64
import re
import urllib.request

SOURCE_FILE = "sources.txt"
OUT_PLAIN = "nodes.txt"
OUT_B64 = "sub.txt"

NODE_PREFIXES = (
    "vless://", "vmess://", "trojan://", "ss://", "ssr://",
    "hysteria://", "hysteria2://", "tuic://"
)

def is_probably_base64(s: str) -> bool:
    s = s.strip()
    if len(s) < 40:
        return False
    return re.fullmatch(r"[A-Za-z0-9+/=\s]+", s) is not None

def try_b64_decode_to_text(s: str):
    try:
        raw = base64.b64decode(s.strip() + "===")
        text = raw.decode("utf-8", errors="ignore")
        if any(p in text for p in NODE_PREFIXES):
            return text
        return None
    except Exception:
        return None

def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")

def extract_nodes(text: str):
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    out = []
    for ln in lines:
        if not ln:
            continue
        if ln.startswith(NODE_PREFIXES):
            out.append(ln)
    return out

def main():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        sources = [ln.strip() for ln in f.read().splitlines() if ln.strip() and not ln.strip().startswith("#")]

    all_nodes = []

    for url in sources:
        try:
            content = fetch_text(url)

            decoded = None
            if is_probably_base64(content):
                decoded = try_b64_decode_to_text(content)

            text = decoded if decoded is not None else content
            nodes = extract_nodes(text)
            all_nodes.extend(nodes)

        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    seen = set()
    unique_nodes = []
    for n in all_nodes:
        if n not in seen:
            seen.add(n)
            unique_nodes.append(n)

    plain = "\n".join(unique_nodes).strip() + ("\n" if unique_nodes else "")
    with open(OUT_PLAIN, "w", encoding="utf-8") as f:
        f.write(plain)

    b64 = base64.b64encode(plain.encode("utf-8")).decode("utf-8")
    with open(OUT_B64, "w", encoding="utf-8") as f:
        f.write(b64 + "\n")

    print(f"Done. Nodes: {len(unique_nodes)}")

if __name__ == "__main__":
    main()
