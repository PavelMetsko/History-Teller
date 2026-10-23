import sys,os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import compose as c
from PIL import Image
pairs=[('massena','regulus',None),('lucullus','wellington',0.55),('pitt','trajan',0.7),('edward4','menshikov',None),('beatrice','flora',0.45),('michelangelo','antony',0.4),('talleyrand','hadrian',None),('roosevelt','galba',0.3),('tiberius','conde',None)]
ims=[c.compose(*p) for p in pairs]
W,H=256,384; out=Image.new('RGBA',(W*3,H*3),(225,220,210,255))
for i,im in enumerate(ims): out.alpha_composite(im.resize((W,H),Image.LANCZOS),((i%3)*W,(i//3)*H))
out.save(sys.argv[1])
