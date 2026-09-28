//#GLOBALS
integer MyAllCnt=266
integer MyUiRoot=0
boolean MyUiBuilt=false
boolean MyUiShown=false
boolean MyChatOpen=false
real MyChatStamp=0.
timer MyClock
timer MyUiTick
integer MyUiTickN=0
trigger MyKeyTrig
trigger MyChatCmdTrig
trigger MyChatAnyTrig
trigger MyEvalTrig
integer MyEvalIdx=0
integer MyEvalPid=0
integer MyProgSerial=0
integer array MyStkUt
integer array MyStkN
integer array MyPct
integer array MyState
boolean array MyResLack
integer MyUiChip=0
boolean MyFltReady=false
boolean MyFltSort=true
integer MyUiPage=0
integer MyUiSel=-1
integer array MyList
integer MyListN=0
integer array MyBkCnt
integer array MyChipBg
integer array MyChipTxt
integer array MyChipLine
integer MyFltReadyBg=0
integer MyFltReadyTxt=0
integer MyFltSortBg=0
integer MyFltSortTxt=0
integer MyPageTxt=0
integer MyCountTxt=0
integer array MyCardBg
integer array MyCardHi
integer array MyCardIcon
integer array MyCardName
integer array MyCardStat
integer array MyCardOwn
integer array MyCardBar
integer array MyCardIdx
integer MyDtBody=0
integer MyDtEmpty=0
integer MyDtIcon=0
integer MyDtName=0
integer MyDtGrade=0
integer MyDtOwn=0
integer MyDtBar=0
integer MyDtPct=0
integer MyDtStat=0
integer array MyRowBg
integer array MyRowIcon
integer array MyRowName
integer array MyRowCnt
integer array MyRowUt
integer MyCmbBg=0
integer MyCmbTxt=0
integer MyCmbFill=0
integer MyBackBg=0
integer array MyHist
integer MyHistN=0
//#END
//#FUNCS
function MyPx takes real myP returns real
return myP/Kx*Ky
endfunction
function MyPy takes real myP returns real
return myP/Kz*K0
endfunction
function MyAt takes integer myF,integer myPar,real myX,real myY returns nothing
call DzFrameSetPoint(myF,0,myPar,0,MyPx(myX),-MyPy(myY))
endfunction
function MySz takes integer myF,real myW,real myH returns nothing
call DzFrameSetSize(myF,MyPx(myW),MyPy(myH))
endfunction
function MyTxt takes integer myPar,real myX,real myY,real myW,real myH,real myFs,integer myAl returns integer
local integer myF=BD6(myPar,"MyAcUI txt")
call DzFrameSetFont(myF,"Fonts\\esamanruMedium.ttf",myFs*K3,0)
call MyAt(myF,myPar,myX,myY)
if myW>0. then
call MySz(myF,myW,myH)
endif
if myAl>0 then
call DzFrameSetTextAlignment(myF,myAl)
endif
call DzFrameSetEnable(myF,false)
return myF
endfunction
function MyBox takes integer myPar,string myTpl,real myX,real myY,real myW,real myH returns integer
local integer myF=BDu(myPar,"MyAcUI box",myTpl)
call MyAt(myF,myPar,myX,myY)
call MySz(myF,myW,myH)
return myF
endfunction
function MyTex takes integer myPar,string myTex,real myX,real myY,real myW,real myH returns integer
local integer myF=BDt(myPar,"MyAcUI tex")
if myTex!="" then
call DzFrameSetTexture(myF,myTex,0)
endif
call MyAt(myF,myPar,myX,myY)
call MySz(myF,myW,myH)
return myF
endfunction
function MyBtn takes integer myPar,real myX,real myY,real myW,real myH,code myC returns integer
local integer myF=BDv(myPar,"MyAcUI btn")
call MyAt(myF,myPar,myX,myY)
call MySz(myF,myW,myH)
call DzFrameSetScriptByCode(myF,1,myC,false)
return myF
endfunction
function MyGradeName takes integer myG returns string
if myG==0 then
return "안흔함"
elseif myG==1 then
return "희귀"
elseif myG==2 then
return "특별"
elseif myG==3 then
return "전설"
elseif myG==4 then
return "히든"
elseif myG==5 then
return "초월"
elseif myG==6 then
return "불멸"
elseif myG==7 then
return "영원"
elseif myG==8 then
return "신비"
elseif myG==9 then
return "제한"
elseif myG==10 then
return "왜곡"
elseif myG==11 then
return "변화"
elseif myG==12 then
return "특수"
elseif myG==13 then
return "세라핌"
elseif myG==14 then
return "랜덤전용"
endif
return "미분류"
endfunction
function MyGradeColor takes integer myG returns string
if myG==0 then
return "|cff9553ec"
elseif myG==1 then
return "|cffff00ff"
elseif myG==2 then
return "|cff0080ff"
elseif myG==3 then
return "|cffff3030"
elseif myG==4 then
return "|cff6f78ff"
elseif myG==5 then
return "|cff00fa9a"
elseif myG==6 then
return "|cffe0474f"
elseif myG==7 then
return "|cffffd700"
elseif myG==8 then
return "|cff51ddf5"
elseif myG==9 then
return "|cffdf9d30"
elseif myG==10 then
return "|cff9fefd1"
elseif myG==11 then
return "|cffff7039"
elseif myG==12 then
return "|cffb70fff"
elseif myG==13 then
return "|cff00ced1"
elseif myG==14 then
return "|cff51ddf5"
endif
return "|cffc0c0c0"
endfunction
function MyLeaf takes integer myUt,integer myD returns integer
local integer myK
local integer myN
local integer myS=0
local integer myT=0
if HaveSavedInteger(MyUiMap,20,myUt) then
return LoadInteger(MyUiMap,20,myUt)
endif
if myD<10 and HaveSavedInteger(MyKeyMap,myUt,0) then
set myK=LoadInteger(MyKeyMap,myUt,0)
set myN=LoadInteger(Wb,myK,We)
loop
exitwhen myS>=myN
if LoadInteger(Wq,myK,myS)==$554E4954 then
set myT=myT+LoadInteger(Ws,myK,myS)*MyLeaf(LoadInteger(Wr,myK,myS),myD+1)
endif
set myS=myS+1
endloop
endif
if myT<=0 then
set myT=1
endif
call SaveInteger(MyUiMap,20,myUt,myT)
return myT
endfunction
function MyRemain takes integer myUt returns integer
if LoadInteger(MyUiMap,31,myUt)!=MyProgSerial then
call SaveInteger(MyUiMap,31,myUt,MyProgSerial)
call SaveInteger(MyUiMap,30,myUt,MyOwned(MyEvalPid,myUt))
endif
return LoadInteger(MyUiMap,30,myUt)
endfunction
function MyEval takes integer myI returns nothing
local integer myK=MyAllKey[myI]
local integer myN=LoadInteger(Wb,myK,We)
local integer myS=0
local integer myC
local integer myM
local integer myQ
local integer myTop=0
local integer myTot=0
local integer myPr=0
local integer myOwn
local integer myUse
local integer mySk
local integer mySn
local integer mySs
local boolean myDirect=true
local integer myPid=MyEvalPid
set MyProgSerial=MyProgSerial+1
set MyResLack[myI]=false
loop
exitwhen myS>=myN
set myC=LoadInteger(Wq,myK,myS)
set myM=LoadInteger(Wr,myK,myS)
set myQ=LoadInteger(Ws,myK,myS)
if myC==$554E4954 then
set myTot=myTot+myQ*MyLeaf(myM,0)
if MyOwned(myPid,myM)<myQ then
set myDirect=false
endif
set MyStkUt[myTop]=myM
set MyStkN[myTop]=myQ
set myTop=myTop+1
elseif myC==$474F4C44 then
if GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_GOLD)<myQ then
set MyResLack[myI]=true
endif
elseif myC==$574F4F44 then
if GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_LUMBER)<myQ then
set MyResLack[myI]=true
endif
elseif myC==$49464354 then
if GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_LUMBER)<myQ+hW[myPid] then
set MyResLack[myI]=true
endif
endif
set myS=myS+1
endloop
loop
exitwhen myTop<=0
set myTop=myTop-1
set myM=MyStkUt[myTop]
set myQ=MyStkN[myTop]
set myOwn=MyRemain(myM)
if myOwn>myQ then
set myUse=myQ
else
set myUse=myOwn
endif
call SaveInteger(MyUiMap,30,myM,myOwn-myUse)
set myPr=myPr+myUse*MyLeaf(myM,0)
set myQ=myQ-myUse
if myQ>0 and HaveSavedInteger(MyKeyMap,myM,0) then
set mySk=LoadInteger(MyKeyMap,myM,0)
set mySn=LoadInteger(Wb,mySk,We)
set mySs=0
loop
exitwhen mySs>=mySn or myTop>=240
if LoadInteger(Wq,mySk,mySs)==$554E4954 then
set MyStkUt[myTop]=LoadInteger(Wr,mySk,mySs)
set MyStkN[myTop]=LoadInteger(Ws,mySk,mySs)*myQ
set myTop=myTop+1
endif
set mySs=mySs+1
endloop
endif
endloop
if myTot<=0 then
set MyPct[myI]=-1
set MyState[myI]=4
return
endif
if myPr>=myTot then
set MyPct[myI]=100
else
set MyPct[myI]=myPr*100/myTot
endif
if MyPct[myI]>=100 then
if myDirect then
set MyState[myI]=2
else
set MyState[myI]=3
endif
else
set MyState[myI]=1
endif
endfunction
function MyEvalCond takes nothing returns boolean
call MyEval(MyEvalIdx)
return false
endfunction
function MyEvalRun takes integer myI returns nothing
set MyEvalIdx=myI
call TriggerEvaluate(MyEvalTrig)
endfunction
function MyStatText takes integer myI returns string
if MyState[myI]==4 then
return "|cffc9a0ff특수 조합|r"
elseif MyState[myI]==2 then
if MyResLack[myI] then
return "|cffffa040자원 부족|r"
endif
return "|cff55ff55조합 가능|r"
elseif MyState[myI]==3 then
return "|cffffd24a하위조합 가능|r"
endif
return "|cffbfbfbf"+I2S(MyPct[myI])+"%|r"
endfunction
function MyBarTex takes integer myI returns string
if MyState[myI]==2 then
return "ReplaceableTextures\\TeamColor\\TeamColor06.blp"
elseif MyState[myI]==3 then
return "ReplaceableTextures\\TeamColor\\TeamColor04.blp"
endif
return "ReplaceableTextures\\TeamColor\\TeamColor09.blp"
endfunction
function MySetBar takes integer myBar,real myW,real myH,integer myPct returns nothing
if myPct<=0 then
call DzFrameShow(myBar,false)
return
endif
if myPct>100 then
set myPct=100
endif
call DzFrameShow(myBar,true)
call MySz(myBar,myW*I2R(myPct)/100.,myH)
endfunction
function MyUtIcon takes integer myUt returns string
local integer myX=LoadInteger(MyUiMap,6,myUt)
if myX>0 then
return MyAllIcon[myX-1]
endif
if HaveSavedString(MyUiMap,5,myUt) then
return LoadStr(MyUiMap,5,myUt)
endif
return "ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp"
endfunction
function MyUtName takes integer myUt returns string
local integer myX=LoadInteger(MyUiMap,6,myUt)
if myX>0 then
return MyGradeColor(MyAllGrade[myX-1])+MyAllShort[myX-1]+"|r"
endif
return GetObjectName(myUt)
endfunction
function MyCntText takes integer myHave,integer myNeed,boolean myCraft returns string
if myHave>=myNeed then
return "|cff55ff55"+I2S(myHave)+" / "+I2S(myNeed)+"|r"
elseif myCraft then
return "|cffffd24a"+I2S(myHave)+" / "+I2S(myNeed)+"  (조합)|r"
endif
return "|cffff6060"+I2S(myHave)+" / "+I2S(myNeed)+"|r"
endfunction
function MyBucket takes integer myI returns integer
if MyState[myI]==2 then
return 103
elseif MyState[myI]==3 then
return 102
elseif MyState[myI]==4 then
return 0
endif
return MyPct[myI]+1
endfunction
function MyUiBuildList takes nothing returns nothing
local integer myI=0
local integer myB=0
local integer myJ
set MyListN=0
loop
exitwhen myB>103
set MyBkCnt[myB]=0
set myB=myB+1
endloop
loop
exitwhen myI>=MyAllCnt
if MyUiChip==0 or MyAllGrade[myI]==MyUiChip-1 then
call MyEvalRun(myI)
if (not MyFltReady) or MyState[myI]==2 or MyState[myI]==3 then
if MyFltSort then
set myB=MyBucket(myI)
call SaveInteger(MyUiMap,40,myB*300+MyBkCnt[myB],myI)
set MyBkCnt[myB]=MyBkCnt[myB]+1
else
set MyList[MyListN]=myI
set MyListN=MyListN+1
endif
endif
endif
set myI=myI+1
endloop
if MyFltSort then
set myB=103
loop
exitwhen myB<0
set myJ=0
loop
exitwhen myJ>=MyBkCnt[myB]
set MyList[MyListN]=LoadInteger(MyUiMap,40,myB*300+myJ)
set MyListN=MyListN+1
set myJ=myJ+1
endloop
set myB=myB-1
endloop
endif
endfunction
function MyUiRenderChips takes nothing returns nothing
local integer myC=0
local string myT
loop
exitwhen myC>=17
if myC==0 then
set myT="전체"
else
set myT=MyGradeName(myC-1)+" |cff777777"+I2S(MyGrpCnt[myC-1])+"|r"
endif
if myC==MyUiChip then
call DzFrameSetText(MyChipTxt[myC],"|cffffd700"+myT+"|r")
call DzFrameSetAlpha(MyChipBg[myC],255)
call DzFrameShow(MyChipLine[myC],true)
else
call DzFrameSetText(MyChipTxt[myC],"|cffb0b0b0"+myT+"|r")
call DzFrameSetAlpha(MyChipBg[myC],110)
call DzFrameShow(MyChipLine[myC],false)
endif
set myC=myC+1
endloop
if MyFltReady then
call DzFrameSetText(MyFltReadyTxt,"|cff55ff55조합 가능만  ON|r")
call DzFrameSetAlpha(MyFltReadyBg,255)
else
call DzFrameSetText(MyFltReadyTxt,"|cff999999조합 가능만  OFF|r")
call DzFrameSetAlpha(MyFltReadyBg,130)
endif
if MyFltSort then
call DzFrameSetText(MyFltSortTxt,"|cff55ff55진행률순 정렬  ON|r")
call DzFrameSetAlpha(MyFltSortBg,255)
else
call DzFrameSetText(MyFltSortTxt,"|cff999999진행률순 정렬  OFF|r")
call DzFrameSetAlpha(MyFltSortBg,130)
endif
endfunction
function MyUiRenderCards takes nothing returns nothing
local integer myS=0
local integer myP
local integer myI
local integer myOwn
local integer myPages=(MyListN+19)/20
if myPages<1 then
set myPages=1
endif
if MyUiPage>=myPages then
set MyUiPage=myPages-1
endif
if MyUiPage<0 then
set MyUiPage=0
endif
loop
exitwhen myS>=20
set myP=MyUiPage*20+myS
if myP<MyListN then
set myI=MyList[myP]
set MyCardIdx[myS]=myI
call DzFrameShow(MyCardBg[myS],true)
call DzFrameSetTexture(MyCardIcon[myS],MyAllIcon[myI],0)
call DzFrameSetText(MyCardName[myS],MyGradeColor(MyAllGrade[myI])+MyAllShort[myI]+"|r")
call DzFrameSetText(MyCardStat[myS],MyStatText(myI))
set myOwn=MyOwned(MyEvalPid,MyAllType[myI])
if myOwn>0 then
call DzFrameSetText(MyCardOwn[myS],"|cff9fd3ff보유 "+I2S(myOwn)+"기|r")
else
call DzFrameSetText(MyCardOwn[myS],"|cff666666미보유|r")
endif
if MyState[myI]==4 then
call MySetBar(MyCardBar[myS],120.,8.,0)
else
call DzFrameSetTexture(MyCardBar[myS],MyBarTex(myI),0)
call MySetBar(MyCardBar[myS],120.,8.,MyPct[myI])
endif
call DzFrameShow(MyCardHi[myS],myI==MyUiSel)
else
set MyCardIdx[myS]=-1
call DzFrameShow(MyCardBg[myS],false)
endif
set myS=myS+1
endloop
call DzFrameSetText(MyPageTxt,"|cffffffff"+I2S(MyUiPage+1)+" / "+I2S(myPages)+"|r")
call DzFrameSetText(MyCountTxt,"|cff8a8a8a"+I2S(MyListN)+"개 유닛|r")
endfunction
function MyRowSet takes integer myR,string myIcon,string myName,string myCnt,integer myUt returns nothing
call DzFrameShow(MyRowBg[myR],true)
call DzFrameSetTexture(MyRowIcon[myR],myIcon,0)
call DzFrameSetText(MyRowName[myR],myName)
call DzFrameSetText(MyRowCnt[myR],myCnt)
set MyRowUt[myR]=myUt
if LoadInteger(MyUiMap,6,myUt)>0 then
call DzFrameSetAlpha(MyRowBg[myR],255)
else
call DzFrameSetAlpha(MyRowBg[myR],170)
endif
endfunction
function MyUiRenderDetail takes nothing returns nothing
local integer myI=MyUiSel
local integer myK
local integer myN
local integer myS=0
local integer myR=0
local integer myC
local integer myM
local integer myQ
local integer myPid=MyEvalPid
local string mySc="ReplaceableTextures\\CommandButtons\\BTNSnazzyScroll.blp"
local string myLb="ReplaceableTextures\\CommandButtons\\BTNBundleOfLumber.blp"
if myI<0 then
call DzFrameShow(MyDtBody,false)
call DzFrameShow(MyDtEmpty,true)
return
endif
call DzFrameShow(MyDtEmpty,false)
call DzFrameShow(MyDtBody,true)
call MyEvalRun(myI)
call DzFrameSetTexture(MyDtIcon,MyAllIcon[myI],0)
call DzFrameSetText(MyDtName,MyGradeColor(MyAllGrade[myI])+MyAllShort[myI]+"|r")
call DzFrameSetText(MyDtGrade,MyGradeColor(MyAllGrade[myI])+MyGradeName(MyAllGrade[myI])+"|r |cff888888등급|r")
call DzFrameSetText(MyDtOwn,"|cff888888보유|r |cffffffff"+I2S(MyOwned(myPid,MyAllType[myI]))+"기|r")
if MyState[myI]==4 then
call MySetBar(MyDtBar,420.,18.,0)
call DzFrameSetText(MyDtPct,"|cffc9a0ff특수 조합|r")
else
call DzFrameSetTexture(MyDtBar,MyBarTex(myI),0)
call MySetBar(MyDtBar,420.,18.,MyPct[myI])
call DzFrameSetText(MyDtPct,"|cffffffff진행률 "+I2S(MyPct[myI])+"%|r")
endif
if MyState[myI]==2 then
if MyResLack[myI] then
call DzFrameSetText(MyDtStat,"|cffffa040재료는 모두 있지만 골드/목재가 부족합니다.|r")
else
call DzFrameSetText(MyDtStat,"|cff55ff55지금 바로 조합할 수 있습니다.|r")
endif
elseif MyState[myI]==3 then
call DzFrameSetText(MyDtStat,"|cffffd24a부족한 재료를 하위 조합으로 채울 수 있습니다. 자동조합을 누르면 순서대로 진행합니다.|r")
elseif MyState[myI]==4 then
call DzFrameSetText(MyDtStat,"|cffaaaaaa유닛 재료가 없는 특수 조합입니다. 아래 조건을 확인하세요.|r")
else
call DzFrameSetText(MyDtStat,"|cffaaaaaa재료가 더 필요합니다. 노란색 재료는 하위 조합으로 만들 수 있고, 클릭하면 조합법을 볼 수 있습니다.|r")
endif
set myK=MyAllKey[myI]
set myN=LoadInteger(Wb,myK,We)
loop
exitwhen myS>=myN or myR>=10
set myC=LoadInteger(Wq,myK,myS)
set myM=LoadInteger(Wr,myK,myS)
set myQ=LoadInteger(Ws,myK,myS)
if myC==$554E4954 then
call MyRowSet(myR,MyUtIcon(myM),MyUtName(myM),MyCntText(MyOwned(myPid,myM),myQ,HaveSavedInteger(MyKeyMap,myM,0)),myM)
set myR=myR+1
elseif myC==$474F4C44 then
call MyRowSet(myR,"ReplaceableTextures\\CommandButtons\\BTNChestOfGold.blp","|cffffd700골드|r",MyCntText(GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_GOLD),myQ,false),0)
set myR=myR+1
elseif myC==$574F4F44 then
call MyRowSet(myR,myLb,"|cff7ad823목재|r",MyCntText(GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_LUMBER),myQ,false),0)
set myR=myR+1
elseif myC==$49464354 then
call MyRowSet(myR,myLb,"|cff7ad823목재|r |cff888888(증가분 포함)|r",MyCntText(GetPlayerState(Player(myPid),PLAYER_STATE_RESOURCE_LUMBER),myQ+hW[myPid],false),0)
set myR=myR+1
elseif myC==$534B5054 then
call MyRowSet(myR,mySc,"|cff1e90ff특성포인트|r","|cffffffff"+I2S(myQ)+"|r",0)
set myR=myR+1
elseif myC==$4954454D then
call MyRowSet(myR,mySc,"아이템 : "+GetObjectName(myM),"",0)
set myR=myR+1
elseif myC==$5049434B then
call MyRowSet(myR,mySc,"|cffff4040랜덤전용 유닛 1기|r","",0)
set myR=myR+1
elseif myC==$43484354 then
call MyRowSet(myR,mySc,"|cffff0080변화가능 횟수|r","|cffffffff"+I2S(myQ)+"|r",0)
set myR=myR+1
elseif myC==$524D4158 then
call MyRowSet(myR,mySc,"|cffff4040"+I2S(myQ)+"라운드|r까지만 조합 가능","",0)
set myR=myR+1
elseif myC==$53504543 or myC==$5244554E then
call MyRowSet(myR,mySc,GetAbilityEffectById(myM,EFFECT_TYPE_CASTER,0),"",0)
set myR=myR+1
elseif myC==$4752454E then
call MyRowSet(myR,mySc,"|cffe32bb4그린블러드|r (신모드 이상에서 입수)","",0)
set myR=myR+1
endif
set myS=myS+1
endloop
loop
exitwhen myR>=10
call DzFrameShow(MyRowBg[myR],false)
set MyRowUt[myR]=0
set myR=myR+1
endloop
if MyState[myI]==2 or MyState[myI]==3 then
call DzFrameSetAlpha(MyCmbBg,255)
call DzFrameShow(MyCmbFill,true)
call DzFrameSetText(MyCmbTxt,"|cffffffff자동조합 실행|r")
else
call DzFrameSetAlpha(MyCmbBg,160)
call DzFrameShow(MyCmbFill,false)
call DzFrameSetText(MyCmbTxt,"|cff8a8a8a자동조합 실행|r")
endif
call DzFrameShow(MyBackBg,MyHistN>0)
endfunction
function MyUiRefresh takes boolean myFull returns nothing
local integer myS=0
if not MyUiBuilt then
return
endif
set MyEvalPid=GetPlayerId(GetLocalPlayer())
if myFull then
call MyUiBuildList()
else
loop
exitwhen myS>=20
if MyCardIdx[myS]>=0 then
call MyEvalRun(MyCardIdx[myS])
endif
set myS=myS+1
endloop
endif
call MyUiRenderChips()
call MyUiRenderCards()
call MyUiRenderDetail()
endfunction
function MyUiSetShown takes boolean myB returns nothing
if not MyUiBuilt then
return
endif
set MyUiShown=myB
call DzFrameShow(MyUiRoot,myB)
if myB then
call MyUiRefresh(true)
endif
endfunction
function MyUiSelect takes integer myI,boolean myKeepHist returns nothing
if myI<0 then
return
endif
if myKeepHist then
if MyUiSel>=0 and MyHistN<16 then
set MyHist[MyHistN]=MyUiSel
set MyHistN=MyHistN+1
endif
else
set MyHistN=0
endif
set MyUiSel=myI
set MyEvalPid=GetPlayerId(GetLocalPlayer())
call MyUiRenderCards()
call MyUiRenderDetail()
endfunction
function MyUiChipClick takes nothing returns nothing
set MyUiChip=LoadInteger(MyUiMap,1,DzGetTriggerUIEventFrame())
set MyUiPage=0
call MyUiRefresh(true)
endfunction
function MyUiFltReadyClick takes nothing returns nothing
set MyFltReady=not MyFltReady
set MyUiPage=0
call MyUiRefresh(true)
endfunction
function MyUiFltSortClick takes nothing returns nothing
set MyFltSort=not MyFltSort
set MyUiPage=0
call MyUiRefresh(true)
endfunction
function MyUiCardClick takes nothing returns nothing
local integer myS=LoadInteger(MyUiMap,0,DzGetTriggerUIEventFrame())
call MyUiSelect(MyCardIdx[myS],false)
endfunction
function MyUiCardEnter takes nothing returns nothing
call DzFrameSetAlpha(MyCardBg[LoadInteger(MyUiMap,0,DzGetTriggerUIEventFrame())],255)
endfunction
function MyUiCardLeave takes nothing returns nothing
call DzFrameSetAlpha(MyCardBg[LoadInteger(MyUiMap,0,DzGetTriggerUIEventFrame())],225)
endfunction
function MyUiRowClick takes nothing returns nothing
local integer myR=LoadInteger(MyUiMap,2,DzGetTriggerUIEventFrame())
local integer myX=LoadInteger(MyUiMap,6,MyRowUt[myR])
if MyRowUt[myR]!=0 and myX>0 then
call MyUiSelect(myX-1,true)
endif
endfunction
function MyUiBackClick takes nothing returns nothing
if MyHistN>0 then
set MyHistN=MyHistN-1
set MyUiSel=MyHist[MyHistN]
set MyEvalPid=GetPlayerId(GetLocalPlayer())
call MyUiRenderCards()
call MyUiRenderDetail()
endif
endfunction
function MyUiPrevClick takes nothing returns nothing
if MyUiPage>0 then
set MyUiPage=MyUiPage-1
set MyEvalPid=GetPlayerId(GetLocalPlayer())
call MyUiRenderCards()
endif
endfunction
function MyUiNextClick takes nothing returns nothing
set MyUiPage=MyUiPage+1
set MyEvalPid=GetPlayerId(GetLocalPlayer())
call MyUiRenderCards()
endfunction
function MyUiComboClick takes nothing returns nothing
if MyUiSel>=0 then
call DzSyncData("MYAC",I2S(MyAllType[MyUiSel]))
endif
endfunction
function MyUiCloseClick takes nothing returns nothing
call MyUiSetShown(false)
endfunction
function MyUiKeyI takes nothing returns nothing
if DzGetTriggerKeyPlayer()!=GetLocalPlayer() then
return
endif
if MyChatOpen and TimerGetElapsed(MyClock)-MyChatStamp<30. then
return
endif
set MyChatOpen=false
call MyUiSetShown(not MyUiShown)
endfunction
function MyUiKeyEnter takes nothing returns nothing
if DzGetTriggerKeyPlayer()!=GetLocalPlayer() then
return
endif
if MyChatOpen then
set MyChatOpen=false
else
set MyChatOpen=true
set MyChatStamp=TimerGetElapsed(MyClock)
endif
endfunction
function MyUiKeyEsc takes nothing returns nothing
if DzGetTriggerKeyPlayer()!=GetLocalPlayer() then
return
endif
if MyChatOpen then
set MyChatOpen=false
return
endif
if MyUiShown then
call MyUiSetShown(false)
endif
endfunction
function MyUiChatAny takes nothing returns nothing
if GetTriggerPlayer()==GetLocalPlayer() then
set MyChatOpen=false
endif
endfunction
function MyUiChatCmd takes nothing returns nothing
if GetTriggerPlayer()==GetLocalPlayer() then
set MyChatOpen=false
call MyUiSetShown(not MyUiShown)
endif
endfunction
function MyUiTickFn takes nothing returns nothing
if not MyUiShown then
return
endif
set MyUiTickN=MyUiTickN+1
if MyUiTickN>=4 then
set MyUiTickN=0
call MyUiRefresh(true)
else
call MyUiRefresh(false)
endif
endfunction
function MyUiBuild takes nothing returns nothing
local integer myG
local integer myF
local integer myT
local integer myB
local integer myC=0
local integer myS=0
local integer myR=0
local real myX
local real myY
local string myYel="ReplaceableTextures\\TeamColor\\TeamColor04.blp"
if MyUiBuilt then
return
endif
call DzLoadToc("war3mapImported\\ORDRTemplates.toc")
set myG=DzGetGameUI()
set MyUiRoot=BDu(myG,"MyAcUI root","ORDRTooltipBack")
call DzFrameSetAbsolutePoint(MyUiRoot,4,.4,.328)
call MySz(MyUiRoot,1400.,620.)
set myF=MyBox(MyUiRoot,"ORDRDashBoardPanel",4.,4.,1392.,612.)
set myF=MyBox(MyUiRoot,"ORDRDashBoardPanel",4.,4.,1392.,612.)
set myT=MyTxt(MyUiRoot,24.,14.,0.,0.,20.,0)
call DzFrameSetText(myT,"|cffffd700조합 도우미|r")
set myT=MyTxt(MyUiRoot,180.,20.,0.,0.,11.,0)
call DzFrameSetText(myT,"|cff8a8a8a[I] 열기/닫기   [Esc] 닫기   재료 클릭 : 하위 조합법   |r|cff55ff55초록|r|cff8a8a8a 바로 조합   |r|cffffd24a노랑|r|cff8a8a8a 하위 조합으로 가능|r")
set myF=MyBox(MyUiRoot,"ORDRTooltipBack",1304.,10.,76.,30.)
set myT=MyTxt(myF,0.,0.,76.,30.,12.,18)
call DzFrameSetText(myT,"|cffff7070닫기|r")
set myB=MyBtn(myF,0.,0.,76.,30.,function MyUiCloseClick)
set myF=MyTex(MyUiRoot,"ReplaceableTextures\\TeamColor\\TeamColor08.blp",24.,50.,1352.,2.)
call DzFrameSetAlpha(myF,90)
loop
exitwhen myC>=17
if myC<9 then
set myX=24.+I2R(myC)*98.
set myY=60.
else
set myX=24.+I2R(myC-9)*98.
set myY=92.
endif
set MyChipBg[myC]=MyBox(MyUiRoot,"ORDRDashBoardPanelBlack",myX,myY,92.,26.)
set MyChipTxt[myC]=MyTxt(MyChipBg[myC],0.,0.,92.,26.,11.,18)
set MyChipLine[myC]=MyTex(MyChipBg[myC],myYel,4.,23.,84.,3.)
set myB=MyBtn(MyChipBg[myC],0.,0.,92.,26.,function MyUiChipClick)
call SaveInteger(MyUiMap,1,myB,myC)
set myC=myC+1
endloop
set MyFltReadyBg=MyBox(MyUiRoot,"ORDRTooltipBack",24.,126.,170.,28.)
set MyFltReadyTxt=MyTxt(MyFltReadyBg,0.,0.,170.,28.,11.,18)
set myB=MyBtn(MyFltReadyBg,0.,0.,170.,28.,function MyUiFltReadyClick)
set MyFltSortBg=MyBox(MyUiRoot,"ORDRTooltipBack",202.,126.,170.,28.)
set MyFltSortTxt=MyTxt(MyFltSortBg,0.,0.,170.,28.,11.,18)
set myB=MyBtn(MyFltSortBg,0.,0.,170.,28.,function MyUiFltSortClick)
set MyCountTxt=MyTxt(MyUiRoot,388.,126.,200.,28.,12.,17)
set myF=MyBox(MyUiRoot,"ORDRTooltipBack",722.,126.,44.,28.)
set myT=MyTxt(myF,0.,0.,44.,28.,13.,18)
call DzFrameSetText(myT,"|cffffffff<|r")
set myB=MyBtn(myF,0.,0.,44.,28.,function MyUiPrevClick)
set MyPageTxt=MyTxt(MyUiRoot,768.,126.,88.,28.,13.,18)
set myF=MyBox(MyUiRoot,"ORDRTooltipBack",858.,126.,44.,28.)
set myT=MyTxt(myF,0.,0.,44.,28.,13.,18)
call DzFrameSetText(myT,"|cffffffff>|r")
set myB=MyBtn(myF,0.,0.,44.,28.,function MyUiNextClick)
loop
exitwhen myS>=20
set myX=24.+I2R(ModuloInteger(myS,4))*220.
set myY=164.+I2R(myS/4)*88.
set myF=MyBox(MyUiRoot,"ORDRTooltipBack",myX,myY,212.,82.)
call DzFrameSetAlpha(myF,225)
set MyCardBg[myS]=myF
set MyCardHi[myS]=BDs(myF,"MyAcUI hi")
call MyAt(MyCardHi[myS],myF,0.,0.)
call MySz(MyCardHi[myS],212.,82.)
set myT=MyTex(MyCardHi[myS],myYel,0.,0.,212.,3.)
set myT=MyTex(MyCardHi[myS],myYel,0.,79.,212.,3.)
set myT=MyTex(MyCardHi[myS],myYel,0.,0.,3.,82.)
set myT=MyTex(MyCardHi[myS],myYel,209.,0.,3.,82.)
set MyCardIcon[myS]=MyTex(myF,"",10.,11.,60.,60.)
set MyCardName[myS]=MyTxt(myF,80.,8.,126.,18.,13.,0)
set MyCardOwn[myS]=MyTxt(myF,80.,28.,126.,15.,11.,0)
set MyCardStat[myS]=MyTxt(myF,80.,44.,126.,15.,11.,0)
set myT=MyTex(myF,"ReplaceableTextures\\TeamColor\\TeamColor08.blp",80.,64.,120.,8.)
call DzFrameSetAlpha(myT,70)
set MyCardBar[myS]=MyTex(myF,"",80.,64.,120.,8.)
set myB=MyBtn(myF,0.,0.,212.,82.,function MyUiCardClick)
call DzFrameSetScriptByCode(myB,2,function MyUiCardEnter,false)
call DzFrameSetScriptByCode(myB,3,function MyUiCardLeave,false)
call SaveInteger(MyUiMap,0,myB,myS)
set MyCardIdx[myS]=-1
set myS=myS+1
endloop
set myF=MyBox(MyUiRoot,"ORDRTooltipBack",920.,60.,456.,548.)
set myT=MyBox(myF,"ORDRDashBoardPanel",3.,3.,450.,542.)
set MyDtEmpty=MyTxt(myF,0.,260.,456.,30.,14.,18)
call DzFrameSetText(MyDtEmpty,"|cffaaaaaa왼쪽 목록에서 유닛을 선택하세요.|r")
set MyDtBody=BDs(myF,"MyAcUI body")
call MyAt(MyDtBody,myF,0.,0.)
call MySz(MyDtBody,456.,548.)
set MyDtIcon=MyTex(MyDtBody,"",18.,16.,72.,72.)
set MyDtName=MyTxt(MyDtBody,104.,18.,336.,24.,17.,0)
set MyDtGrade=MyTxt(MyDtBody,104.,46.,336.,16.,12.,0)
set MyDtOwn=MyTxt(MyDtBody,104.,66.,336.,16.,12.,0)
set myT=MyTex(MyDtBody,"ReplaceableTextures\\TeamColor\\TeamColor08.blp",18.,100.,420.,18.)
call DzFrameSetAlpha(myT,70)
set MyDtBar=MyTex(MyDtBody,"",18.,100.,420.,18.)
set MyDtPct=MyTxt(MyDtBody,18.,100.,420.,18.,12.,18)
set MyDtStat=MyTxt(MyDtBody,18.,124.,420.,30.,11.,0)
set myT=MyTxt(MyDtBody,18.,162.,200.,18.,13.,0)
call DzFrameSetText(myT,"|cffffd700필요 조건|r")
set MyBackBg=MyBox(MyDtBody,"ORDRTooltipBack",342.,156.,96.,26.)
set myT=MyTxt(MyBackBg,0.,0.,96.,26.,12.,18)
call DzFrameSetText(myT,"|cffffffff< 뒤로|r")
set myB=MyBtn(MyBackBg,0.,0.,96.,26.,function MyUiBackClick)
loop
exitwhen myR>=10
set myF=MyBox(MyDtBody,"ORDRDashBoardPanelBlack",18.,188.+I2R(myR)*31.,420.,29.)
set MyRowBg[myR]=myF
set MyRowIcon[myR]=MyTex(myF,"",3.,2.,25.,25.)
set MyRowName[myR]=MyTxt(myF,36.,0.,260.,29.,12.,17)
set MyRowCnt[myR]=MyTxt(myF,290.,0.,122.,29.,12.,20)
set myB=MyBtn(myF,0.,0.,420.,29.,function MyUiRowClick)
call SaveInteger(MyUiMap,2,myB,myR)
set myR=myR+1
endloop
set MyCmbBg=MyBox(MyDtBody,"ORDRTooltipBack",18.,496.,420.,40.)
set MyCmbFill=MyTex(MyCmbBg,"ReplaceableTextures\\TeamColor\\TeamColor06.blp",4.,4.,412.,32.)
call DzFrameSetAlpha(MyCmbFill,110)
set MyCmbTxt=MyTxt(MyCmbBg,0.,0.,420.,40.,15.,18)
set myB=MyBtn(MyCmbBg,0.,0.,420.,40.,function MyUiComboClick)
call DzFrameShow(MyUiRoot,false)
set MyUiBuilt=true
endfunction
function MyUiBoot takes nothing returns nothing
call MyUiBuild()
call DzTriggerRegisterKeyEventByCode(MyKeyTrig,73,bj_KEYEVENTTYPE_RELEASE,false,function MyUiKeyI)
call DzTriggerRegisterKeyEventByCode(MyKeyTrig,13,bj_KEYEVENTTYPE_RELEASE,false,function MyUiKeyEnter)
call DzTriggerRegisterKeyEventByCode(MyKeyTrig,27,bj_KEYEVENTTYPE_RELEASE,false,function MyUiKeyEsc)
call DestroyTimer(GetExpiredTimer())
endfunction
function MyAcSync takes nothing returns nothing
local integer myUt=S2I(DzGetTriggerSyncData())
set MyCurPlayer=DzGetTriggerSyncPlayer()
if MyAcNode(myUt,0) then
call DisplayTimedTextToPlayer(MyCurPlayer,0,0,6,"|cff00ff00[자동조합]|r 조합을 완료했습니다.")
else
call DisplayTimedTextToPlayer(MyCurPlayer,0,0,6,"|cffff0000[자동조합]|r 조합할 수 없습니다. (재료 또는 조건 부족)")
endif
if GetLocalPlayer()==MyCurPlayer and MyUiShown then
call MyUiRefresh(true)
endif
endfunction
//#END
//#INIT
function MyInitUi takes nothing returns nothing
local integer myI=0
loop
exitwhen myI>=MyAllCnt
call SaveInteger(MyUiMap,6,MyAllType[myI],myI+1)
set myI=myI+1
endloop
//#EXTRA_ICONS
set MyEvalTrig=CreateTrigger()
call TriggerAddCondition(MyEvalTrig,Condition(function MyEvalCond))
set MyClock=CreateTimer()
call TimerStart(MyClock,1000000.,false,null)
set MyUiTick=CreateTimer()
call TimerStart(MyUiTick,1.,true,function MyUiTickFn)
call BeE("MYAC",function MyAcSync)
set MyKeyTrig=CreateTrigger()
set MyChatCmdTrig=CreateTrigger()
set MyChatAnyTrig=CreateTrigger()
set myI=0
loop
exitwhen myI>=LG
call TriggerRegisterPlayerChatEvent(MyChatCmdTrig,Player(myI),"-자동조합",true)
call TriggerRegisterPlayerChatEvent(MyChatAnyTrig,Player(myI),"",false)
set myI=myI+1
endloop
call TriggerAddAction(MyChatCmdTrig,function MyUiChatCmd)
call TriggerAddAction(MyChatAnyTrig,function MyUiChatAny)
call TimerStart(CreateTimer(),.5,false,function MyUiBoot)
endfunction
//#END
