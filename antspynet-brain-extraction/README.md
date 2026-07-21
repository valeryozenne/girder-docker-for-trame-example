
docker build -t girder/antspynet .

docker run --rm --gpus all girder/antspynet:latest nvidia-smi

docker run --rm --gpus all girder/antspynet:latest python3 -c 'import tensorflow as tf; print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices("GPU")))'

docker run -dit --gpus all -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout --name antspynet girder/antspynet:latest 





docker exec -ti antspynet bash


docker run --rm --gpus all -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout girder/antspynet:latest -i /opt/inout/Ax_3D_BRAVO_resampled_to_2mm.nii.gz -o /opt/inout/brain_masked.nii.gz


docker run --rm --gpus all -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout girder/antspynet:latest -i /opt/inout/test1_strides_ok.nii.gz -m /opt/inout/mouse_brain_masked.nii.gz -t /opt/inout/mouse_output_tct.nii.gz -n /opt/inout/mouse_output_nick.nii.gz




python3 mask_to_surface.py -i /home/vozenne/Bureau/ToBeDeleted/ants_mnt/brain_masked_1.nii.gz -o /home/vozenne/Bureau/ToBeDeleted/ants_mnt/brain_masked_1.stl --ras-to-lps --smoothing-iterations 10

mkdir /tmp/model/

docker run --rm --gpus all -v /tmp/model/:/opt/model/ -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout girder/antspynet:latest -i /opt/inout/Ax_3D_BRAVO_resampled_to_2mm.nii.gz -o /opt/inout/brain_masked.nii.gz -s /opt/inout/brain_masked.stl -c t1 -d /opt/model/


docker run --rm --gpus all -v /tmp/keras/:/root/.keras/ -v /home/vozenne/Bureau/ToBeDeleted/ants_mnt/:/opt/inout girder/antspynet:latest -i /opt/inout/Ax_3D_BRAVO_resampled_to_2mm.nii.gz -o /opt/inout/brain_masked.nii.gz -s /opt/inout/brain_masked.stl -c t1