# Téléchargeur MP3 - yt-dlp GUI

## Installation et utilisation

### 📁 Fichiers nécessaires
- `yt-dl-fixed.exe` - L'application principale
- `ffmpeg.exe` - **REQUIS** pour la conversion MP3 (à placer dans le même dossier)

### 🔧 Installation de FFmpeg
1. Téléchargez FFmpeg depuis : https://www.gyan.dev/ffmpeg/builds/
2. Extrayez `ffmpeg.exe` du dossier `bin`
3. Placez `ffmpeg.exe` dans le même dossier que `yt-dl-fixed.exe`

### 🎵 Fonctionnalités

#### Onglet "Vidéo(s)"
- Permet de télécharger une ou plusieurs vidéos individuelles
- Entrez une URL par ligne dans le champ de texte
- Supporte le téléchargement en lot

#### Onglet "Playlist"
- Permet de télécharger une playlist YouTube complète
- Entrez l'URL de la playlist

### 🎛️ Options de téléchargement
- **Format** : MP3 192 kbps
- **Métadonnées** : Incluses automatiquement
- **Miniatures** : Intégrées dans les fichiers MP3
- **Noms de fichiers** : Compatibles Windows, limités à 100 caractères

### ⚠️ Important
- FFmpeg est **obligatoire** pour la conversion MP3
- Sans FFmpeg, les vidéos seront téléchargées en format WebM
- L'application vérifiera la présence de FFmpeg au démarrage

### 🐛 Dépannage
- Si vous obtenez des fichiers WebM au lieu de MP3, vérifiez que `ffmpeg.exe` est présent
- Pour les erreurs de téléchargement, vérifiez que les URLs sont valides
- L'application continue même si certaines URLs échouent

### 📝 Exemple d'utilisation multi-vidéos
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=kJQP7kiw5Fk
https://www.youtube.com/watch?v=oHg5SJYRHA0
```

### 📧 Support
- Application créée avec yt-dlp et tkinter
- Compatible Windows
- Interface en français
