"""A simple queue-based desktop front end for yt-dlp."""

import os
import shutil
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from tkinter import filedialog, messagebox

# When packaged as an .exe, make bundled tools such as FFmpeg discoverable.
if getattr(sys, "frozen", False):
    os.environ["PATH"] = str(Path(sys._MEIPASS)) + os.pathsep + os.environ.get("PATH", "")

import customtkinter as ctk

import downloader
import settings as settings_module
from tool_check import missing_tools_message

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


@dataclass
class QueueItem:
    url: str
    output_folder: str
    quality: str
    include_audio: bool
    keep_original: bool
    duplicate_mode: str
    title: str = "Video link"
    status: str = "Waiting"
    filepath: str | None = None
    error: str | None = None


class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Downloader")
        self.geometry("700x780")
        self.minsize(640, 680)

        self.cfg = settings_module.load_settings()
        self.queue: list[QueueItem] = []
        self.queue_thread: threading.Thread | None = None
        self.cancel_event = threading.Event()
        self.preview_url = ""
        self.preview_info: dict | None = None
        self.preview_image = None
        self.last_clipboard = ""

        self._build_ui()
        self._check_clipboard_for_url()

        missing = missing_tools_message()
        if missing:
            self.after(300, lambda: messagebox.showwarning("Missing requirements", missing))

    def _build_ui(self):
        pad_x = 20
        ctk.CTkLabel(self, text="Video Downloader", font=ctk.CTkFont(size=22, weight="bold")).pack(
            pady=(16, 2)
        )
        ctk.CTkLabel(
            self, text="Paste links, preview them, then download them one at a time.",
            font=ctk.CTkFont(size=11), text_color="gray60",
        ).pack(pady=(0, 12))

        ctk.CTkLabel(self, text="Video URL", anchor="w").pack(fill="x", padx=pad_x)
        url_row = ctk.CTkFrame(self, fg_color="transparent")
        url_row.pack(fill="x", padx=pad_x, pady=(2, 0))
        self.url_entry = ctk.CTkEntry(url_row, placeholder_text="https://...")
        self.url_entry.pack(side="left", fill="x", expand=True)
        self.url_entry.insert(0, self.cfg.get("last_url", ""))
        self.url_entry.bind("<Button-3>", self._show_url_context_menu)
        ctk.CTkButton(url_row, text="Paste", width=62, command=self._paste_url).pack(side="left", padx=(8, 0))
        ctk.CTkButton(url_row, text="Clear", width=62, command=self._clear_url).pack(side="left", padx=(6, 0))
        ctk.CTkButton(url_row, text="Preview", width=70, command=self._preview_clicked).pack(side="left", padx=(6, 0))

        preview = ctk.CTkFrame(self)
        preview.pack(fill="x", padx=pad_x, pady=(8, 6))
        self.thumbnail_label = ctk.CTkLabel(preview, text="", width=120, height=68)
        self.thumbnail_label.pack(side="left", padx=(8, 10), pady=8)
        self.preview_label = ctk.CTkLabel(
            preview, text="Preview a link to check its title before adding it to the queue.",
            justify="left", anchor="w", wraplength=480,
        )
        self.preview_label.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)

        options = ctk.CTkFrame(self, fg_color="transparent")
        options.pack(fill="x", padx=pad_x)
        left = ctk.CTkFrame(options, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        right = ctk.CTkFrame(options, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))

        ctk.CTkLabel(left, text="Output Folder", anchor="w").pack(fill="x")
        folder_row = ctk.CTkFrame(left, fg_color="transparent")
        folder_row.pack(fill="x", pady=(2, 8))
        self.folder_entry = ctk.CTkEntry(folder_row)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.folder_entry.insert(0, self.cfg.get("output_folder", str(Path.home() / "Downloads")))
        ctk.CTkButton(folder_row, text="Browse", width=68, command=self._browse_folder).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(left, text="Download Quality", anchor="w").pack(fill="x")
        self.quality_var = ctk.StringVar(value=self.cfg.get("quality", "best"))
        self.quality_labels = {
            "best": "Best Available",
            "1080p": "Up to 1080p",
            "audio_only": "Audio Only (MP3)",
        }
        quality_values_by_label = {label: value for value, label in self.quality_labels.items()}
        self.quality_display_var = ctk.StringVar(
            value=self.quality_labels.get(self.quality_var.get(), "Best Available")
        )
        quality_segmented = ctk.CTkSegmentedButton(
            left,
            values=list(self.quality_labels.values()),
            variable=self.quality_display_var,
            command=lambda label: self.quality_var.set(quality_values_by_label[label]),
        )
        quality_segmented.pack(fill="x", pady=(2, 6))
        self.mute_var = ctk.BooleanVar(value=not self.cfg.get("include_audio", True))
        self.include_audio_checkbox = ctk.CTkCheckBox(
            left, text="No sound (mute video)", variable=self.mute_var
        )
        self.include_audio_checkbox.pack(anchor="w", pady=(5, 0))
        self.quality_var.trace_add("write", self._update_audio_option)
        self._update_audio_option()

        ctk.CTkLabel(right, text="If a file already exists", anchor="w").pack(fill="x")
        self.duplicate_var = ctk.StringVar(value=self.cfg.get("duplicate_mode", "Rename automatically"))
        ctk.CTkOptionMenu(
            right, variable=self.duplicate_var,
            values=["Rename automatically", "Overwrite", "Ask me"],
        ).pack(fill="x", pady=(2, 12))
        self.keep_original_var = ctk.BooleanVar(value=self.cfg.get("keep_original", False))
        ctk.CTkCheckBox(
            right, text="Keep original video when making MP3", variable=self.keep_original_var,
        ).pack(anchor="w", pady=2)
        self.open_folder_var = ctk.BooleanVar(value=self.cfg.get("open_folder_when_finished", True))
        ctk.CTkCheckBox(right, text="Open folder when queue finishes", variable=self.open_folder_var).pack(anchor="w", pady=2)
        self.remove_completed_var = ctk.BooleanVar(value=self.cfg.get("remove_completed", False))
        ctk.CTkCheckBox(right, text="Remove completed items automatically", variable=self.remove_completed_var).pack(anchor="w", pady=2)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=pad_x, pady=(12, 8))
        self.add_btn = ctk.CTkButton(actions, text="Add to Queue", command=self._add_to_queue)
        self.add_btn.pack(side="left", fill="x", expand=True)
        self.start_btn = ctk.CTkButton(actions, text="Start Queue", command=self._start_queue)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=8)
        self.cancel_btn = ctk.CTkButton(actions, text="Pause Current", fg_color="#9b6b30", command=self._cancel_current)
        self.cancel_btn.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(self, text="Download Queue", anchor="w").pack(fill="x", padx=pad_x)
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=pad_x, pady=(3, 6))
        self.queue_listbox = tk.Listbox(
            list_frame, selectmode=tk.SINGLE, activestyle="none", bg="#202020", fg="#eeeeee",
            selectbackground="#1f6aa5", selectforeground="#ffffff", borderwidth=0,
            highlightthickness=0, font=("Segoe UI", 10),
        )
        self.queue_listbox.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scrollbar = tk.Scrollbar(list_frame, command=self.queue_listbox.yview)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 8))
        self.queue_listbox.configure(yscrollcommand=scrollbar.set)

        history_actions = ctk.CTkFrame(self, fg_color="transparent")
        history_actions.pack(fill="x", padx=pad_x, pady=(0, 8))
        ctk.CTkButton(history_actions, text="Remove Selected", width=125, command=self._remove_selected).pack(side="left")
        ctk.CTkButton(history_actions, text="Open Selected File", width=135, command=self._open_selected_file).pack(side="left", padx=8)
        ctk.CTkButton(history_actions, text="Open Selected Folder", width=145, command=self._open_selected_folder).pack(side="left")
        ctk.CTkButton(history_actions, text="Clear Completed", width=120, command=self._clear_completed).pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=pad_x, pady=(2, 3))
        self.status_label = ctk.CTkLabel(self, text="Add a link to begin.", anchor="w")
        self.status_label.pack(fill="x", padx=pad_x, pady=(0, 12))

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_entry.get() or str(Path.home()))
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def _paste_url(self):
        try:
            clipboard_text = self.clipboard_get()
            self.url_entry.insert("insert", clipboard_text)
        except tk.TclError:
            pass

    def _clear_url(self):
        self.url_entry.delete(0, "end")
        self.url_entry.focus()

    def _show_url_context_menu(self, event):
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label="Paste", command=self._paste_url)
        menu.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        menu.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.url_entry._entry.select_range(0, "end"))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def _update_audio_option(self, *_args):
        self.include_audio_checkbox.configure(
            state="disabled" if self.quality_var.get() == "audio_only" else "normal"
        )

    def _check_clipboard_for_url(self):
        if not HAS_CLIPBOARD:
            return
        try:
            clip = pyperclip.paste().strip()
        except Exception:
            clip = None
        if clip and clip != self.last_clipboard and downloader.is_valid_url(clip):
            current = self.url_entry.get().strip()
            # Only auto-fill if the box is empty or still holds the last clip we
            # auto-filled, so we never overwrite something the user typed themselves.
            if not current or current == self.last_clipboard:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clip)
        if clip is not None:
            self.last_clipboard = clip
        # Keep checking every 1.5s so links copied after launch are picked up too.
        self.after(1500, self._check_clipboard_for_url)

    def _preview_clicked(self):
        url = self.url_entry.get().strip()
        if not downloader.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Paste a valid http:// or https:// video link first.")
            return
        self.preview_label.configure(text="Looking up video information...")
        threading.Thread(target=self._load_preview, args=(url,), daemon=True).start()

    def _load_preview(self, url: str):
        try:
            info = downloader.get_video_info(url)
            self.after(0, self._show_preview, url, info)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self.preview_label.configure(text=f"Preview unavailable: {exc}"))

    def _show_preview(self, url: str, info: dict):
        self.preview_url = url
        self.preview_info = info
        if info.get("is_playlist"):
            count = len(info.get("entries") or [])
            self.thumbnail_label.configure(image=None, text="")
            self.preview_image = None
            self.preview_label.configure(
                text=f"Playlist: {info.get('playlist_title', 'Playlist')}\n{count} videos found"
            )
            return
        duration = info.get("duration")
        minutes = f" • {duration // 60}:{duration % 60:02d}" if isinstance(duration, int) else ""
        uploader = f"\n{info.get('uploader')}" if info.get("uploader") else ""
        self.preview_label.configure(text=f"{info.get('title', 'Video')}{uploader}{minutes}")
        thumbnail = info.get("thumbnail")
        if thumbnail and Image is not None:
            threading.Thread(target=self._load_thumbnail, args=(thumbnail,), daemon=True).start()

    def _load_thumbnail(self, thumbnail_url: str):
        try:
            image = Image.open(BytesIO(urlopen(thumbnail_url, timeout=10).read())).convert("RGBA")
            display_image = ctk.CTkImage(light_image=image, dark_image=image, size=(120, 68))
            self.after(0, self._show_thumbnail, display_image)
        except Exception:
            pass

    def _show_thumbnail(self, image):
        self.preview_image = image
        self.thumbnail_label.configure(image=image, text="")

    def _add_to_queue(self):
        url = self.url_entry.get().strip()
        if not downloader.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Paste a valid http:// or https:// video link first.")
            return
        output_folder = self.folder_entry.get().strip()
        try:
            Path(output_folder).mkdir(parents=True, exist_ok=True)
        except OSError:
            messagebox.showerror("Folder Error", "The output folder path is not valid.")
            return

        previewed = self.preview_url == url and self.preview_info

        if previewed and self.preview_info.get("is_playlist"):
            entries = self.preview_info.get("entries") or []
            if not entries:
                messagebox.showwarning(
                    "Empty Playlist", "No downloadable videos were found in this playlist."
                )
                return
            playlist_title = self.preview_info.get("playlist_title", "this playlist")
            add_all = messagebox.askyesno(
                "Playlist Detected",
                f"\"{playlist_title}\" has {len(entries)} videos.\n\n"
                "Add all of them to the queue? Each video downloads and can be "
                "paused/resumed separately.\n\n"
                "Choose No to add only the single link you pasted instead.",
            )
            if add_all:
                for entry in entries:
                    self.queue.append(QueueItem(
                        url=entry["url"], output_folder=output_folder, quality=self.quality_var.get(),
                        include_audio=not self.mute_var.get(), keep_original=self.keep_original_var.get(),
                        duplicate_mode=self.duplicate_var.get(), title=entry.get("title", "Video link"),
                    ))
                self._save_settings(output_folder)
                self._refresh_queue()
                self.status_label.configure(
                    text=f"Added {len(entries)} videos from the playlist to the queue."
                )
                self._clear_url()
                return
            # Falls through to add just the pasted URL as a single item below.

        title = self.preview_info.get("title", "Video link") if previewed and not self.preview_info.get("is_playlist") else "Video link"
        self.queue.append(QueueItem(
            url=url, output_folder=output_folder, quality=self.quality_var.get(),
            include_audio=not self.mute_var.get(), keep_original=self.keep_original_var.get(),
            duplicate_mode=self.duplicate_var.get(), title=title,
        ))
        self._save_settings(output_folder)
        self._refresh_queue()
        self.status_label.configure(text="Added to queue. You can add another link or start downloading.")
        self._clear_url()
        self._clear_url()

    def _save_settings(self, output_folder: str):
        self.cfg.update({
            "output_folder": output_folder, "quality": self.quality_var.get(),
            "include_audio": not self.mute_var.get(), "keep_original": self.keep_original_var.get(),
            "duplicate_mode": self.duplicate_var.get(), "open_folder_when_finished": self.open_folder_var.get(),
            "remove_completed": self.remove_completed_var.get(), "last_url": self.url_entry.get().strip(),
        })
        settings_module.save_settings(self.cfg)

    def _refresh_queue(self):
        self.queue_listbox.delete(0, tk.END)
        for item in self.queue:
            label = item.title if item.title != "Video link" else item.url
            self.queue_listbox.insert(tk.END, f"[{item.status}]  {label}")

    def _start_queue(self):
        if self.queue_thread and self.queue_thread.is_alive():
            return
        if not any(item.status in ("Waiting", "Paused") for item in self.queue):
            self.status_label.configure(text="There are no waiting or paused downloads in the queue.")
            return
        missing = missing_tools_message()
        if missing:
            messagebox.showerror("Missing requirements", missing)
            return
        self.cancel_event.clear()
        self.queue_thread = threading.Thread(target=self._run_queue, daemon=True)
        self.queue_thread.start()

    def _cancel_current(self):
        if self.queue_thread and self.queue_thread.is_alive():
            self.cancel_event.set()
            self.status_label.configure(text="Pausing after the current download check...")

    def _run_queue(self):
        for item in self.queue:
            if self.cancel_event.is_set():
                break
            if item.status not in ("Waiting", "Paused"):
                continue
            self.after(0, self._set_item_downloading, item)
            try:
                result = downloader.download_video(
                    url=item.url, output_dir=item.output_folder, quality=item.quality,
                    include_audio=item.include_audio, keep_original=item.keep_original,
                    duplicate_mode=item.duplicate_mode, cancel_event=self.cancel_event,
                    duplicate_callback=self._ask_duplicate_action,
                    progress_callback=lambda info, queued_item=item: self._queue_progress(queued_item, info),
                )
                item.title = result.title
                item.filepath = result.filepath
                item.status = "Done"
            except downloader.DownloadCancelled:
                item.status = "Paused"
                self.cancel_event.set()
            except Exception as exc:  # noqa: BLE001
                item.status = "Failed"
                item.error = str(exc)
            self.after(0, self._refresh_queue)
        self.after(0, self._queue_finished)

    def _set_item_downloading(self, item: QueueItem):
        item.status = "Downloading"
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Downloading: {item.title}")
        self._refresh_queue()

    def _ask_duplicate_action(self, filepath: str) -> str:
        """Ask on the UI thread while the queue worker waits for the answer."""
        response: dict[str, str] = {}
        answered = threading.Event()

        def ask():
            answer = messagebox.askyesnocancel(
                "File already exists",
                f"{Path(filepath).name} already exists.\n\n"
                "Yes: overwrite it\nNo: save a second copy with a unique name\nCancel: skip this download",
            )
            response["action"] = "overwrite" if answer is True else "rename" if answer is False else "skip"
            answered.set()

        self.after(0, ask)
        answered.wait()
        return response["action"]

    def _queue_progress(self, item: QueueItem, info: dict):
        if info["status"] == "downloading":
            pct = info.get("percent")
            if pct is not None:
                self.after(0, self._show_download_progress, pct, info["speed"], info["eta"])
        elif info["status"] == "finished":
            self.after(0, self._show_processing)

    def _show_download_progress(self, percent: float, speed: str, eta: str):
        self.progress_bar.set(percent / 100)
        self.status_label.configure(text=f"Downloading: {percent:.0f}%  •  {speed}  •  ETA {eta}")

    def _show_processing(self):
        self.progress_bar.set(1)
        self.status_label.configure(text="Processing download...")

    def _queue_finished(self):
        if self.cancel_event.is_set():
            self.status_label.configure(
                text="Queue paused. Click Start Queue to resume the paused download and continue."
            )
        else:
            self.status_label.configure(text="Queue finished.")
            if self.open_folder_var.get() and self.queue:
                try:
                    os.startfile(self.queue[-1].output_folder)
                except OSError:
                    pass
        if self.remove_completed_var.get():
            self.queue = [item for item in self.queue if item.status != "Done"]
        self._refresh_queue()

    def _selected_item(self) -> QueueItem | None:
        selected = self.queue_listbox.curselection()
        return self.queue[selected[0]] if selected else None

    def _remove_selected(self):
        item = self._selected_item()
        if item is None:
            return
        if item.status == "Downloading":
            messagebox.showinfo("Queue", "Pause the current download before removing it.")
            return
        self.queue.remove(item)
        self._refresh_queue()

    def _clear_completed(self):
        self.queue = [item for item in self.queue if item.status not in {"Done", "Failed"}]
        self._refresh_queue()

    def _open_selected_file(self):
        item = self._selected_item()
        if not item or not item.filepath:
            messagebox.showinfo("Open File", "Select a completed download first.")
            return
        try:
            os.startfile(item.filepath)
        except OSError:
            messagebox.showerror("Open File", "The file could not be opened.")

    def _open_selected_folder(self):
        item = self._selected_item()
        if item is None:
            messagebox.showinfo("Open Folder", "Select a queue item first.")
            return
        try:
            os.startfile(item.output_folder)
        except OSError:
            messagebox.showerror("Open Folder", "The folder could not be opened.")


if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()