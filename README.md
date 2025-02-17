Filters the abstracts of all arXiv papers released on the specified date using the specified keywords. E.g.:
```bash
python -m DailyArXiv --subjects="cs.AI" --required-keywords="LLM"
```

# Requirements
* requests
* beautifulsoup4
* rich

# Installation
Download the repo:
```bash
git clone https://github.com/GabPrato/DailyArXiv.git
```
Install required packages:
```bash
pip install -r DailyArXiv/requirements.txt
```
# Instructions
View command arguments:
```
$ python -m DailyArXiv --help
usage: DailyArXiv [-h] [--subjects SUBJECTS] [--date DATE] [--required-keywords REQUIRED_KEYWORDS] [--any-keywords ANY_KEYWORDS]

Searches all arXiv papers in the chosen subjects, released on the specified date, and containing the given keywords in the abstract.
If both --required_keywords and --any_keywords are NOT specified, all papers will be selected. If both are specified,
the search will select papers where the abstract contains all of the keywords from --required-keywords and at least one keyword from --any-keyword.

options:
  -h, --help            show this help message and exit
  --subjects SUBJECTS   List of comma-separated arXiv subjects, where papers must belong to at least one of the specified subjects.
                        View the list at https://arxiv.org/. Searches all Artificial Intelligence (cs.AI) and Machine Learning (cs.LG) papers by default.
  --date DATE           Specify the date in YYYY-MM-DD format. Default is your system's current date.
  --required-keywords REQUIRED_KEYWORDS
                        List of comma separated keywords (e.g., 'quantization,4-bit') that must all appear in the abstract.
                        Keywords are case-insensitive. List is empty by default.
  --any-keywords ANY_KEYWORDS
                        List of comma separated keywords (e.g., 'LLM,language,model'), where a paper will be selected if any of the
                        keywords in this list appear in the abstract. Keywords are case-insensitive. List is empty by default.
```

# Examples
By default, lists all machine learning (`cs.LG`) and AI (`cs.AI`) arXiv releases of today:
```bash
python -m DailyArXiv
```
Specify the subject, e.g., all Classical Physics and General Physics:
```bash
python -m DailyArXiv --subjects="physics.class-ph,physics.gen-ph"
```
Specify the date:
```bash
python -m DailyArXiv --date="2023-12-04"
```
Search for papers where the abstract contains `LLM` and `NLP`. Note that keywords are case-insensitive.
```bash
python -m DailyArXiv --required-keywords="LLM,NLP"
```
Search for papers where the abstract contains either `LLM` or `NLP`:
```bash
python -m DailyArXiv --any-keywords="LLM,NLP"
```
Search for papers where the abstract contains `LLM` and either `NLP` or `quantization`:
```bash
python -m DailyArXiv --required-keywords="LLM" --any-keywords="NLP,quantization"
```
