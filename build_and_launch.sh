#!/bin/bash

# Script pour construire et lancer les nœuds ROS 2 du projet robotique
# À exécuter depuis le répertoire racine du projet

set -e  # Arrête le script en cas d'erreur

# =============================================
# 1. Vérification de l'environnement ROS 2
# =============================================
echo "[1/4] Vérification de l'environnement ROS 2..."
if ! command -v ros2 &> /dev/null; then
    echo "❌ ROS 2 n'est pas installé ou n'est pas sourcé."
    echo "Exécutez : source /opt/ros/humble/setup.bash"
    exit 1
fi
echo "✅ ROS 2 est prêt."

# =============================================
# 2. Construction du workspace ROS 2
# =============================================
echo "[2/4] Construction du workspace ROS 2..."
cd /home/loocist/Documents/IoT/raspberry/robot_autonome_ws
colcon build --symlink-install
if [ $? -eq 0 ]; then
    echo "✅ Construction réussie !"
else
    echo "❌ Échec de la construction."
    exit 1
fi

# =============================================
# 3. Sourcing du workspace
# =============================================
echo "[3/4] Sourcing du workspace..."
source /home/loocist/Documents/IoT/raspberry/robot_autonome_ws/install/setup.bash
echo "✅ Workspace sourcé."

# =============================================
# 4. Lancement des nœuds ROS 2
# =============================================
echo "[4/4] Lancement des nœuds ROS 2..."
echo "Appuyez sur Ctrl+C pour arrêter tous les nœuds."
echo ""

# Lancement des nœuds dans des terminaux séparés
# Note : Pour que cela fonctionne, assurez-vous que gnome-terminal est installé
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --tab --title="UART Reader" -- bash -c "ros2 run uart_reader uart_reader; exec bash"
    sleep 1
    gnome-terminal --tab --title="Motor Controller" -- bash -c "ros2 run motor_controller motor_controller; exec bash"
    sleep 1
    gnome-terminal --tab --title="Brain" -- bash -c "ros2 run brain brain; exec bash"
    sleep 1
    gnome-terminal --tab --title="LiDAR Node" -- bash -c "ros2 run rplidar_ros rplidar_node; exec bash"
    sleep 1
    gnome-terminal --tab --title="RViz2" -- bash -c "rviz2; exec bash"
else
    echo "⚠️ gnome-terminal n'est pas installé. Lancement des nœuds en arrière-plan..."
    ros2 run uart_reader uart_reader &
    sleep 1
    ros2 run motor_controller motor_controller &
    sleep 1
    ros2 run brain brain &
    sleep 1
    ros2 run rplidar_ros rplidar_node &
    sleep 1
    rviz2 &
fi

echo ""
echo "========================================="
echo "✅ Tous les nœuds sont lancés !"
echo "========================================="
echo ""
echo "Pour vérifier les topics :"
echo "  ros2 topic list"
echo ""
echo "Pour arrêter tous les nœuds :"
echo "  pkill -f "ros2 run""
echo ""
