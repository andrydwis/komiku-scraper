import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

app_url = "https://komiku.id"
api_url = "https://api.komiku.id"


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs"}


@app.get("/manga/search")
async def search(keyword: str):
    html = httpx.get(
        api_url + "/?post_type=manga&s=" + keyword,
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        link = manga.find("a")["href"]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        genres = [{"id": genre_id, "name": genre}]
        mangas.append(
            {
                "id": id,
                "title": title,
                "description": description,
                "image": image,
                "link": link,
                "main_genres": genres,
            }
        )

    return mangas


@app.get("/manga/recent-update")
async def get_recent_update(page: int = 1):
    html = httpx.get(
        api_url + "/manga/page/" + str(page) + "/?orderby=modified",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        link = manga.find("a")["href"]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        genres = [{"id": genre_id, "name": genre}]

        mangas.append(
            {
                "id": id,
                "title": title,
                "description": description,
                "genres": genres,
                "link": link,
                "image": image,
            }
        )

    return mangas


@app.get("/manga/popular")
async def get_popular(page: int = 1):
    html = httpx.get(
        api_url + "/manga/page/" + str(page) + "/?orderby=meta_value_num",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        link = manga.find("a")["href"]

        mangas.append(
            {
                "id": id,
                "title": title,
                "description": description,
                "link": link,
                "image": image,
            }
        )

    return mangas


@app.get("/manga/{id}")
async def get_manga(id: str):
    html = httpx.get(app_url + "/manga/" + id, follow_redirects=True)

    soup = BeautifulSoup(html.content, "html.parser")

    title_tag = soup.find("td", text="Judul Komik")
    title = title_tag.find_next_sibling("td").text.strip()

    author_tag = soup.find("td", text="Pengarang")
    author = author_tag.find_next_sibling("td").text.strip()

    status_tag = soup.find("td", text="Status")
    status = status_tag.find_next_sibling("td").text.strip()

    image = soup.find("section", id="Informasi").find("img")["src"].split("?")[0]

    genres = []
    for genre in soup.find("li", class_="genre").find_all("a"):
        id = genre["href"].split("/")[-2]
        name = genre.text.strip()
        genres.append({"id": id, "name": name})

    chapters_section = soup.find("table", id="Daftar_Chapter")
    chapters = []
    for chapter in chapters_section.find_all("tr")[1:]:
        id = chapter.find("a")["href"].split("/")[-2]
        title = chapter.find("a").text.strip()
        date = chapter.find("td", class_="tanggalseries").text.strip()
        chapters.append({"id": id, "title": title, "date": date})

    return {
        "id": id,
        "title": title,
        "author": author,
        "status": status,
        "image": image,
        "genres": genres,
        "chapters": chapters,
    }


@app.get("/chapter/{id}")
async def get_chapter(id: str):
    html = httpx.get(app_url + "/" + id, follow_redirects=True)

    soup = BeautifulSoup(html.text, "html.parser")

    title_tag = soup.find("td", text="Judul")
    title = title_tag.find_next_sibling("td").text.strip()

    date_tag = soup.find("td", text="Tanggal Rilis")
    date = date_tag.find_next_sibling("td").text.strip()

    pages = []
    for page in soup.find_all("img", class_="ww"):
        page_number = page["id"]
        image = page["src"]
        pages.append({"page_number": page_number, "image": image})

    return {
        "id": id,
        "title": title,
        "date": date,
        "pages": pages,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("routes:app", host="0.0.0.0", port=8001, reload=True)
