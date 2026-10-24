# Robot traducteur multilingue

Le robot écoute une phrase en français, un LLM comprend la demande, NLLB-200 traduit en anglais ou en darija,
la synthèse vocale la lit, et chaque échange est enregistré dans une plateforme de suivi.

Projet capstone S9 · HESTIM 5A IIIA · Awa Aimée Benzekry & Ramatoulaye Diawane · Encadrant : Dr. Sridath TULA

## Installation (Windows, Mac ou Linux)

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate      Linux/Mac : source .venv/bin/activate
pip install -r requirements.txt
```

Pour le LLM : installer Ollama (https://ollama.com), puis `ollama pull qwen2.5:3b`.

## Lancer

```bash
streamlit run tableau_de_bord.py      # tableau de bord dans le navigateur
python tester_pipeline.py             # test rapide en ligne de commande
```

Sans modèles installés, tout fonctionne en **mode démo** (pastilles jaunes dans le tableau de bord).

## Organisation

| Dossier / fichier | Contenu |
|---|---|
| `config.py` | Noms des modèles, langues, chemin de la base |
| `ia/comprendre.py` | LLM (Ollama) qui comprend la demande, avec règles de secours |
| `ia/transcription.py` | Whisper : voix → texte |
| `ia/traduction.py` | NLLB-200 : français → anglais / darija |
| `ia/voix.py` | MMS-TTS : texte → voix |
| `ia/pipeline.py` | La chaîne complète, utilisée par le tableau de bord et par ROS 2 |
| `donnees/db.py` | Base SQLite de l'historique |
| `donnees/phrases_test.csv` | Jeu de test (références darija à faire écrire par des locuteurs natifs) |
| `tableau_de_bord.py` | Interface Streamlit : Commander, Historique, Statistiques |
| `ros2/robot_traducteur/` | Paquet ROS 2 : nœuds `traducteur` et `voix` |

## ROS 2

```bash
cp -r ros2/robot_traducteur ~/ros2_ws/src/
cd ~/ros2_ws && colcon build && source install/setup.bash
export ROBOT_TRADUCTEUR_DIR=/chemin/vers/robot-traducteur
ros2 launch robot_traducteur robot_traducteur.launch.py
# autre terminal :
ros2 topic pub --once /texte_entree std_msgs/msg/String "{data: 'Comment on dit merci en darija ?'}"
```
# robot_traducteur
