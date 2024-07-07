from config import cfg
from .functions import *
from memory import Memory
import time
from context.compression import ContextCompressor, DB_MODE, SEARCH_API_MODE
from db.PostgresqlPool import search_vec_pg

AGENT_ROLE_PROMPT = "You are an AI research assistant specializing in sedimentology, equipped with a vast database of geological knowledge. Your mission is to assist geologists and researchers in uncovering the secrets hidden within Earth's sedimentary layers. As a knowledgeable guide in the realm of sedimentology, you provide insights on sedimentary structures, analyze depositional environments, and offer assistance in the interpretation of sedimentary sequences. Your virtual presence serves as a valuable resource for Earth scientists, helping them navigate the intricate world of sediments and contributing to the understanding of Earth's dynamic history through the study of its geological archives."


class GPTResearcher:
    """
    GPT Researcher
    """

    def __init__(self, query, report_type, websocket=None, conn=None, cfg=cfg):
        """
        Initialize the GPT Researcher class.
        Args:
            query:
            report_type:
            config_path:
            websocket:
        """
        self.query = query
        self.agent = None
        self.role = None
        self.report_type = report_type
        self.websocket = websocket
        self.cfg = cfg
        self.retriever = get_retriever(self.cfg.retriever)
        self.context = []
        self.memory = Memory()
        self.visited_urls = set()
        self.conn = conn

    @property
    def role(self):
        """Getter for the role property."""
        return self._role

    @role.setter
    def role(self, new_role):
        """Setter for the role property."""
        # 在设置 role 时可以执行一些额外的逻辑
        self._role = new_role

    def append_context(self, context):
        self.context.append(context)

    async def run(self):
        """
        Runs the GPT Researcher
        Returns:
            Report
        """
        print(f"🔎 Running research for '{self.query}'...")
        # Generate Agent
        self.agent, self.role = await choose_agent(self.query, self.cfg)
        await stream_output("logs", self.agent, self.websocket)

        # Generate Sub-Queries including original query
        sub_queries = await get_sub_queries(self.query, self.role, self.cfg) + [self.query]
        await stream_output("logs",
                            f"🧠 I will conduct my research based on the following queries: {sub_queries}...",
                            self.websocket)

        # Run Sub-Queries
        await self.sub_query(sub_queries)
        return await self.generate_report()

    async def sub_query(self, sub_queries):
        for sub_query in sub_queries:
            await stream_output("logs", f"\n🔎 Running research for '{sub_query}' in internet...", self.websocket)
            scraped_sites = await self.scrape_sites_by_query(sub_query)
            context = await self.get_similar_content_by_query(sub_query, scraped_sites)
            await stream_output("logs", f"📃 {context}", self.websocket)
            self.context.append(context)
        return self.context

    async def generate_report(self):
        await stream_output("logs", f"✍️ Writing {self.report_type} for research task: {self.query}...", self.websocket)
        report = await generate_report(query=self.query, context=self.context,
                                       agent_role_prompt=self.role, report_type=self.report_type,
                                       websocket=self.websocket, cfg=self.cfg)
        time.sleep(2)
        return report

    async def get_new_urls(self, url_set_input):
        """ Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                await stream_output("logs", f"✅ Adding source url to research: {url}\n", self.websocket)

                self.visited_urls.add(url)
                new_urls.append(url)

        return new_urls

    async def scrape_sites_by_query(self, sub_query):
        """
        Runs a sub-query
        Args:
            sub_query:

        Returns:
            Summary
        """
        # Get Urls
        retriever = self.retriever(sub_query)
        search_results = retriever.search(max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self.get_new_urls([url.get("href") for url in search_results])

        # Scrape Urls
        # await stream_output("logs", f"📝Scraping urls {new_search_urls}...\n", self.websocket)
        await stream_output("logs", f"🤔Researching for relevant information...\n", self.websocket)
        scraped_content_results = scrape_urls(new_search_urls, self.cfg)
        return scraped_content_results

    async def get_similar_content_by_query(self, query, pages, mode=SEARCH_API_MODE):
        await stream_output("logs", f"🌐 Summarizing url: {query}", self.websocket)
        # Summarize Raw Data
        context_compressor = ContextCompressor(documents=pages, embeddings=self.memory.get_embeddings())
        # Run Tasks
        return context_compressor.get_context(query, max_results=4, mode=mode)

    async def run_with_db(self):
        await stream_output("logs", f"🔎 Running research for '{self.query}'...", self.websocket)
        await stream_output("logs", "🌍 Paleogeography Agent", self.websocket)
        self.role = AGENT_ROLE_PROMPT
        # step 1: 分解问题 get sub-queries
        sub_queries = await get_sub_queries(self.query, self.role, self.cfg) + [self.query]
        await stream_output("logs",
                            f"🧠 I will conduct my research based on the following queries: {sub_queries}...", self.websocket)
        # step 2: do search for sub-queries
        await self.sub_query(sub_queries)
        # step 3: get more detailed info in personal db
        for query in sub_queries:
            await stream_output("logs", f"\n🔎 Running research for '{query}' in DB...", self.websocket)
            related_sentences = search_vec_pg(sentences=query, table_name='sedimentology_paper_paragraph',
                                              conn=self.conn,
                                              limit=15)
            context = await self.get_similar_content_by_query(query, related_sentences, mode=DB_MODE)
            await stream_output("logs", f"📃 {context}", self.websocket)
            self.context.append(context)
        # step 4: generate report
        return await self.generate_report()

