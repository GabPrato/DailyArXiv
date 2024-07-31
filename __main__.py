import argparse
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown


def parse_args():
    parser = argparse.ArgumentParser(
        prog="DailyArXiv",
        description="Searches all arXiv papers in the chosen subjects, released on the specified date, and containing the given keywords in the abstract. " \
        "If both --required_keywords and --any_keywords are NOT specified, all papers will be selected. " \
        "If both are specified, the search will select papers where the abstract contains all of the keywords from --required-keywords and at least one keyword from --any-keyword.")
    parser.add_argument(
        '--subjects',
        type=str,
        default="cs.AI,cs.LG",
        help="List of comma-separated arXiv subjects, where papers must belong to at least one of the specified subjects. View the list at https://arxiv.org/. " \
        "Searches all Artificial Intelligence (cs.AI) and Machine Learning (cs.LG) papers by default.")
    parser.add_argument(
        '--date',
        type=str,
        default=str(datetime.now().date()),
        help="Specify the date in YYYY-MM-DD format. Default is your system's current date."
    )
    parser.add_argument(
        '--required-keywords',
        type=str,
        help="List of comma separated keywords (e.g., 'quantization,4-bit') that must all appear in the abstract. Keywords are case-insensitive. List is empty by default."
    )
    parser.add_argument(
        '--any-keywords',
        type=str,
        help="List of comma separated keywords (e.g., 'LLM,language,model'), where a paper will be selected if any of the keywords in this list appear in the abstract. " \
        "Keywords are case-insensitive. List is empty by default."
    )
    return parser.parse_args()


def extract_papers_with_keywords(subjects="cs.AI,cs.LG", date=datetime.now(), required_keywords=[], any_keywords=[]):
    daily_paper_urls = {}
    for subject in subjects:
        response = requests.get(f"https://arxiv.org/list/{subject}/recent?skip=0&show=10000")
        assert response.status_code == 200, f"Webpage returned code: {response.status_code}"

        # Parse the content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Format the date as it appears in the <h3> tag
        formatted_date = date.strftime("%a, %-d %b %Y")

        # Find the specific <h3> tag that matches the formatted date
        date_header = None
        for h3 in soup.find_all('h3'):
            if formatted_date in h3.text:
                date_header = h3
                break

        assert date_header, "Date header not found"

        # Find all daily papers
        next_sibling = date_header.find_next_sibling()
        while next_sibling and next_sibling.name != 'h3':
            if next_sibling.name == 'dt':
                # Extract the link to the paper's abstract page
                paper_link = next_sibling.find('a', href=True, title='Abstract')['href']
                paper_url = f"https://arxiv.org{paper_link}"
                paper_title = next_sibling.find_next_sibling('dd').find('div', class_='list-title').text.replace('Title:', '').strip()
                
                daily_paper_urls[paper_title] = paper_url

            next_sibling = next_sibling.find_next_sibling()

    console = Console()
    selected_papers = []
    for title, url in daily_paper_urls.items():
        # Get the paper's abstract page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve paper {url}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        abstract_block = soup.find('blockquote', class_='abstract')

        if not abstract_block:
            print(f"Abstract not found for paper {paper_url}")
            continue

        # Extract the abstract text by removing the 'Abstract:' descriptor
        abstract_text = ''.join(abstract_block.stripped_strings).replace('Abstract:', '', 1).strip()

        # Check if any of the keywords are in the abstract
        select_paper = False
        if len(required_keywords) == 0 and len(any_keywords) == 0:
            select_paper = True
        elif len(required_keywords) > 0 and len(any_keywords) == 0:
            select_paper = all(re.search(keyword, abstract_text, re.IGNORECASE) for keyword in required_keywords)
        elif len(required_keywords) == 0 and len(any_keywords) > 0:
            select_paper = any(re.search(keyword, abstract_text, re.IGNORECASE) for keyword in any_keywords)
        else: # len(required_keywords) > 0 and len(any_keywords) > 0
            select_paper = all(re.search(keyword, abstract_text, re.IGNORECASE) for keyword in required_keywords) and any(re.search(keyword, abstract_text, re.IGNORECASE) for keyword in any_keywords)
        
        if select_paper:
            selected_papers.append({
                'title': title,
                'abstract': abstract_text,
                'url': url
            })

            console.print(Markdown(f"# {title}"))
            console.print(abstract_text)
            console.print(url)
            print()

    return selected_papers


def main():
    args = parse_args()
    
    assert args.subjects is not None
    assert args.date is not None
    
    args.subjects = args.subjects.split(',')
    args.date = datetime.strptime(args.date, '%Y-%m-%d')
    args.required_keywords = args.required_keywords.split(',') if args.required_keywords is not None else []
    args.any_keywords = args.any_keywords.split(',') if args.any_keywords is not None else []

    extract_papers_with_keywords(args.subjects, args.date, args.required_keywords, args.any_keywords)

if __name__ == '__main__':
    main()
