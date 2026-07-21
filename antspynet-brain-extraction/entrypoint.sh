#!/bin/bash


# ── Gestion dynamique des droits utilisateur ──────────────────────────────────
USER_ID=$(id -u)
GROUP_ID=$(id -g)

groupadd -f -g ${GROUP_ID} usergroup 2>/dev/null
id -u ${USER_ID} &>/dev/null || \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash dynamicuser 2>/dev/null

# Si on est root (cas du -u non passé), on relance avec gosu
if [ "$(id -u)" = "0" ] && [ "${USER_ID}" != "0" ]; then
    exec gosu ${USER_ID}:${GROUP_ID} "$0" "$@"
fi

# ── Vérification des droits utilisateur ──────────────────────────────────────
hline() { printf "%80s\n" | tr ' ' '-'; }

hline
echo -e "\033[1;33m     Informations utilisateur :\033[0m"
echo -e "     |   Utilisateur : $(whoami 2>/dev/null || echo UID=$(id -u))"
echo -e "     |   UID         : $(id -u)"
echo -e "     |   GID         : $(id -g)"
echo -e "     |   Groupes     : $(id -Gn 2>/dev/null)"
hline
echo -e "\033[1;33m     Vérification des permissions sur les montages :\033[0m"
for DIR in /opt/inout /opt/input /opt/output; do
    if touch ${DIR}/.test_write 2>/dev/null; then
        rm -f ${DIR}/.test_write
        echo -e "     |   \033[0;32m[OK]\033[0m  ${DIR} — accessible en écriture"
    else
        echo -e "     |   \033[0;31m[KO]\033[0m  ${DIR} — NON accessible en écriture"
    fi
done
hline

############################################################
# Help                                                     #
############################################################
Help()
{
   echo "Script pour extraire un masque et une surface à partir d'une entrée."
   echo
   echo "Syntax: $0 [-i|m|s|h]"
   echo "options:"
   echo "  -i     Fichier d'entrée (obligatoire)."
   echo "  -m     Chemin pour le masque de sortie (obligatoire)."
   echo "  -s     Chemin pour la surface de sortie (obligatoire)."
   echo "  -h     Affiche cette aide."
   echo
}

function HelpViaAnts {
    cat <<HELP
Usage:
`basename $0` -i <input> -o <mask_output> -s <surface_output>

Exemple:
`basename $0` -i input.nii.gz -o mask.nii.gz -s surface.nii.gz

Arguments obligatoires:
     -i: Fichier d'entrée (ex: image.nii.gz).
     -o: Chemin pour le masque de sortie (ex: /mnt/output/mask.nii.gz).
     -s: Chemin pour la surface de sortie (ex: /mnt/output/surface.nii.gz).

--------------------------------------------------------------------------------------
HELP
    exit 1
}

############################################################
############################################################
# Main program                                             #
############################################################
############################################################

# Initialisation des variables
INPUT=""
MASK=""
SURFACE=""
VERBOSE=0

# Affichage de l'aide si aucun argument ou -h
if [[ "$1" == "-h" || $# -eq 0 ]]; then
    HelpViaAnts >&2
    exit 1
fi

# Lecture des arguments
while getopts "i:o:s:c:v:h" OPT; do
  case $OPT in
      h) # Aide
         HelpViaAnts
         exit 0
         ;;
      i) # Fichier d'entrée
         INPUT=$OPTARG
         ;;
      o) # Masque de sortie
         MASK=$OPTARG
         ;;
      s) # Surface de sortie
         SURFACE=$OPTARG
         ;;
      c) # Surface de sortie
         CONTRAST=$OPTARG
         ;; 
      v) # Mode verbose
         VERBOSE=1
         ;;
     \?) # Erreur dans les options
         echo "Option invalide: -$OPT" >&2
         HelpViaAnts
         exit 1
         ;;
  esac
done

# Vérification des arguments obligatoires
if [[ -z "$INPUT" || -z "$MASK" || -z "$SURFACE" ]]; then
    echo -e "\033[0;31mErreur : Les arguments -i, -o et -s sont obligatoires.\033[0m"
    HelpViaAnts
    exit 1
fi

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ligne horizontale
hline() {
    printf "%${COLUMNS}s\n" | tr ' ' '-'
}

clear
echo -e "${RED}"
figlet "  Smart Heat ablation planning"
echo -e "${NC}"

hline
echo -e "${YELLOW}     Smart Heat App was created by:${NC}"
echo -e "     |   Valéry Ozenne, CNRS, Bordeaux, France, 2026"
echo -e "     |   Nino Avetikovi, CNRS, Bordeaux, France, 2026"
echo -e "     |   Manon Desclides, University of Bordeaux, France, 2026"
echo -e "     |   Hippolyte Salles, University of Bordeaux, France, 2026"
echo -e "     |   Eya Ben Amor, University of Bordeaux, France, 2026"
echo -e "     |   ${GREEN} TODO ${NC}"
hline

echo -e "${YELLOW}     Relevant references for this script include:${NC}"
echo -e "     |   ${BLUE}https://link${NC}"
echo -e "     |   ${BLUE}https://link${NC}"
echo -e "     |   ${BLUE}https://link${NC}"
echo -e "     |   ${BLUE}https://link${NC}"
hline

echo ----------------------------------------------------------------------------------------------

if [ ${VERBOSE} -eq 1 ]; then
    echo "INPUT is ${INPUT}"
    echo "MASK is ${MASK}"
    echo "SURFACE is ${SURFACE}"
    echo "CONTRAST is ${CONTRAST}"
    echo "DIRECTORY is ${DIRECTORY}"
    echo "VERBOSE is ${VERBOSE}"
fi

echo ----------------------------------------------------------------------------------------------

# Affiche les informations de l'utilisateur
echo "Utilisateur dans le conteneur : $(whoami)"
echo "UID: $(id -u), GID: $(id -g)"

# Vérification que les chemins de sortie sont valides
for OUTPUT_PATH in "$MASK" "$SURFACE"; do
    OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo -e "\033[0;31mErreur : Le dossier de sortie $OUTPUT_DIR n'existe pas.\033[0m"
        exit 1
    fi
    if ! touch "$OUTPUT_DIR/.test_write" 2>/dev/null; then
        echo -e "\033[0;31mErreur : Impossible d'écrire dans $OUTPUT_DIR.\033[0m"
        exit 1
    else
        rm -f "$OUTPUT_DIR/.test_write"
    fi
done

# Vérification que le fichier d'entrée existe
if [ ! -f "$INPUT" ]; then
    echo -e "\033[0;31mErreur : Le fichier d'entrée $INPUT n'existe pas.\033[0m"
    exit 1
fi

echo -e "\033[0;32mToutes les vérifications sont réussies. Lancement du traitement...\033[0m"

# Appeler le premier script Python
echo "Exécution de brain_extraction..."
#
python3 /opt/code/brain_extraction.py -i "$INPUT" -o "$MASK" -c "$CONTRAST"  #-d "$DIRECTORY"

# Appeler le deuxième script Python
python3 /opt/code/mask_to_surface.py  -i "$MASK" -o "$SURFACE" --ras-to-lps

echo "Les scripts ont été exécutés avec succès."
