"""Nœud ROS 2 « voix » (tourne là où se trouve le haut-parleur).
Écoute /traduction et joue le fichier audio de la traduction."""
import json
import os
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Voix(Node):
    def __init__(self):
        super().__init__("voix")
        self.create_subscription(String, "/traduction", self.recevoir, 10)
        self.get_logger().info("Prêt. J'écoute /traduction")
    # Fonction de rappel pour recevoir les messages de traduction
    def recevoir(self, msg):
        r = json.loads(msg.data)
        self.get_logger().info(f"Je dis ({r['langue']}) : {r['traduction']}")
        if r.get("audio_sortie") and os.path.exists(r["audio_sortie"]):
            subprocess.run(["aplay", "-q", r["audio_sortie"]], check=False)
        else:
            self.get_logger().warn("Pas de fichier audio (voix non disponible) : texte seulement")

# Fonction principale pour initialiser le nœud ROS 2 et le faire tourner
def main():
    rclpy.init()
    rclpy.spin(Voix())


if __name__ == "__main__":
    main()
