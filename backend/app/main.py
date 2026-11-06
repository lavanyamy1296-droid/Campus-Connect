from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "campus.db"
app = FastAPI(title="Campus Connect API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS announcements(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,body TEXT NOT NULL,category TEXT DEFAULT 'General',author TEXT DEFAULT 'Admin',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,date TEXT NOT NULL,venue TEXT NOT NULL,attendees INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT,author TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,likes INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS lost_found(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,kind TEXT NOT NULL,location TEXT NOT NULL,contact TEXT NOT NULL,details TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        if con.execute("SELECT COUNT(*) FROM announcements").fetchone()[0] == 0:
            con.executemany("INSERT INTO announcements(title,body,category,author) VALUES(?,?,?,?)", [
                ("Welcome to the new semester", "A fresh semester begins! Check your timetable and make the most of every opportunity.", "Campus", "Principal's Office"),
                ("Library hours extended", "The central library will remain open until 8:00 PM on weekdays during examination preparation.", "Academics", "Library Team"),
                ("TechFest registrations are open", "Showcase your ideas, join workshops and compete with the brightest minds on campus.", "Events", "Student Council")])
            con.executemany("INSERT INTO events(title,description,date,venue,attendees) VALUES(?,?,?,?,?)", [
                ("Campus TechFest 2026", "A day of coding battles, demos, workshops and innovation.", "2026-11-18", "Main Auditorium", 128),
                ("Cultural Evening", "Music, dance and performances from our student community.", "2026-11-24", "Open Air Stage", 86),
                ("Career Connect", "Meet industry mentors and get your resume reviewed.", "2026-12-02", "Seminar Hall", 54)])
            con.executemany("INSERT INTO posts(author,content,likes) VALUES(?,?,?)", [
                ("Aarav • CSE", "Anyone forming a team for the upcoming hackathon? Looking for two frontend developers!", 12),
                ("Meera • AIML", "The AI club is hosting a beginner-friendly Python study circle this Friday. Everyone is welcome.", 8)])
            con.executemany("INSERT INTO lost_found(title,kind,location,contact,details) VALUES(?,?,?,?,?)", [
                ("Blue water bottle", "Found", "Library - 2nd floor", "campus@example.com", "Found near the reading area. Claim it at the help desk.")])

@app.on_event("startup")
def startup():
    init_db()

class AnnouncementIn(BaseModel):
    title: str
    body: str
    category: str = "General"
    author: str = "Campus Admin"

class EventIn(BaseModel):
    title: str
    description: str
    date: str
    venue: str

class PostIn(BaseModel):
    author: str = "Student"
    content: str

class LostIn(BaseModel):
    title: str
    kind: str = "Lost"
    location: str
    contact: str
    details: str

def rows(sql, params=()):
    with connect() as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Campus Connect"}

@app.get("/api/announcements")
def announcements():
    return rows("SELECT * FROM announcements ORDER BY id DESC")

@app.post("/api/announcements")
def add_announcement(item: AnnouncementIn):
    with connect() as con:
        cur = con.execute("INSERT INTO announcements(title,body,category,author) VALUES(?,?,?,?)", (item.title,item.body,item.category,item.author))
        return dict(con.execute("SELECT * FROM announcements WHERE id=?", (cur.lastrowid,)).fetchone())

@app.get("/api/events")
def events():
    return rows("SELECT * FROM events ORDER BY date")

@app.post("/api/events")
def add_event(item: EventIn):
    with connect() as con:
        cur = con.execute("INSERT INTO events(title,description,date,venue) VALUES(?,?,?,?)", (item.title,item.description,item.date,item.venue))
        return dict(con.execute("SELECT * FROM events WHERE id=?", (cur.lastrowid,)).fetchone())

@app.post("/api/events/{event_id}/register")
def register_event(event_id: int):
    with connect() as con:
        cur = con.execute("UPDATE events SET attendees=attendees+1 WHERE id=?", (event_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Event not found")
        return {"message": "Registration recorded"}

@app.get("/api/posts")
def posts():
    return rows("SELECT * FROM posts ORDER BY id DESC")

@app.post("/api/posts")
def add_post(item: PostIn):
    with connect() as con:
        cur = con.execute("INSERT INTO posts(author,content) VALUES(?,?)", (item.author,item.content))
        return dict(con.execute("SELECT * FROM posts WHERE id=?", (cur.lastrowid,)).fetchone())

@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int):
    with connect() as con:
        cur = con.execute("UPDATE posts SET likes=likes+1 WHERE id=?", (post_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Post not found")
        return {"message": "Liked"}

@app.get("/api/lost-found")
def lost_found():
    return rows("SELECT * FROM lost_found ORDER BY id DESC")

@app.post("/api/lost-found")
def add_lost(item: LostIn):
    with connect() as con:
        cur = con.execute("INSERT INTO lost_found(title,kind,location,contact,details) VALUES(?,?,?,?,?)", (item.title,item.kind,item.location,item.contact,item.details))
        return dict(con.execute("SELECT * FROM lost_found WHERE id=?", (cur.lastrowid,)).fetchone())
