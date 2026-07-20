FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 AS base_image

# Avoid user interaction.
ARG DEBIAN_FRONTEND=noninteractive


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      apt-transport-https \
      build-essential \
      ca-certificates \
      curl \
      git \
      gnupg \
      libpng-dev \
      software-properties-common


RUN apt-get -y install pip cmake

# Dépendances système + Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Mettre pip à jour (nécessaire pour les wheels manylinux2014)
RUN pip3 install --upgrade pip    

RUN pip3 install "tensorflow==2.15.*"

RUN pip install pandas pyyaml numpy scikit-image scikit-learn statsmodels webcolors matplotlib Pillow nibabel

RUN apt-get update && \
    apt-get install -y git vim locate tree figlet gosu

FROM base_image AS antspy_layer


RUN pip install antspyx
# prepare installation de antsPY
#RUN cd /opt/ && \
#    git clone https://github.com/ANTsX/ANTsPy.git  

#RUN cd /opt/ANTsPy && \
#    python3 setup.py install

RUN python3 -m pip install antspynet vtk

############"
# ANTsPyNet
############"       

FROM antspy_layer AS user_permissions_layer

# Arguments pour l'UID/GID de l'utilisateur local
ARG USERNAME=girder
ARG USER_ID=1000
ARG GROUP_ID=1000

# Création de l'utilisateur avec l'UID/GID passé en argument
RUN groupadd -g ${GROUP_ID} ${USERNAME} && \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USERNAME} && \
    mkdir -p /opt/code /opt/input /opt/output /opt/inout /opt/model /root/.keras/ /root/.keras/ANTsXNet/ && \
    chown -R ${USERNAME}:${GROUP_ID} /opt/code /opt/input /opt/output /opt/inout /root/.keras/ /root/.keras/ANTsXNet/

FROM user_permissions_layer AS final_image

WORKDIR /opt/code
ENV IMRT_DOCKER_GAUSSIAN_SIGMA=3.0

COPY brain_extraction.py /opt/code/brain_extraction.py
COPY structure_extraction.py /opt/code/structure_extraction.py
COPY mask_to_surface.py /opt/code/mask_to_surface.py

# Copie du script entrypoint.sh dans le conteneur
COPY entrypoint.sh /opt/code/entrypoint.sh

# Rendre le script exécutable
RUN chmod +x /opt/code/entrypoint.sh

# Définir le point d'entrée du conteneur
ENTRYPOINT ["/opt/code/entrypoint.sh"]
#ENTRYPOINT ["python3", "/opt/code/brain_extraction.py"]