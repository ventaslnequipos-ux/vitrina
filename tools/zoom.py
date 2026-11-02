import sys
from PIL import Image, ImageDraw
S="/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad"
# uso: zoom.py archivo x0 y0 x1 y1 salida [escala]
f,x0,y0,x1,y1,out=sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6]
k=float(sys.argv[7]) if len(sys.argv)>7 else 2
im=Image.open(f"{S}/img/{f}").convert("RGB").crop((x0,y0,x1,y1)); im=im.resize((int(im.width*k),int(im.height*k)))
d=ImageDraw.Draw(im)
step=10 if (x1-x0)<300 else 20
for x in range((x0//step+1)*step,x1,step):
  X=(x-x0)*k; d.line([(X,0),(X,6 if x%100 else 16)],fill="red"); 
  if x%(step*5)==0: d.text((X+2,8),str(x),fill="red")
for y in range((y0//step+1)*step,y1,step):
  Y=(y-y0)*k; d.line([(0,Y),(6 if y%100 else 16,Y)],fill="red")
  if y%(step*5)==0: d.text((8,Y+2),str(y),fill="red")
im.save(out)
