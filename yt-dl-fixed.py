import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil

# URL test (playlist): https://www.youtube.com/playlist?list=PLsJMz620V0MWTBgpGrRhvWcKP0zIbnkq_

# Variable globale pour éviter les exécutions multiples
_app_initialized = False

# Vérifie si un module est installé (pour les versions compilées, on assume qu'ils sont inclus)
def install_package(package):
    try:
        __import__(package)
        return True
    except ImportError:
        # En mode compilé, on ne peut pas installer de packages
        if getattr(sys, 'frozen', False):
            messagebox.showerror("Erreur", f"Module {package} manquant dans l'exécutable compilé.")
            return False
        else:
            # En mode développement uniquement
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                return True
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'installer {package}: {e}")
                return False

# Vérifie la présence de yt-dlp (inclus dans l'exécutable compilé)
def ensure_yt_dlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        if getattr(sys, 'frozen', False):
            messagebox.showerror("Erreur", "yt-dlp manquant dans l'exécutable compilé.")
            return False
        else:
            try:
                subprocess.run(["yt-dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("Installation de yt-dlp en cours...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                    return True
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'installer yt-dlp: {e}")
                    return False

# Télécharge et installe ffmpeg dans le dossier local si nécessaire
def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return True

    # En mode compilé, on ne peut pas télécharger ffmpeg automatiquement
    if getattr(sys, 'frozen', False):
        messagebox.showwarning("FFmpeg manquant", 
                             "FFmpeg n'est pas installé. Veuillez l'installer manuellement ou le placer dans le même dossier que l'exécutable.")
        return False

    try:
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        import requests, zipfile, io

        messagebox.showinfo("FFmpeg", "Téléchargement de FFmpeg en cours...")

        r = requests.get(ffmpeg_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        extract_path = os.path.join(os.getcwd(), "ffmpeg")
        z.extractall(extract_path)

        # Ajoute ffmpeg dans le PATH temporairement
        bin_path = next((os.path.join(extract_path, d, "bin") for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))), None)
        if bin_path:
            os.environ["PATH"] += os.pathsep + bin_path
        return True
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de télécharger FFmpeg: {e}")
        return False

# Fonctions pour choisir les dossiers de destination
def choose_output_dir_video():
    directory = filedialog.askdirectory(title="Choisissez le dossier de destination pour la vidéo")
    if directory:
        output_dir_video.set(directory)

def choose_output_dir_playlist():
    directory = filedialog.askdirectory(title="Choisissez le dossier de destination pour la playlist")
    if directory:
        output_dir_playlist.set(directory)

# Télécharge la vidéo ou playlist en MP3
def download():
    # Détermine quel onglet est actif
    current_tab = notebook.tab(notebook.select(), "text")
    is_playlist = (current_tab == "Playlist")
    
    if is_playlist:
        url = url_entry_playlist.get().strip()
        output_dir = output_dir_playlist.get().strip()
        urls = [url] if url else []
    else:
        # Pour l'onglet vidéo(s), récupère toutes les lignes
        url_text_content = url_text_video.get("1.0", tk.END).strip()
        urls = [line.strip() for line in url_text_content.split('\n') if line.strip()]
        output_dir = output_dir_video.get().strip()
    
    if not urls:
        messagebox.showerror("Erreur", "Veuillez entrer au moins une URL.")
        return
    
    if not output_dir:
        messagebox.showerror("Erreur", "Veuillez choisir un dossier de destination.")
        return

    # Désactive le bouton pendant le téléchargement
    download_btn.config(state='disabled')
    status_label.config(text="Téléchargement en cours...", fg="orange")
    root.update()

    # En mode compilé, utilise yt_dlp directement
    if getattr(sys, 'frozen', False):
        # Vérification de FFmpeg pour la conversion MP3
        if not shutil.which("ffmpeg"):
            messagebox.showerror("FFmpeg requis", 
                               "FFmpeg est nécessaire pour convertir en MP3.\n"
                               "Veuillez placer ffmpeg.exe dans le même dossier que l'exécutable.")
            download_btn.config(state='normal')
            return
            
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }, {
                    'key': 'FFmpegMetadata',
                }, {
                    'key': 'EmbedThumbnail',
                }],
                'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                'restrictfilenames': True,
                'windowsfilenames': True,
                'ignoreerrors': True,
                'noplaylist': not is_playlist,
                'writethumbnail': True,
            }
            
            total_downloaded = 0
            total_urls = len(urls)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for i, url in enumerate(urls, 1):
                    try:
                        status_label.config(text=f"Téléchargement en cours... ({i}/{total_urls})", fg="orange")
                        root.update()
                        ydl.download([url])
                        total_downloaded += 1
                    except Exception as e:
                        print(f"Erreur pour l'URL {url}: {e}")
            
            status_label.config(text="Prêt", fg="green")
            if total_downloaded > 0:
                messagebox.showinfo("Succès", f"Téléchargement terminé!\n{total_downloaded}/{total_urls} vidéo(s) téléchargée(s).")
            else:
                messagebox.showerror("Erreur", "Aucune vidéo n'a pu être téléchargée.")
            
        except Exception as e:
            status_label.config(text="Erreur", fg="red")
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")
    else:
        # Mode développement - utilise subprocess
        total_downloaded = 0
        total_urls = len(urls)
        error_messages = []
        
        for i, url in enumerate(urls, 1):
            status_label.config(text=f"Téléchargement en cours... ({i}/{total_urls})", fg="orange")
            root.update()
            
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-x", "--audio-format", "mp3",
                "--audio-quality", "192K",
                "--embed-thumbnail",
                "--add-metadata",
                "--restrict-filenames",
                "--windows-filenames",
                "--ignore-errors",
                "-o", os.path.join(output_dir, "%(title).100s.%(ext)s"),
                url
            ]

            if is_playlist:
                cmd.append("--yes-playlist")
            else:
                cmd.append("--no-playlist")

            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', bufsize=1, universal_newlines=True)
                
                video_downloaded = False
                
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if "[download]" in line and "100%" in line:
                        video_downloaded = True
                        status_label.config(text=f"Téléchargement en cours... ({i}/{total_urls}) - Terminé", fg="orange")
                        root.update()
                    
                    elif "ERROR:" in line:
                        error_messages.append(f"URL {i}: {line}")
                        print(f"Erreur détectée pour URL {i}: {line}")
                    
                    elif "[ExtractAudio]" in line:
                        root.update()
                    
                    elif any(keyword in line.lower() for keyword in ["warning:", "skipping", "unavailable"]):
                        print(f"Attention URL {i}: {line}")
                
                process.wait()
                
                if process.returncode == 0 or video_downloaded:
                    total_downloaded += 1
                    
            except Exception as e:
                error_messages.append(f"URL {i}: Erreur subprocess - {str(e)}")
                print(f"Erreur subprocess pour URL {i}: {e}")
        
        # Affichage du résultat final
        if total_downloaded > 0:
            status_label.config(text="Prêt", fg="green")
            success_msg = f"Téléchargement terminé!\n{total_downloaded}/{total_urls} vidéo(s) téléchargée(s)."
            if error_messages:
                success_msg += f"\n\nNote: {len(error_messages)} erreur(s) détectée(s)."
            messagebox.showinfo("Succès", success_msg)
        else:
            status_label.config(text="Erreur", fg="red")
            error_msg = f"Aucune vidéo n'a pu être téléchargée sur {total_urls} URL(s)."
            if error_messages:
                error_msg += f"\n\nDernières erreurs:\n" + "\n".join(error_messages[-3:])
            messagebox.showerror("Erreur", error_msg)
    
    # Réactive le bouton dans tous les cas
    download_btn.config(state='normal')

