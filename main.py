from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from schemas import Book, Chapter
from bible_data import load_all_books, get_book as lookup_book


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_books()
    yield


app = FastAPI(
    title="Ethiopic Bible API",
    description="An API for accessing the books of the Ethiopic Bible in Amharic.",
    version="1.0.0",
    lifespan=lifespan,
)

# GZip compression for responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS — allow all origins (tighten in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", summary="Health Check")
async def health():
    """Returns service status. Used by the keep-alive ping to prevent Render free tier from sleeping."""
    return {"status": "ok"}


def get_book_data(book_name: str) -> dict:
    """Look up a book from the in-memory cache."""
    data = lookup_book(book_name)
    if data is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return data

@app.get("/book/{book_name}", response_model=Book, summary="Retrieve a Book")
async def get_book(book_name: str):
    """
     **Fetches a specific book by its name**. For example, use **'ኦሪት ዘፍጥረት'** to retrieve the book of Genesis. The book name should match the file name in the data directory (case-insensitive)
  
    - ኦሪት ዘፍጥረት
    - ኦሪት ዘጸአት
    - ኦሪት ዘሌዋውያን
    - ኦሪት ዘኍልቍ
    - ኦሪት ዘዳግም
    - መጽሐፈ ኢያሱ ወልደ ነዌ
    - መጽሐፈ መሣፍንት
    - መጽሐፈ ሩት
    - መጽሐፈ ሳሙኤል ቀዳማዊ
    - መጽሐፈ ሳሙኤል ካል
    - መጽሐፈ ነገሥት ቀዳማዊ
    - መጽሐፈ ነገሥት ካልዕ
    - መጽሐፈ ዜና መዋዕል ቀዳማዊ
    - መጽሐፈ ዜና መዋዕል ካልዕ
    - መጽሐፈ ዕዝራ
    - መጽሐፈ ነህምያ
    - መጽሐፈ አስቴር
    - መጽሐፈ ኢዮብ
    - መዝሙረ ዳዊት
    - መጽሐፈ ምሳሌ
    - መጽሐፈ መክብብ
    - መኃልየ መኃልይ ዘሰሎሞን
    - ትንቢተ ኢሳይያስ
    - ትንቢተ ኤርምያስ
    - ሰቆቃው ኤርምያስ
    - ትንቢተ ሕዝቅኤል
    - ትንቢተ ዳንኤል
    - ትንቢተ ሆሴዕ
    - ትንቢተ ኢዮኤል
    - ትንቢተ አሞጽ
    - ትንቢተ አብድዩ
    - ትንቢተ ዮናስ
    - ትንቢተ ሚክያስ
    - ትንቢተ ናሆም
    - ትንቢተ ዕንባቆም
    - ትንቢተ ሶፎንያስ
    - ትንቢተ ሐጌ
    - ትንቢተ ዘካርያስ
    - ትንቢተ ሚልክያ
    - የማቴዎስ ወንጌል
    - የማርቆስ ወንጌል
    - የሉቃስ ወንጌል
    - የዮሐንስ ወንጌል
    - የሐዋርያት ሥራ
    - ወደ ሮሜ ሰዎች
    - 1ኛ ወደ ቆሮንቶስ ሰዎች
    - 2ኛ ወደ ቆሮንቶስ ሰዎች
    - ወደ ገላትያ ሰዎች
    - ወደ ኤፌሶን ሰዎች
    - ወደ ፊልጵስዩስ ሰዎች
    - ወደ ቆላስይስ ሰዎች
    - 1ኛ ወደ ተሰሎንቄ ሰዎች
    - 2ኛ ወደ ተሰሎንቄ ሰዎች
    - 1ኛ ወደ ጢሞቴዎስ
    - 2ኛ ወደ ጢሞቴዎስ
    - ወደ ቲቶ
    - ወደ ፊልሞና
    - ወደ ዕብራውያን
    - የያዕቆብ መልእክት
    - 1ኛ የጴጥሮስ መልእክት
    - 2ኛ የጴጥሮስ መልእክት
    - 1ኛ የዮሐንስ መልእክት
    - 2ኛ የዮሐንስ መልእክት
    - 3ኛ የዮሐንስ መልእክት
    - የይሁዳ መልእክት
    - የዮሐንስ ራእይ
    """
    return get_book_data(book_name)

@app.get("/book/{book_name}/chapter/{chapter_number}", response_model=Chapter, summary="Retrieve a Chapter", description="Fetches a specific chapter from a book by its chapter number. The chapter number should match the chapter identifier in the book's data.")
async def get_chapter(book_name: str, chapter_number: str):
    book = get_book_data(book_name)
    chapter = next((ch for ch in book['chapters'] if ch['chapter'] == chapter_number), None)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@app.get("/book/{book_name}/chapter/{chapter_number}/verse/{verse_number}", summary="Retrieve a Verse", description="Fetches a specific verse from a chapter in a book by its verse number. The verse number should be within the range of verses in the chapter.")
async def get_verse(book_name: str, chapter_number: str, verse_number: int):
    book = get_book_data(book_name)
    chapter = next((ch for ch in book['chapters'] if ch['chapter'] == chapter_number), None)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if 0 <= verse_number < len(chapter['verses']):
        return {"verse": verse_number, "text": chapter['verses'][verse_number]}
    raise HTTPException(status_code=404, detail="Verse not found")
