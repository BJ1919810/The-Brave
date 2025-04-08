import pygame,sys,os,random,time
from pygame.locals import *
import easygui as eg
pygame.init()

eg.msgbox("1.本游戏由老BJ着力开发,本人技术欠佳,游戏不好还请见谅\n2.本游戏无止境,无剧情,只有史莱姆一种怪;疗伤物品会随机刷新,是灵芝,但是吗...(doge)\n3.空格为切换徒手与持剑,j为普通攻击,k为特殊攻击\n4.如果听到'叮'的一声,则说明特殊技能的冷却已结束\n5.score可以作为自己辉煌的历史(只是历史),并不会保存\n6.游戏愉快~","Van前须知")
name=eg.enterbox("请输入玩家名字...","君の名は")
if name=="":
    name="听说你不喜欢取名字?"
try:
    len(name)
except TypeError:
    name="听说你不喜欢取名字?"
    
now=os.getcwd()+'/'
canvas = pygame.display.set_mode((900, 600))
bg=pygame.image.load(now+'spirites/bg.png')
pygame.mixer.music.load(now+"sounds/いつもの風景から始まる物語 (从老风景开始的故事) - 神前暁 (こうさき さとる).ogg")
pygame.mixer.music.play(-1)

def isActionTime(lastTime, interval):
    if lastTime == 0:
        return True
    currentTime = time.time()
    return currentTime - lastTime >= interval

class Charactor(object):
    def __init__(self,x,y,v,name,pitv,ai,life,damage,normalwidth):#v[vx,vy]
        self.x=x
        self.y=y
        self.v=v
        self.width=0
        self.height=0
        self.name=name
        self.imgs={"stay":'',"walk":'',"hurt":'',"attack":''}
        self.isimgok=False
        self.id=0
        self.activity="stay"
        self.turn='right'
        self.attackid=ai
        self.isl=False
        self.isr=False
        self.isu=False
        self.isd=False
        self.fulllife=life
        self.life=life
        self.damage=damage
        self.lifelength=5/3*normalwidth
        self.plastTime=0
        self.pitv=pitv
        self.mlastTime=0
    def imgload(self):
        for i in self.imgs:
            img=[]
            nums=len(os.listdir(now+'spirites/'+self.name+"/"+i))
            for j in range(nums):
                img.append(pygame.image.load(now+'spirites/'+self.name+"/"+i+"/"+str(j)+'.png').convert_alpha())
            self.imgs[i]=img
    def move(self):
        if isActionTime(self.mlastTime, 0.1):
            if self.isr==True and self.x+self.width/2<900:
                self.x+=self.v[0]
                self.turn='right'
            if self.isl==True and self.x-self.width/2>0:
                self.turn='left'
                self.x-=self.v[0]
            if self.isu==True and self.y-self.height>349:
                self.y-=self.v[1]
            if self.isd==True and self.y<600:
                self.y+=self.v[1]
            self.mlastTime=time.time() 
    def paint(self):
        if isActionTime(self.plastTime,self.pitv):
            self.id+=1
            if self.id==len(self.imgs[self.activity]):
                self.id=0
                if self.activity!='walk'+self.weap or self.activity!='stay'+self.weap:
                    self.activity='stay'+self.weap
            size=self.imgs[self.activity][self.id].get_rect()
            self.width=size[2]
            self.height=size[3]
            self.plastTime=time.time()
        willpaint=self.imgs[self.activity][self.id]
        if self.turn=='left':
            willpaint=pygame.transform.flip(willpaint,True,False)
        canvas.blit(willpaint,(self.x-self.width/2,self.y-self.height))
        gcolor=int(255*(self.life/self.fulllife))
        blood=str(self.life)+"/"+str(self.fulllife)
        pygame.draw.rect(canvas,(0,0,0),(self.x-5*self.width/6,self.y-self.height-7,self.lifelength,5),1)
        if gcolor<0:
            gcolor=1
        pygame.draw.line(canvas,(255-gcolor,gcolor,0),(self.x-5*self.width/6+1,self.y-self.height-5),(self.x-5*self.width/6+(self.life/self.fulllife)*(self.lifelength-2),self.y-self.height-5),3)
        renderText(blood,(self.x-5*self.width/6+(self.lifelength-len(blood)*6)/2,self.y-self.height-16),(255-gcolor,gcolor,0),16)
        '''
           * ...
            .   .
           ...#...  /# is the position/* is the painting position/
        '''
    def hit(self,c):
        return c.x-c.width/2>self.x-self.width/2-c.width and c.x-c.width/2<self.x+self.width/2 and \
               c.y-c.height>self.y-self.height-c.height and c.y-c.height<self.y-self.height+self.height
    def direction(self,c):
        if c.x<=self.x:
            return "left"
        else:
            return "right"
    def houyao(self):
        return (self.activity !="stay" or self.activity!="walk") and self.id==len(self.imgs[self.activity])