# === Interface graphique ===
def main():        
    global _app_initialized, notebook, url_text_video, url_entry_playlist
    global output_dir_video, output_dir_playlist, status_label, download_btn, root
    
    # Protection contre les exécutions multiples
    if _app_initialized:
        return
    _app_initialized = True
    
    # Vérifications des dépendances
    if not install_package("requests"):
        return
    if not ensure_yt_dlp():
        return
    ensure_ffmpeg()  # FFmpeg est optionnel

    root = tk.Tk()
    root.title("Téléchargeur MP3 - yt-dlp GUI")
    root.geometry("550x400")
    root.resizable(False, False)

    # Création du système d'onglets
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # === Onglet Vidéo Simple ===
    video_frame = ttk.Frame(notebook)
    notebook.add(video_frame, text="Vidéo(s)")

    # Texte explicatif
    explanation_label = tk.Label(video_frame, 
                                text="Entrez une ou plusieurs URLs de vidéos YouTube :\n(Une URL par ligne pour télécharger plusieurs vidéos)", 
                                font=("Arial", 9), 
                                fg="gray")
    explanation_label.pack(pady=(10, 5))

    # Zone de texte multilignes pour les URLs
    url_frame_video = tk.Frame(video_frame)
    url_frame_video.pack(padx=10, pady=(0, 10), fill="both", expand=True)
    
    url_text_video = tk.Text(url_frame_video, height=6, width=60, wrap=tk.WORD)
    url_text_video.pack(side="left", fill="both", expand=True)
    
    # Scrollbar pour la zone de texte
    scrollbar_video = tk.Scrollbar(url_frame_video, orient="vertical", command=url_text_video.yview)
    scrollbar_video.pack(side="right", fill="y")
    url_text_video.config(yscrollcommand=scrollbar_video.set)

    # Dossier de destination pour vidéo
    dest_frame_video = tk.Frame(video_frame)
    dest_frame_video.pack(pady=(10, 5), padx=10, fill="x")
    
    tk.Label(dest_frame_video, text="Dossier de destination :").pack(anchor="w")
    
    dest_entry_frame_video = tk.Frame(dest_frame_video)
    dest_entry_frame_video.pack(fill="x", pady=(5, 0))
    
    output_dir_video = tk.StringVar()
    dest_entry_video = tk.Entry(dest_entry_frame_video, textvariable=output_dir_video, width=45)
    dest_entry_video.pack(side="left", fill="x", expand=True)
    
    browse_btn_video = tk.Button(dest_entry_frame_video, text="Parcourir", command=choose_output_dir_video)
    browse_btn_video.pack(side="right", padx=(5, 0))

    # === Onglet Playlist ===
    playlist_frame = ttk.Frame(notebook)
    notebook.add(playlist_frame, text="Playlist")

    tk.Label(playlist_frame, text="URL de la playlist YouTube :").pack(pady=(10, 5))
    url_entry_playlist = tk.Entry(playlist_frame, width=60)
    url_entry_playlist.pack(padx=10)

    # Dossier de destination pour playlist
    dest_frame_playlist = tk.Frame(playlist_frame)
    dest_frame_playlist.pack(pady=(10, 5), padx=10, fill="x")
    
    tk.Label(dest_frame_playlist, text="Dossier de destination :").pack(anchor="w")
    
    dest_entry_frame_playlist = tk.Frame(dest_frame_playlist)
    dest_entry_frame_playlist.pack(fill="x", pady=(5, 0))
    
    output_dir_playlist = tk.StringVar()
    dest_entry_playlist = tk.Entry(dest_entry_frame_playlist, textvariable=output_dir_playlist, width=45)
    dest_entry_playlist.pack(side="left", fill="x", expand=True)
    
    browse_btn_playlist = tk.Button(dest_entry_frame_playlist, text="Parcourir", command=choose_output_dir_playlist)
    browse_btn_playlist.pack(side="right", padx=(5, 0))

    # === Boutons et statut (communs aux deux onglets) ===
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

    download_btn = tk.Button(bottom_frame, text="Télécharger en MP3", command=download, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    download_btn.pack(pady=10)

    status_label = tk.Label(bottom_frame, text="Prêt", fg="green", font=("Arial", 9))
    status_label.pack()

    root.mainloop()

if __name__ == "__main__":
    # Protection nécessaire pour PyInstaller avec multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()
