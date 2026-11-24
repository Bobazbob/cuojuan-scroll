from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageCms
from scipy.ndimage import distance_transform_edt
import numpy as np, cv2, csv, json, shutil

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'H05_character_base_v01'
OUT=ROOT/'H06_characters_v01'
SOURCE=Path(r'C:/Users/Bobazbob/.codex/generated_images/01a2076e-95aa-72a1-b0dd-073304092804')
OUT.mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True)
PROFILE=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
JOBS=[('daiyu','happy','exec-ce205481-bd82-403e-80ab-352e4a3b4e6c.png'),('daiyu','upset','exec-7f3e3e17-9e7c-4e85-829d-3a2ed4c07d7d.png'),('wukong','happy','exec-149103cd-edef-4b67-9d2d-1750edee9da4.png'),('wukong','angry','exec-60815a8d-39a7-490b-a41c-cbc450c07646.png')]
POLYGONS={'daiyu':[(348,143),(395,136),(417,150),(419,188),(403,212),(369,207),(347,184)],'wukong':[(382,186),(435,182),(468,199),(474,240),(454,278),(413,276),(392,248)]}
HEAD={'daiyu':(258,54,430,236),'wukong':(293,115,484,296)}
BASE_ROWS=list(csv.DictReader((BASE/'assets.csv').open(encoding='utf-8-sig')))
ROWS=[];REPORT=[]
MASTERS={}
for character in ['daiyu','wukong']:
    old=Image.open(BASE/'characters'/character/f'{character}_neutral.png').convert('RGBA')
    a=np.array(old);alpha=a[:,:,3]
    gap=distance_transform_edt(~(alpha>=16))
    residue=(alpha>0)&(alpha<16)&(gap>3)
    a[residue]=0
    a[a[:,:,3]==0,:3]=0
    assert np.array_equal(np.array(old)[:,:,3]>=16,a[:,:,3]>=16)
    master=Image.fromarray(a);MASTERS[character]=master
    target=OUT/'characters'/character/f'{character}_neutral.png';target.parent.mkdir(parents=True,exist_ok=True)
    master.save(target,icc_profile=PROFILE,optimize=True)
    row=dict(next(row for row in BASE_ROWS if row['character']==character))
    row['notes']+='；按A反馈清理离主体>3px的低alpha残留，主体alpha≥16与锚点不变'
    ROWS.append(row)
    REPORT.append({'file':row['file_relpath'],'low_alpha_residue_removed':int(residue.sum()),'visible_alpha_mask_unchanged':True,'foot_anchor_unchanged':True})
for character,expression,filename in JOBS:
    source=SOURCE/filename;shutil.copy2(source,OUT/'sources'/f'{character}_{expression}_generated.png')
    master=MASTERS[character];a=np.array(master)
    edited=Image.open(source).convert('RGBA').convert('RGBa').resize((768,1024),Image.Resampling.LANCZOS).convert('RGBA')
    b=np.array(edited)
    x0,y0,x1,y1=HEAD[character]
    template=cv2.cvtColor(a[y0:y1,x0:x1,:3],cv2.COLOR_RGB2GRAY).astype('float32')/255
    image=cv2.cvtColor(b[y0:y1,x0:x1,:3],cv2.COLOR_RGB2GRAY).astype('float32')/255
    warp=np.eye(2,3,dtype=np.float32)
    try:
        score,warp=cv2.findTransformECC(template,image,warp,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,150,1e-6),None,3)
        assert abs(float(warp[0,2]))<15 and abs(float(warp[1,2]))<15
    except (cv2.error,AssertionError):
        score=0;warp=np.eye(2,3,dtype=np.float32)
    aligned=cv2.warpAffine(b[:,:,:3],warp,(768,1024),flags=cv2.INTER_CUBIC|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
    mask=Image.new('L',(768,1024));ImageDraw.Draw(mask).polygon(POLYGONS[character],fill=255)
    mask=np.array(mask.filter(ImageFilter.GaussianBlur(1.4))).astype(float)/255
    mask[a[:,:,3]<240]=0
    result=a.copy();result[:,:,:3]=np.round(a[:,:,:3]*(1-mask[:,:,None])+aligned*mask[:,:,None]).astype(np.uint8)
    result[a[:,:,3]==0,:3]=0
    target=OUT/'characters'/character/f'{character}_{expression}.png'
    Image.fromarray(result).save(target,icc_profile=PROFILE,optimize=True)
    assert np.array_equal(result[:,:,3],a[:,:,3])
    assert np.array_equal(result[mask==0],a[mask==0])
    row=dict(next(row for row in BASE_ROWS if row['character']==character))
    row.update(asset_id=character+'_'+expression,expression=expression,file_relpath=target.relative_to(OUT).as_posix(),notes='实际图像模型编辑表情；注册后仅合成面部内区；面部外像素/完整alpha与本包neutral逐像素一致；实测足底沿母版；未游戏切换')
    ROWS.append(row)
    REPORT.append({'file':row['file_relpath'],'registration_translation':warp[:,2].tolist(),'registration_score':float(score),'outside_face_identical':True,'alpha_identical':True,'head_foot_shift_pixels':0,'face_polygon':POLYGONS[character]})
header=list(BASE_ROWS[0].keys())
with (OUT/'assets.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(ROWS)
(OUT/'alignment-check.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=Image.new('RGB',(1500,1400),'#f4ebdd');draw=ImageDraw.Draw(board)
for i,character in enumerate(['daiyu','wukong']):
    expressions=['neutral','happy','upset' if character=='daiyu' else 'angry']
    for j,expression in enumerate(expressions):
        im=Image.open(OUT/'characters'/character/f'{character}_{expression}.png')
        thumb=im.copy();thumb.thumbnail((370,650),Image.Resampling.LANCZOS)
        panel=Image.new('RGBA',(500,680),'#ede9df');panel.alpha_composite(thumb,((500-thumb.width)//2,20))
        board.paste(panel.convert('RGB'),(j*500,i*700));draw.text((j*500+10,i*700+5),character+' '+expression,fill='black')
board.save(OUT/'preview.png')
faces=Image.new('RGB',(1350,620),'#efeadd');draw=ImageDraw.Draw(faces)
for i,character in enumerate(['daiyu','wukong']):
    for j,expression in enumerate(['neutral','happy','upset' if character=='daiyu' else 'angry']):
        im=Image.open(OUT/'characters'/character/f'{character}_{expression}.png')
        crop=im.crop(HEAD[character]);crop.thumbnail((400,270),Image.Resampling.LANCZOS)
        crop=crop.resize((round(crop.width*1.3),round(crop.height*1.3)),Image.Resampling.LANCZOS)
        bg=Image.new('RGBA',crop.size,'#eee8dc');bg.alpha_composite(crop);faces.paste(bg.convert('RGB'),(j*450+5,i*310+20))
        draw.text((j*450+5,i*310+3),character+' '+expression,fill='black')
faces.save(OUT/'face-comparison.png')
print(json.dumps(REPORT,ensure_ascii=False,indent=2))
