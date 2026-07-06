import argparse
import os
import shutil

def make_default_output_name(input_path: str) -> str:
    base = os.path.basename(str(input_path or "image.nii.gz"))

    if base.endswith(".nii.gz"):
        return base.replace(".nii.gz", "_gaussian.nii.gz")

    if base.endswith(".nii"):
        return base.replace(".nii", "_gaussian.nii")

    return base + "_gaussian.nii.gz"


def apply_vtk_gaussian_nifti(input_path: str, output_path: str, sigma: float):
    """
    Même logique que l'étape prepare_gaussian côté Trame :
    - lecture directe NIfTI ;
    - vtkImageGaussianSmooth ;
    - écriture NIfTI ;
    - conservation QForm/SForm si possible.
    """
    from vtk import vtkImageGaussianSmooth, vtkNIFTIImageReader, vtkNIFTIImageWriter

    reader = vtkNIFTIImageReader()
    reader.SetFileName(input_path)
    reader.Update()

    gaussian_filter = vtkImageGaussianSmooth()
    gaussian_filter.SetInputConnection(reader.GetOutputPort())
    gaussian_filter.SetStandardDeviation(float(sigma))
    gaussian_filter.Update()

    writer = vtkNIFTIImageWriter()
    writer.SetFileName(output_path)
    writer.SetInputConnection(gaussian_filter.GetOutputPort())

    try:
        qform = reader.GetQFormMatrix()
        if qform is not None:
            writer.SetQFormMatrix(qform)
            print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] QForm conservé", flush=True)
    except Exception as exc:
        print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] QForm non conservé:", repr(exc), flush=True)

    try:
        sform = reader.GetSFormMatrix()
        if sform is not None:
            writer.SetSFormMatrix(sform)
            print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] SForm conservé", flush=True)
    except Exception as exc:
        print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] SForm non conservé:", repr(exc), flush=True)

    writer.Write()

    if not os.path.exists(output_path):
        raise RuntimeError(f"Le fichier de sortie n'a pas été créé : {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Gaussian VTK filter on NIfTI image")

    parser.add_argument("-i", "--input", required=True, help="Input NIfTI file")
    parser.add_argument("-o", "--output", required=True, help="Output NIfTI file")

    parser.add_argument(
        "--sigma",
        type=float,
        default=float(
            os.environ.get(
                "GAUSSIAN_SIGMA",
                os.environ.get("IMRT_DOCKER_GAUSSIAN_SIGMA", "4.0"),
            )
        ),
        help="Gaussian sigma. Default: 4.0",
    )

    parser.add_argument(
        "--copy-only",
        action="store_true",
        help="Only copy input to output without filtering",
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    sigma = float(args.sigma)

    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] input =", input_path, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] output =", output_path, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] sigma =", sigma, flush=True)
    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] copy_only =", bool(args.copy_only), flush=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if args.copy_only:
        shutil.copyfile(input_path, output_path)
        print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] copied input to output", flush=True)
        return

    apply_vtk_gaussian_nifti(
        input_path=input_path,
        output_path=output_path,
        sigma=sigma,
    )

    print("[DOCKER NIFTI APPLY GAUSSIAN VTKFILTER] gaussian filter done", flush=True)


if __name__ == "__main__":
    main()