class Braver(Charactor):
    def __init__(self,x,y,score):
        Charactor.__init__(self,x,y,[7,6],"The Brave",0.1,[4,5,6,7],100,4,24)
        self.isweap=False
        self.weap=''
        self.imgs={"stay":'',"stay_weap":'',"walk":'',"walk_weap":'',"hurt":'',"attack":'',"attack_weap":''}
        self.score=0
        self.weap_qi_recovery=0
        self.isweap_qi_recovery=True
    def recover_weap_qi(self):
        if self.isweap_qi_recovery==False and isActionTime(self.weap_qi_recovery,2):
            pygame.mixer.Sound(now+"sounds/weap_qi_recovery.ogg").play()
            self.isweap_qi_recovery=True

class Weap_qi():
    def __init__(self,x,y,v,turn,life,img):
        self.x=x
        self.y=y
        self.v=v
        self.turn=turn
        self.id=0
        self.width=16
        self.height=40
        self.imgs=img
        self.life=life
        self.mlastTime=0
        self.plastTime=0
    def checkImg(self):
        if self.imgs=='weap_qi':
            self.imgs=[pygame.image.load(now+'spirites/The Brave/weap_qi.png').convert_alpha()]
        else:
            self.imgs=[]
            for i in range(4):
                self.imgs.append(pygame.image.load(now+'spirites/The Brave/qi/'+str(i)+'.png').convert_alpha())
    def hit(self,c):
        return c.x-c.width/2>self.x-self.width/2-c.width and c.x-c.width/2<self.x+self.width/2 and \
               c.y-c.height>self.y-self.height-c.height and c.y-c.height<self.y-self.height+self.height
    def move(self):
        if isActionTime(self.mlastTime, 0.1):
            if self.turn=='right':
                self.x+=self.v
            else:
                self.x-=self.v
    def paint(self):
        if isActionTime(self.plastTime,0.1):
            self.id+=1
            if self.id==len(self.imgs):
                self.id=0
            size=self.imgs[self.id].get_rect()
            self.width=size[2]
            self.height=size[3]
            self.plastTime=time.time()
        willpaint=self.imgs[self.id]
        if self.turn=='left':
            willpaint=pygame.transform.flip(willpaint,True,False)
        canvas.blit(willpaint,(self.x-self.width/2,self.y-self.height))

class Medicine():
    def __init__(self):
        self.width=25
        self.height=25
        self.x=random.randint(int(self.width/2),int(900-self.width/2))
        self.y=random.randint(350,600)
        self.img=pygame.image.load(now+'spirites/medicine.png').convert_alpha()
    def paint(self):
        canvas.blit(self.img,(self.x-self.width/2,self.y-self.height))
        
class Slime(Charactor):
    def __init__(self):
        Charactor.__init__(self,0,0,[2,1.3],"slime",0.2,[2],24,3,30)
        self.x=random.randint(int(self.width/2),int(900-self.width/2))
        self.y=random.randint(350,600)
        self.score=5
        self.weap=''
    def zhui(self,c):
        self.isl,self.isr,self.isd,self.isu=False,False,False,False
        if c.x>self.x:
            self.isr=True
        elif c.x<self.x:
            self.isl=True
        if c.y>self.y:
            self.isd=True
        elif c.y<self.y:
            self.isu=True
            
class Damagetext():
    def __init__(self,sign,damage,pst):
        self.damage=damage
        self.pst=pst
        self.sign=sign
        self.dlt=time.time()
        self.color= (255,0,0) if self.sign=='-' else (0,255,0)
    def paint(self):
        renderText(self.sign+str(self.damage),self.pst,self.color,28)
    def isdelete(self):
        if isActionTime(self.dlt,0.7):
            return True
        return False

def componentEnter():
    if isActionTime(Factor.demonlastTime,random.randint(5,10)):
        Factor.demons.append(Slime())
        Factor.demonlastTime=time.time()
    if isActionTime(Factor.medicinelastTime,random.randint(10,20)):
        Factor.medicines.append(Medicine())
        Factor.medicinelastTime=time.time()
def componentPaint():
    canvas.blit(bg,(0,0))
    for i in Factor.demons:
        if i.isimgok==False:
            i.imgload()
            i.isimgok=True
        i.paint()
    for i in Factor.medicines:
        i.paint()
    for i in Factor.weap_qis:
        i.paint()
    Factor.braver.paint()
    renderText(name,(Factor.braver.x-5*Factor.braver.width/6+(Factor.braver.lifelength-len(name)*13)/2,Factor.braver.y-Factor.braver.height-28),(255,255,255),20)
    renderText('Score:'+str(Factor.braver.score),(0,0),(255,255,255),40)
    for i in Factor.nums:
        i.paint()
