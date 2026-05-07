import os
import asyncio
from modules.discovery import DiscoveryManager, Subfinder, Assetfinder
from core.db_manager import DBManager
from modules.prober import Prober
from core.notifier import TelegramNotifier
from modules.loot_scanner import LootScanner
from modules.secret_finder import JSSecretFinder
from core.config_parser import Config

class VigilantReaper:
    def __init__(self, target: str):
        self.target = target
        
        cfg = Config()
        

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, "database", "reaper.db")
        self.bin_dir = os.path.join(self.base_dir, "bin")
        self.results_dir = os.path.join(self.base_dir, "results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.notifier = TelegramNotifier(cfg.telegram_token, cfg.chat_id)
        self.db = DBManager(self.db_path)
        self.discovery_manager = DiscoveryManager([
            Subfinder(self.bin_dir),
            Assetfinder(self.bin_dir)
        ])
        self.prober = Prober(threads=cfg.threads)
        self.loot_scanner = LootScanner(threads=10)
        self.js_finder = JSSecretFinder(threads=15)



    def _save_to_file(self, filename: str, data: list):
        path = os.path.join(self.results_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(f"{line}\n")
        return path

    async def run_pipeline(self):
        print(f"🚀 [START] Жнець виходить на полювання: {self.target}")

        # --- ЭТАП 1 & 2: DISCOVERY + DATABASE ---
        all_subs = self.discovery_manager.discover(self.target)
        self._save_to_file(f"{self.target}_all_subs.txt", all_subs)
        new_subs = self.db.filter_new_subdomains(all_subs, self.target)
        
        print(f"[+] Знайдено всього: {len(all_subs)} | Нових: {len(new_subs)}")
        if not new_subs:
            print("[-] Нічого нового. Відпочиваємо.")
            return

        # --- ЭТАП 3: PROBING ---
        print(f"[*] Перевірка на 'живучість' {len(new_subs)} доменів...")
        live_results = await self.prober.run(new_subs)
        report_lines = [f"[{res['status']}] {res['domain']} | {res['title']}" for res in live_results]
        self._save_to_file(f"{self.target}_live_report.txt", report_lines)
        if not live_results:
            print("[-] Нові домени знайдені, але вони не відповідають по HTTP.")
            return
        await self.notifier.send_new_targets_notification(self.target, live_results)

        # --- ЭТАП 4: LOOT SCANNING (.env, .git) ---
        print(f"[*] Запуск LootScanner на {len(live_results)} хостах...")
        critical_loot = await self.loot_scanner.run(live_results)
        if critical_loot:
            loot_links = [loot['url'] for loot in critical_loot]
            self._save_to_file(f"{self.target}_CRITICAL_LOOT.txt", loot_links)
            print(f"🔥 [!!!] ЗНАЙДЕНО КРИТИЧНІ ФАЙЛИ: {len(critical_loot)}")
            for loot in critical_loot:
                alert = f"🔥 <b>CRITICAL LOOT FOUND</b> 🔥\n\n<b>URL:</b> <code>{loot['url']}</code>"
                await self.notifier.send_message(alert)
        else:
            print("[#] Секретних файлів (.env) не знайдено.")

        # --- ЭТАП 5: JS SECRET FINDER ---
        print(f"\n[*] Запуск JSSecretFinder. Аналіз вихідного коду...")
        js_secrets = await self.js_finder.run(live_results)
        if js_secrets:
            # Зберігаємо з рівнем критичності
            js_report = [f"[{s['severity']}] {s['type']} | {s['key']} | {s['url']}" for s in js_secrets]
            self._save_to_file(f"{self.target}_JS_SECRETS.txt", js_report)
            print(f"💰 [!!!] ЗНАЙДЕНО КЛЮЧІ В JS: {len(js_secrets)}")
            
            for secret in js_secrets:
                # Гарні емодзі під кожну критичність
                icon = "🚨" if secret['severity'] == "CRITICAL" else "🔥" if secret['severity'] == "HIGH" else "⚠️"
                alert = (
                    f"{icon} <b>JS SECRET FOUND</b> {icon}\n\n"
                    f"<b>Severity:</b> {secret['severity']}\n"
                    f"<b>Type:</b> <code>{secret['type']}</code>\n"
                    f"<b>Key:</b> <code>{secret['key']}</code>\n"
                    f"<b>File:</b> <code>{secret['url']}</code>"
                )
                await self.notifier.send_message(alert)
        else:
            print("[-] API ключів у JS файлах не знайдено.")

        print(f"✅ [FINISH] Полювання на {self.target} завершено.")

async def main():
    target_domain = "nung.edu.ua"
    reaper = VigilantReaper(target_domain)
    await reaper.run_pipeline()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Робота зупинена користувачем.")