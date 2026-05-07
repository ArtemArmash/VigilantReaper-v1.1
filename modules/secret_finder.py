import re
import asyncio
import httpx
from urllib.parse import urljoin

class JSSecretFinder:
    
    def __init__(self, threads: int = 15):
        self.semaphore = asyncio.Semaphore(threads)
        self.headers = {"User-Agent": "VigilantReaper/1.2"}

        self.secret_patterns = [
            ("AWS Access Key ID", "HIGH", re.compile(r"\b((?:AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ABIA)[0-9A-Z]{16})\b")),
            ("AWS Secret Access Key", "CRITICAL", re.compile(r"(?ix)aws(.{0,20})?(secret|sk)(.{0,20})?['\"]([A-Za-z0-9/+=]{40})['\"]")),
            ("Google API Key", "HIGH", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
            ("Google OAuth Client ID", "MEDIUM", re.compile(r"\b\d+-[a-z0-9_]{20,}\.apps\.googleusercontent\.com\b")),
            ("Stripe Secret Key", "CRITICAL", re.compile(r"\bsk_live_[0-9a-zA-Z]{24,}\b")),
            ("Stripe Restricted Key", "HIGH", re.compile(r"\brk_live_[0-9a-zA-Z]{24,}\b")),
            ("Slack Token", "HIGH", re.compile(r"\bxox[abprs]-[0-9A-Za-z-]{10,}\b")),
            ("Slack Webhook", "MEDIUM", re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Z]{8,}/B[0-9A-Z]{8,}/[A-Za-z0-9]{20,}")),
            ("GitHub PAT", "CRITICAL", re.compile(r"\bghp_[0-9A-Za-z]{36}\b")),
            ("GitHub Fine-grained PAT", "CRITICAL", re.compile(r"\bgithub_pat_[0-9A-Za-z_]{82}\b")),
            ("GitHub OAuth", "HIGH", re.compile(r"\bgho_[0-9A-Za-z]{36}\b")),
            ("Mailgun API Key", "HIGH", re.compile(r"\bkey-[0-9a-zA-Z]{32}\b")),
            ("SendGrid API Key", "HIGH", re.compile(r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b")),
            ("Twilio API Key", "HIGH", re.compile(r"\bSK[0-9a-fA-F]{32}\b")),
            ("Generic Bearer JWT", "MEDIUM", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
            ("Firebase URL", "LOW", re.compile(r"https?://[a-z0-9-]+\.firebaseio\.com")),
            ("Private RSA Key", "CRITICAL", re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----")),
        ]

    async def _get_js_links(self, client: httpx.AsyncClient, domain_url: str) -> list:
        pattern = r'src=["\']([^"\']+\.js)["\']'
        try:
            response = await client.get(domain_url, headers=self.headers, follow_redirects=True, timeout=7.0)
            if response.status_code == 200:
                js_links = re.findall(pattern, response.text, re.IGNORECASE)
                full_js_links = [urljoin(domain_url, link) for link in js_links]
                return list(set(full_js_links))

        except Exception:
            return []
        return []

    async def _scan_in_file(self, client: httpx.AsyncClient, js_url: str) -> list:
        found_keys = []
        async with self.semaphore:
            try:
                response = await client.get(
                    js_url, 
                    headers=self.headers, 
                    follow_redirects=True, 
                    timeout=7.0
                )
                if response.status_code == 200:
                    for label, severity, pattern in self.secret_patterns:
                        for match in pattern.finditer(response.text):
                            
                            found_text = match.group(0)[:100]
                            
                            if not any(k['key'] == found_text for k in found_keys):
                                found_keys.append({
                                    "url": js_url,
                                    "type": label,
                                    "severity": severity,  # ДОДАЛИ КРИТИЧНІСТЬ
                                    "key": found_text
                                })
            except Exception:
                pass

        return found_keys

    async def run(self, live_targets: list) -> list:
        results = []
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            print(f"[*] JSSecretFinder: Пошук JS-файлів на {len(live_targets)} хостах...")

            for live_target in live_targets:

                domain = live_target.get("domain")
                if not domain:
                    continue
                domain_url = f"https://{domain}"

                js_links = await self._get_js_links(client, domain_url)
                js_links.append(domain_url)

                if not js_links:
                    continue
                tasks = [
                    self._scan_in_file(client, js_link) for js_link in js_links
                ]

                js_results = await asyncio.gather(*tasks)
                for item in js_results:
                    results.extend(item)
        return results