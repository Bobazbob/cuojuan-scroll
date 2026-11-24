from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageCms
from scipy.ndimage import distance_transform_edt
import numpy as np, json,csv,shutil

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'H09_ui_v01'
SOURCE=Path(r'C:/Users/Bobazbob/.codex/generated_images/01a2076e-95aa-72a1-b0dd-073304092804')
(OUT/'ui').mkdir(parents=True,exist_ok=True);(OUT/'sources').mkdir(exist_ok=True);(OUT/'reference').mkdir(exist_ok=True)
PROFILE=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
FILES=[('scroll_frame','exec-783163f3-d9a4-431c-817b-a901778a17e7.png'),('paper_texture','exec-d0268bf5-7d64-412e-b126-8eb1807afb00.png'),('ending_card_frame','exec-fb2b856c-cbbd-430a-8874-b47b9adab1a4.png')]
ROWS=[];CHECKS=[]
for name,filename in FILES:
    shutil.copy2(SOURCE/filename,OUT/'sources'/f'{name}_generated.png')
    im=Image.open(SOURCE/filename).convert('RGBA');arr=np.array(im)
    a=arr[:,:,3];dist=distance_transform_edt(a>=240)
    nearest=distance_transform_edt(~(dist>=3),return_distances=False,return_indices=True)
    rgb=arr[:,:,:3];hi=rgb.max(axis=2).astype(float);lo=rgb.min(axis=2).astype(float)
    bad=(a>0)&(dist<4)&(hi>215)&((hi-lo)/(hi+1)>0.80)
    rgb[bad]=rgb[nearest[0][bad],nearest[1][bad]]
    arr[a==0,:3]=0;im=Image.fromarray(arr)
    crop_h=im.width*9/16;top=(im.height-crop_h)/2
    im=im.convert('RGBa').resize((1600,900),Image.Resampling.LANCZOS,box=(0,max(0,top),im.width,min(im.height,top+crop_h))).convert('RGBA')
    arr=np.array(im);a=arr[:,:,3];gap=distance_transform_edt(~(a>=16))
    residue=(a>0)&(a<16)&(gap>3);arr[residue]=0
    if name=='paper_texture':
        # A translucent overlay of the actual generated fiber image, not a synthesized texture.
        arr[:,:,3]=np.round(arr[:,:,3].astype(float)*0.12).astype(np.uint8)
    arr[arr[:,:,3]==0,:3]=0
    target=OUT/'ui'/f'{name}.png';Image.fromarray(arr).save(target,icc_profile=PROFILE,optimize=True)
    alpha=arr[:,:,3];hist=np.bincount(alpha.ravel(),minlength=256)
    assert hist[0]>0 and alpha.max()>0
    notes='真实图像工具生成；1600×900 RGBA/sRGB；中心透明；整幅等比使用，不做九宫格拉伸'
    if name=='paper_texture':notes='真实生成纸纹的12%alpha透明叠加版；无缝平铺未验证，按整幅16:9使用；不作为底色'
    ROWS.append(dict(asset_id='ui_'+name,kind='ui',character='',scene='',expression='',layer='',file_relpath='ui/'+name+'.png',width=1600,height=900,has_alpha='true',foot_anchor_x='',foot_anchor_y='',status='measured',notes=notes))
    CHECKS.append(dict(file='ui/'+name+'.png',dimensions=[1600,900],alpha_extrema=[int(alpha.min()),int(alpha.max())],transparent_pixels=int(hist[0]),opaque_pixels=int(hist[255]),bytes=target.stat().st_size,icc_srgb=True))
with (OUT/'assets.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(ROWS[0]));writer.writeheader();writer.writerows(ROWS)
(OUT/'validation.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
board=Image.new('RGB',(1600,930),'#f4ebdd');draw=ImageDraw.Draw(board)
for i,(name,_) in enumerate(FILES):
    im=Image.open(OUT/'ui'/f'{name}.png');im.thumbnail((1540,285),Image.Resampling.LANCZOS)
    bg=Image.new('RGBA',(1540,285),'#d8ded6');bg.alpha_composite(im,((1540-im.width)//2,(285-im.height)//2))
    board.paste(bg.convert('RGB'),(30,i*310+25));draw.text((40,i*310+2),name,font=font,fill='#342f2a')
board.save(OUT/'preview.png')
for folder,scene in [('H07_huaguoshan_v01','huaguoshan'),('H08_daguanyuan_v01','daguanyuan')]:
    shutil.copy2(ROOT/folder/'preview.png',OUT/'reference'/f'{scene}_daiyu.png')
    shutil.copy2(ROOT/folder/'annotated-preview.png',OUT/'reference'/f'{scene}_annotated.png')

scene=Image.open(ROOT/'H07_huaguoshan_v01/preview.png').convert('RGBA')
scene.alpha_composite(Image.open(OUT/'ui/scroll_frame.png'))
scene.save(OUT/'stage-art-reference.png',icc_profile=PROFILE,optimize=True)

# Static card composition reference, not a screenshot, runtime renderer, or baked UI asset.
card=Image.new('RGBA',(1600,900),'#f4ebdd')
card.alpha_composite(Image.open(OUT/'ui/paper_texture.png'))
painting=Image.open(ROOT/'H07_huaguoshan_v01/preview.png').convert('RGBA').resize((1008,567),Image.Resampling.LANCZOS)
card.alpha_composite(painting,(75,132))
draw=ImageDraw.Draw(card)
fontpath='C:/Windows/Fonts/simsun.ttc'
titlefont=ImageFont.truetype(fontpath,48);bodyfont=ImageFont.truetype(fontpath,27);caption=ImageFont.truetype(fontpath,24)
draw.text((92,74),'错卷 · 花果山',font=caption,fill='#3f6c61')
draw.line((1120,164,1120,709),fill='#b7b2a1',width=2)
draw.text((1170,172),'花有归处',font=titlefont,fill='#342f2a')
text=json.loads((ROOT/'H04_stories_v01/endings.json').read_text(encoding='utf-8'))['endings'][0]['text']
line='';lines=[]
for char in text:
    if draw.textlength(line+char,font=bodyfont)>330 and line:
        lines.append(line);line=char
    else:line+=char
if line:lines.append(line)
for i,line in enumerate(lines):draw.text((1170,250+i*37),line,font=bodyfont,fill='#4a4640')
draw.text((92,752),'林黛玉 · 先安葬落花',font=caption,fill='#3f6c61')
draw.text((92,802),'静态排版参考，正文由程序生成；不是网页实录',font=caption,fill='#70675d')
card.alpha_composite(Image.open(OUT/'ui/ending_card_frame.png'))
card.save(OUT/'ending-card-reference.png',icc_profile=PROFILE,optimize=True)
endings=json.loads((ROOT/'H04_stories_v01/endings.json').read_text(encoding='utf-8'))['endings']
with (OUT/'ending-effects.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['endingId','expression','effects','runtime_status'])
    for e in endings:w.writerow([e['endingId'],e['expression'],'|'.join(e['effects']),'由A运行实现与验证；B已检查引用'])
print(json.dumps(CHECKS,ensure_ascii=False,indent=2))
