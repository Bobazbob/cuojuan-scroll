from pathlib import Path
from PIL import Image, ImageCms, ImageDraw
from scipy.ndimage import distance_transform_edt
import numpy as np
import json, csv, shutil

ROOT=Path(__file__).resolve().parents[1]/'H05_character_base_v01'
SOURCE=Path(r'C:/Users/Bobazbob/.codex/generated_images/01a2076e-95aa-72a1-b0dd-073304092804')
ITEMS=[('daiyu','exec-050c0877-c167-4818-8640-69c8dd2c8145.png'),('wukong','exec-a250cef9-cdad-442d-bfeb-503a7f913b71.png')]
PROFILE=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
ROWS=[]
for character,filename in ITEMS:
    source=SOURCE/filename
    (ROOT/'sources').mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,ROOT/'sources'/f'{character}_generated.png')
    im=Image.open(source).convert('RGBA')
    rgba=np.array(im); alpha=rgba[:,:,3]
    distance=distance_transform_edt(alpha>=240)
    nearest=distance_transform_edt(~(distance>=3),return_distances=False,return_indices=True)
    rgb=rgba[:,:,:3]; high=rgb.max(axis=2).astype(float); low=rgb.min(axis=2).astype(float)
    contaminated=(alpha>0)&(distance<4)&(high>215)&((high-low)/(high+1)>0.80)
    rgb[contaminated]=rgb[nearest[0][contaminated],nearest[1][contaminated]]
    rgba[alpha==0,:3]=0
    im=Image.fromarray(rgba)
    mask=alpha>=128; y_last=int(np.where(mask)[0].max())
    xs=np.where(mask[max(0,y_last-12):y_last+1])[1]
    contact_mid=(int(xs.min())+int(xs.max()))/2
    scale=768/im.width
    resized=im.convert('RGBa').resize((768,1024),Image.Resampling.LANCZOS).convert('RGBA')
    dx=round(384-contact_mid*scale); dy=round(1004-y_last*scale)
    canvas=Image.new('RGBA',(768,1024),(0,0,0,0));canvas.alpha_composite(resized,(dx,dy))
    target=ROOT/'characters'/character/f'{character}_neutral.png';target.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(target,icc_profile=PROFILE,optimize=True)
    final=np.array(canvas.getchannel('A'));solid=final>=128;fy=int(np.where(solid)[0].max())
    support=np.where(solid[max(0,fy-8):fy+1])[1];fx=(int(support.min())+int(support.max()))/2
    ROWS.append(dict(asset_id=character+'_neutral',kind='character',character=character,scene='',expression='neutral',layer='',file_relpath=target.relative_to(ROOT).as_posix(),width=768,height=1024,has_alpha='true',foot_anchor_x=f'{fx/768:.3f}',foot_anchor_y=f'{fy/1024:.3f}',status='measured',notes=f'RGBA真透明/sRGB ICC；实测鞋履接触带中点({fx},{fy})；边缘去污染{int(contaminated.sum())}像素；未游戏试放'))
header=['asset_id','kind','character','scene','expression','layer','file_relpath','width','height','has_alpha','foot_anchor_x','foot_anchor_y','status','notes']
with (ROOT/'assets.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(ROWS)
(ROOT/'measurements.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=Image.new('RGB',(1000,1050),'#f4ebdd');draw=ImageDraw.Draw(board)
for j,(character,_) in enumerate(ITEMS):
    im=Image.open(ROOT/'characters'/character/f'{character}_neutral.png')
    for k,color in enumerate(['#efefef','#253c38']):
        panel=Image.new('RGBA',(500,510),color);figure=im.copy();figure.thumbnail((360,480),Image.Resampling.LANCZOS)
        panel.alpha_composite(figure,((500-figure.width)//2,20));board.paste(panel.convert('RGB'),(j*500,k*520))
        draw.text((j*500+12,k*520+8),character+' neutral / alpha preview',fill=('#342f2a' if k==0 else 'white'))
board.save(ROOT/'preview.png')
print(json.dumps(ROWS,ensure_ascii=False,indent=2))
