import requests
import openai
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



font_path = "arial.ttf"


pdfmetrics.registerFont(TTFont("Arial", font_path))





def export_to_pdf(title, content):

    pdf_file = f"{title}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)


    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles["Title"]))


    styles = getSampleStyleSheet()
    content_paragraph = Paragraph(content, styles["Normal"])
    content_paragraph.fontName = "Arial" 
    elements.append(content_paragraph)


    doc.build(elements)

    print(f"Exported to {pdf_file}")





    

def split_text(text, max_len):

    words = text.split()
    chunks = []
    chunk = ""
    for word in words:

        if len(chunk) + len(word) + 1 > max_len:
            chunks.append(chunk.strip())
            chunk = ""

        chunk += " " + word

    if chunk:
        chunks.append(chunk.strip())
    return chunks
def translate(lang, text):
    key = 'sk-yourkey'
    openai.api_key = key
    print("Translating to:", lang)
    print("Please wait ... ")
    chunks = split_text(text, 990)
    translated_chunks = []
    for chunk in chunks:
        translation = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Translate this {len(chunk)}-character text into {lang}: {chunk}",
            temperature=0.7,
            max_tokens=1024,
            n=1,
            timeout=10,
            stop=None
        )
        translated_text = translation.choices[0].text.strip()
        translated_chunks.append(translated_text)
    translated_text = " ".join(translated_chunks)
    return translated_text

def save_to_file(lang,title, content, content_trans):
    f = open('Data.txt', 'w', encoding="utf-8")
    f.write("Title: ")
    f.writelines(title)
    f.write("\n")
    f.write("Content: ")
    f.writelines(content)
    f.write("\n")
    f.write("Translate: ")
    f.writelines(translate(lang, content_trans))
    f.write("\n")
    f.close()


def crawlContent(nPage, lang):
    url = "https://vnexpress.net"

    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html.parser", from_encoding='utf-8')

    article_links = [a['href'] for i, a in enumerate(soup.select('h3.title-news a[href]')) if i < nPage]
    print(article_links)

    for link in article_links:
        article_req = requests.get(link)
        article_soup = BeautifulSoup(article_req.content, "html.parser")

        title = article_soup.find('h1', {'class': 'title-detail'})
        if title is None:
            break
        else:
            title = title.text.strip()
        content = [p.get_text() for p in article_soup.find_all('p')]
        string = ''.join(content)
        print("Title:", title)

        if not string.startswith("Translated to"):
            chunks = [string[i:i + 1000] for i in range(0, len(string), 1000)]
            translated_chunks = []

            for chunk in chunks:
                translated_chunk = translate(lang, chunk)
                translated_chunks.append(translated_chunk)

            translated_string = ''.join(translated_chunks)

            print("Translating is in progress. Please wait ... ")
            print(translated_string)
            print('\n')

            export_to_pdf(title, translated_string)


if __name__ == "__main__":
    lang = input("Enter language to translate: ")
    crawlContent(1, lang)
    print ("Done translation")
