"""
Pipeline VTK :
1. Lecture d'un masque binaire NIfTI (.nii / .nii.gz)
2. Extraction de la plus grande région connexe (label == 1)
3. Génération de l'isosurface (mesh surfacique) via Marching Cubes discret
4. Remise à l'échelle/orientation correcte via la matrice sform/qform du NIfTI
   (vtkImageData ne peut pas stocker de rotation : le mesh sort donc "droit"
   tant qu'on n'applique pas cette matrice explicitement sur le polydata)
5. (Optionnel) lissage + calcul des normales
6. Export du mesh (.stl ou .vtp)

Dépendance : pip install vtk --break-system-packages
"""

import argparse
import sys

import vtk


def mask_to_largest_region_surface(
    input_nifti_path: str,
    output_mesh_path: str,
    smooth: bool = True,
    smoothing_iterations: int = 20,
    decimate: bool = False,
    decimate_reduction: float = 0.5,
    apply_orientation: bool = True,
    ras_to_lps: bool = False,
):
    # ------------------------------------------------------------------
    # 1. Lecture du NIfTI
    # ------------------------------------------------------------------
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(input_nifti_path)
    reader.Update()

    image = reader.GetOutput()

    # ------------------------------------------------------------------
    # 2. Extraction de la plus grande composante connexe
    #    vtkImageConnectivityFilter travaille directement sur l'image
    #    (plus robuste/rapide que de le faire sur le mesh après coup).
    # ------------------------------------------------------------------
    connectivity = vtk.vtkImageConnectivityFilter()
    connectivity.SetInputData(image)
    # On considère comme "objet" tout voxel dans cet intervalle de scalaires
    connectivity.SetScalarRange(1, 1)  # le mask contient des 0 et des 1
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.SetLabelModeToConstantValue()
    connectivity.SetLabelConstantValue(1)  # la région gardée est relabellisée à 1
    connectivity.Update()

    largest_region_image = connectivity.GetOutput()

    # ------------------------------------------------------------------
    # 3. Isosurface (Marching Cubes discret, adapté aux masques labellisés)
    # ------------------------------------------------------------------
    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputData(largest_region_image)
    dmc.SetValue(0, 1)  # contour de la valeur 1 (la région extraite)
    dmc.ComputeNormalsOn()
    dmc.Update()

    mesh = dmc.GetOutput()

    # ------------------------------------------------------------------
    # 4. Lissage (optionnel mais recommandé pour un mask "en escalier")
    # ------------------------------------------------------------------
    if smooth:
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputData(mesh)
        smoother.SetNumberOfIterations(smoothing_iterations)
        smoother.BoundarySmoothingOff()
        smoother.FeatureEdgeSmoothingOff()
        smoother.SetPassBand(0.1)
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()
        smoother.Update()
        mesh = smoother.GetOutput()

    # ------------------------------------------------------------------
    # 4bis. Décimation (optionnel, pour réduire le nombre de triangles)
    # ------------------------------------------------------------------
    if decimate:
        decimator = vtk.vtkDecimatePro()
        decimator.SetInputData(mesh)
        decimator.SetTargetReduction(decimate_reduction)
        decimator.PreserveTopologyOn()
        decimator.Update()
        mesh = decimator.GetOutput()

    # ------------------------------------------------------------------
    # 5. Orientation correcte dans l'espace monde (sform/qform NIfTI)
    #
    #    vtkImageData ne peut représenter qu'un repère aligné sur les axes
    #    (spacing + origine), pas une rotation. Si le header NIfTI contient
    #    une rotation (sform/qform non diagonale), elle est ignorée par la
    #    géométrie de l'image et doit donc être appliquée manuellement sur
    #    le polydata en sortie, sous peine d'un mesh mal placé/orienté.
    # ------------------------------------------------------------------
    if apply_orientation:
        orientation_matrix = reader.GetSFormMatrix()
        if orientation_matrix is None:
            orientation_matrix = reader.GetQFormMatrix()

        if orientation_matrix is not None:
            transform = vtk.vtkTransform()
            transform.SetMatrix(orientation_matrix)

            if ras_to_lps:
                # NIfTI : convention RAS+. De nombreux outils (Slicer, DICOM,
                # planification chirurgicale...) attendent du LPS+.
                # On post-multiplie par la matrice de conversion RAS -> LPS.
                ras_to_lps_matrix = vtk.vtkMatrix4x4()
                ras_to_lps_matrix.Identity()
                ras_to_lps_matrix.SetElement(0, 0, -1)
                ras_to_lps_matrix.SetElement(1, 1, -1)
                transform.PostMultiply()
                transform.Concatenate(ras_to_lps_matrix)

            transform_filter = vtk.vtkTransformPolyDataFilter()
            transform_filter.SetTransform(transform)
            transform_filter.SetInputData(mesh)
            transform_filter.Update()
            mesh = transform_filter.GetOutput()
        else:
            print(
                "Avertissement : aucune matrice sform/qform trouvée dans le "
                "header NIfTI, le mesh reste dans l'espace voxel/spacing brut."
            )

    # ------------------------------------------------------------------
    # 6. Recalcul des normales (propre après transformation/décimation)
    # ------------------------------------------------------------------
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(mesh)
    normals.ConsistencyOn()
    normals.SplittingOff()
    normals.Update()
    mesh = normals.GetOutput()

    # ------------------------------------------------------------------
    # 7. Export
    # ------------------------------------------------------------------
    if output_mesh_path.lower().endswith(".stl"):
        writer = vtk.vtkSTLWriter()
    elif output_mesh_path.lower().endswith(".vtp"):
        writer = vtk.vtkXMLPolyDataWriter()
    elif output_mesh_path.lower().endswith(".ply"):
        writer = vtk.vtkPLYWriter()
    else:
        raise ValueError("Extension de sortie non supportée : utilisez .stl, .vtp ou .ply")

    writer.SetFileName(output_mesh_path)
    writer.SetInputData(mesh)
    writer.Write()

    print(f"Mesh écrit : {output_mesh_path}")
    print(f"  Points : {mesh.GetNumberOfPoints()}")
    print(f"  Triangles : {mesh.GetNumberOfCells()}")

    return mesh


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extrait la plus grande région connexe d'un masque binaire NIfTI "
            "et génère le mesh surfacique (isosurface) correspondant."
        )
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Chemin du masque binaire NIfTI en entrée (.nii ou .nii.gz)",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Chemin du mesh en sortie (.stl, .vtp ou .ply)",
    )
    parser.add_argument(
        "--no-smooth",
        action="store_true",
        help="Désactive le lissage du mesh (activé par défaut)",
    )
    parser.add_argument(
        "--smoothing-iterations",
        type=int,
        default=20,
        help="Nombre d'itérations de lissage (défaut : 20)",
    )
    parser.add_argument(
        "--decimate",
        action="store_true",
        help="Active la décimation du mesh pour réduire le nombre de triangles",
    )
    parser.add_argument(
        "--decimate-reduction",
        type=float,
        default=0.5,
        help="Fraction de triangles à supprimer lors de la décimation, entre 0 et 1 (défaut : 0.5)",
    )
    parser.add_argument(
        "--no-orientation",
        action="store_true",
        help=(
            "Désactive l'application de la matrice sform/qform du NIfTI sur le "
            "mesh (activée par défaut ; à désactiver seulement si vous gérez "
            "l'orientation vous-même en aval)"
        ),
    )
    parser.add_argument(
        "--ras-to-lps",
        action="store_true",
        help=(
            "Convertit les coordonnées du mesh de RAS+ (convention NIfTI) vers "
            "LPS+ (convention DICOM/Slicer/planification chirurgicale)"
        ),
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.decimate and not (0.0 < args.decimate_reduction < 1.0):
        parser.error("--decimate-reduction doit être compris strictement entre 0 et 1")

    try:
        mask_to_largest_region_surface(
            input_nifti_path=args.input,
            output_mesh_path=args.output,
            smooth=not args.no_smooth,
            smoothing_iterations=args.smoothing_iterations,
            decimate=args.decimate,
            decimate_reduction=args.decimate_reduction,
            apply_orientation=not args.no_orientation,
            ras_to_lps=args.ras_to_lps,
        )
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
