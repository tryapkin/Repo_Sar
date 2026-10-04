S=[]
def ln(x1,y1,x2,y2,w=2): S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="{w}"/>')
def dot(x,y): S.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#111"/>')
def tx(x,y,t,sz=14,a="start",b=False,col="#111"):
    w=' font-weight="700"' if b else ''
    S.append(f'<text x="{x}" y="{y}" font-size="{sz}" text-anchor="{a}" fill="{col}"{w}>{t}</text>')
RAIL,GND=60,330
def channel(ox,n,title,led0):
    tx(ox+130,40,title,14,b=True)
    # Cin
    ln(ox+70,RAIL,ox+70,170); ln(ox+58,170,ox+82,170); ln(ox+58,180,ox+82,180); ln(ox+70,180,ox+70,GND)
    dot(ox+70,RAIL); dot(ox+70,GND); tx(ox+80,178,"Cin",12)
    # VIN
    ln(ox+140,RAIL,ox+140,150); dot(ox+140,RAIL); dot(ox+140,105)
    # Rs
    ln(ox+140,105,ox+170,105); S.append(f'<rect x="{ox+170}" y="97" width="40" height="16" fill="none" stroke="#111" stroke-width="2"/>')
    ln(ox+210,105,ox+240,105); ln(ox+240,105,ox+240,150); dot(ox+240,105); tx(ox+190,90,"Rs 0,15",12,"middle")
    # IC
    S.append(f'<rect x="{ox+120}" y="150" width="140" height="100" fill="#f3f6fb" stroke="#111" stroke-width="2"/>')
    tx(ox+190,205,"PT4115",15,"middle",True); tx(ox+190,223,"U",12,"middle")
    tx(ox+144,168,"VIN",11); tx(ox+222,168,"CSN",11); tx(ox+256,219,"SW",11,"end"); tx(ox+190,244,"GND",11,"middle"); tx(ox+124,204,"DIM",11)
    ln(ox+100,200,ox+120,200); S.append(f'<circle cx="{ox+97}" cy="200" r="3" fill="#fff" stroke="#111" stroke-width="1.5"/>')
    ln(ox+190,250,ox+190,GND); dot(ox+190,GND)
    # LED string
    ln(ox+240,105,ox+340,105); ln(ox+340,105,ox+340,215)
    for i in range(n):
        y=120+30*i
        S.append(f'<polygon points="{ox+330},{y} {ox+350},{y} {ox+340},{y+18}" fill="#fff" stroke="#111" stroke-width="2"/>')
        ln(ox+330,y+18,ox+350,y+18)
        # white bg to hide wire inside triangle
        S.append(f'<line x1="{ox+360}" y1="{y+2}" x2="{ox+372}" y2="{y-6}" stroke="#d98a00" stroke-width="2"/>')
        tx(ox+358,y+22,f"LED{led0+i}",12)
    # L
    ln(ox+340,215,ox+324,215)
    S.append(f'<path d="M {ox+324},215 a6,6 0 0 0 -12,0 a6,6 0 0 0 -12,0 a6,6 0 0 0 -12,0" fill="none" stroke="#111" stroke-width="2"/>')
    ln(ox+288,215,ox+260,215); dot(ox+270,215); tx(ox+312,242,"L",13,"middle")
    # D
    ln(ox+270,215,ox+270,285); ln(ox+270,285,ox+420,285); ln(ox+420,285,ox+420,200)
    S.append(f'<polygon points="{ox+410},200 {ox+430},200 {ox+420},182" fill="#fff" stroke="#111" stroke-width="2"/>')
    ln(ox+410,182,ox+430,182); ln(ox+420,182,ox+420,RAIL); dot(ox+420,RAIL); tx(ox+434,195,"D (Шоттки)",12)
channel(0,3,"Канал A: LED1–LED3 (3 посл., ≈10 В)",1)
channel(540,2,"Канал B: LED4–LED5 (2 посл., ≈6,6 В)",4)
ln(30,RAIL,960,RAIL); ln(30,GND,740,GND)
for (x,y,t) in [(30,RAIL,"+12 В"),(30,GND,"GND")]:
    S.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="#111" stroke-width="2"/>'); tx(x-6,y+5,t,14,"end",True)
tx(30,22,"Светильник: 5× OSRAM OSLON, питание 12 В DC",19,b=True)
notes=["Почему так: 5 LED по ≈3,3 В в одну цепочку = 16,5 В > 12 В; резистор на каждый LED греет ≈30 Вт. Две цепочки (3+2) с драйвером тока — КПД ≈90%.",
"Ток: Rs = 0,1 В / I → Rs = 0,15 Ом ⇒ ≈667 мА (цель 700 мА). LED ≈2,3 Вт каждый, всего ≈11,5 Вт; от 12 В потребление ≈1,1 А.",
"Внимание: цепочка A ≈10 В от 12 В — запас мал. Питание держать 12–13,8 В и проверить на макете; запасной вариант — каналы 2+2+1.",
"Перечень: LED1–5 OSRAM OSLON белый (≈3,2–3,4 В @700 мА); U ×2 PT4115 (до 1,2 А); Rs ×2 0,15 Ом 1% 1206; L ×2 33–47 мкГн (Isat ≥ 1,5 А);",
"D ×2 SS24/SS34 (2–3 А, 40 В); Cin ×2 10 мкФ 25–50 В X7R + 220 мкФ 25 В на входе; DIM — NC (100%) или ШИМ. Плата — алюминиевая (MCPCB) на радиатор.",
"Значения подобраны по памяти: тип OSLON, Vf, параметры PT4115 и номиналы L/D сверьте с даташитами и расчётом."]
for i,t in enumerate(notes): tx(30,385+24*i,t,13)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="540" viewBox="0 0 1160 540" font-family="Liberation Sans, Arial, sans-serif"><rect width="1160" height="540" fill="#fff"/><g transform="translate(60,0)">'+"".join(S)+'</g></svg>'
open('lamp_schematic.svg','w',encoding='utf-8').write(svg)
