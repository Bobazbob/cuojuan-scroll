from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parents[2]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def board(items,name,cols=2,width=640):
 rows=(len(items)+cols-1)//cols;cellh=width*9//16+40
 result=Image.new('RGB',(cols*width,rows*cellh),'#eee6da');d=ImageDraw.Draw(result)
 for i,(label,p) in enumerate(items):
  im=Image.open(OUT/p).convert('RGB');im.thumbnail((width,cellh-40))
  x=(i%cols)*width;y=(i//cols)*cellh
  d.text((x+12,y+10),label,font=small,fill='#342f2a')
  result.paste(im,(x+(width-im.width)//2,y+40))
 result.save(OUT/name)
board([
 ('PUBLIC / cover','public_desktop_bury/01_cover.png'),
 ('PUBLIC / character selection','public_desktop_bury/02_character.png'),
 ('PUBLIC / placement','public_desktop_bury/03_placement.png'),
 ('PUBLIC / intro','public_desktop_bury/04_intro_1.png'),
 ('PUBLIC / choice','public_desktop_bury/05_choice.png'),
 ('PUBLIC / ending 1 + petal gather','public_desktop_bury/06_effect_5.png'),
 ('PUBLIC / ending 2 + petal fall','public_desktop_protect/06_effect_5.png'),
 ('PUBLIC / replay','public_desktop_protect/08_replay.png'),
],'public-flow-contact.png')

# Screenshot crops only; the lower panel is a diagnostic DOM mask-off render, not a repaired page.
result=Image.new('RGB',(1360,330),'#f4ebdd');d=ImageDraw.Draw(result)
for y,label,name in [(0,'ACTUAL PUBLIC: mask affects text + control','diagnostic-actual-1600.png'),
                     (165,'DIAGNOSTIC ONLY: mask disabled in browser DOM','diagnostic-mask-off-1600.png')]:
 d.text((10,y+5),label,font=font,fill='#342f2a')
 im=Image.open(OUT/name).crop((130,706,1470,821)).convert('RGB')
 result.paste(im,(10,y+40))
 for x0,x1 in [(37,117),(1209,1305)]:
  d.rectangle((10+x0,y+42,10+x1,y+149),outline='#b73333',width=2)
result.save(OUT/'issue-V01-mask.png')

result=Image.new('RGB',(770,650),'#f4ebdd');d=ImageDraw.Draw(result)
for x,w,label in [(15,390,'390px: scene ratio 1.738 (expected 1.778)'),(430,320,'320px: 1.713 (expected 1.778)')]:
 d.text((x,14),str(w)+'px / ACTUAL PUBLIC',font=small,fill='#342f2a')
 im=Image.open(OUT/f'diagnostic-actual-{w}.png').convert('RGB')
 result.paste(im,(x,48))
 d.rectangle((x+12,60,x+w-12,60+(211 if w==390 else 173)),outline='#b73333',width=2)
 d.text((x,620),label.split(': ')[-1],font=small,fill='#9b2828')
result.save(OUT/'issue-V02-small-screen.png')

# Read-only hashes tie the displayed official images to B's accepted deliveries.
manifest=json.loads((PROJECT/'work/b-deliveries/B_delivery_manifest_v01.json').read_text(encoding='utf8'))
(OUT/'manifest-structure.txt').write_text(str(type(manifest))+'\n'+str(list(manifest) if isinstance(manifest,dict) else manifest[:1]),encoding='utf8')
inventory=[]
for path in sorted(OUT.rglob('*')):
 if path.is_file() and path.name!='evidence-index.json':
  inventory.append({'path':path.relative_to(OUT).as_posix(),'bytes':path.stat().st_size,
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT/'evidence-index.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False),encoding='utf8')
print('screenshots',sum(x['path'].endswith('.png') for x in inventory),'files',len(inventory))
