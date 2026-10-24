"""Nœud ROS 2 « traducteur » (tourne sur le PC).
Écoute /texte_entree (phrase en français) et publie /traduction (résultat en JSON).
Il réutilise exactement la même chaîne IA que le tableau de bord."""
import json
import os
import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Dossier du projet (là où se trouve ia/ et donnees/). À adapter si besoin.
PROJET = os.environ.get("ROBOT_TRADUCTEUR_DIR", os.path.expanduser("~/robot-traducteur"))
sys.path.insert(0, PROJET)
from ia.pipeline import traiter  # noqa: E402


class Traducteur(Node):
    def __init__(self):
        super().__init__("traducteur")
        self.pub = self.create_publisher(String, "/traduction", 10)
        self.create_subscription(String, "/texte_entree", self.recevoir, 10)
        self.get_logger().info("Prêt. J'écoute /texte_entree")

    def recevoir(self, msg):
        self.get_logger().info(f"Reçu : {msg.data}")
        r = traiter(texte=msg.data, canal="ros2")
        sortie = String()
        sortie.data = json.dumps({k: r[k] for k in ("phrase_fr", "langue", "traduction", "audio_sortie", "temps_total_ms")},
                                 ensure_ascii=False)
        self.pub.publish(sortie)
        self.get_logger().info(f"Traduction ({r['langue']}) : {r['traduction']}")


def main():
    rclpy.init()
    rclpy.spin(Traducteur())


if __name__ == "__main__":
    main()
