import # URL test (playlist): https://www.youtube.com/playlist?list=PLsJMz620V0MWTBgpGrRhvWcKP0zIbnkq_

# Variable globale pour éviter les exécutions multiples
_app_initialized = False

# Vérifie si un module est installé (pour les versions compilées, on assume qu'ils sont inclus)
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        # En mode compilé, on ne peut pas installer de packages
        if getattr(sys, 'frozen', False):
            messagebox.showerror("Erreur", f"Module {package} manquant dans l'exécutable compilé.")
            return False
        else:
            # En mode développement uniquement
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return True

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
                subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                return Trueocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

# URL test (playlist): https://www.youtube.com/playlist?list=PLsJMz620V0MWTBgpGrRhvWcKP0zIbnkq_

# Vérifie si un module est installé, sinon l’installe
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Installe yt-dlp via pip
def ensure_yt_dlp():
    try:
        subprocess.run(["yt-dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Installation de yt-dlp en cours...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

# Télécharge et installe ffmpeg dans le dossier local si nécessaire
def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return

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

# Télécharge la vidéo ou playlist en MP3
def download():
    url = url_entry.get().strip()
    is_playlist = playlist_var.get()
    
    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL.")
        return

    output_dir = filedialog.askdirectory(title="Choisissez le dossier de destination")
    if not output_dir:
        return

    # Désactive le bouton pendant le téléchargement
    download_btn.config(state='disabled')
    status_label.config(text="Téléchargement en cours...", fg="orange")
    root.update()

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "192K",
        "--embed-thumbnail",
        "--add-metadata",
        "--restrict-filenames",  # Limite les caractères dans les noms de fichiers
        "--windows-filenames",   # Compatible avec Windows
        "--ignore-errors",       # Continue même en cas d'erreur sur une vidéo
        "-o", os.path.join(output_dir, "%(title).100s.%(ext)s"),  # Limite la longueur du titre
        url
    ]

    if is_playlist:
        cmd.append("--yes-playlist")
    else:
        cmd.append("--no-playlist")

    try:
        # Lance le processus et capture la sortie
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', bufsize=1, universal_newlines=True)
        
        downloaded_count = 0
        error_messages = []
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
                
            # Détection du téléchargement terminé
            if "[download]" in line and "100%" in line:
                downloaded_count += 1
                status_label.config(text=f"Téléchargement en cours... ({downloaded_count} musique(s) téléchargée(s))", fg="orange")
                root.update()
            
            # Détection des erreurs
            elif "ERROR:" in line:
                error_messages.append(line)
                print(f"Erreur détectée: {line}")
            
            # Détection de la conversion audio
            elif "[ExtractAudio]" in line:
                root.update()
            
            # Détection d'autres messages importants
            elif any(keyword in line.lower() for keyword in ["warning:", "skipping", "unavailable"]):
                print(f"Attention: {line}")
        
        # Attendre que le processus se termine
        process.wait()
        
        if process.returncode == 0 or downloaded_count > 0:
            status_label.config(text="Prêt", fg="green")
            if downloaded_count == 0:
                downloaded_count = 1  # Au moins une musique si le processus s'est bien passé
            
            success_msg = f"Téléchargement terminé!\n{downloaded_count} musique(s) téléchargée(s)."
            if error_messages and process.returncode != 0:
                success_msg += f"\n\nNote: Certaines vidéos ont été ignorées à cause d'erreurs."
            
            messagebox.showinfo("Succès", success_msg)
        else:
            status_label.config(text="Erreur", fg="red")
            error_msg = "Le téléchargement a échoué complètement."
            if error_messages:
                error_msg += f"\n\nDernière erreur:\n{error_messages[-1]}"
            messagebox.showerror("Erreur", error_msg)
            
    except Exception as e:
        status_label.config(text="Erreur", fg="red")
        messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")
    finally:
        # Réactive le bouton
        download_btn.config(state='normal')

# === Interface graphique ===
def main():        
    # Protection contre les imports multiples avec PyInstaller
    if hasattr(main, '_already_running'):
        return
    main._already_running = True
    
    # Installations
    install_package("requests")
    ensure_yt_dlp()
    ensure_ffmpeg()

    global url_entry, playlist_var, status_label, download_btn, root

    root = tk.Tk()
    root.title("Téléchargeur MP3 - yt-dlp GUI")
    root.geometry("450x250")
    root.resizable(False, False)

    tk.Label(root, text="URL de la vidéo ou playlist YouTube :").pack(pady=10)
    url_entry = tk.Entry(root, width=60)
    url_entry.pack(padx=10)

    playlist_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Cochez si c'est une playlist", variable=playlist_var).pack(pady=5)

    download_btn = tk.Button(root, text="Télécharger en MP3", command=download)
    download_btn.pack(pady=15)

    # Label de statut
    status_label = tk.Label(root, text="Prêt", fg="green")
    status_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    # Protection nécessaire pour PyInstaller avec multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()
