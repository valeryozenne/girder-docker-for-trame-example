import os
import time
import ants
import antspynet
import argparse
import shutil

import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def check_file_exist(file):
   if not (os.path.isfile(file)):
    raise ValueError("Error folder", file)

def check_folder_exist(folder):
   if not (os.path.isdir(folder)):
    raise ValueError("Error folder", folder)

def check_folder_exist_or_create_it(folder):
   if not (os.path.isdir(folder)):
      os.mkdir(folder)

def main():
    parser = argparse.ArgumentParser(description="Gaussian VTK filter on NIfTI image")

    parser.add_argument("-i", "--input", required=True, help="Input NIfTI file")
    parser.add_argument("-o", "--output", required=True, help="Output NIfTI file")
    parser.add_argument('-c', '--contrast', nargs='?', const='t1', default='t1', help='contrast name', type=str)
    parser.add_argument(
        "--copy-only",
        action="store_true",
        help="Only copy input to output without filtering",
    )


    args = parser.parse_args()
    print(args)
    t1= time.time()

    # get arguments

    input_path = args.input
    output_path = args.output
    contrast=args.contrast
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] input =", input_path, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] output =", output_path, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] sigma =", contrast, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] copy_only =", bool(args.copy_only), flush=True)

    if args.copy_only:
        shutil.copyfile(input_path, output_path)
        print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] copied input to output", flush=True)
    else:
        brain_image= ants.image_read(input_path)
        probability_brain_mask = antspynet.brain_extraction(brain_image, modality=contrast)
        ants.image_write(probability_brain_mask, output_path)

if __name__ == "__main__":
    main()


#      brain_image = sitk.ReadImage(input_file_name)
#      dims = brain_image.GetSize()
#      print("Input dims:", dims)
#      print("Input origin:", brain_image.GetOrigin())
#      print("Input direction:", brain_image.GetDirection())
#      probability_brain_mask = brain_image
#      sitk.WriteImage(probability_brain_mask, output_file_name)
#for k in brain_image.GetMetaDataKeys(): 
#     v = brain_image.GetMetaData(k) 
#     print("({0}) = = \"{1}\"".format(k,v)) 


#print(output_file_name)                                                                                                                                                   80,1          Bot

