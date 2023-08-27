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
import textwrap

# ------------------------------------------------------------

# Script that will be called during the startup
def script_load(settings):
    global script_settings
    script_settings = settings
    
# Function that will be called when the script's settings have been changed
def script_update(settings):
    global selected_version
    global selected_book
    global selected_chapter
    global selected_verse
    
    selected_version = obs.obs_data_get_string(settings, "bibleversion")
    selected_book = obs.obs_data_get_string(settings, "book")
    selected_chapter = obs.obs_data_get_int(settings, "chapter")
    selected_verse = obs.obs_data_get_int(settings, "verse")
    
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

# Fetch the json of the selected chapter
def get_json_scripture(version,book,chapter):
    
    # Define the GraphQL query
    query = f"""
    {{
    passages(version: {version}, book: "{book}", chapter: {chapter}) {{
        verses {{
            book
            chapter
            verse
            type
            content
            book
        }}
    }}
    }}
    """

    # Define the API endpoint URL
    url = 'https://bible.sonnylab.com/'

    # Set the headers and query variables if needed
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://bible.sonnylab.com'
    }

    # Create the request payload
    data = {
        "query": query
    }
    
    # Make the POST request to the GraphQL API
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        json_data = response.json()
        verses = json_data["data"]["passages"]["verses"]
        return verses
    else:
        print("Request failed with status code:", response.status_code)
        print(response.text)
    
# Add the loaded verse to the dedicated list
def get_verse():
    global verse_loaded
    
    verse_loaded = []
    
    for verse in scripture:
        if verse["type"] == "content":
            verse_loaded.append(verse["content"])
            
# Show all the verse in the selected chapter
def add_preview_chapter(props):
    
    # Combine all the verse into one string
    preview_all_verse = ""
    index = 1
    for verse in verse_loaded:
        preview_all_verse += f"{index} {verse}\n~\n"
        index += 1
    
    # Add display counter to preview verse description
    preview_chapter_prop = obs.obs_properties_get(props, "previewchapter")
    obs.obs_property_set_description(preview_chapter_prop, f"Preview\n{selected_book} {selected_chapter}:")	
    
    # Put the combined wrapped verse into the preview verse text field
    obs.obs_data_set_string(script_settings, "previewchapter", preview_all_verse)

# Show how the verse will be displayed (Add displayed verse to the field)
def add_preview_verse(props):
    
    # Get the max width and line
    width = obs.obs_data_get_int(script_settings, "maxwidth")
    line = obs.obs_data_get_int(script_settings, "maxline")
    
    if (width < 15 | line < 1):
        width = 15
        line = 1

    # Wrap the verse (putting them into list)
    wrapper = textwrap.TextWrapper(width=width)
    wrapped_verse_list = wrapper.wrap(text = verse_loaded[selected_verse - 1])

    # Combine the wrapped verse into one string
    displayed_verse_text = ""
    line_counter = line 
    display_counter = 1
    
    for verse in wrapped_verse_list:
        if line_counter == 0:
            displayed_verse_text += "\n~\n"
            line_counter = line
            display_counter += 1
        elif (line_counter > 0 and line_counter < line):
            displayed_verse_text += "\n"
        displayed_verse_text += verse
        line_counter -= 1
        
    # Add display counter to preview verse description
    preview_verse_prop = obs.obs_properties_get(props, "previewverse")
    obs.obs_property_set_description(preview_verse_prop, f"Display ({display_counter}):")	
    
    # Put the combined wrapped verse into the preview verse text field
    obs.obs_data_set_string(script_settings, "previewverse", displayed_verse_text)

        
# When Load Verses button is pressed, function get_json_scripture will be called
def load_pressed(props, prop):
    global scripture
    global selected_verse
    global verse_loaded # The list of verse from get_verse()
    
    scripture = get_json_scripture(
        selected_version,
        selected_book,
        selected_chapter
    )
    # Remove the copyright from the scripture list
    scripture.pop()
    
    get_verse()
    
    # Will set the selected_verse to the max of total verse on the selected chapter
    # if selected_verse exceed it
    if len(verse_loaded) < selected_verse:
        selected_verse = len(verse_loaded)
        obs.obs_data_set_int(
            script_settings,
            "verse",
            selected_verse)
    
    add_preview_chapter(props)
    
    add_preview_verse(props)
    
    return True
    
    
    
    
    
    
    

# ------------------------------------------------------------

# UI

# Description of the script
def script_description():
    return """A script to show Bible scriptures.
By KevinJP

Versions: Terjemahan Baru (tb), New King James Version (nkjv), New International Version (niv), New English Translation (net), Authorized Version (av)"""


def script_properties():
    
    props = obs.obs_properties_create()
    
    # Add input field for Text Source and Title Text Source
    text_source = obs.obs_properties_add_list(
        props,
        "textsource",
        "Text Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING
    )
    title_source = obs.obs_properties_add_list(
        props,
        "titlesource",
        "Title Source",
        obs.OBS_COMBO_TYPE_LIST,
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
                obs.obs_property_list_add_string(
                    text_source,
                    name,
                    name
                )
                obs.obs_property_list_add_string(
                    title_source,
                    name,
                    name
                )				
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
        obs.obs_property_list_add_string(
            versions_ph,
            version,
            version
        )
    
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
        obs.obs_property_list_add_string(
            book_ph,
            book,
            book
        )
        
    # Add a input field for the chapter 
    chapter_ph = obs.obs_properties_add_int(
        props,
        "chapter",
        "Chapter:",
        1, # min
        150, # max
        1 # iter
    )
    
    # Add placeholder list for verse
    verse_ph = obs.obs_properties_add_int(
        props,
        "verse",
        "Verse:",
        1, # min
        176, # max
        1 # iter
    )
    
    # Load the bible verses
    obs.obs_properties_add_button(
        props,
        "loadverses",
        "Load Verses",
        load_pressed
    )

    # Show the verse of selected chapter
    preview_chapter = obs.obs_properties_add_text(
        props,
        "previewchapter",
        "Preview\nChapter:",
        obs.OBS_TEXT_MULTILINE
    )
    
    # Show verse that will be displayed
    preview_verse = obs.obs_properties_add_text(
        props,
        "previewverse",
        "Display:",
        obs.OBS_TEXT_MULTILINE
    )

    # Maximum characters per line that will be displayed
    max_width = obs.obs_properties_add_int(
        props,
        "maxwidth",
        "Width (Chars):",
        15, # min
        70, # max
        1 # iter
    )
    
    # Maximum line that will be displayed
    max_line = obs.obs_properties_add_int(
        props,
        "maxline",
        "Height (Lines):",
        1, # min
        12,# max
        1 # iter 
    )
    return props
