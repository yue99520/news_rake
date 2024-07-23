from typing import List

from bs4 import BeautifulSoup
import lxml_html_clean as clean


class CleanUtils:
    SAFE_ATTRS = {'src', 'alt', 'href', 'title', 'width', 'height'}
    KILL_TAGS = ['object', 'iframe']
    __cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=SAFE_ATTRS, kill_tags=KILL_TAGS)

    @staticmethod
    def convert_weird_chars(html_content: str):
        html_content = html_content.replace('“', '"')
        html_content = html_content.replace('”', '"')
        html_content = html_content.replace('‘', "'")
        html_content = html_content.replace('’', "'")
        html_content = html_content.replace('–', "-")
        return html_content

    @staticmethod
    def clean_attributes(html_content: str):
        return CleanUtils.__cleaner.clean_html(html_content)

    @staticmethod
    def remove_tags(html_content: str, removes: List[str]):
        soup = BeautifulSoup(html_content, 'html.parser')
        for remove_tag in removes:
            for found in soup.find_all(remove_tag):
                found.decompose()
        return str(soup)
