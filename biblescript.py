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

# Fetch the list of total chapter in every book
# def fetch_chapter() -> list:
#     url = "https://www.biblememorygoal.com/how-many-chapters-verses-in-the-bible/"
#     response = requests.get(url)
#     html_content = response.content

#     soup = BeautifulSoup(html_content, "html.parser")
    
#     old_testam = soup.select("tbody")[0]
#     new_testam = soup.select("tbody")[-1]
#     chapter_list = []

#     for tr in old_testam.find_all('tr'):
#         num_of_chap = tr.find_all("td")[1].text
#         if num_of_chap == '':
#             continue
#         num_of_chapt = int(num_of_chap)
#         chapter_list.append(num_of_chapt)

#     for tr in new_testam.find_all('tr'):
#         num_of_chap = tr.find_all("td")[1].text
#         if num_of_chap == '':
#             continue
#         num_of_chapt = int(num_of_chap)
#         chapter_list.append(num_of_chapt)
        
#     return chapter_list

# Callback function when the book is selected
# def book_changed(props, prop, settings):
#     selected_book = obs.obs_data_get_string(settings, "book")
#     if (selected_book == ""):
#         selected_book = "Kejadian"
        
#     index_sb = book_list.index(selected_book)
    
#     chapter_list = fetch_chapter()
#     chapter_prop = obs.obs_properties_get(props,"chapter")
    
#     # Get the total chapter of selected book
#     chapter_of_sb = chapter_list[index_sb]
#     # Set the max of total chapter that can be selected
#     obs.obs_property_int_set_limits(chapter_prop, 1, chapter_of_sb, 1)
    
#     return True



# ------------------------------------------------------------

# UI

# Description of the script
def script_description():
    return """A script to show Bible scriptures.
By KevinJP"""


def script_properties():
    # global book_list
    
    props = obs.obs_properties_create()
    
    # Add input field for Text Source and Title Text Source
    text_source = obs.obs_properties_add_list(
        props,
        "textsource",
        "Text Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    title_source = obs.obs_properties_add_list(
        props,
        "titlesource",
        "Title Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )	
    sources = obs.obs_enum_sources()
    if sources is not None:
        n = list()
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                n.append(obs.obs_source_get_name(source))
        n.sort()
        for name in n:
                obs.obs_property_list_add_string(text_source, name, name)
                obs.obs_property_list_add_string(title_source, name, name)				
    obs.source_list_release(sources)
  
    # Add a placeholder list of bible version
    versions_ph = obs.obs_properties_add_list(
        props,
        "bibleversion",
        "Bible Version:",
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
        "Book:",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING
    )
    
    # Add list of book to the placeholder by iterating book_list
    book_list = parse_book()
    for book in book_list:
        obs.obs_property_list_add_string(book_ph, book, book)
    
    # Call the callback function when the book is selected
    #obs.obs_property_set_modified_callback(book_ph, book_changed)
    
    # Add a input field for the chapter 
    chapter_ph = obs.obs_properties_add_int(
        props,
        "chapter",
        "Chapter:",
        1, # min
        150, # max
        1 # iter
    )
    
    
    # Add a input field for the verse
    # verse_ph = obs.obs_properties_add_int(
    #     props,
    #     "verse",
    #     "Chapter:",
    #     1, # min
    #     176, # max
    #     1 # iter
    # )
    
    
    return props
