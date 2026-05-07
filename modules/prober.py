import asyncio
import httpx
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Prober:
    def __init__(self, threads: int = 50):
        self.semaphore = asyncio.Semaphore(threads)
        self.headers = {
            "User-Agent": "VigilantReaper/1.0 (Bug Bounty Bot)"
        }
    
    async def _check_domain(self, client: httpx.AsyncClient, domain: str) -> dict:
        async with self.semaphore:
            URL = f"https://{domain}"
            try:
                response = await client.get(URL, headers=self.headers, follow_redirects=True, timeout=7.0)
                if 200 <= response.status_code <= 499:
                    match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                    title = match.group(1) if match else "No title"
                    return {"domain": domain , "status": response.status_code, "title": title[:50]}
            except Exception:
                return None
    
    async def run(self, domains: str) -> list:
        results = []
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            tasks = [
                self._check_domain(client, domain) for domain in domains
            ]
            response = await asyncio.gather(*tasks)
        
        results = [r for r in response if r is not None]

        return results
            