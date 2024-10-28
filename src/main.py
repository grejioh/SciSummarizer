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


async def save_summaries_to_json(summaries: List[Summary], keyword: str) -> None:
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
                [summary.model_dump() for summary in summaries],
                file,
                indent=2,
                ensure_ascii=False,
            )
        logging.info(f"Summaries saved to {file_path}")
    except IOError as e:
        logging.error(f"Error saving summaries to {file_path}: {e}")
        raise


async def process_paper(
    fetcher: ArxivFetcher, processor: PDFProcessor, paper: dict, keyword: str
) -> Optional[Summary]:
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
    pdf_path = await fetcher.download_pdf(paper, f"data/{keyword}/pdfs")
    if pdf_path:
        try:
            paper_content = processor.extract_text_from_fisrt_N_pages(pdf_path, 2)
            return await b.SummaryPaper(paper_content)
        except Exception as e:
            logging.error(f"Error processing paper {paper['title']}: {e}")
    return None


async def save_summaries_to_md(summaries: List[Summary], keyword: str) -> None:
    try:
        os.makedirs(f"data/{keyword}", exist_ok=True)
        file_path = f"data/{keyword}/{keyword}.md"
        with open(file_path, "w") as file:
            file.write(SummariesToMDConverter(2).from_summaries(summaries, keyword))
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

    papers = fetcher.fetch_papers_byIdList(idlist)

    tasks = [process_paper(fetcher, processor, paper, args.keyword) for paper in papers]
    summaries = await asyncio.gather(*tasks)
    summaries = [summary for summary in summaries if summary is not None]

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
    convert_one_pdf_to_img(args)

def convert_one_pdf_to_img(args):
    try:
        pdf_folder = f"./data/{args.keyword}/pdfs"
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        if pdf_files:
            selected_pdf = os.path.join(pdf_folder, pdf_files[0])
            pdf_to_images(selected_pdf)
            logging.info(f"已将PDF文件 {selected_pdf} 转换为图像，保存在同文件夹下")
        else:
            logging.warning(f"在 {pdf_folder} 中未找到PDF文件")
    except Exception as e:
        logging.error(f"PDF转图像过程中出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
