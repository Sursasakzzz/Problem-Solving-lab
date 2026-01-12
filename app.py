import streamlit as st

# ---------- Song Class ----------
class Song:
    def __init__(self, title, artist, audio_bytes):
        self.title = title
        self.artist = artist
        self.audio_bytes = audio_bytes
        self.next = None

    def __str__(self):
        return f"{self.title} by {self.artist}"


# ---------- MusicPlaylist Class (Linked List) ----------
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current = None
        self.length = 0

    def add_song(self, title, artist, audio_bytes):
        song = Song(title, artist, audio_bytes)
        if not self.head:
            self.head = song
            self.current = song
        else:
            node = self.head
            while node.next:
                node = node.next
            node.next = song
        self.length += 1
        st.success(f"Added: {song}")

    def show(self):
        items = []
        node = self.head
        i = 1
        while node:
            mark = "▶️ " if node == self.current else ""
            items.append(f"{mark}{i}. {node.title} - {node.artist}")
            node = node.next
            i += 1
        return items

    def play(self):
        if self.current:
            st.info(f"Now playing: {self.current}")
            st.audio(self.current.audio_bytes)
        else:
            st.warning("No song selected")

    def next_song(self):
        if self.current and self.current.next:
            self.current = self.current.next
        else:
            st.warning("End of playlist")

    def prev_song(self):
        if self.current == self.head:
            st.warning("Already first song")
            return
        node = self.head
        while node.next != self.current:
            node = node.next
        self.current = node

    def delete(self, title):
        if not self.head:
            return
        if self.head.title == title:
            self.head = self.head.next
            self.current = self.head
            self.length -= 1
            return
        prev = self.head
        node = self.head.next
        while node:
            if node.title == title:
                prev.next = node.next
                self.length -= 1
                return
            prev = node
            node = node.next


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Music Playlist", page_icon="🎶")
st.title("🎶 Music Playlist App")

# Force re-initialization of the playlist to ensure the latest class definition is used
st.session_state.playlist = MusicPlaylist()

st.sidebar.header("➕ Add Song")
title = st.sidebar.text_input("Song Title")
artist = st.sidebar.text_input("Artist")
file = st.sidebar.file_uploader("Upload audio", type=["mp3", "wav", "ogg"])

if st.sidebar.button("Add"):
    if title and artist and file:
        st.session_state.playlist.add_song(title, artist, file.read())

st.sidebar.markdown("---")
del_title = st.sidebar.text_input("Delete by title")
if st.sidebar.button("Delete"):
    st.session_state.playlist.delete(del_title)

st.header("📃 Playlist")
for s in st.session_state.playlist.show():
    st.write(s)

st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("⏪ Prev"):
        st.session_state.playlist.prev_song()
        st.session_state.playlist.play()

with c2:
    if st.button("▶️ Play"):
        st.session_state.playlist.play()

with c3:
    if st.button("⏩ Next"):
        st.session_state.playlist.next_song()
        st.session_state.playlist.play()

st.write(f"Total songs: {st.session_state.playlist.length}")
