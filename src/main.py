from dotenv import load_dotenv

load_dotenv()
import sys

sys.path.append(".")
import json
import asyncio
import argparse
import logging
import os
from typing import List, Optional
import arxiv
from baml_client.async_client import b
from baml_client.types import Summary
from arxiv_fetcher import ArxivFetcher
from pdf_processor import PDFProcessor
from summaries_to_md_convertor import SummariesToMDConverter
from pdf2img import pdf_to_images
import glob

class SummaryWithPath:
    def __init__(self, summary: Summary, pdf_path: str):
        self.summary = summary
        self.pdf_path = pdf_path

def setup_logging():
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Summarize arXiv papers")
    parser.add_argument("keyword", help="Keyword to search for papers")
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of papers to process",
    )
    return parser.parse_args()


async def save_summaries_to_json(summaries: List[SummaryWithPath], keyword: str) -> None:
    """
    Save summaries to a JSON file.

    Args:
        summaries (List[Summary]): List of summaries to save.
        keyword (str): Keyword used for searching papers.

    Raises:
        IOError: If there's an error writing to the file.
    """
    os.makedirs(f"data/{keyword}", exist_ok=True)
    file_path = f"data/{keyword}/{keyword}.json"

    try:
        with open(file_path, "w") as file:
            json.dump(
                [summary.summary.model_dump() for summary in summaries],
                file,
                indent=2,
                ensure_ascii=False,
            )
        logging.info(f"Summaries saved to {file_path}")
    except IOError as e:
        logging.error(f"Error saving summaries to {file_path}: {e}")
        raise

async def download_pdf(fetcher: ArxivFetcher, paper: dict, keyword: str):
    await fetcher.download_pdf(paper, f"data/{keyword}/pdfs")

async def summarize_paper(pdf_path: str, processor: PDFProcessor) -> Optional[Summary]:
    """
    Process a single paper: download PDF, extract text, and generate summary.

    Args:
        fetcher (ArxivFetcher): Instance of ArxivFetcher.
        processor (PDFProcessor): Instance of PDFProcessor.
        paper (dict): Paper information.
        keyword (str): Keyword used for searching papers.

    Returns:
        Optional[Summary]: Generated summary or None if processing failed.
    """
    if pdf_path:
        try:
            paper_content = processor.extract_text_from_fisrt_N_pages(pdf_path, 2).encode('utf-8', 'ignore').decode()
            return await b.SummaryPaper(paper_content)
        except Exception as e:
            logging.error(f"Error processing paper : {e}")
    return None


async def save_summaries_to_md(summaries: List[SummaryWithPath], keyword: str) -> None:
    try:
        os.makedirs(f"data/{keyword}", exist_ok=True)
        file_path = f"data/{keyword}/{keyword}.md"
        real_summaries = [summary.summary for summary in summaries]
        with open(file_path, "w") as file:
            file.write(SummariesToMDConverter(2).from_summaries(real_summaries, keyword))
        logging.info(f"Summaries saved to {file_path}")
    except IOError as e:
        logging.error(f"Error saving summaries to {file_path}: {e}")
        raise


async def main():
    setup_logging()
    args = parse_arguments()

    fetcher = ArxivFetcher(
        max_results=args.max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    processor = PDFProcessor()

    idlist = []
    try:
        with open(f"./data/{args.keyword}/id.txt", "r") as file:
            for line in file:
                idlist.append(line.strip())
    except FileNotFoundError:
        logging.error(f"File ./data/{args.keyword}/id.txt not found.")

    if idlist:
        papers = fetcher.fetch_papers_byIdList(idlist)
        pdf_download_tasks = [download_pdf(fetcher, paper, args.keyword) for paper in papers]
        await asyncio.gather(*pdf_download_tasks)

    pdf_paths = glob.glob(f"./data/{args.keyword}/pdfs/*.pdf")


    summary_tasks = [summarize_paper(pdf_path, processor) for pdf_path in pdf_paths]
    summaries = await asyncio.gather(*summary_tasks)
    summaries = [SummaryWithPath(summary, pdf_path) for summary, pdf_path in zip(summaries, pdf_paths) if summary is not None]

    try:
        await save_summaries_to_json(summaries, args.keyword)
    except IOError:
        logging.error(
            "Failed to save summaries. Continuing with the rest of the program."
        )

    try:
        await save_summaries_to_md(summaries, args.keyword)
    except IOError:
        logging.error(
            "Failed to save summaries. Continuing with the rest of the program."
        )
    # 选择一个PDF文件并转换为图像
    convert_one_pdf_to_img(summaries)

def convert_one_pdf_to_img(summaries: List[SummaryWithPath]):
    try:
        for summary in summaries:
            if summary.summary.repo:
                pdf_to_images(summary.pdf_path)
                logging.info(f"已将PDF文件 {summary.pdf_path} 转换为图像，保存在同文件夹下")
                return
        pdf_to_images(summaries[0].pdf_path)
        logging.info(f"已将第一个PDF文件 {summaries[0].pdf_path} 转换为图像，保存在同文件夹下")
    except Exception as e:
        logging.error(f"PDF转图像过程中出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
