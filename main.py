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

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        "Cookie": "download-count=5",
        "Priority": "u=0, i",
        "Referer": "https://standardebooks.org/ebooks/adam-smith/the-wealth-of-nations",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    azw3_link = soup.select_one('a[href*="download?format=azw3"]')["href"]
    azw3_url = base_url + azw3_link

    split_link = azw3_link.split("/")
    author = split_link[2]
    book_title = split_link[3]
    azw3_file = f"{author}_{book_title}.azw3"

    # Find the thumbnail link
    thumbnail_link = soup.select_one('a[href*="thumbnail_"]')["href"]
    thumbnail_url = base_url + thumbnail_link

    # Download the AZW3 file
    azw3_response = requests.get(
        azw3_url, headers=headers, stream=True, allow_redirects=True
    )
    if azw3_response.status_code == 200:
        with open(os.path.join(epub_dir, azw3_file), "wb") as file:
            file.write(azw3_response.content)
    else:
        print("Failed to download AZW3 file for " + title)

    thumbnail_response = requests.get(thumbnail_url)
    if thumbnail_response.status_code == 200:
        temp = thumbnail_response.headers["Content-Disposition"]
        thumb_file = temp.split("filename=")[1].strip("'\"")
        with open(os.path.join(image_dir, thumb_file), "wb") as file:
            file.write(thumbnail_response.content)
    else:
        print("Failed to download thumbnail image for " + title)


for collection in collections:
    downloadCollection(collection)
