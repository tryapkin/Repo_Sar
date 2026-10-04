K=8
def board(ox,oy,on):
    X=lambda v: ox+K*v; Y=lambda v: oy+K*v
    g=[]
    A=g.append
    A(f'<rect x="{ox}" y="{oy}" width="{130*K}" height="{50*K}" rx="26" fill="#f4f4ef" stroke="#cfd2cc" stroke-width="3" filter="url(#sh)"/>')
    # traces (copper under mask)
    def path(d,w=9,c="#e9d6ae"): A(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    P=lambda pts:'M '+' L '.join(f'{X(a)},{Y(b)}' for a,b in pts)
    path(P([(27,14),(55,14)])); path(P([(27,14),(24,14),(24,31)])); path(P([(55,14),(60,14),(60,24),(46,24),(46,35)]))
    path(P([(67,14),(80,14)])); path(P([(67,14),(74,14),(74,31)])); path(P([(80,14),(88,14),(88,24),(96,24),(96,35)]))
    path(P([(9,22),(16,22),(16,30),(110,30)]),11,"#e3c98e"); path(P([(9,28),(14,28),(14,48),(112,48)]),11,"#e3c98e")
    # holes
    for hx,hy in [(4.5,4.5),(125.5,4.5),(4.5,45.5),(125.5,45.5)]:
        A(f'<circle cx="{X(hx)}" cy="{Y(hy)}" r="{2.4*K}" fill="#d8dbe0" stroke="#b9bec6" stroke-width="2"/><circle cx="{X(hx)}" cy="{Y(hy)}" r="{1.6*K}" fill="#1d2127"/>')
    # glow under LEDs
    xs=[28,41,54,67,80]
    if on:
        for x in xs: A(f'<circle cx="{X(x)}" cy="{Y(14)}" r="{13*K}" fill="url(#glow)"/>')
    # LEDs
    for i,x in enumerate(xs):
        A(f'<rect x="{X(x-2.4)}" y="{Y(14-1.3)}" width="{4.8*K}" height="{2.6*K}" rx="3" fill="#d4af37"/>')
        A(f'<rect x="{X(x-1.5)}" y="{Y(14-1.5)}" width="{3*K}" height="{3*K}" rx="4" fill="#fbfbf6" stroke="#b9b9b0" stroke-width="1.5"/>')
        A(f'<rect x="{X(x-0.85)}" y="{Y(14-0.85)}" width="{1.7*K}" height="{1.7*K}" rx="2" fill="{"#fffbe0" if on else "#e9b92a"}" stroke="#c99a1a" stroke-width="1"/>')
        if on: A(f'<circle cx="{X(x)}" cy="{Y(14)}" r="{2.2*K}" fill="#fff6c0" filter="url(#bl)"/>')
        A(f'<text x="{X(x)}" y="{Y(20)}" font-size="17" text-anchor="middle" fill="#222">LED{i+1}</text>')
    # terminal
    A(f'<rect x="{X(3)}" y="{Y(18.5)}" width="{9*K}" height="{13*K}" rx="4" fill="#2f6fd6" stroke="#1d4a99" stroke-width="2"/>')
    for cy in (22,28): A(f'<circle cx="{X(8.2)}" cy="{Y(cy)}" r="{2.1*K}" fill="#d7dbe1" stroke="#8d949e" stroke-width="2"/><line x1="{X(7.0)}" y1="{Y(cy)}" x2="{X(9.4)}" y2="{Y(cy)}" stroke="#555" stroke-width="3"/>')
    A(f'<rect x="{X(3)}" y="{Y(19.5)}" width="{2*K}" height="{11*K}" fill="#1d4a99"/>')
    A(f'<text x="{X(7.5)}" y="{Y(17.2)}" font-size="17" text-anchor="middle" fill="#222">+12V</text><text x="{X(7.5)}" y="{Y(34.2)}" font-size="17" text-anchor="middle" fill="#222">GND</text>')
    def res(cx,cy,vert=False,body="#1c1c1c",cap="#c9ccd1",w=3.2,h=1.6):
        if vert: w,h=h,w
        A(f'<rect x="{X(cx-w/2)}" y="{Y(cy-h/2)}" width="{w*K}" height="{h*K}" rx="2" fill="{body}"/>')
        if not vert:
            A(f'<rect x="{X(cx-w/2)}" y="{Y(cy-h/2)}" width="{.7*K}" height="{h*K}" fill="{cap}"/><rect x="{X(cx+w/2-.7)}" y="{Y(cy-h/2)}" width="{.7*K}" height="{h*K}" fill="{cap}"/>')
        else:
            A(f'<rect x="{X(cx-w/2)}" y="{Y(cy-h/2)}" width="{w*K}" height="{.7*K}" fill="{cap}"/><rect x="{X(cx-w/2)}" y="{Y(cy+h/2-.7)}" width="{w*K}" height="{.7*K}" fill="{cap}"/>')
    def drv(dx):
        res(dx+20,39,True,"#c9a66b")      # Cin
        res(dx+24,33)                      # Rs
        # U PT4115 SOT-89-5
        for k in (-1.5,0,1.5): A(f'<rect x="{X(dx+31+k-.3)}" y="{Y(39.9)}" width="{.6*K}" height="{1.4*K}" fill="#c9ccd1"/>')
        for k in (-.75,.75): A(f'<rect x="{X(dx+31+k-.3)}" y="{Y(35.7)}" width="{.6*K}" height="{1.3*K}" fill="#c9ccd1"/>')
        A(f'<rect x="{X(dx+31-2.25)}" y="{Y(36.5)}" width="{4.5*K}" height="{3.6*K}" rx="3" fill="#2b2e33"/>')
        A(f'<text x="{X(dx+31)}" y="{Y(38.7)}" font-size="9" text-anchor="middle" fill="#9aa0aa">PT4115</text>')
        # L
        A(f'<rect x="{X(dx+43)}" y="{Y(35)}" width="{6*K}" height="{6*K}" rx="5" fill="#3d4047" stroke="#2a2c31" stroke-width="2"/>')
        A(f'<rect x="{X(dx+43)}" y="{Y(35)}" width="{1*K}" height="{6*K}" fill="#c9ccd1"/><rect x="{X(dx+48)}" y="{Y(35)}" width="{1*K}" height="{6*K}" fill="#c9ccd1"/>')
        A(f'<text x="{X(dx+46)}" y="{Y(38.4)}" font-size="11" text-anchor="middle" fill="#aab0ba">47µ</text>')
        # D (SMA)
        A(f'<rect x="{X(dx+53.9)}" y="{Y(38.7)}" width="{4.3*K}" height="{2.6*K}" rx="2" fill="#16171a"/><rect x="{X(dx+56.8)}" y="{Y(38.7)}" width="{.7*K}" height="{2.6*K}" fill="#d9dce1"/>')
        A(f'<rect x="{X(dx+52.9)}" y="{Y(39.1)}" width="{1.2*K}" height="{1.8*K}" fill="#c9ccd1"/><rect x="{X(dx+58.1)}" y="{Y(39.1)}" width="{1.2*K}" height="{1.8*K}" fill="#c9ccd1"/>')
    drv(0); drv(50)
    A(f'<text x="{X(31)}" y="{Y(44.5)}" font-size="15" text-anchor="middle" fill="#222">U1</text><text x="{X(81)}" y="{Y(44.5)}" font-size="15" text-anchor="middle" fill="#222">U2</text>')
    A(f'<text x="{X(65)}" y="{Y(6)}" font-size="24" text-anchor="middle" fill="#222" font-weight="700">LAMP 5×OSLON 12V</text>')
    A(f'<text x="{X(112)}" y="{Y(13)}" font-size="30" text-anchor="middle" fill="#222" font-weight="700">700 mA</text>')
    A(f'<text x="{X(112)}" y="{Y(19)}" font-size="14" text-anchor="middle" fill="#222">REV A · MCPCB</text>')
    return "".join(g)
W,H=1180,1060
defs='''<defs>
<filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" flood-opacity="0.55"/></filter>
<filter id="bl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
<radialGradient id="glow"><stop offset="0" stop-color="#ffd24a" stop-opacity="0.85"/><stop offset="0.35" stop-color="#ffd24a" stop-opacity="0.35"/><stop offset="1" stop-color="#ffd24a" stop-opacity="0"/></radialGradient></defs>'''
body=f'<rect width="{W}" height="{H}" fill="#23272e"/>'
body+='<text x="70" y="52" font-size="26" fill="#f2f4f7" font-weight="700">Макет платы светильника (вид сверху, условная компоновка)</text>'
body+='<text x="70" y="100" font-size="18" fill="#aab2bd">Выключен</text>'+board(70,115,False)
body+='<text x="70" y="590" font-size="18" fill="#aab2bd">Включён (700 мА, тёплый белый)</text>'+board(70,605,True)
body+='<text x="70" y="1048" font-size="15" fill="#8a929d">Алюминиевая плата MCPCB ≈130×50 мм, белая паяльная маска, чёрная шелкография. Размещение условное: разводка и Gerber ещё не сделаны.</text>'
open('lamp_mockup.svg','w',encoding='utf-8').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Liberation Sans, Arial, sans-serif">{defs}{body}</svg>')
