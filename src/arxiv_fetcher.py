# src/arxiv_fetcher.py

import arxiv
import aiohttp
import aiofiles
import asyncio
import os
import logging
import re
import unicodedata

from typing import List, Dict, Any


class ArxivFetcher:
    def __init__(
        self,
        max_results: int = 5,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    ):
        self.max_results = max_results
        self.sort_by = sort_by
        self.logger = logging.getLogger(__name__)
        self.client = arxiv.Client()

    def fetch_papers(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Fetch papers from arXiv based on the given keyword.
        """
        self.logger.info(f"Fetching papers for keyword: {keyword}")
        search = arxiv.Search(
            query=keyword, max_results=self.max_results, sort_by=self.sort_by
        )

        papers = self.getPapersFromSearch(search)
        return papers

    def getPapersFromSearch(self, search):
        papers = []
        for result in self.client.results(search):
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "pdf_url": result.pdf_url,
                "published": result.published,
            }
            papers.append(paper)
            self.logger.debug(f"Found paper: {paper['title']}")

        self.logger.info(f"Fetched {len(papers)} papers")
        return papers

    def fetch_papers_byIdList(self, id_list: List[str]) -> List[Dict[str, Any]]:
        search = arxiv.Search(id_list=id_list, sort_by=self.sort_by)

        papers = self.getPapersFromSearch(search)
        return papers

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize the filename to ensure it's valid.
        """
        # 将 Unicode 字符转换为 ASCII (或最接近的等效字符)
        filename = (
            unicodedata.normalize("NFKD", filename).encode("ASCII", "ignore").decode()
        )

        # 移除或替换不允许的字符
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)  # 移除 Windows 不允许的字符
        filename = re.sub(r"\s+", "_", filename)  # 将空白字符替换为下划线

        # 确保文件名不以 . 开头（隐藏文件）
        filename = filename.lstrip(".")

        # 截断文件名长度（如果需要）
        max_length = 255  # 大多数文件系统的最大长度
        if len(filename) > max_length:
            filename = filename[:max_length]

        # 如果文件名为空，使用默认名称
        if not filename:
            filename = "unnamed_file"

        return filename

    async def download_pdf(
        self, paper: Dict[str, Any], output_dir: str = "data/pdfs"
    ) -> str:
        """
        Download the PDF for a given paper.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pdf_url = paper["pdf_url"]
        sanitized_title = self.sanitize_filename(paper["title"])
        filename = f"{sanitized_title[:50]}.pdf"
        filepath = os.path.join(output_dir, filename)

        self.logger.info(f"Downloading PDF: {filename}")

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # todo check proxy
                    async with session.get(pdf_url, proxy="socks5://127.0.0.1:7890") as response:
                        if response.status == 200:
                            async with aiofiles.open(filepath, "wb") as f:
                                await f.write(await response.read())
                            file_size = os.path.getsize(filepath)
                            if file_size >= 10 * 1024:  # 大于等于10KB
                                self.logger.info(f"PDF 下载成功: {filepath}，大小: {file_size} 字节")
                                return filepath
                            else:
                                self.logger.warning(f"下载的PDF可能无效: {filepath}，大小: {file_size} 字节")
                                if attempt < max_retries - 1:
                                    self.logger.info(f"尝试重新下载 PDF: {filename}，第 {attempt + 2} 次")
                                else:
                                    self.logger.error(f"多次尝试后仍无法下载有效的PDF: {filepath}")
                                    return None
                        else:
                            self.logger.error(f"下载PDF失败: {pdf_url}，状态码: {response.status}")
                            if attempt < max_retries - 1:
                                self.logger.info(f"尝试重新下载 PDF: {filename}，第 {attempt + 2} 次")
                            else:
                                return None
                except aiohttp.ClientError as e:
                    self.logger.error(f"连接错误: {str(e)}")
                    if attempt < max_retries - 1:
                        self.logger.info(f"尝试重新下载 PDF: {filename}，第 {attempt + 2} 次")
                    else:
                        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetcher = ArxivFetcher(max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)
    id = ["2410.03537"]
    papers = fetcher.fetch_papers_byIdList(id)
    for paper in papers:
        pdf_path = asyncio.run(fetcher.download_pdf(
            paper,
        ))
        if pdf_path:
            print(f"Downloaded: {pdf_path}")
