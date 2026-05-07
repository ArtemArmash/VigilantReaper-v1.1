from abc import ABC, abstractmethod
from core.executor import Executor
import os

class DiscoveryTool(ABC):

    @abstractmethod
    def get_subdomains(self, domain: str) -> list:
        pass

class Subfinder(DiscoveryTool):
    
    def __init__(self, bin_path: str):
        self.path = os.path.join(bin_path, "subfinder.exe")
    
    def get_subdomains(self, domain: str) -> list:
        print(f"[*] Running subfinder for {domain}...")
        output = Executor.run_command([self.path, "-d", domain, "-silent"])
        return output.splitlines()
    
class Assetfinder(DiscoveryTool):
    
    def __init__(self, bin_path: str):
        self.path = os.path.join(bin_path, "assetfinder.exe")
    
    def get_subdomains(self, domain: str) -> list:
        print(f"[*] Running assetfinder for {domain}...")
        output = Executor.run_command([self.path, "--subs-only", domain])
        return output.splitlines()
    
class DiscoveryManager:

    def __init__(self, tools: list):
        self.tools = tools
    
    def discover(self, domain: str) -> list:
        results = []
        for tool in self.tools:
            found = tool.get_subdomains(domain)
            results.extend(found)

        clean_results = sorted(list(set(
            line.strip().lower() for line in results if line.strip()
        )))
        return clean_results
    
