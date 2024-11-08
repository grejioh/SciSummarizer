import logging
from typing import List

from baml_client.types import Summary


class SummariesToMDConverter:
    def __init__(self, title_level):
        self.logger = logging.getLogger(__name__)
        self.title_level = title_level

    def indexedItems(self, title: str, items: List[str]) -> str:
        temp_title_level = self.title_level + 1
        temp_content = ("#" * temp_title_level) + " " + title + "\n"

        for i, item in enumerate(items, 1):
            temp_content += f"{i}. {item}\n"
        return temp_content

    def from_summaries(self, summaries: List[Summary], keyword: str) -> str:
        md_content = ""
        for summary in summaries:
            md_content += f"## {summary.title}\n"
            md_content += summary.chinese_title + "\n"
            md_content += "论文：\n"
            if summary.repo:
                md_content += f"代码：{summary.repo}\n"
            md_content += ("#" * (1 + self.title_level)) + " " + "文章解析" + "\n"
            md_content += summary.core_ideas_summary + "\n"
            md_content += self.indexedItems("创新点", summary.innovations)
            md_content += self.indexedItems("研究方法", summary.methodology)
            md_content += self.indexedItems("研究结论", summary.conclusions)

        return md_content


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
