from PIL import Image, ImageDraw, ImageFont, ImageOps
S="/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad/"
F=S+"fonts/gf/ofl/"
noche=(2,31,77); azul=(5,54,131); ama=(240,173,19); blanco=(255,255,255); soft=(201,212,230)
W,H=1200,630
im=Image.new("RGB",(W,H),noche); d=ImageDraw.Draw(im)
fotos=["cs78b","jcb","dieci2","lg936"]; cw,ch=330,315
for i,n in enumerate(fotos):
  f=Image.open(S+"img/"+n+".jpg"); f=ImageOps.fit(f,(cw-4,ch-4),centering=(0.5,0.55))
  im.paste(f,((i%2)*cw+2,(i//2)*ch+2))
d.rectangle([660,0,668,H],fill=ama)
def t(x,y,s,font,size,col):
  fo=ImageFont.truetype(F+font,size); d.text((x,y),s,font=fo,fill=col); return d.textlength(s,font=fo)
t(704,48,"CATÁLOGO DE VENTA","barlowcondensed/BarlowCondensed-SemiBold.ttf",30,ama)
t(704,96,"LA VITRINA","barlowcondensed/BarlowCondensed-Bold.ttf",70,blanco)
w=t(704,168,"DE LAS MÁQUINAS","barlowcondensed/BarlowCondensed-Bold.ttf",70,blanco); print("w",704+w)
t(704,258,"by Nestor Sierra","barlowcondensed/BarlowCondensed-SemiBold.ttf",40,ama)
t(704,332,"Maquinaria y vehículos usados","barlow/Barlow-Medium.ttf",28,soft)
t(704,368,"Equipos verificables en Barranquilla","barlow/Barlow-Medium.ttf",28,soft)
d.rectangle([704,450,1156,560],fill=azul)
t(726,462,"WHATSAPP","barlow/Barlow-SemiBold.ttf",22,soft)
t(726,490,"301 795 9540","barlowcondensed/BarlowCondensed-Bold.ttf",56,ama)
im.save(S+"site/og.jpg",quality=84,optimize=True)
