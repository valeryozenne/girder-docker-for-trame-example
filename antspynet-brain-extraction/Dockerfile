#################
# Stage BUILD : installation des paquets Python
#################
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04 AS builder
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git curl \
      python3 python3-pip python3-dev libpng-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir "tensorflow==2.15.*" \
        pandas pyyaml numpy scikit-image scikit-learn statsmodels \
        webcolors matplotlib Pillow nibabel antspyx antspynet vtk

#################
# Stage FINAL : runtime seulement
#################
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04 AS final_image
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip libpng16-16 libgomp1 curl && \
    rm -rf /var/lib/apt/lists/*

# Copie uniquement des packages Python installés, pas du toolkit de build
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Utilisateur + permissions
ARG USERNAME=girder
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} ${USERNAME} && \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USERNAME} && \
    mkdir -p /opt/code /opt/input /opt/output /opt/inout /opt/model /root/.keras/ANTsXNet && \
    chown -R ${USERNAME}:${GROUP_ID} /opt/code /opt/input /opt/output /opt/inout /root/.keras

WORKDIR /opt/code
ENV IMRT_DOCKER_GAUSSIAN_SIGMA=3.0

COPY brain_extraction.py structure_extraction.py mask_to_surface.py entrypoint.sh /opt/code/
RUN chmod +x /opt/code/entrypoint.sh

ENTRYPOINT ["/opt/code/entrypoint.sh"]