def componentStep():
    if Factor.braver.isweap==True:
        Factor.braver.weap="_weap"
    else:
        Factor.braver.weap=""
    if Factor.braver.id in Factor.braver.attackid:
        if Factor.braver.turn=='right':
            Factor.braver.x+=1.5
        elif Factor.braver.turn=='left':
            Factor.braver.x-=1.5
    Factor.braver.recover_weap_qi()
    if Factor.braver.isl==False and Factor.braver.isr==False and Factor.braver.isu==False and Factor.braver.isd==False:
        if Factor.braver.houyao():
            Factor.braver.id=0
            Factor.braver.activity="stay"+Factor.braver.weap
    else:
        Factor.braver.activity="walk"+Factor.braver.weap
    if Factor.braver.activity=="walk"+Factor.braver.weap:
        Factor.braver.move()
    for i in Factor.demons:
        i.zhui(Factor.braver)
        if i.isl==False and i.isr==False and i.isu==False and i.isd==False:
            i.id=0
            i.activity="stay"
        else:
            if not i.houyao():
                i.activity="walk"
        if i.activity=="walk":
            i.move()
    for i in Factor.weap_qis:
        i.move()
def componentDelete():
    for i in Factor.demons:
        if i.life<=0:
            pygame.mixer.Sound(now+"sounds/"+i.name+"_death.ogg").play()
            Factor.demons.remove(i)
            Factor.braver.score+=i.score
    for i in Factor.weap_qis:
        if i.life<=0 or outofbound(i):
            Factor.weap_qis.remove(i)
    for i in Factor.nums:
        if i.isdelete()==True:
            Factor.nums.remove(i)
def outofbound(c):
    return c.x-c.width/2>900 or c.x+c.width/2<0 or c.y-c.height>600 or c.y<0
def checkHit():
    for demon in Factor.demons:
        for m in Factor.medicines:
            if demon.hit(m):
                if demon.fulllife>demon.life>demon.fulllife-10:
                    cha=demon.fulllife-demon.life
                    demon.life=demon.fulllife
                    Factor.nums.append(Damagetext('+',cha,(demon.x+random.randint(0,8),demon.y-demon.height-random.randint(20,28)))) 
                    pygame.mixer.Sound(now+"sounds/medicine.ogg").play()
                    Factor.medicines.remove(m)
                elif demon.life<=demon.fulllife-10:
                    demon.life+=10
                    Factor.nums.append(Damagetext('+',10,(demon.x+random.randint(0,8),demon.y-demon.height-random.randint(20,28)))) 
                    pygame.mixer.Sound(now+"sounds/medicine.ogg").play()
                    Factor.medicines.remove(m)
            elif Factor.braver.hit(m):
                if Factor.braver.fulllife>Factor.braver.life>Factor.braver.fulllife-10:
                    cha=Factor.braver.fulllife-Factor.braver.life
                    Factor.braver.life=Factor.braver.fulllife
                    Factor.nums.append(Damagetext('+',cha,(Factor.braver.x+random.randint(0,8),Factor.braver.y-Factor.braver.height-random.randint(20,28)))) 
                    pygame.mixer.Sound(now+"sounds/medicine.ogg").play()
                    Factor.medicines.remove(m)
                elif Factor.braver.life<=Factor.braver.fulllife-10:
                    Factor.braver.life+=10
                    Factor.nums.append(Damagetext('+',10,(Factor.braver.x+random.randint(0,8),Factor.braver.y-Factor.braver.height-random.randint(20,28)))) 
                    pygame.mixer.Sound(now+"sounds/medicine.ogg").play()
                    Factor.medicines.remove(m)
        if Factor.braver.hit(demon):
            demon.activity="attack"
            if Factor.braver.activity=="attack"+Factor.braver.weap and (Factor.braver.id in Factor.braver.attackid) and Factor.braver.turn == Factor.braver.direction(demon):
                pygame.mixer.Sound(now+"sounds/"+demon.name+"_hurt.ogg").play()
                jlife=int(Factor.braver.damage+random.randint(-int(Factor.braver.damage/3),int(Factor.braver.damage/3)))
                demon.life-=jlife
                Factor.nums.append(Damagetext('-',jlife,(demon.x+random.randint(0,8),demon.y-demon.height-random.randint(20,28))))
                demon.activity='hurt'
                demon.id=0
                if Factor.braver.turn=="right":
                    demon.x+=8
                else:
                    demon.x-=8
            if demon.activity=="attack" and (demon.id in demon.attackid) and demon.turn == demon.direction(Factor.braver):
                jlife=int(demon.damage+random.randint(-int(demon.damage/3),int(demon.damage/3)))
                Factor.braver.life-=jlife
                Factor.nums.append(Damagetext('-',jlife,(Factor.braver.x+random.randint(0,8),Factor.braver.y-Factor.braver.height-random.randint(20,28))))
                Factor.braver.id=0
                if Factor.braver.activity!='attack'+Factor.braver.weap:
                    Factor.braver.activity='hurt'
                if demon.turn=="right":
                    Factor.braver.x+=8   
                else:
                    Factor.braver.x-=8
        for qi in Factor.weap_qis:
            if qi.hit(demon):
                pygame.mixer.Sound(now+"sounds/"+demon.name+"_hurt.ogg").play()
                jlife=int(Factor.braver.damage+random.randint(-int(Factor.braver.damage/3),int(Factor.braver.damage/3)))
                demon.life-=jlife
                Factor.nums.append(Damagetext('-',jlife,(demon.x+random.randint(0,8),demon.y-demon.height-random.randint(20,28))))
                qi.life-=1
                demon.activity='hurt'
                demon.id=0
                if qi.turn=="right":
                    demon.x+=8
                else:
                    demon.x-=8
