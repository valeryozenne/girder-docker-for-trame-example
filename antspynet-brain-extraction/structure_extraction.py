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
    parser.add_argument("-m", "--output_mask", required=True, help="Output NIfTI file")    
    parser.add_argument("-t", "--output_tct", required=True, help="Output NIfTI file")
    parser.add_argument("-n", "--output_nick", required=True, help="Output NIfTI file")
    
    #parser.add_argument('-c', '--contrast', nargs='?', const='t1', default='t1', help='contrast name', type=str)
    #parser.add_argument(
    #    "--copy-only",
    #    action="store_true",
    #    help="Only copy input to output without filtering",
    #)


    args = parser.parse_args()
    print(args)
    t1= time.time()

    # get arguments

    input_path = args.input
    output_path_mask = args.output_mask
    output_path_tct = args.output_tct
    output_path_nick = args.output_nick
    #contrast=args.contrast
    print("[DOCKER NIFTI ANTSPY] input =", input_path, flush=True)
    print("[DOCKER NIFTI ANTSPY] output =", output_path_tct, flush=True)
    print("[DOCKER NIFTI ANTSPY] output =", output_path_nick, flush=True)
    
    #if args.copy_only:
    #    shutil.copyfile(input_path, output_path_tct)
    #    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] copied input to output", flush=True)
    #else:
    mouse_t2 = ants.image_read(input_path)
    mouse_t2_n4 = ants.n4_bias_field_correction(mouse_t2, 
                                                rescale_intensities=True,
                                                shrink_factor=2, 
                                                convergence={'iters': [50, 50, 50, 50], 'tol': 0.0}, 
                                                spline_param=20, verbose=True)
    
    mask_brain = antspynet.mouse_brain_extraction(mouse_t2_n4, modality='t2', verbose=True)
    ants.image_write(mask_brain, output_path_mask) 

    parc_nick = antspynet.mouse_brain_parcellation(mouse_t2_n4, 
                                                   mask=mask_brain, 
                                                   which_parcellation="nick",      
                                                   return_isotropic_output=True,  
                                                   verbose=True)
    
    ants.image_write(parc_nick['image_segmentation'], output_path_nick) 

    parc_tct = antspynet.mouse_brain_parcellation(mouse_t2_n4, 
                                                  mask=mask_brain, 
                                                  which_parcellation="tct",      
                                                  return_isotropic_output=True,  
                                                  verbose=True) 

    
    ants.image_write(parc_tct['image_segmentation'], output_path_tct)
       
        #brain_image= ants.image_read(input_path)
        #probability_brain_mask = antspynet.brain_extraction(brain_image, modality=contrast)
        #ants.image_write(probability_brain_mask, output_path)

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

