#!/bin/bash

# Script d'installation automatique de ROS 2 Humble + dépendances pour le projet robotique
# Compatible avec Ubuntu 22.04 (Jammy)
# A exécuter en root ou avec sudo

set -e  # Arrête le script en cas d'erreur

# =============================================
# 1. Vérification de la distribution Ubuntu
# =============================================
echo "[1/7] Vérification de la distribution..."
UBUNTU_VERSION=$(lsb_release -rs)
if [ "$UBUNTU_VERSION" != "22.04" ]; then
    echo "❌ Ce script est conçu pour Ubuntu 22.04 (Jammy)."
    echo "Votre version : $UBUNTU_VERSION"
    exit 1
fi
echo "✅ Ubuntu 22.04 détecté."

# =============================================
# 2. Mise à jour du système et installation des dépendances de base
# =============================================
echo "[2/7] Mise à jour du système et installation des dépendances..."
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    locales \
    python3-colcon-common-extensions \
    python3-pip

# =============================================
# 3. Configuration de la locale (UTF-8)
# =============================================
echo "[3/7] Configuration de la locale..."
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
echo "✅ Locale configurée : $(locale)"

# =============================================
# 4. Ajout du dépôt ROS 2 et installation des clés
# =============================================
echo "[4/7] Ajout du dépôt ROS 2..."
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Alternative (méthode officielle avec ros2-apt-source)
ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
rm /tmp/ros2-apt-source.deb

sudo apt update -y

# =============================================
# 5. Installation de ROS 2 Humble Desktop
# =============================================
echo "[5/7] Installation de ROS 2 Humble Desktop..."
sudo apt install -y \
    ros-humble-desktop \
    ros-humble-rplidar-ros \
    ros-dev-tools

# =============================================
# 6. Installation des dépendances Python et outils
# =============================================
echo "[6/7] Installation des dépendances Python..."
pip3 install --upgrade pip
pip3 install pyserial setuptools==58.2.0

# =============================================
# 7. Configuration de l'environnement ROS 2
# =============================================
echo "[7/7] Configuration de l'environnement ROS 2..."
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "✅ Ajout du sourcing ROS 2 dans ~/.bashrc"
fi

# Sourcing immédiat pour la session actuelle
source /opt/ros/humble/setup.bash

# =============================================
# Vérification finale
# =============================================
echo ""
echo "========================================="
echo "✅ Installation terminée !"
echo "========================================="
echo ""
echo "Pour finaliser, exécutez :"
echo "  1. 'source ~/.bashrc' ou ouvrez un nouveau terminal."
echo "  2. Testez ROS 2 avec :"
echo "     ros2 run demo_nodes_cpp talker"
echo "     (dans un autre terminal) ros2 run demo_nodes_py listener"
echo ""
echo "Pour désinstaller ROS 2 plus tard :"
echo "  sudo apt remove '~nros-humble-*' && sudo apt autoremove"
echo ""
echo "Dépendances supplémentaires installées :"
echo "  - rplidar_ros (pour le LiDAR)"
echo "  - pyserial (pour la communication UART)"
echo "  - colcon (pour construire vos packages ROS 2)"
echo ""
