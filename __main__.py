import argparse
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown


def extract_papers_with_keywords(url, date, keywords):
    # Send a request to the webpage
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return []

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

    if not date_header:
        print("Date header not found")
        return []

    papers = []
    next_sibling = date_header.find_next_sibling()

    while next_sibling and next_sibling.name != 'h3':
        if next_sibling.name == 'dt':
            dt = next_sibling

            # Extract the link to the paper's abstract page
            paper_link = dt.find('a', href=True, title='Abstract')['href']
            paper_url = f"https://arxiv.org{paper_link}"

            # Get the paper's abstract page content
            paper_response = requests.get(paper_url)
            if paper_response.status_code != 200:
                print(f"Failed to retrieve paper {paper_url}")
                next_sibling = next_sibling.find_next_sibling()
                continue

            paper_soup = BeautifulSoup(paper_response.content, 'html.parser')
            abstract_block = paper_soup.find('blockquote', class_='abstract')

            if not abstract_block:
                print(f"Abstract not found for paper {paper_url}")
                next_sibling = next_sibling.find_next_sibling()
                continue

            # Extract the abstract text by removing the 'Abstract:' descriptor
            abstract_text = ''.join(abstract_block.stripped_strings).replace('Abstract:', '', 1).strip()

            # Check if any of the keywords are in the abstract
            if any(re.search(keyword, abstract_text, re.IGNORECASE) for keyword in keywords):
                paper_title = dt.find_next_sibling('dd').find('div', class_='list-title').text.replace('Title:', '').strip()
                #paper_authors = dt.find_next_sibling('dd').find('div', class_='list-authors').text.strip()
                papers.append({
                    'title': paper_title,
                    #'authors': paper_authors,
                    'abstract': abstract_text,
                    'url': paper_url
                })
        next_sibling = next_sibling.find_next_sibling()

    return papers


parser = argparse.ArgumentParser()
parser.add_argument(
    '--date',
    type=str,
    default=str(datetime.now().date()),
    help='Specify the date in YYYY-MM-DD format (default: current date)'
)
args = parser.parse_args()
args.date = datetime.strptime(args.date, '%Y-%m-%d').date()

URL = "https://arxiv.org/list/cs.LG/recent?skip=0&show=2000"
KEYWORDS = ["LLM", "LLMs", "language model", "language models", "language-model", "language-models"]

papers = extract_papers_with_keywords(URL, args.date, KEYWORDS)
console = Console()
for paper in papers:
    md = Markdown(f"# {paper['title']}")
    console.print(md)
    console.print(f"{paper['abstract']}")
    console.print(f"{paper['url']}\n")
    #print(f"Authors: {paper['authors']}")
