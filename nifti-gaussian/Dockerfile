FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir vtk numpy

ENV IMRT_DOCKER_GAUSSIAN_SIGMA=4.0

WORKDIR /app

COPY gaussian_nifti.py /app/gaussian_nifti.py

ENTRYPOINT ["python", "/app/gaussian_nifti.py"]