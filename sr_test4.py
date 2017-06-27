import numpy as np
import matplotlib.pyplot as plt
from sr_export_PES import *

def normalize_pts(pts, minSize, maxSize):
    pts = np.array(pts)

    new_pts = []
    i = 0
    best_size = (maxSize + minSize)/2.0

    while i < pts.shape[0]-1:
        point1 = pts[i]
        point2 = pts[i + 1]

        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        vector = [(x2 - x1),(y2 - y1)]
        #catch divide by zero...
        if dist < 0.001:
            dist = 0.001
        unit_vector = [vector[0] / dist, vector[1] / dist]
        print point1, point2, dist
        #create intermediary points if dist > maxsize
        if dist >= maxSize:
            count = int(dist/best_size) +1
            # not needed because j=0 ----- new_pts.append(point1)
            for j in range(count):
                temp_pt = [x1 + (best_size * j * unit_vector[0]), y1 + (j* best_size * unit_vector[1])]
                print 'new pt"', temp_pt
                new_pts.append(temp_pt)
            new_pts.append(point2)
        #skip over really close points
        elif dist <= minSize :
            new_pts.append(point1)
            print 'point skipped', point2
            nextPoint = 2
            while dist < minSize:
                try:
                    point2 = pts[i + nextPoint]
                except:
                    break
                x2, y2 = pts[i + nextPoint]
                dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                vector = [(x2 - x1), (y2 - y1)]
                if dist < 0.001:
                    dist = 0.001
                unit_vector = [vector[0] / dist, vector[1] / dist]
                dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                print 'trying', point2, dist
                nextPoint = nextPoint + 1
            # create intermediary points if dist > maxsize
            if dist >= maxSize:
                count = int(dist / best_size) +1
                # not needed because j=0 ----- new_pts.append(point1)
                for j in range(count):
                    temp_pt = [x1 + (best_size * j * unit_vector[0]), y1 + (j * best_size * unit_vector[1])]
                    print 'new pt"', temp_pt
                    new_pts.append(temp_pt)
                new_pts.append(point2)
            else:
                print 'using', point2, dist
                new_pts.append(point2)
            i = i + nextPoint - 1
        #otherwise points are good
        else:
            new_pts.append(point1)
            new_pts.append(point2)
        i = i+2

    return np.array(new_pts)


thread_offset = 12.7
r1_ink = [63.500000000253991, -170.54285593401548]
r2_ink = [63.500000000253991, -221.34285593421868]
r1_emb = [0.0, 25.399999999999999]
r2_emb = [0.0, -25.399999999999999]
pts = [(50.800000000203198, -182.69999866739747), (50.800000000203198, -182.69999866739747), (50.800000000203198, -182.69999866739747), (88.90000000035559, -195.39999866744824), (88.90000000035559, -195.39999866744824), (88.90000000035559, -195.39999866744824), (50.800000000203198, -208.09999866749905), (50.800000000203198, -208.09999866749905), (50.800000000203198, -208.09999866749905)]
new_pts = [(-12.699999999999992, 13.242857266666626), (-12.699999999999992, 13.242857266666626), (-10.328291754873707, 12.452287851624531), (-7.9565835097474222, 11.661718436582438), (-5.5848752646211377, 10.871149021540344), (-3.2131670194948523, 10.080579606498251), (-0.84145877436856686, 9.2900101914561564), (1.5302494707577168, 8.4994407764140618), (3.9019577158840022, 7.708871361371969), (6.2736659610102876, 6.9183019463298754), (8.645374206136573, 6.1277325312877817), (11.017082451262858, 5.3371631162456881), (13.388790696389144, 4.5465937012035944), (15.760498941515426, 3.7560242861614999), (18.132207186641711, 2.9654548711194071), (20.503915431767997, 2.1748854560773125), (22.875623676894282, 1.3843160410352198), (25.247331922020567, 0.59374662599312522), (25.399999999999999, 0.5428572666666468), (25.399999999999999, 0.5428572666666468), (23.028291754873713, -0.2477121483754483), (20.656583509747431, -1.0382815634175433), (18.284875264621146, -1.8288509784596387), (15.913167019494862, -2.6194203935017337), (13.541458774368579, -3.4099898085438292), (11.169750529242293, -4.2005592235859242), (8.7980422841160113, -4.9911286386280196), (6.4263340389897259, -5.7816980536701141), (4.0546257938634405, -6.5722674687122096), (1.6829175487371586, -7.362836883754305), (-0.68879069638912682, -8.1534062987963996), (-3.0604989415154122, -8.9439757138384941), (-5.4322071866416941, -9.7345451288805886), (-7.803915431767976, -10.525114543922685), (-10.175623676894261, -11.31568395896478), (-12.547331922020547, -12.106253374006874), (-12.699999999999992, -12.157142733333359), (-12.699999999999992, -12.157142733333359), (-12.699999999999992, -12.157142733333359)]
# saved to: c:\pesfolder\inkscape.pes




r1_ink = np.array(r1_ink)
r2_ink = np.array(r2_ink)
r1_emb = np.array(r1_emb)
r2_emb = np.array(r2_emb)
pts = np.array(pts)
new_pts = np.array(new_pts)

#plot the origianl points
x,y = pts.T
plt.plot(x, y, 'r-')
#plot the inkscape registration points
x,y = r1_ink
plt.plot(x, y, 'ro')
x,y = r2_ink
plt.plot(x, y, 'r^')

#plot the embroidery registration points
x,y =np.array(r1_emb)
plt.plot(x, y, 'mo')
x,y = np.array(r2_emb)
plt.plot(x, y, 'm^')

x,y = new_pts.T
plt.plot(x, y, '.' )
print new_pts.shape

# new_pts2 = normalize_pts(new_pts, 10,14)
#
#
# x,y = new_pts2.T
# plt.plot(x, y, 'r.' )
# print new_pts2.shape

plt.show()

result = make_pes('c:\\pesfolder\\', 'test4.pes', new_pts, True)







