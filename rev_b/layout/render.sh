#!/bin/bash
# render.sh BOARD OUTDIR [LAYERS] : PDF export of the board, split into three PNG sections (left, middle, right).
set -euo pipefail
B=$1; O=$2; LAY=${3:-F.Cu,B.Cu,F.Fab,Edge.Cuts,User.Comments}
CLI=/home/jari/dev/tube_preamp_kicad/tools/p2k/bin/kicad-cli
mkdir -p "$O"
$CLI pcb export pdf --mode-single -l "$LAY" --scale 0 -o "$O/board.pdf" "$B" >/dev/null
pdftoppm -r 900 -png -singlefile "$O/board.pdf" "$O/full"
python3 - "$O" <<'PY'
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
o=sys.argv[1]; im=Image.open(f"{o}/full.png").convert("RGB")
bg=Image.new("RGB",im.size,(255,255,255)); 
from PIL import ImageChops
bb=ImageChops.difference(im,bg).getbbox(); im=im.crop(bb); w,h=im.size
for i,n in enumerate("LMR"):
    im.crop((int(i*w/3)-40 if i else 0,0,min(w,int((i+1)*w/3)+40),h)).save(f"{o}/{n}.png")
print(im.size)
PY
