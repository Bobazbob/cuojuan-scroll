from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageCms
from scipy.ndimage import distance_transform_edt
import numpy as np,json,csv,shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(r'C:/Users/Bobazbob/.codex/generated_images/01a2076e-95aa-72a1-b0dd-073304092804')
PROFILE=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
SCENES={
 'huaguoshan':('H07_huaguoshan_v01','exec-3686fdf4-84ed-4ee6-a872-eb9a41e89a2c.png',[
 'exec-6eabf2e3-00d2-490d-a783-76b145d19241.png','exec-44a4ce93-fd52-4453-919a-53d21c01a498.png','exec-c8a000fb-f1ae-4605-a6a8-f3bd76362cbe.png','exec-8bc56d12-7a56-4ff9-866f-379d6ec9fd4f.png']),
 'daguanyuan':('H08_daguanyuan_v01','exec-984aa08c-7337-42c0-a5c3-55d3f3f2a674.png',[
 'exec-73d58526-c620-4056-b3e5-74de3eca8b4f.png','exec-73c9018f-aef1-48ad-861f-ec724683a953.png','exec-f4a399c7-13fb-41cb-8875-ba3ff67802ac.png','exec-ec82bece-29c5-4cb1-8d83-0b2f451822a9.png'])}
CHARACTERS=ROOT/'H06_characters_v01'
CHAR_ROWS={r['character']:r for r in csv.DictReader((CHARACTERS/'assets.csv').open(encoding='utf-8-sig')) if r['expression']=='neutral'}
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
SMALL=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)

def normalize(path,opaque=False):
    im=Image.open(path).convert('RGBA');arr=np.array(im)
    if not opaque:
        alpha=arr[:,:,3];dist=distance_transform_edt(alpha>=240)
        nearest=distance_transform_edt(~(dist>=3),return_distances=False,return_indices=True)
        rgb=arr[:,:,:3];hi=rgb.max(axis=2).astype(float);lo=rgb.min(axis=2).astype(float)
        bad=(alpha>0)&(dist<4)&(hi>215)&((hi-lo)/(hi+1)>0.80)
        rgb[bad]=rgb[nearest[0][bad],nearest[1][bad]]
        arr[alpha==0,:3]=0;im=Image.fromarray(arr)
    crop_h=im.width*9/16;crop_y=(im.height-crop_h)/2
    assert crop_y>=-1
    output=im.convert('RGBa').resize((1600,900),Image.Resampling.LANCZOS,box=(0,max(0,crop_y),im.width,min(im.height,crop_y+crop_h))).convert('RGBA')
    array=np.array(output)
    if opaque: array[:,:,3]=255
    else:
        a=array[:,:,3];gap=distance_transform_edt(~(a>=16));residue=(a>0)&(a<16)&(gap>3)
        array[residue]=0;array[array[:,:,3]==0,:3]=0
    return Image.fromarray(array)

