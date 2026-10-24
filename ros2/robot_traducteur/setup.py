from setuptools import setup
from glob import glob

setup(
    name="robot_traducteur",
    version="0.1.0",
    packages=["robot_traducteur"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/robot_traducteur"]),
        ("share/robot_traducteur", ["package.xml"]),
        ("share/robot_traducteur/launch", glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    entry_points={"console_scripts": [
        "traducteur = robot_traducteur.traducteur_node:main",
        "voix = robot_traducteur.voix_node:main",
    ]},
)
