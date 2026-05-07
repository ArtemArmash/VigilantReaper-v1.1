import httpx

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot8795264803:AAER3H4uV8LxWpmFejcB5CCyzaK83aPmtqM/sendMessage"

    async def send_message(self, text: str):
        json_data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, json=json_data, timeout=10.0)
                if response.status_code != 200:
                    print(f"[!] Telegram Error: {response.text}")
            except Exception as e:
                 print(f"[!] Could not send Telegram alert: {e}")

    async def send_new_targets_notification(self, target_name: str, live_results: list):
        if not live_results:
            return

        header = f"🚀 <b>[VigilantReaper]</b>\nTarget: <code>{target_name}</code>\nFound <b>{len(live_results)}</b> live assets:\n\n"

        message = header

        for item in live_results:
            domain = item.get("domain", "unknown")
            status = item.get("status", "N/A")
            title = item.get("title", "No title")
            
            line = f"<b>[{status}]</b> {domain} | <i>{title}</i>\n"
            if len(message+line) > 400:
                await self.send_message(message)
                message = "... продовження:\n\n"
            message+=line
            
        await self.send_message(message)