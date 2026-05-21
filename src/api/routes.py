"""
Rotas da API.

Separadas em um APIRouter para deixar o `main.py` enxuto.
"""
import logging
import time
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from src import __version__
from src.api.monitoring import (
    LAST_PREDICTION_VALUE,
    TrackPrediction,
)
from src.api.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionItem,
    PredictRequest,
    PredictResponse,
    SymbolPredictRequest,
    SymbolPredictResponse,
)
import requests as http_requests

from src.data_loader import fetch_recent_window

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================ #
@router.get("/api/chart/{symbol}", tags=["chart"])
def chart_proxy(symbol: str, range: str = "3mo", interval: str = "1d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}"
    try:
        resp = http_requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================ #
@router.get("/", tags=["root"], response_class=HTMLResponse)
def root(request: Request):
    try:
        return _build_dashboard(request)
    except Exception as exc:
        logger.exception("Erro no GET /")
        return HTMLResponse(
            f"<html><body style='background:#050507;color:#FF3B3B;font-family:monospace;padding:40px;'>"
            f"<h2>Internal Server Error</h2><pre>{exc}</pre></body></html>",
            status_code=500,
        )


def _build_dashboard(request: Request) -> HTMLResponse:
    predictor = getattr(request.app.state, "predictor", None)
    md = predictor.metadata if predictor else {}
    metrics = md.get("metrics", {}) if md else {}
    status_color = "#00FF88" if predictor else "#FF3B3B"
    status_text = "ONLINE" if predictor else "DEGRADED"
    model_badge = "● MODELO CARREGADO" if predictor else "○ MODELO NÃO DISPONÍVEL"

    mae_val = str(metrics.get("mae", "—"))[:5] if metrics else "—"
    rmse_val = str(metrics.get("rmse", "—"))[:5] if metrics else "—"
    mape_val = str(metrics.get("mape", "—"))[:5] if metrics else "—"
    mape_num = metrics.get("mape", 0) if metrics else 0
    symbol = str(md.get("symbol", "—")) if md else "—"
    window_size = str(md.get("window_size", "—")) if md else "—"
    lstm_1 = str(md.get("lstm_units_1", "?")) if md else "?"
    lstm_2 = str(md.get("lstm_units_2", "?")) if md else "?"
    trained_at = md.get("trained_at", "—") if md else "—"
    if trained_at != "—":
        trained_at = str(trained_at)[:10]

    # Build HTML — use string replacement to avoid f-string brace hell
    _SC = status_color
    _ST = status_text
    _MB = model_badge
    _SY = symbol
    _MV = mae_val
    _RV = rmse_val
    _MPV = mape_val
    _MPN = mape_num
    _W = str(window_size)
    _L1 = lstm_1
    _L2 = lstm_2
    _TR = trained_at
    _VER = __version__
    _NOW = datetime.now().strftime('%Y-%m-%d %H:%M')
    _ACC = f'{100 - mape_num:.1f}%' if mape_num > 0 else '—'

    _HTML = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Trading Terminal</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#050507;color:#A1A1AA;font-family:'JetBrains Mono',monospace;min-height:100vh;padding:16px;background-image:radial-gradient(ellipse at 20% 50%,rgba(0,255,136,0.03) 0%,transparent 50%),radial-gradient(ellipse at 80% 50%,rgba(183,148,244,0.03) 0%,transparent 50%)}
body::before{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.008) 2px,rgba(0,255,136,0.008) 4px);z-index:9999}
.c{max-width:1120px;width:100%;margin:0 auto}
.tb{font-size:0.6rem;color:#3F3F46;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.tb-p{color:#00FF88}
.tb-c{animation:bl 1s step-end infinite}
@keyframes bl{50%{opacity:0}}
.tr{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:10px}
.b{display:flex;align-items:center;gap:14px}
.b-i{width:34px;height:34px;border:1px solid #00FF88;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#00FF88;font-weight:700;font-size:.95rem;box-shadow:0 0 14px rgba(0,255,136,0.1)}
.b-n{font-size:1.1rem;font-weight:700;color:#FAFAFA;letter-spacing:-0.3px}
.b-n span{color:#00FF88}
.b-t{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.15em}
.sp{display:flex;align-items:center;gap:8px;padding:5px 12px;background:#0A0A0F;border:1px solid #18181B;border-radius:20px;font-size:0.6rem}
.sp-d{width:7px;height:7px;border-radius:50%;background:__SC__;box-shadow:0 0 8px __SC__;animation:pd 2s ease-in-out infinite}
@keyframes pd{0%,100%{opacity:1}50%{opacity:0.3}}
.mm{font-size:0.5rem;color:#3F3F46;text-align:right;line-height:1.6}
.tape{overflow:hidden;background:#0A0A0F;border:1px solid #18181B;border-radius:6px;margin-bottom:20px;padding:6px 0;white-space:nowrap}
.tape-inner{display:inline-flex;animation:scroll 40s linear infinite}
.tape-inner:hover{animation-play-state:paused}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ti{display:inline-flex;align-items:center;gap:6px;padding:0 18px;font-size:0.6rem;border-right:1px solid #18181B}
.ti-s{color:#FAFAFA;font-weight:600}
.ti-p{color:#A1A1AA}
.ti-c{font-weight:500}
.ti-c.up{color:#00FF88}
.ti-c.dn{color:#FF3B3B}
.ti-d{width:3px;height:3px;border-radius:50%;background:#3F3F46}
.es{display:flex;align-items:center;justify-content:center;gap:32px;margin-bottom:24px;flex-wrap:wrap}
.ep{position:relative;width:90px;height:90px;flex-shrink:0}
.eg{width:90px;height:90px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#1a3a4a,#0a1a2a 50%,#050a12);box-shadow:inset -12px -6px 20px rgba(0,0,0,0.6),0 0 25px rgba(0,255,136,0.1);position:relative;overflow:hidden}
.eg::before{content:'';position:absolute;inset:0;border-radius:50%;background:linear-gradient(90deg,transparent 30%,rgba(0,255,136,0.05) 50%,transparent 70%);animation:spin 8s linear infinite}
@keyframes spin{0%{transform:translateX(-30%)}100%{transform:translateX(30%)}}
.rg{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:90px;height:90px;border-radius:50%;border:1px solid rgba(0,255,136,0.1);animation:exp 3s ease-out infinite}
.rg:nth-child(2){animation-delay:1s}
.rg:nth-child(3){animation-delay:2s}
@keyframes exp{0%{width:90px;height:90px;opacity:1}100%{width:200px;height:200px;opacity:0}}
.sh{display:flex;gap:18px;flex-wrap:wrap}
.si{text-align:center}
.sn{font-size:1rem;font-weight:600}
.sl{font-size:0.45rem;color:#52525B;text-transform:uppercase;letter-spacing:0.12em;margin-top:2px}
.kr{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:6px}
.k{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:12px;cursor:pointer;transition:all .25s;position:relative;overflow:hidden}
.k::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:transparent;transition:background .25s}
.k:hover{border-color:#27272A;background:#0E0E15}
.k.on{border-color:#333}
.k.green.on::before{background:#00FF88}
.k.blue.on::before{background:#5B9DFF}
.k.purple.on::before{background:#B794F4}
.k.amber.on::before{background:#FF9500}
.kh{display:flex;justify-content:space-between;align-items:center}
.kl{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em}
.ki{font-size:0.6rem;color:#3F3F46}
.kv{font-size:1rem;font-weight:600;color:#FAFAFA;margin:3px 0}
.kd{font-size:0.5rem}
.kd.up{color:#00FF88}
.kd.dn{color:#FF3B3B}
.kd.nt{color:#FBBF24}
.db{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:16px;margin-bottom:18px;display:none;animation:sl .3s ease}
.db.sh{display:block}
@keyframes sl{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}
.dt{font-size:0.45rem;color:#52525B;text-transform:uppercase;letter-spacing:0.15em}
.dti{font-size:.9rem;font-weight:600;color:#FAFAFA;margin:4px 0 8px}
.dtx{font-size:0.7rem;color:#A1A1AA;line-height:1.6}
.dtx b{color:#FAFAFA}
.mg{display:grid;grid-template-columns:1.8fr 1fr;gap:14px;margin-bottom:16px}
.cc{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:12px}
.ct{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.ctl{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em}
.rg2{display:flex;gap:4px}
.rb{padding:2px 8px;background:transparent;border:1px solid #18181B;border-radius:4px;color:#52525B;font-family:inherit;font-size:0.5rem;cursor:pointer;transition:all .2s}
.rb:hover{border-color:#333;color:#A1A1AA}
.rb.ac{border-color:#00FF88;color:#00FF88}
.cb{height:280px}
.cb>div{width:100%!important;height:100%!important}
.pc{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:12px}
.pt{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px}
.pr{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #0E0E15;font-size:0.6rem}
.pr:last-child{border-bottom:none}
.pd{color:#3F3F46}
.pv{color:#FAFAFA;font-weight:500}
.pch{font-size:0.55rem}
.pch.pos{color:#00FF88}
.pch.neg{color:#FF3B3B}
.mb{display:inline-block;padding:2px 6px;border:1px solid #00FF88;border-radius:4px;font-size:0.45rem;color:#00FF88;margin-top:8px}
.ig{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}
.il{font-size:0.4rem;color:#3F3F46;text-transform:uppercase;letter-spacing:0.1em}
.iv{font-size:0.65rem;color:#FAFAFA;font-weight:500}
.hc{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:12px;margin-bottom:14px}
.ht{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px}
.tbl{width:100%;border-collapse:collapse;font-size:0.55rem}
.tbl th{color:#3F3F46;font-weight:500;text-align:left;padding:4px 6px;border-bottom:1px solid #0E0E15;text-transform:uppercase;letter-spacing:0.08em}
.tbl td{padding:4px 6px;border-bottom:1px solid #0E0E15;color:#A1A1AA}
.tbl td:first-child{color:#FAFAFA;font-weight:500}
.badge{display:inline-block;padding:1px 6px;border-radius:3px;font-size:0.45rem;font-weight:600}
.badge.up{background:rgba(0,255,136,0.1);color:#00FF88}
.badge.dn{background:rgba(255,59,59,0.1);color:#FF3B3B}
.badge.nt{background:rgba(251,191,36,0.1);color:#FBBF24}
.ig2{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px;margin-bottom:14px}
.ic{background:#0A0A0F;border:1px solid #18181B;border-radius:6px;padding:10px}
.ih{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.il2{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em}
.iv2{font-size:0.4rem;color:#3F3F46}
.it{font-size:0.6rem;color:#A1A1AA;line-height:1.5}
.it b{color:#FAFAFA}
.prediction-box{background:linear-gradient(135deg,rgba(0,255,136,0.04),transparent);border:1px solid rgba(0,255,136,0.15);border-radius:8px;padding:14px;text-align:center;margin-bottom:14px}
.prediction-box .pb-label{font-size:0.5rem;color:#52525B;text-transform:uppercase;letter-spacing:0.1em}
.prediction-box .pb-value{font-size:1.5rem;font-weight:700;color:#00FF88;margin:4px 0}
.prediction-box .pb-sub{font-size:0.6rem;color:#A1A1AA}
.prediction-box .pb-conf{display:inline-block;padding:2px 10px;background:rgba(0,255,136,0.1);border-radius:10px;font-size:0.55rem;color:#00FF88;margin-top:6px}
.ft{text-align:center;margin-top:20px;font-size:0.5rem;color:#3F3F46;padding-bottom:20px}
.ft a{color:#52525B;text-decoration:none}
.ft a:hover{color:#A1A1AA}
@media(max-width:768px){.kr{grid-template-columns:repeat(2,1fr)}.mg{grid-template-columns:1fr}.ig2{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class=c>
<div class=tb><span class=tb-p>►</span><span>AI Quant Terminal · v__VER__ · __NOW__Z</span><span class=tb-c>▌</span></div>
<div class=tr>
  <div class=b><div class=b-i>◆</div><div><div class=b-n>AI <span>Quant</span></div><div class=b-t>LSTM Trading Terminal</div></div></div>
  <div class=sp><span class=sp-d></span><span style=color:__SC__;font-weight:500>__ST__</span><span style=color:#3F3F46>·</span><span style=color:#52525B>__MB__</span></div>
  <div class=mm><div>MODEL __SY__</div><div>TRAIN __TR__</div></div>
</div>
<div class=tape id=tape><div class=tape-inner id=tapeInner></div></div>
<div class=es>
  <div class=ep><div class=rg></div><div class=rg></div><div class=rg></div><div class=eg></div></div>
  <div class=sh>
    <div class=si><div class=sn style=color:#00FF88>__SY__</div><div class=sl>Simbolo</div></div>
    <div class=si><div class=sn style=color:#B794F4>__MV__</div><div class=sl>MAE</div></div>
    <div class=si><div class=sn style=color:#5B9DFF>__RV__</div><div class=sl>RMSE</div></div>
    <div class=si><div class=sn style=color:#FBBF24>__MPV__%</div><div class=sl>MAPE</div></div>
    <div class=si><div class=sn style=color:#FF9500>__W__</div><div class=sl>Window</div></div>
  </div>
</div>
<div class=kr>
  <div class="k green" data-k=p onclick=kC(this)><div class=kh><span class=kl>Preco Atual</span><span class=ki>$</span></div><div class=kv id=kP>—</div><div class="kd up" id=kPD>—</div></div>
  <div class="k blue" data-k=v onclick=kC(this)><div class=kh><span class=kl>Volatilidade</span><span class=ki>s</span></div><div class=kv id=kV>—</div><div class=kd id=kVD>—</div></div>
  <div class="k purple" data-k=d onclick=kC(this)><div class=kh><span class=kl>Tendencia (20d)</span><span class=ki>D</span></div><div class=kv id=kT>—</div><div class=kd id=kTD>—</div></div>
  <div class="k amber" data-k=a onclick=kC(this)><div class=kh><span class=kl>Confianca IA</span><span class=ki>l</span></div><div class=kv id=kA>—</div><div class="kd up" id=kAD>—</div></div>
</div>
<div class=db id=dB><div class=dt id=dTag></div><div class=dti id=dTi></div><div class=dtx id=dTx></div></div>
<div class=prediction-box id=pb>
  <div class=pb-label>* LSTM PREDICTION * D+1</div>
  <div class=pb-value id=pbV>—</div>
  <div class=pb-sub id=pbS>carregando...</div>
  <div class=pb-conf id=pbC></div>
</div>
<div class=mg>
  <div class=cc>
    <div class=ct><div class=ctl>CANDLE * __SY__</div><div class=rg2 id=rG><button class="rb ac" data-r=1mo>1M</button><button class=rb data-r=3mo>3M</button><button class=rb data-r=6mo>6M</button><button class=rb data-r=1y>1A</button></div></div>
    <div class=cb id=cB></div>
  </div>
  <div class=pc>
    <div class=pt>Previsao LSTM * Proximos Dias</div>
    <div id=pB><div style=text-align:center;padding:20px 0;color:#3F3F46;font-size:0.6rem>carregando...</div></div>
    <div class=mb>LSTM __L1__+__L2__ * window __W__</div>
    <div class=ig>
      <div><div class=il>MAE</div><div class=iv style=color:#FF9500>__MV__</div></div>
      <div><div class=il>RMSE</div><div class=iv style=color:#FBBF24>__RV__</div></div>
      <div><div class=il>MAPE</div><div class=iv style=color:#00FF88>__MPV__%</div></div>
      <div><div class=il>Acuracia</div><div class=iv style=color:#00FF88>__ACC__</div></div>
    </div>
  </div>
</div>
<div class=hc><div class=ht>Historico Recente * Ultimas Sessoes</div><table class=tbl id=hT><tr><th>Data</th><th>Abertura</th><th>Fechamento</th><th>Volume</th><th>Var %</th><th>Status</th></tr></table></div>
<div class=ht style=margin-bottom:6px>AI Insights</div>
<div class=ig2 id=iG></div>
<div class=ft>
  Tech Challenge Fase 4 * PosTech MLET FIAP *
  <a href=https://github.com/dionebraga/Pos_Tech_MLET-Fase-4 target=_blank>GitHub</a> *
  <a href=/health>System Health</a> * <a href=/docs>API Docs</a>
</div>
</div>
<script>
const SY='__SY__',MP=__MPN__,CF=MP>0?(100-MP).toFixed(1):'--';
const DD={p:{t:'Asset Price',ti:'Analise de Preco',tx:'Carregando...',c:'green'},v:{t:'Risk Metric',ti:'Volatilidade Anualizada',tx:'Carregando...',c:'blue'},d:{t:'Technical',ti:'Analise de Tendencia',tx:'Carregando...',c:'purple'},a:{t:'Model Output',ti:'Confianca do Modelo LSTM',tx:'Carregando...',c:'amber'}};
let ch=null,ar='3mo';
const TK=[['AAPL',280.12,3.53],['MSFT',521.40,1.24],['GOOGL',198.55,-0.42],['AMZN',245.80,2.11],['TSLA',412.60,-1.85],['META',745.30,0.92],['NVDA',198.12,4.21],['BTC',98521.0,1.68],['ETH',4280.50,2.40],['S&P500',6122.4,0.18],['USD/BRL',5.42,-0.32],['OURO',2782.1,0.74]];
function iTape(){document.getElementById('tapeInner').innerHTML=TK.concat(TK).map(function(s){return'<div class=ti><span class=ti-s>'+s[0]+'</span><span class=ti-p>$'+s[1].toFixed(2)+'</span><span class="ti-c '+(s[2]>=0?'up':'dn')+'">'+(s[2]>=0?'+':'')+s[2].toFixed(2)+'%</span><span class=ti-d></span></div>'}).join('')}
iTape();
function kC(e){var k=e.dataset.k,b=document.getElementById('dB'),s=b.classList.contains('sh')&&b.dataset.k===k;document.querySelectorAll('.k').forEach(function(c){c.classList.remove('on')});if(s){b.classList.remove('sh');b.dataset.k='';return}e.classList.add('on');b.dataset.k=k;var d=DD[k];document.getElementById('dTag').textContent=d.t;document.getElementById('dTi').textContent=d.ti;document.getElementById('dTx').innerHTML=d.tx;b.className='db sh'}
function iC(){var c=LightweightCharts.createChart(document.getElementById('cB'),{layout:{background:{type:'solid',color:'#0A0A0F'},textColor:'#52525B',fontFamily:'JetBrains Mono'},grid:{vertLines:{color:'#0E0E15'},horzLines:{color:'#0E0E15'}},timeScale:{borderColor:'#18181B',timeVisible:false},rightPriceScale:{borderColor:'#18181B'},crosshair:{mode:LightweightCharts.CrosshairMode.Normal},width:0,height:280});return{c:c,cs:c.addCandlestickSeries({upColor:'#00FF88',downColor:'#FF3B3B',borderUpColor:'#00FF88',borderDownColor:'#FF3B3B',wickUpColor:'#00FF88',wickDownColor:'#FF3B3B'}),vs:c.addHistogramSeries({priceFormat:{type:'volume'},color:'rgba(0,255,136,0.08)'})}}
async function load(r){try{var h=await(await fetch('/health')).json();if(!h.model_loaded)throw Error}catch(e){document.getElementById('cB').innerHTML='<div style=text-align:center;padding:40px;color:#52525B;font-size:0.65rem>Modelo offline</div>';return}
var pd=null;try{pd=await(await fetch('/predict/symbol',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:SY,days_ahead:5})})).json()}catch(e){}
if(pd){document.getElementById('kP').textContent='$'+pd.last_close.toFixed(2);var pc=((pd.predictions[0].predicted_price-pd.last_close)/pd.last_close*100),ps=(pc>=0?'+':'')+pc.toFixed(2)+'%',eL=document.getElementById('kPD');eL.textContent=ps+' (D+1 $'+pd.predictions[0].predicted_price.toFixed(2)+')';eL.className='kd '+(pc>=0?'up':'dn');DD.p.tx='O ativo <b>'+SY+'</b> opera em <b>$'+pd.last_close.toFixed(2)+'</b>. Previsao LSTM D+1: <b>$'+pd.predictions[0].predicted_price.toFixed(4)+'</b> ('+ps+'). MAPE: <b>'+'__MPV__'+'%</b>.';DD.a.tx='Modelo LSTM <b>__L1__+__L2__</b> treinado em <b>'+SY+'</b> window=<b>__W__</b>. D+1: <b>$'+pd.predictions[0].predicted_price.toFixed(2)+'</b>. MAPE: <b>__MPV__%</b>. Acuracia: <b>'+CF+'%</b>.';document.getElementById('kA').textContent=CF+'%';document.getElementById('kAD').textContent='MAPE __MPV__%';document.getElementById('pbV').textContent='$'+pd.predictions[0].predicted_price.toFixed(2);document.getElementById('pbS').textContent='vs ultimo close * '+ps;document.getElementById('pbC').textContent='Confianca '+CF+'%';document.getElementById('pB').innerHTML=pd.predictions.map(function(p,i){var cg=i===0&&pd.last_close?((p.predicted_price-pd.last_close)/pd.last_close*100):0;return'<div class=pr><span class=pd>D+'+p.day+'</span><span class=pv>$'+p.predicted_price.toFixed(2)+'</span><span class="pch '+(cg>=0?'pos':'neg')+'">'+(cg>=0?'+':'')+cg.toFixed(2)+'%</span></div>'}).join('')}else{document.getElementById('pB').innerHTML='<div style=text-align:center;padding:14px 0;color:#3F3F46;font-size:0.55rem>Previsao indisponivel</div>'}
try{var j=await(await fetch('/api/chart/'+SY+'?range='+r+'&interval=1d')).json(),q=j.chart.result[0],t=q.timestamp,o=q.indicators.quote[0].open,hh=q.indicators.quote[0].high,ll=q.indicators.quote[0].low,cl=q.indicators.quote[0].close,vo=q.indicators.quote[0].volume,cd=[],vs=[],last8=[];var mi=Infinity,ma=-Infinity,prevC=null;for(var i=0;i<t.length;i++){if(o[i]==null||cl[i]==null)continue;cd.push({time:t[i],open:o[i],high:hh[i]||o[i],low:ll[i]||cl[i],close:cl[i]});vs.push({time:t[i],value:vo[i]||0,color:cl[i]>=o[i]?'rgba(0,255,136,0.08)':'rgba(255,59,59,0.08)'});if(o[i]<mi)mi=o[i];if(cl[i]>ma)ma=cl[i];last8.push({t:new Date(t[i]*1000).toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'}),o:o[i],c:cl[i],v:vo[i]||0,chg:prevC?((cl[i]-prevC)/prevC*100):0});prevC=cl[i]}
last8.reverse().slice(0,8).reverse();
var vola=((ma-mi)/mi*100);document.getElementById('kV').textContent=vola.toFixed(1)+'%';var vE=document.getElementById('kVD');vE.textContent=vola<30?'ok risco controlado':'up volatilidade elevada';vE.className='kd '+(vola<30?'up':'dn');DD.v.tx='Volatilidade <b>'+vola.toFixed(2)+'%</b> no periodo ('+r+'). O ativo esta <b>'+(vola<30?'dentro':'acima')+'</b> dos niveis de risco usuais.';
var l20=cl.filter(function(c){return c!=null}).slice(-20),sl=l20.length>1?(l20[l20.length-1]-l20[0])/l20[0]*100:0,tTxt=sl>0.5?'ALTA':sl<-0.5?'BAIXA':'LATERAL',tCls=sl>0.5?'up':sl<-0.5?'dn':'nt',tNm=sl>0.5?'Bullish':sl<-0.5?'Bearish':'Neutral';document.getElementById('kT').textContent=tTxt;var tE=document.getElementById('kTD');tE.textContent=tNm+' * '+sl.toFixed(2)+'%';tE.className='kd '+tCls;DD.d.tx='Tendencia <b>'+tTxt+'</b> ('+tNm+') ultimos 20d. Inclinacao: <b>'+sl.toFixed(2)+'%</b>.';
var tB=document.getElementById('hT');for(var i=Math.max(0,last8.length-8);i<last8.length;i++){var x=last8[i],bg=x.chg>0.5?'up':x.chg<-0.5?'dn':'nt',st=x.chg>0.5?'ALTA':x.chg<-0.5?'BAIXA':'FLAT';tB.innerHTML+='<tr><td>'+x.t+'</td><td>$'+x.o.toFixed(2)+'</td><td>$'+x.c.toFixed(2)+'</td><td>'+(x.v/1e6).toFixed(0)+'M</td><td style=color:'+(x.chg>=0?'#00FF88':'#FF3B3B')+'>'+(x.chg>=0?'+':'')+x.chg.toFixed(2)+'%</td><td><span class="badge '+bg+'">'+st+'</span></td></tr>'}
var cl2=cl.filter(function(c){return c!=null}),l20_2=cl2.slice(-20),sma=l20_2.reduce(function(a,b){return a+b},0)/l20_2.length,stdv=Math.sqrt(l20_2.reduce(function(s,v){return s+(v-sma)*(v-sma)},0)/l20_2.length),bb=(cl2[cl2.length-1]-sma)/(stdv*2);
var rsi=50;if(cl2.length>14){var g=cl2.slice(-15),diffs=[];for(var i=1;i<g.length;i++)diffs.push(g[i]-g[i-1]);var avgG=diffs.filter(function(d){return d>0}).reduce(function(a,b){return a+b},0)/14||0,avgL=Math.abs(diffs.filter(function(d){return d<0}).reduce(function(a,b){return a+b},0))/14||1;rsi=100-(100/(1+avgG/avgL))}
var macdH=0,macdL=0,macdS=0;if(cl2.length>26){var ma12=cl2.slice(-12).reduce(function(a,b){return a+b},0)/12,ma26=cl2.slice(-26).reduce(function(a,b){return a+b},0)/26;macdL=ma12-ma26;macdS=cl2.slice(-9).reduce(function(a,b){return a+b},0)/9;macdH=macdL-macdS}
var sr=cl2.slice(-20),supp=Math.min.apply(null,sr),res=Math.max.apply(null,sr),dS=((cl2[cl2.length-1]-supp)/supp*100),dR=((res-cl2[cl2.length-1])/cl2[cl2.length-1]*100);
var v5=cl2.slice(-5).reduce(function(a,b){return a+b},0)/5,v20=cl2.slice(-20).reduce(function(a,b){return a+b},0)/20,vR=v5/v20;
var rsiT=rsi>70?'RSI <b>'+rsi.toFixed(1)+'</b> - sobrecomprado. Possivel reversao.':rsi<30?'RSI <b>'+rsi.toFixed(1)+'</b> - sobrevendido. Possivel reversao.':'RSI <b>'+rsi.toFixed(1)+'</b> - neutro.';
var macdT=macdH>0&&macdL>macdS?'MACD positivo - <b>momentum altista</b>.':macdH<0&&macdL<macdS?'MACD negativo - <b>momentum baixista</b>.':macdH>0?'MACD se aproximando - possivel reversao.':'MACD perdendo forca.';
var bbT=bb>0.9?'Preco na borda superior das BB - <b>possivel sobrecompra</b>.':bb<-0.9?'Preco na borda inferior das BB - <b>possivel oversold</b>.':'Preco dentro das Bandas de Bollinger - volatilidade normal.';
var volT=vR>1.5?'Volume <b>'+vR.toFixed(1)+'x</b> acima da media - forte participacao.':vR<0.5?'Volume <b>'+vR.toFixed(1)+'x</b> abaixo da media - baixa participacao.':'Volume dentro da media - atividade normal.';
var srT='Suporte <b>$'+supp.toFixed(2)+'</b> ('+dS.toFixed(1)+'%) * Resistencia <b>$'+res.toFixed(2)+'</b> ('+dR.toFixed(1)+'%)';
var insights=[['RSI','14 periodos',rsiT],['MACD','12/26/9',macdT],['Bollinger','2s',bbT],['Volume','5d vs 20d',volT],['Sup/Res',SY,srT]];
document.getElementById('iG').innerHTML=insights.map(function(x){return'<div class=ic><div class=ih><span class=il2>'+x[0]+'</span><span class=iv2>'+x[1]+'</span></div><div class=it>'+x[2]+'</div></div>'}).join('');
if(ch)ch.c.remove();var nc=iC();ch=nc;nc.cs.setData(cd);nc.vs.setData(vs);nc.c.timeScale().fitContent()}catch(e){document.getElementById('cB').innerHTML='<div style=text-align:center;padding:40px;color:#52525B;font-size:0.65rem>Grafico indisponivel</div>'}}
document.getElementById('rG').querySelectorAll('.rb').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.rb').forEach(function(x){x.classList.remove('ac')});this.classList.add('ac');ar=this.dataset.r;load(ar)})});
load(ar);
</script>
</body>
</html>'''

    html = (
        _HTML.replace('__SC__', _SC)
        .replace('__ST__', _ST)
        .replace('__MB__', _MB)
        .replace('__SY__', _SY)
        .replace('__MV__', _MV)
        .replace('__RV__', _RV)
        .replace('__MPV__', _MPV)
        .replace('__MPN__', str(_MPN))
        .replace('__W__', _W)
        .replace('__L1__', _L1)
        .replace('__L2__', _L2)
        .replace('__TR__', _TR)
        .replace('__VER__', _VER)
        .replace('__NOW__', _NOW)
        .replace('__ACC__', _ACC)
    )
    return HTMLResponse(html)


# ============================================================ #
@router.get("/healthz", tags=["health"])
def healthz():
    """Render's routing layer probes this endpoint for readiness."""
    return {"status": "ok"}


# ============================================================ #
@router.get("/health", tags=["health"])
def health_check(request: Request):
    predictor = getattr(request.app.state, "predictor", None)
    md = predictor.metadata if predictor else {}
    metrics_data = md.get("metrics", {}) if md else {}
    engine_status = "ok" if predictor is not None else "degraded"

    now = datetime.now()
    uptime_seconds = (now - getattr(request.app.state, "_started_at", now)).seconds if hasattr(request.app.state, "_started_at") else 0

    query_format = request.query_params.get("format", "")
    accept = request.headers.get("accept", "")
    if query_format == "json" or "text/html" not in accept:
        return {
            "status": engine_status,
            "model_loaded": predictor is not None,
            "version": __version__,
            "model": {
                "symbol": md.get("symbol", "—") if md else "—",
                "metrics": {
                    "mae": metrics_data.get("mae"),
                    "rmse": metrics_data.get("rmse"),
                    "mape": metrics_data.get("mape"),
                } if metrics_data else None,
                "window_size": md.get("window_size") if md else None,
                "trained_at": md.get("trained_at") if md else None,
            } if predictor else None,
            "uptime_seconds": uptime_seconds,
            "timestamp": now.isoformat(),
        }

    status_color = "#00FF88" if predictor else "#FF3B3B"
    status_text = "ONLINE" if predictor else "DEGRADED"
    symbol = md.get("symbol", "—") if md else "—"
    trained_at = md.get("trained_at", "—") if md else "—"
    window_size = md.get("window_size", "—") if md else "—"

    mae_raw = metrics_data.get("mae") if metrics_data else None
    rmse_raw = metrics_data.get("rmse") if metrics_data else None
    mape_raw = metrics_data.get("mape") if metrics_data else None
    mae_v = f"{mae_raw:.4f}" if mae_raw is not None else "—"
    rmse_v = f"{rmse_raw:.4f}" if rmse_raw is not None else "—"
    mape_v = f"{mape_raw:.2f}" if mape_raw is not None else "—"

    mae_bar = f"{min(100, max(5, int(mae_raw * 10)))}" if mae_raw is not None else "0"
    rmse_bar = f"{min(100, max(5, int(rmse_raw * 8)))}" if rmse_raw is not None else "0"
    mape_bar = f"{min(100, max(5, int(mape_raw * 12)))}" if mape_raw is not None else "0"

    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Health</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background:#050507; color:#A1A1AA; font-family:'JetBrains Mono',monospace;
    min-height:100vh; padding:32px 20px; display:flex; flex-direction:column; align-items:center;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.03) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 50%, rgba(183,148,244,0.03) 0%, transparent 50%);
  }}
  body::before {{
    content:''; position:fixed; inset:0; pointer-events:none;
    background:repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,136,0.008) 2px, rgba(0,255,136,0.008) 4px);
    z-index:9999;
  }}
  .container {{ max-width:680px; width:100%; }}
  .prompt {{ font-size:0.6rem; color:#3F3F46; margin-bottom:24px; display:flex; align-items:center; gap:8px; }}
  .prompt-sym {{ color:#00FF88; }}
  .cursor {{ animation:blink 1s step-end infinite; }}
  @keyframes blink {{ 50%{{opacity:0}} }}

  .card {{
    background:#0A0A0F; border:1px solid #18181B; border-radius:8px;
    padding:24px; margin-bottom:16px;
  }}
  .card-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:16px; }}

  .status-row {{ display:flex; align-items:center; gap:12px; margin-bottom:24px; }}
  .status-dot {{ width:12px; height:12px; border-radius:50%; background:{status_color};
    box-shadow:0 0 16px {status_color}; animation:pulse-dot 2s ease-in-out infinite; }}
  @keyframes pulse-dot {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
  .status-label {{ font-size:1.1rem; font-weight:600; color:{status_color}; }}
  .status-sub {{ font-size:0.65rem; color:#52525B; }}

  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .field {{}}
  .field-label {{ font-size:0.5rem; color:#3F3F46; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px; }}
  .field-value {{ font-size:0.85rem; color:#FAFAFA; font-weight:500; }}
  .field-value.green {{ color:#00FF88; }}
  .field-value.blue {{ color:#5B9DFF; }}
  .field-value.purple {{ color:#B794F4; }}
  .field-value.yellow {{ color:#FBBF24; }}
  .field-value.orange {{ color:#FF9500; }}
  .field-value.red {{ color:#FF3B3B; }}

  .bar-group {{ margin-top:16px; }}
  .bar-row {{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }}
  .bar-label {{ font-size:0.55rem; color:#52525B; width:60px; flex-shrink:0; }}
  .bar-track {{ flex:1; height:6px; background:#0E0E15; border-radius:3px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:3px; }}

  .meta {{ font-size:0.6rem; color:#3F3F46; text-align:center; margin-top:24px; }}
  .meta a {{ color:#52525B; text-decoration:none; }}
  .meta a:hover {{ color:#A1A1AA; }}

  .section {{ margin-top:20px; }}
  .section-title {{ font-size:0.55rem; color:#52525B; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:12px; }}

  .endpoints {{ background:#0A0A0F; border:1px solid #18181B; border-radius:8px; overflow:hidden; }}
  .endpoint-row {{
    display:flex; justify-content:space-between; align-items:center;
    padding:10px 16px; border-bottom:1px solid #18181B; font-size:0.72rem;
    transition:background .2s; text-decoration:none; color:inherit;
  }}
  .endpoint-row:last-child {{ border-bottom:none; }}
  .endpoint-row:hover {{ background:#0E0E15; }}
  .endpoint-method {{
    display:inline-block; width:44px; padding:2px 0; text-align:center;
    border-radius:4px; font-size:0.55rem; font-weight:700;
  }}
  .get {{ background:rgba(97,175,254,0.15); color:#61AFFE; }}
  .endpoint-path {{ color:#FAFAFA; font-weight:500; margin-left:10px; }}
  .endpoint-desc {{ color:#52525B; font-size:0.6rem; margin-left:auto; }}

  .json-btn {{
    display:inline-block; margin-top:12px; padding:6px 14px;
    background:transparent; border:1px solid #18181B; border-radius:4px;
    color:#52525B; font-family:inherit; font-size:0.6rem; cursor:pointer;
    text-decoration:none; transition:all .2s;
  }}
  .json-btn:hover {{ border-color:#333; color:#A1A1AA; }}

  @media (max-width:500px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="prompt">
    <span class="prompt-sym">►</span>
    <span>healthcheck — {now.strftime('%Y-%m-%d %H:%M:%S')}Z</span>
    <span class="cursor">▌</span>
  </div>

  <div class="card">
    <div class="card-title">Status do Sistema</div>
    <div class="status-row">
      <span class="status-dot"></span>
      <div>
        <div class="status-label">{status_text}</div>
        <div class="status-sub">v{__version__} · {uptime_str} de atividade</div>
      </div>
    </div>

    <div class="grid">
      <div class="field">
        <div class="field-label">Modelo</div>
        <div class="field-value green">{'CARREGADO' if predictor else 'NÃO DISPONÍVEL'}</div>
      </div>
      <div class="field">
        <div class="field-label">Símbolo</div>
        <div class="field-value blue">{symbol}</div>
      </div>
      <div class="field">
        <div class="field-label">Janela (window)</div>
        <div class="field-value purple">{window_size}</div>
      </div>
      <div class="field">
        <div class="field-label">Treinado em</div>
        <div class="field-value" style="font-size:0.7rem;">{trained_at[:19] if trained_at != '—' else '—'}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Métricas do Modelo</div>
    <div class="grid">
      <div class="field">
        <div class="field-label">MAE</div>
        <div class="field-value orange">{mae_v}</div>
      </div>
      <div class="field">
        <div class="field-label">RMSE</div>
        <div class="field-value yellow">{rmse_v}</div>
      </div>
      <div class="field">
        <div class="field-label">MAPE</div>
        <div class="field-value green">{mape_v}%</div>
      </div>
      <div class="field">
        <div class="field-label">Acurácia</div>
        <div class="field-value green">{f'{100 - mape_raw:.2f}%' if mape_raw is not None else '—'}</div>
      </div>
    </div>

    <div class="bar-group">
      <div class="bar-row">
        <span class="bar-label">MAE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{mae_bar}%;background:#FF9500;"></div></div>
      </div>
      <div class="bar-row">
        <span class="bar-label">RMSE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{rmse_bar}%;background:#FBBF24;"></div></div>
      </div>
      <div class="bar-row">
        <span class="bar-label">MAPE</span>
        <div class="bar-track"><div class="bar-fill" style="width:{mape_bar}%;background:#00FF88;"></div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Endpoints</div>
    <div class="endpoints">
      <a class="endpoint-row" href="/">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/</span></span>
        <span class="endpoint-desc">Dashboard principal</span>
      </a>
      <a class="endpoint-row" href="/model/info">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/model/info</span></span>
        <span class="endpoint-desc">Metadados do treinamento</span>
      </a>
      <a class="endpoint-row" href="/docs">
        <span><span class="endpoint-method" style="background:rgba(255,255,255,0.06);color:#888;">DOC</span><span class="endpoint-path">Swagger UI</span></span>
        <span class="endpoint-desc">Documentação interativa</span>
      </a>
      <a class="endpoint-row" href="/metrics">
        <span><span class="endpoint-method get">GET</span><span class="endpoint-path">/metrics</span></span>
        <span class="endpoint-desc">Métricas Prometheus</span>
      </a>
    </div>
  </div>

  <div style="text-align:center;margin-top:16px;">
    <a class="json-btn" href="/health?format=json">⎔ Ver JSON</a>
  </div>

  <div class="meta">
    <a href="/">⟨⟩ AI Quant Terminal</a> · <a href="/docs">API Docs</a> · {now.strftime('%Y-%m-%d %H:%M:%S')}Z
  </div>
</div>
</body>
</html>""")


# ============================================================ #
@router.get("/model/info", tags=["model"])
def model_info(request: Request):
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    md = predictor.metadata
    query_format = request.query_params.get("format", "")
    accept = request.headers.get("accept", "")

    want_json = query_format == "json" or "application/json" in accept
    if not want_json:
        metrics = md.get("metrics", {})
        mae = metrics.get("mae", "—")
        rmse = metrics.get("rmse", "—")
        mape = metrics.get("mape", "—")
        trained_at_str = str(md.get("trained_at", "—"))[:19]
        lstm_str = f"{md.get('lstm_units_1', '?')}+{md.get('lstm_units_2', '?')}"

        mae_v = f"{mae:.4f}" if isinstance(mae, (int, float)) else "—"
        rmse_v = f"{rmse:.4f}" if isinstance(rmse, (int, float)) else "—"
        mape_v = f"{mape:.2f}%" if isinstance(mape, (int, float)) else "—"

        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Quant · Model Info</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#050507;color:#A1A1AA;font-family:'JetBrains Mono',monospace;min-height:100vh;padding:32px 20px;display:flex;flex-direction:column;align-items:center}}
body::before{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,0.008) 2px,rgba(0,255,136,0.008) 4px);z-index:9999}}
.container{{max-width:680px;width:100%}}
.prompt{{font-size:0.6rem;color:#3F3F46;margin-bottom:24px;display:flex;align-items:center;gap:8px}}
.prompt-sym{{color:#00FF88}}
.cursor{{animation:blink 1s step-end infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.card{{background:#0A0A0F;border:1px solid #18181B;border-radius:8px;padding:24px;margin-bottom:16px}}
.card-title{{font-size:0.55rem;color:#52525B;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:16px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.field{{}}
.field-label{{font-size:0.5rem;color:#3F3F46;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px}}
.field-value{{font-size:0.85rem;color:#FAFAFA;font-weight:500}}
.field-value.green{{color:#00FF88}}
.field-value.blue{{color:#5B9DFF}}
.field-value.purple{{color:#B794F4}}
.field-value.orange{{color:#FF9500}}
.meta{{font-size:0.6rem;color:#3F3F46;text-align:center;margin-top:24px}}
.meta a{{color:#52525B;text-decoration:none}}
.meta a:hover{{color:#A1A1AA}}
.json-btn{{display:inline-block;margin-top:12px;padding:6px 14px;background:transparent;border:1px solid #18181B;border-radius:4px;color:#52525B;font-family:inherit;font-size:0.6rem;cursor:pointer;text-decoration:none;transition:all .2s}}
.json-btn:hover{{border-color:#333;color:#A1A1AA}}
@media(max-width:500px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class=container>
<div class=prompt><span class=prompt-sym>►</span><span>model/info — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}Z</span><span class=cursor>▌</span></div>
<div class=card>
<div class=card-title>Modelo LSTM</div>
<div class=grid>
<div class=field><div class=field-label>Símbolo</div><div class=field-value green>{md.get("symbol", "?")}</div></div>
<div class=field><div class=field-label>Arquitetura</div><div class=field-value purple>{lstm_str}</div></div>
<div class=field><div class=field-label>Window</div><div class=field-value blue>{md.get("window_size", "?")}</div></div>
<div class=field><div class=field-label>Dropout</div><div class=field-value>{md.get("dropout_rate", "?")}</div></div>
<div class=field><div class=field-label>Epochs</div><div class=field-value>{md.get("epochs_trained", "?")}</div></div>
<div class=field><div class=field-label>Amostras (treino)</div><div class=field-value>{md.get("train_samples", "?")}</div></div>
<div class=field><div class=field-label>Amostras (teste)</div><div class=field-value>{md.get("test_samples", "?")}</div></div>
<div class=field><div class=field-label>Treinado em</div><div class=field-value style=font-size:0.7rem;>{trained_at_str}</div></div>
</div></div>
<div class=card>
<div class=card-title>Métricas</div>
<div class=grid>
<div class=field><div class=field-label>MAE</div><div class=field-value orange>{mae_v}</div></div>
<div class=field><div class=field-label>RMSE</div><div class=field-value>{rmse_v}</div></div>
<div class=field><div class=field-label>MAPE</div><div class=field-value green>{mape_v}</div></div>
<div class=field><div class=field-label>Acurácia</div><div class=field-value green>{f'{100 - mape:.2f}%' if isinstance(mape, (int, float)) else '—'}</div></div>
</div></div>
<div style=text-align:center;margin-top:8px;><a class=json-btn href=/model/info?format=json>⎔ Ver JSON</a></div>
<div class=meta><a href=/>⟨⟩ AI Quant Terminal</a> · <a href=/docs>API Docs</a> · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}Z</div>
</div>
</body>
</html>""")

    return ModelInfoResponse(
        symbol_trained_on=md.get("symbol", "?"),
        window_size=md["window_size"],
        lstm_units_1=md["lstm_units_1"],
        lstm_units_2=md["lstm_units_2"],
        dropout_rate=md["dropout_rate"],
        epochs_trained=md["epochs_trained"],
        train_samples=md["train_samples"],
        test_samples=md["test_samples"],
        metrics=md["metrics"],
        trained_at=md["trained_at"],
    )


# ============================================================ #
@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["prediction"],
    summary="Previsão a partir de histórico fornecido",
)
def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    """
    Recebe uma lista de preços históricos e retorna a previsão.

    A lista precisa ter ao menos `window_size` (60) valores em ordem
    cronológica crescente.
    """
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    if len(payload.close_prices) < predictor.window_size:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Forneça pelo menos {predictor.window_size} preços. "
                f"Recebidos: {len(payload.close_prices)}."
            ),
        )

    start = time.perf_counter()
    with TrackPrediction(endpoint="/predict"):
        if payload.days_ahead == 1:
            preds: List[float] = [predictor.predict_next(payload.close_prices)]
        else:
            preds = predictor.predict_multistep(
                payload.close_prices, steps=payload.days_ahead
            )
    elapsed_ms = (time.perf_counter() - start) * 1000

    items = [
        PredictionItem(day=i + 1, predicted_price=round(p, 4))
        for i, p in enumerate(preds)
    ]

    if preds:
        LAST_PREDICTION_VALUE.labels(symbol="custom").set(preds[-1])

    return PredictResponse(
        predictions=items,
        inference_time_ms=round(elapsed_ms, 2),
    )


# ============================================================ #
@router.post(
    "/predict/symbol",
    response_model=SymbolPredictResponse,
    tags=["prediction"],
    summary="Previsão buscando histórico recente via Yahoo Finance",
)
def predict_from_symbol(
    payload: SymbolPredictRequest, request: Request
) -> SymbolPredictResponse:
    """
    Busca o histórico recente do yfinance e prevê o(s) próximo(s) preço(s).
    """
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado.")

    try:
        closes = fetch_recent_window(payload.symbol, predictor.window_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        logger.exception("Erro ao buscar dados do yfinance")
        raise HTTPException(status_code=502, detail=f"Falha ao buscar dados: {e}")

    last_close = float(closes.iloc[-1])
    last_date = str(closes.index[-1].date())

    start = time.perf_counter()
    with TrackPrediction(endpoint="/predict/symbol"):
        if payload.days_ahead == 1:
            preds = [predictor.predict_next(closes.tolist())]
        else:
            preds = predictor.predict_multistep(
                closes.tolist(), steps=payload.days_ahead
            )
    elapsed_ms = (time.perf_counter() - start) * 1000

    items = [
        PredictionItem(day=i + 1, predicted_price=round(p, 4))
        for i, p in enumerate(preds)
    ]

    if preds:
        LAST_PREDICTION_VALUE.labels(symbol=payload.symbol).set(preds[-1])

    return SymbolPredictResponse(
        symbol=payload.symbol,
        last_close=round(last_close, 4),
        last_close_date=last_date,
        predictions=items,
        inference_time_ms=round(elapsed_ms, 2),
    )
