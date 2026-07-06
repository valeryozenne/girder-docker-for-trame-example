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
    apt-get install -y git vim locate tree 

FROM base_image AS antspy_layer


RUN pip install antspyx
# prepare installation de antsPY
#RUN cd /opt/ && \
#    git clone https://github.com/ANTsX/ANTsPy.git  

#RUN cd /opt/ANTsPy && \
#    python3 setup.py install

RUN python3 -m pip install antspynet

############"
# ANTsPyNet
############"       

FROM antspy_layer AS user_permissions_layer

# Arguments pour l'UID/GID de l'utilisateur local
#ARG USERNAME=girder
#ARG USER_ID=1000
#ARG GROUP_ID=1000

# Création de l'utilisateur avec l'UID/GID passé en argument
#RUN groupadd -g ${GROUP_ID} ${USERNAME} && \
#    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USERNAME} && \
#    mkdir -p /opt/code /opt/input /opt/output /opt/inout && \
#    chown -R ${USERNAME}:${GROUP_ID} /opt/code /opt/input /opt/output /opt/inout

# prepare installation de ANTsPyNet    , une image docker de ANTsPyNet est aussi disponible  

#RUN cd /opt/ && \
#    git clone https://github.com/ANTsX/ANTsPyNet.git 	
    
#RUN cd /opt/ANTsPyNet && \    
#    pip install -r requirements.txt    

#RUN pip install antspynet

#RUN cd /opt/ && mkdir Applications &&\
#    cd Applications && \
#    git clone https://github.com/ANTsXNet/BrainExtraction.git
         
#RUN pip install simpleITK

WORKDIR /opt/code
ENV IMRT_DOCKER_GAUSSIAN_SIGMA=3.0

COPY brain_extraction.py /opt/code/brain_extraction.py

ENTRYPOINT ["python3", "/opt/code/brain_extraction.py"]