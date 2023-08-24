# OBS Studio Python Script

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# biblescript.py
# A script to show Bible scriptures that is fetched from Alkitab-API (by sonnylazuardi)

import obspython as obs
from bs4 import BeautifulSoup
import requests


# ------------------------------------------------------------

# Fetch the list of the book in the Bible from the url below
# and will return list of the book
def parse_book() -> list:
    url = "https://alkitab.sabda.org/advanced.php"
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")
    form_bible = soup.find("select", {"name": "book"})
    # Fetch the <option> tag
    books = form_bible.contents 
    # Remove "\n" from the list 
    books_updated = [book for book in books if book != "\n"]

    list_book = []
    for book in books_updated:
        list_book += book.contents
    # Remove all the whitespaces because of the AlkitabAPI is sensitive to whitespaces 
    list_book = [book.replace(' ', '') if ' ' in book else book for book in list_book]        
    
    return list_book

# UI

# Description of the script
def script_description():
    return """A script to show Bible scriptures.
By KevinJP"""


def script_properties():
    props = obs.obs_properties_create()
    
    # Add a placeholder list of bible version
    versions_ph = obs.obs_properties_add_list(
        props,
        "bibleversion",
        "Bible Version",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    
    # Add bible version to placeholder list by iterating versions list
    versions = ["tb", "nkjv", "niv", "net", "av"]
    
    for version in versions:
        name = ""
        if version == "tb":
            name = "Terjemahan Baru (TB)"
        elif version == "nkjv":
            name = "New King James Version (NKJV)"
        elif version == "niv":
            name = "New International Version (NIV)"
        elif version == "net":
            name = "New English Translation (NET)"
        elif version == "av":
            name = "Authorized Version (AV)"
        
        obs.obs_property_list_add_string(versions_ph, name, version)
    
    # Add a placeholder list for the book of the bible
    book_ph = obs.obs_properties_add_list(
        props,
        "book",
        "Book",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    
    # Add book to the placeholder by iterating book_list
    book_list = parse_book()
    for book in book_list:
        obs.obs_property_list_add_string(book_ph, book, book)
    
    return props
