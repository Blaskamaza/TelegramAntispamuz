import asyncio
import json
import aiohttp
from typing import List, Dict, Any
from agents.base import BaseAgent, AgentResult, PromptMixin
from agents.config import GEMINI_FLASH_MODEL, GITHUB_TOKEN, HF_TOKEN, N8N_TEMPLATES_API

class SolutionFinder(BaseAgent, PromptMixin):
    """
    Solution Finder Agent — Поиск готовых решений (GitHub, n8n, HuggingFace).
    Помогает оценить 'Ease of Creation' и найти базу для реализации.
    """
    
    name = "SolutionFinder"
    model = GEMINI_FLASH_MODEL

    async def _search_github(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub for repositories."""
        if not GITHUB_TOKEN:
            self.logger.warning("⚠️ No GITHUB_TOKEN found. Skipping GitHub search.")
            return []
            
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])[:3] # Top 3
                        self.logger.info(f"✅ GitHub Search '{query}': Found {len(items)} items")
                        return [
                            {
                                "title": item["full_name"],
                                "url": item["html_url"],
                                "type": "github",
                                "stars": item["stargazers_count"],
                                "description": item["description"]
                            }
                            for item in items
                        ]
                    else:
                        text = await response.text()
                        self.logger.error(f"❌ GitHub API Error {response.status}: {text}")
                        return []
            except Exception as e:
                self.logger.error(f"❌ GitHub Request Failed: {e}")
                return []

    async def _search_n8n(self, query: str) -> List[Dict[str, Any]]:
        """Search n8n community templates."""
        url = f"{N8N_TEMPLATES_API}?search={query}&rows=5"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        workflows = data.get("workflows", [])[:3]  # Top 3
                        self.logger.info(f"✅ n8n Search '{query}': Found {len(workflows)} templates")
                        return [
                            {
                                "title": wf.get("name", "Unknown"),
                                "url": f"https://n8n.io/workflows/{wf.get('id', '')}",
                                "type": "n8n",
                                "downloads": wf.get("totalViews", 0),
                                "description": wf.get("description", "")[:200] if wf.get("description") else ""
                            }
                            for wf in workflows
                        ]
                    else:
                        self.logger.warning(f"⚠️ n8n API returned {response.status}")
                        return []
            except Exception as e:
                self.logger.error(f"❌ n8n Request Failed: {e}")
                return []

    async def _search_huggingface(self, query: str) -> List[Dict[str, Any]]:
        """Search HuggingFace models and spaces."""
        if not HF_TOKEN:
            self.logger.warning("⚠️ No HF_TOKEN found. Skipping HuggingFace search.")
            return []

        # Search models API
        url = f"https://huggingface.co/api/models?search={query}&limit=3&sort=downloads&direction=-1"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        models = await response.json()
                        self.logger.info(f"✅ HuggingFace Search '{query}': Found {len(models)} models")
                        return [
                            {
                                "title": model.get("modelId", "Unknown"),
                                "url": f"https://huggingface.co/{model.get('modelId', '')}",
                                "type": "huggingface",
                                "downloads": model.get("downloads", 0),
                                "description": model.get("pipeline_tag", "")
                            }
                            for model in models[:3]
                        ]
                    else:
                        self.logger.warning(f"⚠️ HuggingFace API returned {response.status}")
                        return []
            except Exception as e:
                self.logger.error(f"❌ HuggingFace Request Failed: {e}")
                return []

    async def _execute_async(self, input_data: Dict[str, Any]) -> AgentResult:
        """Async execution wrapper."""
        if not input_data or "pain_summary" not in input_data:
            return self.build_result(False, {}, "Missing pain_summary in input_data")

        pain_summary = input_data["pain_summary"]
        self.logger.info(f"🔍 Finding solutions for: {pain_summary}")

        try:
            # 1. Generate search queries
            search_queries = self._generate_search_queries(pain_summary)

            # 2. Search all sources in parallel
            solutions = []
            for query in search_queries:
                # Run all searches concurrently
                gh_task = self._search_github(query)
                n8n_task = self._search_n8n(query)
                hf_task = self._search_huggingface(query)

                results = await asyncio.gather(gh_task, n8n_task, hf_task, return_exceptions=True)

                for result in results:
                    if isinstance(result, list):
                        solutions.extend(result)
                    elif isinstance(result, Exception):
                        self.logger.warning(f"Search task failed: {result}")

            # Deduplicate by URL
            unique_solutions = {s["url"]: s for s in solutions}.values()

            return self.build_result(True, {
                "pain_summary": pain_summary,
                "search_queries": search_queries,
                "found_solutions": list(unique_solutions),
                "sources_searched": ["github", "n8n", "huggingface"],
                "ease_of_creation_score": self._calculate_ease_score(list(unique_solutions))
            })
        except Exception as e:
            self.logger.error(f"Solution search failed: {e}")
            return self.build_result(False, {}, str(e))

    def execute(self, input_data: Dict[str, Any] = None) -> AgentResult:
        return asyncio.run(self._execute_async(input_data))

    def _generate_search_queries(self, pain: str) -> List[str]:
        prompt = f"""
        Generate 3 search queries to find open-source solutions on GitHub for:
        "{pain}"
        
        Queries should be in English, concise, and technical.
        Return ONLY a list of strings, one per line. Do not number them.
        Example:
        telegram bot shop
        ecommerce bot python
        telegram marketplace
        """
        response = self.generate(prompt)
        # Cleanup: split by newline, remove empty lines and numbering
        queries = []
        for line in response.split("\n"):
            clean_line = line.strip()
            # Remove leading numbers like "1. " or "- "
            if clean_line and clean_line[0].isdigit():
                clean_line = clean_line.lstrip("0123456789.- ")
            elif clean_line.startswith("- "):
                clean_line = clean_line[2:]
                
            if clean_line:
                queries.append(clean_line)
                
        return queries[:3]

    def _calculate_ease_score(self, solutions: List[Dict[str, Any]]) -> int:
        """Calculate ease score (1-10) based on found solutions."""
        if not solutions:
            return 2  # Hard if no existing solutions

        score = 4

        # Check for high-quality GitHub repos
        stars = [s.get("stars", 0) for s in solutions if s.get("type") == "github"]
        if any(s > 1000 for s in stars):
            score += 3
        elif any(s > 100 for s in stars):
            score += 1

        # Check for n8n templates (ready-to-use automation)
        n8n_results = [s for s in solutions if s.get("type") == "n8n"]
        if n8n_results:
            score += 2  # n8n templates are easy to integrate

        # Check for HuggingFace models (ML solutions)
        hf_downloads = [s.get("downloads", 0) for s in solutions if s.get("type") == "huggingface"]
        if any(d > 10000 for d in hf_downloads):
            score += 1  # Popular ML models available

        return min(score, 10)

if __name__ == "__main__":
    finder = SolutionFinder()
    # Mock input for testing
    res = finder.execute({"pain_summary": "Telegram bot for selling clothes"})
    print(json.dumps(res.data, indent=2, ensure_ascii=False))