for scene,(folder,reference,names) in SCENES.items():
    out=ROOT/folder;(out/'sources').mkdir(parents=True,exist_ok=True)
    target_dir=out/'scenes'/scene;target_dir.mkdir(parents=True,exist_ok=True)
    shutil.copy2(SOURCE/reference,out/'sources/reference_generated.png')
    normalize(SOURCE/reference,True).save(out/'reference.png',icc_profile=PROFILE,optimize=True)
    layers=[];rows=[];checks=[]
    for n,(name,layer) in enumerate(zip(names,['back','mid','ground','front']),1):
        shutil.copy2(SOURCE/name,out/'sources'/f'layer{n}_generated.png')
        im=normalize(SOURCE/name,n==1)
        target=target_dir/f'{scene}_layer{n}_{layer}.png'
        im.save(target,icc_profile=PROFILE,optimize=True);layers.append(im)
        alpha=np.array(im.getchannel('A'));hist=np.bincount(alpha.ravel(),minlength=256)
        if n==1: assert alpha.min()==255
        else: assert hist[0]>100000
        if n in [2,4]: assert alpha[720:,:].max()==0
        if n==4: assert alpha[36:108,1152:1504].max()==0
        row=dict(asset_id=f'{scene}_layer{n}_{layer}',kind='scene_layer',character='',scene=scene,expression='',layer=layer,file_relpath=target.relative_to(out).as_posix(),width=1600,height=900,has_alpha='true',foot_anchor_x='',foot_anchor_y='',status='measured',notes='实际图像工具生成；等比精确导出；RGBA/sRGB ICC；底层全不透明' if n==1 else '实际图像工具生成的透明独立层；清除远处低alpha残留；实际叠合另看preview；未页面验收')
        rows.append(row);checks.append(dict(file=row['file_relpath'],dimensions=[1600,900],alpha_min=int(alpha.min()),alpha_max=int(alpha.max()),zero_alpha_pixels=int(hist[0]),reading_area_alpha_max=int(alpha[720:,:].max()),bytes=target.stat().st_size,icc_srgb=True))
    scene_image=Image.new('RGBA',(1600,900));
    for im in layers: scene_image.alpha_composite(im)
    scene_image.save(out/'preview_scene.png',icc_profile=PROFILE,optimize=True)
    previews={};measures={}
    for character,x,height in [('daiyu',1000,504),('wukong',1200,480)]:
        config=CHAR_ROWS[character]
        sprite=Image.open(CHARACTERS/config['file_relpath']).convert('RGBA')
        sprite=sprite.convert('RGBa').resize((height*3//4,height),Image.Resampling.LANCZOS).convert('RGBA')
        left=round(x-float(config['foot_anchor_x'])*sprite.width);top=round(675-float(config['foot_anchor_y'])*height)
        picture=Image.new('RGBA',(1600,900))
        for im in layers[:3]: picture.alpha_composite(im)
        picture.alpha_composite(sprite,(left,top));picture.alpha_composite(layers[3])
        picture.save(out/('preview.png' if character=='daiyu' else 'preview_wukong.png'),icc_profile=PROFILE,optimize=True)
        previews[character]=picture
        a=np.array(sprite.getchannel('A'));ys,xs=np.where(a>=16)
        bbox=[int(xs.min()+left),int(ys.min()+top),int(xs.max()+left+1),int(ys.max()+top+1)]
        assert 288<=bbox[0]<bbox[2]<=1312 and 108<=bbox[1]<bbox[3]<=720,bbox
        # Static overlap counts: foreground may obscure ground, never the character at these choices.
        sprite_mask=Image.new('L',(1600,900));sprite_mask.paste(sprite.getchannel('A'),(left,top))
        overlap=int(np.sum((np.array(sprite_mask)>=16)&(np.array(layers[3].getchannel('A'))>=16)))
        measures[character]=dict(suggested_drop_point={'x':round(x/1600,3),'y':0.750},sprite_canvas_height_px=height,sprite_canvas_height_ratio=round(height/900,3),measured_static_visible_bbox=bbox,static_foreground_overlap_pixels=overlap,foot_anchor_from_character={'x':float(config['foot_anchor_x']),'y':float(config['foot_anchor_y'])},runtime_placement_verified=False)
    annotated=previews['daiyu'].convert('RGB');draw=ImageDraw.Draw(annotated)
    draw.rectangle((288,108,1312,720),outline='#27634e',width=3)
    draw.rectangle((96,720,1504,873),outline='#9d5143',width=3)
    draw.rectangle((1152,36,1504,108),outline='#765da0',width=3)
    for x,label,color in [(1000,'黛玉建议脚底 (0.625,0.750)','#246648'),(1200,'悟空建议脚底 (0.750,0.750)','#965928')]:
        draw.ellipse((x-7,668,x+7,682),fill=color)
        draw.line((x,675,x,700),fill=color,width=2)
        draw.text((x-190,694),label,font=SMALL,fill=color)
    draw.rectangle((15,15,690,97),fill='#f4ebdd')
    draw.text((27,24),'静态合成标注：绿色=人物框，红色=阅读/选项区',font=FONT,fill='#342f2a')
    draw.text((27,59),'位置为B建议；游戏内落点与遮挡仍由A实测',font=FONT,fill='#342f2a')
    annotated.save(out/'annotated-preview.png',icc_profile=PROFILE,optimize=True)
    with (out/'assets.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'validation.json').write_text(json.dumps({'layers':checks,'composition':measures,'scene_alpha_extrema':scene_image.getchannel('A').getextrema(),'runtime_verified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scene':scene,'layers':checks,'composition':measures},ensure_ascii=False,indent=2))
