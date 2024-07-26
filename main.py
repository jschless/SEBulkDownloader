import requests
import os
from bs4 import BeautifulSoup


collections = [
    "https://standardebooks.org/collections/encyclopaedia-britannicas-great-books-of-the-western-world",
    "https://standardebooks.org/collections/the-bbcs-100-greatest-british-novels-2015",
]

base_dir = "/Users/joeschlessinger/Programming/SEBulkDownloader"


def downloadCollection(collection_url: str):
    response = requests.get(collection_url)

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.select("ol.ebooks-list li")

    collection_name = collection_url.split("/")[-1]
    print(collection_name)

    collection_dir = os.path.join(base_dir, collection_name)
    image_dir = os.path.join(collection_dir, "cover_art")
    epub_dir = os.path.join(collection_dir, "epubs")

    if not os.path.exists(collection_dir):
        os.mkdir(collection_dir)
        os.mkdir(image_dir)
        os.mkdir(epub_dir)

    base_url = "https://standardebooks.org"
    for book in books:
        title = book.select_one('p > a > span[property="schema:name"]').text
        author = book.select_one('p.author > a > span[property="schema:name"]').text
        book_url = book.select_one('p > a[property="schema:url"]')["href"]
        # print(f"Title: {title}, Author: {author}, URL: {book_url}")
        downloadBook(title + "_" + author, base_url + book_url, epub_dir, image_dir)


def downloadBook(
    title: str, book_url: str, epub_dir: str, image_dir: str, format="kindle"
):
    # downloads a given book from its url to the target dir
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, "html.parser")
    base_url = "https://standardebooks.org"

    azw3_link = soup.select_one('a[href*="download?format=azw3"]')["href"]
    azw3_url = base_url + azw3_link

    # Find the thumbnail link
    thumbnail_link = soup.select_one('a[href*="thumbnail_"]')["href"]
    thumbnail_url = base_url + thumbnail_link

    # Download the AZW3 file
    azw3_response = requests.get(azw3_url)
    if azw3_response.status_code == 200:
        with open(os.path.join(epub_dir, title + ".azw3"), "wb") as file:
            file.write(azw3_response.content)
    else:
        print("Failed to download AZW3 file for " + title)

    thumbnail_response = requests.get(thumbnail_url)
    if thumbnail_response.status_code == 200:
        with open(os.path.join(image_dir, title + ".jpg"), "wb") as file:
            file.write(thumbnail_response.content)
    else:
        print("Failed to download thumbnail image for " + title)
