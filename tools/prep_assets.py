import os,re,glob
from PIL import Image
SRC=r"C:\Users\rsagl\OneDrive\Desktop\Red_12_24\articulate\ELH Challenges\done\Tell me your story"
OUT=os.path.dirname(os.path.abspath(__file__))+"\\..\\img"
os.makedirs(OUT,exist_ok=True)
assets=[]  # (name,file)
def save(im,name,maxdim):
    im=im.convert("RGBA")
    bb=im.split()[3].point(lambda v:255 if v>10 else 0).getbbox()
    if bb: im=im.crop(bb)
    im.thumbnail((maxdim,maxdim),Image.LANCZOS)
    fn=name+".png"; im.save(os.path.join(OUT,fn),optimize=True); assets.append((name,fn))
# title: crop to alpha/non-white bbox
t=Image.open(SRC+r"\title.png").convert("RGBA")
bg=Image.new("RGBA",t.size,(255,255,255,255)); diff=Image.composite(t,bg,t.split()[3])
from PIL import ImageChops
bbox=ImageChops.difference(diff.convert("RGB"),Image.new("RGB",t.size,(255,255,255))).getbbox()
tc=t.crop(bbox)
# make near-white transparent
px=tc.load()
for y in range(tc.height):
    for x in range(tc.width):
        r,g,b,a=px[x,y]
        if r>245 and g>245 and b>245: px[x,y]=(r,g,b,0)
save(tc,"ui_title",900)
for n,f in [("lvl_rookie","Picture6"),("lvl_expert","Picture7"),("lvl_master","Picture8"),("lvl_guru","Picture9")]:
    save(Image.open(f"{SRC}\\{f}.png"),n,300)
save(Image.open(SRC+r"\home-run.png"),"ui_home",96)
save(Image.open(SRC+r"\repeat.png"),"ui_repeat",96); save(Image.open(SRC+r"\question.png"),"ui_question",180)
cats=[("card1","chracters","Character"),("card2","place","Place"),("card3","weather","Weather"),("card4","card4","Twist"),("card5","card5","Object")]
lua=["return {"]
for i,(cid,folder,label) in enumerate(cats,1):
    d=SRC+f"\\icons\\new\\{folder}"
    items=[]
    for f in sorted(glob.glob(d+"\\*.png")):
        base=os.path.splitext(os.path.basename(f))[0]
        if "(1)" in base: continue
        key=re.sub(r"[^a-z0-9]+","_",base.lower()).strip("_")
        name=f"c{i}_{key}"
        save(Image.open(f),name,220)
        items.append((name,base.replace("-"," ").replace("_"," ")))
    lua.append(f'  {{ label = "{label}", items = {{ '+", ".join(f'{{ id = "{n}", name = "{d_}" }}' for n,d_ in items)+" } },")
lua.append("}")
open(os.path.dirname(os.path.abspath(__file__))+"\\..\\cards_data.luau","w",encoding="utf-8").write("\n".join(lua)+"\n")
rml=['<Rive version="1" kind="fragment">',
'  <Artboard name="TellMe" width="1280" height="720" defaultStateMachineId="0:7" styleId="0:5" id="0:2">',
'    <LayoutComponentStyle name="Artboard Style" id="0:5" />',
'    <LayoutComponent width="1280" height="720" styleId="0:11" name="Stage" id="0:10">',
'      <LayoutComponentStyle layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto" name="Stage Style" id="0:11" />',
'      <ScriptedLayout scriptAssetId="0:80" name="Game" id="0:12"><FocusData /></ScriptedLayout>',
'    </LayoutComponent>',
'    <LinearAnimation name="Idle" fps="60" duration="60" loopValue="loop" id="0:6" />',
'    <StateMachine name="Main" id="0:7"><StateMachineLayer name="Base" id="0:8">',
'      <AnyState x="200" y="-120" /><ExitState x="400" y="-120" />',
'      <EntryState x="0" y="0" id="0:9"><StateTransition stateToId="0:13" /></EntryState>',
'      <AnimationState x="200" y="0" animationId="0:6" id="0:13" />',
'    </StateMachineLayer></StateMachine>',
'  </Artboard>',
'  <FontAsset file="Montserrat-Bold.ttf" name="Bold" id="0:30" />',
'  <FontAsset file="Montserrat-Medium.ttf" name="Medium" id="0:31" />',
'  <ScriptAsset file="cards_data.luau" isModule="true" name="cards_data" id="0:81" />',
'  <ScriptAsset file="main.luau" name="main" id="0:80" />']
for k,(n,fn) in enumerate(assets):
    rml.append(f'  <ImageAsset file="img/{fn}" name="{n}" id="1:{k+1}" />')
rml.append('</Rive>')
open(os.path.dirname(os.path.abspath(__file__))+"\\..\\scene.rml","w",encoding="utf-8").write("\n".join(rml)+"\n")
print(len(assets),"assets")

