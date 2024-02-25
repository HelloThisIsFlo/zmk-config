#!/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

cd "$DIR"


cd ./config
GENERATED_FILENAME=combos_winpc_GENERATED.dtsi
GENERATED_FILEFULLPATH=./features/__GENERATED__/$GENERATED_FILENAME


function generate_winpc_combo_for {
  combo_file=$1


  keep_combo_any=.'*COMBO_ANY_..._....\(.*'
  keep_combo_alpha_aks='.*COMBO_LAY_..._HAND\(l_alpha_aks.*'
  keep_2nd_line_of_2_lines_combos='^                   .*\)'


  cat  $combo_file |


  ###### Filter lines #######################
  sed -E "/($keep_combo_any|$keep_combo_alpha_aks|$keep_2nd_line_of_2_lines_combos)/!d" | # Filter relevant lines
  sed -E '/#define/d' | # Remove #define
  sed -E '/^\/\/.*/d' | # Remove commented out
  sed -E 's/ \/\/.*//g' | # Remove end of line comments (for easier filtering on the next step)
  tr '\n' '\t' | sed -e 's/)\t[ A-Z0-4]*)\t/)\t/g'  | tr '\t' '\n' | # Remove 2nd Line of 2-line combos that related to a filtered out combo
  tr '\n' '\t' | sed -e 's/^[ A-Z0-4]*)\t/\t/g'  | tr '\t' '\n' | # Remove 2nd Line of 2-line combos that related to a filtered out combo

  ###### Migrate Combos to WinPC layer ######
  sed -e 's/l_alpha_aks,/l_winpc,    /g' |
  sed -e 's/COMBO_ANY_ONE_HAND(           /COMBO_LAY_ONE_HAND(l_winpc,   /g' | 
  sed -e 's/COMBO_ANY_TWO_HAND(           /COMBO_LAY_TWO_HAND(l_winpc,   /g' | 
  sed -e 's/COMBO_ANY_NON_ADJC(           /COMBO_LAY_NON_ADJC(l_winpc,   /g' | 

  ###### Migrate CMD to CTRL ################
  sed -e 's/LG(/LC(/g' |

  ###### Migrate Special Cases ##############
  sed -e 's/bk LA(BSPC)/bk LC(BSPC)/g' | # Special Case: Delete Word

  ###### Prevent duplicate combo name #######
  sed -E 's/.*l_winpc,     [a-zA-Z]*/&\_win/g' | # Add suffix to combo name
  sed -E 's/^    .*\)/    &/g' | # Re-align line 2 of multi-line combos


  cat >> $GENERATED_FILEFULLPATH

}



# Clear the file
echo -n '' > $GENERATED_FILEFULLPATH


for combo_file in $(find . -name "*combos*dtsi" -not -name "$GENERATED_FILENAME"); do
  echo "Processing $combo_file"
  generate_winpc_combo_for $combo_file


done


cd - >/dev/null