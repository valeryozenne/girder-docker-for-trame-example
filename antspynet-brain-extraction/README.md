
docker build -t girder/antspynet .

docker run --rm --gpus all girder/antspynet:latest nvidia-smi

docker run --rm --gpus all girder/antspynet:latest python3 -c 'import tensorflow as tf; print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices("GPU")))'

docker run -dit --gpus all -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout --name antspynet girder/antspynet:latest 



docker exec -ti antspynet bash


docker run --rm --gpus all -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout girder/antspynet:latest -i /opt/inout/Ax_3D_BRAVO.nii.gz -o /opt/inout/test2.nii.gz
