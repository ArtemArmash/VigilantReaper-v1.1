import asyncio 
import httpx

class LootScanner: 
    def __init__(self, threads: int = 10): 
        self.semaphore = asyncio.Semaphore(threads)

        self.headers = {"User-Agent": "VigilantReaper/1.1"} 
        self.loot_paths=[
        "/.env", 
        "/.git/config", 
        "/.vscode/sftp.json",
        "/phpinfo.php",
        "/backup.zip",
        "/config.php.bak"
        ]

    async def _scan_hosts(self, client: httpx.AsyncClient, domain: str) -> list:
        results = []
        async with self.semaphore:
            for path in self.loot_paths:
                URL = f"https://{domain}/{path.lstrip('/')}"
                try:
                    response = await client.get(URL, headers=self.headers, timeout=5.0, follow_redirects=True)
                    if response.status_code == 200:
                        text = response.text.lower()
                        markers = ["db_password", "aws_access", "secret_key", "[core]", "redis_"]
                        if any(marker in text for marker in markers) or "phpinfo()" in text:
                            results.append({"url": URL, "type": path})
                except Exception:
                    continue
            return results

    async def run(self, live_targets: list) -> list:
        results = []
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:

            domains = [t['domain'] if isinstance(t, dict) else t for t in live_targets]
            tasks = [
                self._scan_hosts(client, domain) for domain in domains
            ]
            response = await asyncio.gather(*tasks)
            for sublist in response:
                if sublist:
                    results.extend(sublist)
        return results