def renderText(text,position,color,big):
    my_font = pygame.font.SysFont("SimHei", big-6)
    newText = my_font.render(text,True,color)
    canvas.blit(newText,position)
            
def handleEvent():
    for event in pygame.event.get():
        if event.type==pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_j:
            if Factor.braver.activity!='hurt':
                Factor.braver.activity='attack'+Factor.braver.weap
        if event.type == KEYDOWN and event.key == K_k:
            if Factor.braver.activity not in ['hurt','attack'+Factor.braver.weap]:
                if Factor.braver.isweap_qi_recovery==True:
                    Factor.braver.isweap_qi_recovery=False
                    Factor.braver.weap_qi_recovery=time.time()
                    if Factor.braver.turn=="left":
                        xx=Factor.braver.x-Factor.braver.width/2
                    else:
                        xx=Factor.braver.x+Factor.braver.width/2
                    if Factor.braver.isweap==True:
                        pygame.mixer.Sound(now+"sounds/weap_qi.ogg").play()
                        wq=Weap_qi(xx,Factor.braver.y,5,Factor.braver.turn,2,'weap_qi')
                    else:
                        pygame.mixer.Sound(now+"sounds/qi.ogg").play()
                        wq=Weap_qi(xx,Factor.braver.y,2,Factor.braver.turn,5,'qi')
                    wq.checkImg()
                    Factor.weap_qis.append(wq)
        if event.type == KEYDOWN and event.key == K_w:
            Factor.braver.isu=True
            Factor.braver.id=0
        elif event.type == KEYUP and event.key == K_w:
            Factor.braver.isu=False
            Factor.braver.id=0
        if event.type == KEYDOWN and event.key == K_s:
            Factor.braver.isd=True
            Factor.braver.id=0
        elif event.type == KEYUP and event.key == K_s:
            Factor.braver.isd=False
            Factor.braver.id=0
        if event.type == KEYDOWN and event.key == K_a:
            Factor.braver.isl=True
            Factor.braver.turn='left'
            Factor.braver.id=0
        elif event.type == KEYUP and event.key == K_a:
            Factor.braver.isl=False
            Factor.braver.id=0
        if event.type == KEYDOWN and event.key == K_d:
            Factor.braver.isr=True
            Factor.braver.turn='right'
            Factor.braver.id=0
        elif event.type == KEYUP and event.key == K_d:
            Factor.braver.isr=False
            Factor.braver.id=0
        if event.type == KEYDOWN and event.key == K_SPACE:
            Factor.braver.isweap=not Factor.braver.isweap
            Factor.braver.activity="stay"+Factor.braver.weap
            Factor.braver.id=0
            if Factor.braver.isweap==True:
                Factor.braver.damage=6
                Factor.braver.attackid=[4,5,6,8,9,10]
            else:
                Factor.braver.damage=4
                Factor.braver.attackid=[4,5,6,7]
class Factor():
    demonlastTime=0
    medicinelastTime=0
    demons=[]
    medicines=[]
    weap_qis=[]
    nums=[]
    braver=Braver(679,349,0)
    braver.imgload()
while Factor.braver.life>0:
    handleEvent()
    componentEnter()
    componentStep()
    componentPaint()
    checkHit()
    componentDelete()
    pygame.display.update()
    pygame.time.delay(15)
pygame.mixer.music.stop()
dead=pygame.image.load(now+'spirites/dead.png').convert_alpha()
pygame.mixer.music.load(now+'sounds/Sad Romance (Violin ver_) - 韩国群星 (Korea Various Artists).ogg')
pygame.mixer.music.play(-1)
while True:
    canvas.blit(dead,(0,0))
    renderText("You Dead!",(170,530),(255,0,0),80)
    for event in pygame.event.get():
        if event.type==pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            pass
    pygame.display.update()
    pygame.time.delay(15)
