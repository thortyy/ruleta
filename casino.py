"""Lokální webové kasino s virtuálními žetony. Spusť: python casino.py"""

import json
import random
import threading
import unittest
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


HOST = "127.0.0.1"
PORT = 8765
SAVE_FILE = Path(__file__).with_name("casino_save.json")
STARTING_BALANCE = 2500
DAILY_BONUS = 250
RNG = random.SystemRandom()
STATE_LOCK = threading.RLock()
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

PAGE = r'''<!doctype html>
<html lang="cs"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#131a17">
<title>Lucky Roulette | Evropská ruleta</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{color-scheme:light;--ink:#18211d;--muted:#738078;--paper:#f1f3ed;--white:#fffefa;--line:#dfe4dc;--green:#294b3d;--lime:#d3f36b;--orange:#ff744f;--mono:"DM Mono",Consolas,monospace;--sans:"Space Grotesk","Segoe UI",sans-serif}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans)}button,input,select{font:inherit}button{cursor:pointer}.topline{height:30px;display:flex;align-items:center;justify-content:center;gap:8px;background:var(--lime);color:#20271d;font:11px var(--mono)}.topline i{width:7px;height:7px;border-radius:50%;background:var(--green)}header{position:sticky;top:0;z-index:5;background:#131a17;color:white;border-bottom:1px solid #35413b}.nav{width:min(1180px,calc(100% - 40px));min-height:74px;margin:auto;display:flex;align-items:center;gap:28px}.brand{min-width:200px;display:flex;align-items:center;gap:10px;color:white;text-decoration:none;font-weight:700}.brand-mark{width:35px;height:35px;display:grid;place-items:center;border-radius:10px 10px 10px 3px;background:var(--lime);color:var(--ink);font-size:19px;transform:rotate(-4deg)}.brand-name{font-size:14px;line-height:1}.brand-name small{display:block;margin-top:5px;color:#a7b2ab;font:9px var(--mono)}.nav-links{display:flex;align-items:center;gap:4px;flex:1}.nav-link{border:0;border-radius:6px;padding:10px 12px;background:transparent;color:#c1cbc4;font-size:12px}.nav-link:hover,.nav-link.active{background:#28352e;color:white}.wallet{display:flex;align-items:center;gap:9px;padding:7px 10px 7px 12px;border:1px solid #3b4941;border-radius:8px;white-space:nowrap}.wallet-label{display:block;color:#a7b2ab;font:9px var(--mono)}.wallet-value{display:block;margin-top:2px;color:var(--lime);font:14px var(--mono)}.wallet-icon{width:29px;height:29px;display:grid;place-items:center;border-radius:50%;background:#33453a;color:var(--lime)}.mobile-menu{display:none}main{width:min(1180px,calc(100% - 40px));margin:auto}.intro{display:flex;justify-content:space-between;align-items:end;gap:20px;padding:34px 0 21px;animation:rise .4s ease-out both}.eyebrow{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:var(--green);font:10px var(--mono);text-transform:uppercase}.eyebrow:before{content:"";width:20px;height:2px;background:var(--orange)}h1{margin:0;font-size:clamp(27px,4vw,38px);line-height:1.08}.intro-copy{max-width:370px;margin:0 0 3px;color:var(--muted);font-size:12px;line-height:1.6}.page{display:none;padding-bottom:45px}.page.active{display:block;animation:rise .25s ease-out both}.section-heading{display:flex;justify-content:space-between;align-items:end;gap:15px;margin:0 0 14px}.section-heading h2{margin:0;font-size:18px}.section-heading p{margin:5px 0 0;color:var(--muted);font-size:11px}.panel{overflow:hidden;border:1px solid var(--line);border-radius:9px;background:var(--white)}.drop-layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(275px,.85fr);gap:15px}.drop-stage{min-height:348px;position:relative;display:grid;grid-template-rows:auto 1fr auto;padding:19px 20px 17px;background:#1a2821;color:white;isolation:isolate}.drop-stage:before{content:"";position:absolute;z-index:-1;inset:0;opacity:.22;background-image:linear-gradient(30deg,transparent 48%,#96ba9b 49%,transparent 50%),linear-gradient(150deg,transparent 48%,#96ba9b 49%,transparent 50%);background-size:38px 66px;mask-image:linear-gradient(to bottom,black,transparent 86%)}.stage-top{display:flex;justify-content:space-between;align-items:start}.stage-title{margin:0;font-size:13px}.stage-subtitle{margin:4px 0 0;color:#a6b6aa;font:10px var(--mono)}.tag{padding:6px 8px;border:1px solid #65796a;border-radius:5px;color:var(--lime);font:9px var(--mono)}.case-art{align-self:center;justify-self:center;position:relative;width:190px;height:140px;display:grid;place-items:center;filter:drop-shadow(0 18px 16px #080d0ab0);transition:transform .25s}.case-art.opening{animation:shake .11s linear infinite}.crate{width:145px;height:92px;position:relative;border:2px solid #e8eddb;border-radius:8px;background:linear-gradient(140deg,#d3f36b 0 18%,#89ad52 18% 22%,#354c38 22% 75%,#213229 75%);transform:skewY(-4deg)}.crate:before{content:"";position:absolute;left:15px;right:15px;top:12px;height:8px;border-radius:8px;background:#f1f5d9;opacity:.84}.crate:after{content:"LF";position:absolute;inset:27px 0 auto;color:#eef4de;text-align:center;font:700 30px var(--sans)}.crate-side{position:absolute;right:7px;bottom:11px;width:24px;height:75px;background:#b0d456;transform:skewY(-31deg);border:2px solid #e8eddb;border-left:0;border-radius:0 6px 6px 0}.stage-controls{display:flex;align-items:center;justify-content:space-between;gap:11px}.case-picker{display:flex;gap:6px;flex-wrap:wrap}.case-choice{padding:8px 9px;border:1px solid #4a5a50;border-radius:6px;background:#23342a;color:#d0d8d1;font-size:10px}.case-choice.active{border-color:var(--lime);color:var(--lime)}.primary{min-height:41px;display:inline-flex;justify-content:center;align-items:center;gap:8px;padding:0 16px;border:0;border-radius:6px;background:var(--lime);color:#20291d;font-weight:700;font-size:11px;transition:transform .15s,filter .15s}.primary:hover:not(:disabled){transform:translateY(-2px);filter:brightness(1.04)}.primary:disabled{opacity:.48;cursor:not-allowed}.side-stack{display:grid;grid-template-rows:auto 1fr;gap:14px}.result-card{min-height:175px;padding:17px}.label{color:var(--muted);font:9px var(--mono);text-transform:uppercase}.result-placeholder{display:grid;min-height:112px;place-items:center;color:#a4ada5;text-align:center;font-size:11px}.result-placeholder strong{display:block;margin-bottom:5px;color:#819087;font-size:24px}.result-item{display:flex;align-items:center;gap:12px;min-height:112px}.item-gem{width:52px;height:52px;display:grid;place-items:center;flex:0 0 auto;border-radius:8px;background:#eaf0dd;color:var(--green);font-size:23px}.item-name{margin:0;font-size:13px}.item-tier{display:block;margin:4px 0;color:var(--muted);font:9px var(--mono);text-transform:uppercase}.item-value{color:var(--green);font:11px var(--mono)}.recent-panel{padding:16px}.recent-title{display:flex;justify-content:space-between;margin-bottom:11px;font-size:11px;font-weight:700}.recent-title span{color:var(--muted);font:9px var(--mono)}.history-list{display:grid;gap:8px;max-height:164px;overflow:auto}.history-row{display:flex;align-items:center;gap:8px;font-size:10px}.history-row span:last-child{margin-left:auto;color:var(--muted);font:9px var(--mono);white-space:nowrap}.history-dot{width:7px;height:7px;flex:0 0 auto;border-radius:50%;background:var(--orange)}.history-row.win .history-dot{background:#83b951}.empty-history{color:var(--muted);font-size:10px}.cases-section{margin-top:27px}.case-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}.case-card{min-height:127px;padding:15px;border:1px solid var(--line);border-radius:8px;background:var(--white);cursor:pointer;transition:transform .16s,border .16s}.case-card:hover,.case-card.selected{transform:translateY(-2px);border-color:#91ae78}.case-card.selected:after{content:"VYBRÁNO";float:right;color:var(--green);font:8px var(--mono)}.case-symbol{width:40px;height:40px;display:grid;place-items:center;margin-bottom:10px;border-radius:8px;background:#e5ebdd;font-size:19px}.case-card:nth-child(2) .case-symbol{background:#fbe4d8}.case-card:nth-child(3) .case-symbol{background:#dcebf0}.case-card strong{display:block;font-size:11px}.case-card small{display:block;margin-top:4px;color:var(--muted);font:9px var(--mono)}.odds-tag{padding:7px 9px;border-radius:5px;background:#edf1e8;color:var(--green);font:9px var(--mono);white-space:nowrap}.game-box{padding:20px}.game-head{display:flex;justify-content:space-between;align-items:start;gap:15px;padding-bottom:16px;border-bottom:1px solid var(--line)}.game-head h2{margin:0;font-size:18px}.game-head p{margin:5px 0 0;color:var(--muted);font-size:11px}.form-row{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:16px}.field{display:grid;gap:7px;color:var(--muted);font:9px var(--mono)}.field input,.field select{width:100%;height:41px;padding:0 11px;border:1px solid var(--line);border-radius:6px;outline:none;background:white;color:var(--ink);font:12px var(--sans)}.field input:focus,.field select:focus{border-color:#78956e;box-shadow:0 0 0 3px #d8e7cc}.full{grid-column:1/-1}.game-action{display:flex;align-items:center;gap:10px;margin-top:15px}.feedback{min-height:18px;color:var(--muted);font-size:10px}.roulette-board{display:flex;flex-wrap:wrap;justify-content:center;gap:7px;padding:24px 0}.roulette-number{width:43px;height:43px;display:grid;place-items:center;border:1px solid var(--line);border-radius:6px;background:white;font:11px var(--mono)}.roulette-number.red{background:#ffede7;border-color:#ffd0c2;color:#bd4b31}.roulette-number.black{background:#25302a;border-color:#25302a;color:white}.roulette-number.green{background:var(--lime);border-color:var(--lime)}.roulette-number.picked{outline:3px solid var(--orange);outline-offset:2px}.blackjack-table{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:19px 0 8px}.hand{min-height:112px;padding:12px;border:1px solid var(--line);border-radius:8px;background:#f9faf6}.hand-label{margin:0 0 13px;color:var(--muted);font:9px var(--mono);text-transform:uppercase}.cards{display:flex;gap:5px;min-height:42px;align-items:center}.playing-card{width:34px;height:43px;display:grid;place-items:center;border:1px solid #d8ddd6;border-radius:5px;background:white;box-shadow:0 2px 5px #14201810;font:11px var(--mono)}.playing-card.red-suit{color:#cc5941}.secondary{min-height:40px;padding:0 12px;border:1px solid var(--line);border-radius:6px;background:white;color:var(--ink);font-size:10px;font-weight:600}.secondary:disabled{opacity:.45;cursor:not-allowed}.upgrade-display{display:grid;grid-template-columns:1fr 32px 1fr;gap:5px}.upgrade-item{padding:8px 3px}.bonus-card{padding:18px}footer{flex-direction:column}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
/* The roulette is the only game shown on this page. */
.topline,#page-drop,#page-blackjack,#page-upgrade,#page-bonus,.intro,footer{display:none!important}
#page-roulette{display:block!important;animation:pageEnter .42s cubic-bezier(.2,.75,.25,1) both}
.nav-links,.mobile-menu{display:none!important}
.roulette-heading{display:flex;align-items:end;justify-content:space-between;gap:16px;margin:35px 0 20px}
.roulette-heading h1{margin:0;font-size:34px}
.roulette-heading p:last-child{margin:7px 0 0;color:var(--muted);font-size:13px}
.roulette-page{padding-bottom:35px}
.roulette-page .game-box{padding:22px}
.roulette-note{margin:14px 0;color:var(--muted);font-size:10px;text-align:center}
@media(max-width:560px){.roulette-heading{align-items:flex-start;flex-direction:column;margin-top:24px}.roulette-heading h1{font-size:29px}.roulette-page .game-box{padding:15px}}
</style></head><body>
<header><div class="nav"><a class="brand" href="#roulette"><span class="brand-mark">◉</span><span class="brand-name">LUCKY ROULETTE<small>EVROPSKÁ RULETA</small></span></a>
<nav class="nav-links" id="nav-links" aria-label="Herní sekce"><button class="nav-link active" data-page="drop">Drop</button><button class="nav-link" data-page="roulette">Ruleta</button><button class="nav-link" data-page="blackjack">Blackjack</button><button class="nav-link" data-page="upgrade">Upgrade</button><button class="nav-link" data-page="bonus">Bonusy</button></nav>
<div class="wallet" aria-live="polite"><span class="wallet-icon">◈</span><span><span class="wallet-label">TVŮJ ZŮSTATEK</span><strong class="wallet-value" id="balance">2 500 ž</strong></span></div><button class="mobile-menu" id="mobile-menu" aria-label="Otevřít navigaci" aria-expanded="false">☰</button></div></header>
<main><section class="intro"><div><p class="eyebrow">Herní klub · otevřeno nonstop</p><h1>Štěstí přeje odvážným.<br>Rozum tě dostane dál.</h1></div><p class="intro-copy">Otevírej bedny, zkus ruletu nebo si zahraj blackjack. Všechny hry používají jen virtuální žetony uložené v tomto počítači.</p></section>
<section class="page active" id="page-drop"><div class="section-heading"><div><h2>Drop room</h2><p>Vyber bednu, otevři ji a zjisti, co se ukrývá uvnitř.</p></div><span class="odds-tag">VÝHRY JSOU NÁHODNÉ</span></div>
<div class="drop-layout"><div class="panel drop-stage"><div class="stage-top"><div><h3 class="stage-title" id="selected-case-title">Greenhouse Case</h3><p class="stage-subtitle" id="selected-case-subtitle">Botanická kolekce · 100 ž</p></div><span class="tag">DROP / 01</span></div><div class="case-art" id="case-art" aria-hidden="true"><div class="crate"></div><div class="crate-side"></div></div><div class="stage-controls"><div class="case-picker" id="case-picker"></div><button class="primary" id="open-case">Otevřít bednu</button></div></div>
<div class="side-stack"><div class="panel result-card"><span class="label">POSLEDNÍ DROP</span><div id="last-drop" class="result-placeholder"><div><strong>◇</strong>Tvůj další nález se ukáže tady.</div></div></div><div class="panel recent-panel"><div class="recent-title">Tvoje poslední hry <span id="games-count">0 HER</span></div><div class="history-list" id="history-list"><p class="empty-history">Zatím tu nic není. První hra je na tobě.</p></div></div></div></div>
<div class="cases-section"><div class="section-heading"><div><h2>Kolekce beden</h2><p>Každá bedna má vlastní cenu i možné nálezy.</p></div></div><div class="case-grid" id="case-grid"></div></div></section>
<section class="page" id="page-roulette"><div class="section-heading"><div><h2>Evropská ruleta</h2><p>Jedna nula, třicet šest čísel. Vyber si barvu nebo konkrétní číslo.</p></div><span class="odds-tag">0–36 · 1:1 / 35:1</span></div><div class="panel game-box"><div class="game-head"><div><h2>Roztoč kolo</h2><p>Barva vyplácí 2×, přesné číslo 36× včetně vkladu.</p></div><span class="mono label">EUROPEAN WHEEL</span></div><div class="roulette-board" id="roulette-board" aria-label="Výsledek posledního kola"></div><div class="form-row"><label class="field">VIRTUÁLNÍ SÁZKA<input id="roulette-bet" type="number" min="1" value="100"></label><label class="field">TYP TIPU<select id="roulette-type"><option value="red">Červená · 2×</option><option value="black">Černá · 2×</option><option value="green">Zelená 0 · 36×</option><option value="number">Přesné číslo · 36×</option></select></label><label class="field full" id="roulette-number-wrap" hidden>ČÍSLO 0–36<input id="roulette-number" type="number" min="0" max="36" value="7"></label></div><div class="game-action"><button class="primary" id="spin-roulette">Roztočit ruletu ↗</button><span class="feedback" id="roulette-feedback" aria-live="polite">Sázky používají pouze virtuální žetony.</span></div></div></section>
<section class="page" id="page-blackjack"><div class="section-heading"><div><h2>Blackjack</h2><p>Dostaň se co nejblíž k 21. Eso má hodnotu 1 nebo 11.</p></div><span class="odds-tag">DEALER STOJÍ NA 17</span></div><div class="panel game-box"><div class="game-head"><div><h2>Stůl číslo jedna</h2><p>Blackjack platí 3:2. Remíza vrací celou sázku.</p></div><span class="mono label">21 TABLE</span></div><div class="blackjack-table"><div class="hand"><p class="hand-label">Dealer <span id="dealer-score"></span></p><div class="cards" id="dealer-cards"><span class="label">Čeká na rozdání</span></div></div><div class="hand"><p class="hand-label">Ty <span id="player-score"></span></p><div class="cards" id="player-cards"><span class="label">Zadej sázku a začni</span></div></div></div><div class="form-row"><label class="field">VIRTUÁLNÍ SÁZKA<input id="blackjack-bet" type="number" min="1" value="100"></label></div><div class="game-action"><button class="primary" id="deal-blackjack">Rozdat karty</button><button class="secondary" id="hit-blackjack" disabled>Další kartu</button><button class="secondary" id="stand-blackjack" disabled>Stát</button><span class="feedback" id="blackjack-feedback" aria-live="polite">Dealer rozdává po jedné kartě.</span></div></div></section>
<section class="page" id="page-upgrade"><div class="section-heading"><div><h2>Upgrade lab</h2><p>Riskni část žetonů a zkus je proměnit ve větší výhru.</p></div><span class="odds-tag">VÝŠE = NIŽŠÍ ŠANCE</span></div><div class="panel game-box"><div class="game-head"><div><h2>Vylepši svůj vklad</h2><p>Vyšší násobek znamená menší pravděpodobnost úspěchu.</p></div><span class="mono label">UPGRADE / 02</span></div><div class="upgrade-display"><div class="upgrade-item"><strong>◈ Vklad</strong><small id="upgrade-input-label">100 ž</small></div><div class="upgrade-arrow">→</div><div class="upgrade-item"><strong>✳ Cíl</strong><small id="upgrade-target-label">2× · šance 45 %</small></div></div><div class="form-row"><label class="field">VIRTUÁLNÍ VKLAD<input id="upgrade-bet" type="number" min="1" value="100"></label><label class="field">CÍLOVÝ NÁSOBEK<select id="upgrade-multiplier"><option value="1.5">1,5× · šance 60 %</option><option value="2" selected>2× · šance 45 %</option><option value="3">3× · šance 30 %</option><option value="5">5× · šance 18 %</option></select></label></div><div class="game-action"><button class="primary" id="run-upgrade">Zkusit upgrade ↗</button><span class="feedback" id="upgrade-feedback" aria-live="polite">Úspěch připíše násobek vkladu včetně něj.</span></div></div></section>
<section class="page" id="page-bonus"><div class="section-heading"><div><h2>Bonusy a promo kódy</h2><p>Malé virtuální přilepšení na další kolo.</p></div><span class="odds-tag">BEZ PENĚŽNÍ HODNOTY</span></div><div class="bonus-layout"><div class="bonus-card"><span class="tag">DENNÍ ODMĚNA</span><h2>Vrať se pro dalších 250 žetonů.</h2><p>Bonus je dostupný jednou denně. Žetony nelze koupit ani vybrat, slouží jen pro hraní v této ukázce.</p><button class="primary" id="daily-bonus">Vybrat denní bonus ↗</button></div><div class="panel promo-card"><h3>Máš promo kód?</h3><p>Zadej jeden z ukázkových kódů a přidej si virtuální žetony.</p><div class="promo-input"><input id="promo-code" placeholder="NAPŘ. START" aria-label="Promo kód"><button class="secondary" id="redeem-code">Použít</button></div><p class="feedback" id="promo-feedback" style="margin-top:9px" aria-live="polite"></p><p class="footnote">Demo kódy: <strong>START</strong> a <strong>DROP</strong>. Každý lze použít pouze jednou.</p></div></div><p class="footnote">Lucky Foundry je nekomerční herní ukázka. Nepřijímá vklady, nevyplácí výhry a nepoužívá skutečné peníze.</p></section>
<footer><span>LUCKY FOUNDRY · HRAJ PRO ZÁBAVU, NE PRO VÝDĚLEK</span><span class="mono">LOKÁLNÍ DEMO / 2026</span></footer></main><div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
let state=null,toastTimer;const $=id=>document.getElementById(id),fmt=n=>`${Math.floor(n).toLocaleString("cs-CZ")} ž`;
async function api(path,data){const response=await fetch(path,{method:data?"POST":"GET",headers:data?{"Content-Type":"application/json"}:{},body:data?JSON.stringify(data):undefined});const result=await response.json();if(!response.ok)throw Error(result.error||"Požadavek se nepodařil.");state=result.state;render();if(result.message)toast(result.message);return result}
function render(){if(state)$("balance").textContent=fmt(state.balance)}
function toast(message){const element=$("toast");element.textContent=message;element.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>element.classList.remove("show"),2400)}
function fail(error){toast(error.message)}
const ROULETTE_ORDER=[0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26];
const ROULETTE_REDS=new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
function renderRouletteWheel(winningNumber=null,reds=[...ROULETTE_REDS]){const board=$("roulette-board"),segment=360/ROULETTE_ORDER.length;const colorFor=number=>number===0?"green":reds.includes(number)?"red":"black";const gradients=ROULETTE_ORDER.map((number,index)=>`${number===0?"#198653":reds.includes(number)?"#c8443d":"#252a27"} ${index*segment}deg ${(index+1)*segment}deg`).join(",");board.innerHTML=`<div class="roulette-wheel" style="background:conic-gradient(${gradients})">${ROULETTE_ORDER.map((number,index)=>`<span class="roulette-pocket ${colorFor(number)} ${number===winningNumber?"winner":""}" data-number="${number}" style="--angle:${index*segment}deg">${number}</span>`).join("")}<span class="roulette-center">LR</span></div><span class="roulette-pointer" aria-hidden="true"></span>`;return board.querySelector(".roulette-wheel")}
renderRouletteWheel();
function updateNumberBetVisibility(){const visible=$("roulette-type").value==="number";$("roulette-number-wrap").hidden=!visible;$("roulette-number-wrap").style.display=visible?"grid":"none"}
$("roulette-type").onchange=updateNumberBetVisibility;
updateNumberBetVisibility();
async function animateRoulette(result){const wheel=renderRouletteWheel(null,result.reds),index=ROULETTE_ORDER.indexOf(result.number),rotation=360*5-index*360/ROULETTE_ORDER.length;const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;wheel.style.transition=reduced?"none":"";wheel.style.transform="rotate(0deg)";void wheel.offsetWidth;if(reduced){wheel.style.transform=`rotate(${rotation}deg)`}else{await new Promise(resolve=>{let timer;const finish=()=>{clearTimeout(timer);resolve()};wheel.addEventListener("transitionend",finish,{once:true});timer=setTimeout(finish,6200);wheel.style.transform=`rotate(${rotation}deg)`})}wheel.querySelector(`[data-number="${result.number}"]`).classList.add("winner")}
$("spin-roulette").onclick=async()=>{const button=$("spin-roulette");button.disabled=true;try{const result=await api("/api/roulette",{bet:Number($("roulette-bet").value),choice:$("roulette-type").value,number:Number($("roulette-number").value)});await animateRoulette(result);$("roulette-feedback").textContent=`Padlo ${result.number} · ${result.color}. ${result.won?`Výhra ${fmt(result.payout)}.`:"Tentokrát bez výhry."}`}catch(error){fail(error)}finally{button.disabled=false}};
api("/api/state").catch(fail);
</script></body></html>'''


PAGE = r'''<!doctype html>
<html lang="cs"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#15201a">
<title>Ruleta | Evropské kolo</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{color-scheme:light;--ink:#18211d;--muted:#718078;--paper:#eef1e9;--white:#fffefa;--line:#d9dfd7;--green:#294b3d;--lime:#d3f36b;--red:#c8443d;--black:#252a27;--gold:#c2a44b;--mono:"DM Mono",Consolas,monospace;--sans:"Space Grotesk","Segoe UI",sans-serif}*{box-sizing:border-box}body{min-height:100vh;margin:0;background:radial-gradient(ellipse at 50% 48%,#ffffff 0,#eef1e9 64%);color:var(--ink);font-family:var(--sans)}button,input,select{font:inherit}button{cursor:pointer}header{background:#151d18;color:#fff;border-bottom:1px solid #37453c}.nav{width:min(1040px,calc(100% - 36px));min-height:70px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{display:flex;align-items:center;gap:10px;color:#fff;text-decoration:none;font-weight:700}.brand-mark{width:34px;height:34px;display:grid;place-items:center;border:2px solid var(--gold);border-radius:50%;color:var(--lime);font-size:20px}.brand-name{font-size:14px}.brand-name small{display:block;margin-top:3px;color:#a7b2ab;font:9px var(--mono)}.wallet{display:flex;align-items:center;gap:9px;padding:7px 11px;border:1px solid #435047;border-radius:7px}.wallet-label{display:block;color:#a7b2ab;font:9px var(--mono)}.wallet-value{display:block;margin-top:2px;color:var(--lime);font:14px var(--mono)}.wallet-icon{color:var(--gold)}main{width:min(920px,calc(100% - 28px));margin:auto}.heading{display:flex;align-items:end;justify-content:space-between;gap:14px;margin:32px 0 17px}.eyebrow{margin:0 0 7px;color:var(--green);font:10px var(--mono)}h1{margin:0;font-size:32px;line-height:1.1}.heading-copy{margin:6px 0 0;color:var(--muted);font-size:12px}.odds{padding:7px 9px;border-radius:5px;background:#e2e9d9;color:var(--green);font:9px var(--mono);white-space:nowrap}.table{padding:18px;border:1px solid var(--line);border-radius:9px;background:var(--white);box-shadow:0 8px 28px #18211d0b}.table-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:13px;border-bottom:1px solid var(--line)}.table-head h2{margin:0;font-size:17px}.table-head p{margin:4px 0 0;color:var(--muted);font-size:11px}.wheel-wrap{display:grid;place-items:center;padding:15px 0 11px}.roulette-board{position:relative;display:grid;grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,1fr);place-items:center;width:min(100%,310px);aspect-ratio:1;margin:0 auto;padding:0}.roulette-wheel{position:relative;width:100%;height:100%;border:10px solid var(--gold);border-radius:50%;box-shadow:0 0 0 3px #332915,0 12px 26px #16201830,inset 0 0 0 3px #e8d28b;transform:rotate(0);transition:transform 5.4s cubic-bezier(.08,.82,.12,1);will-change:transform}.roulette-wheel:before{content:"";position:absolute;inset:7px;border:1px solid #e8d28b99;border-radius:50%;pointer-events:none}.roulette-pocket{position:absolute;top:50%;left:50%;width:22px;height:26px;display:flex;justify-content:center;align-items:flex-start;padding-top:2px;border:1px solid #d7c38366;color:#fff;font:9px var(--mono);transform:translate(-50%,-50%) rotate(var(--angle)) translateY(-115px);transform-origin:center}.roulette-pocket.red{background:var(--red)}.roulette-pocket.black{background:var(--black)}.roulette-pocket.green{background:#198653;font-weight:700}.roulette-pocket.winner{z-index:2;outline:2px solid var(--lime);outline-offset:2px;box-shadow:0 0 12px #d3f36bcc}.roulette-center{position:absolute;top:50%;left:50%;width:70px;height:70px;display:grid;place-items:center;border:4px solid #b39443;border-radius:50%;background:radial-gradient(circle at 38% 32%,#4a6552,#1e2c23 70%);box-shadow:0 0 0 4px #19241d;color:var(--lime);font:700 14px var(--mono);transform:translate(-50%,-50%)}.roulette-pointer{position:absolute;z-index:3;top:8px;left:50%;width:0;height:0;border-right:11px solid transparent;border-left:11px solid transparent;border-top:22px solid var(--lime);filter:drop-shadow(0 2px 3px #101710aa);transform:translateX(-50%)}.form{display:grid;grid-template-columns:1fr 1.3fr;gap:10px;margin-top:7px}.field{display:grid;gap:6px;color:var(--muted);font:9px var(--mono)}.field input,.field select{width:100%;height:41px;padding:0 11px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink);font:12px var(--sans)}.field input:focus,.field select:focus{outline:2px solid #d3f36b;outline-offset:1px}.full{grid-column:1/-1}[hidden]{display:none!important}.action{display:flex;align-items:center;gap:12px;margin-top:12px}.spin{min-height:42px;padding:0 17px;border:0;border-radius:6px;background:var(--lime);color:#20291d;font-size:12px;font-weight:700;transition:transform .16s}.spin:hover:not(:disabled){transform:translateY(-2px)}.spin:disabled{opacity:.5;cursor:wait}.feedback{color:var(--muted);font-size:11px}.note{margin:12px 0 24px;color:var(--muted);font-size:10px;text-align:center}.toast{position:fixed;right:16px;bottom:16px;padding:11px 14px;border-radius:6px;background:#18211d;color:#fff;font-size:11px;opacity:0;pointer-events:none;transition:opacity .2s}.toast.show{opacity:1}@media(max-width:560px){.nav{min-height:62px}.heading{align-items:flex-start;flex-direction:column;margin-top:22px}h1{font-size:28px}.table{padding:13px}.roulette-board{width:min(100%,276px)}.roulette-pocket{width:20px;height:24px;font-size:8px;transform:translate(-50%,-50%) rotate(var(--angle)) translateY(-101px)}.roulette-center{width:62px;height:62px;font-size:12px}.roulette-pointer{top:3px}.form{grid-template-columns:1fr}.full{grid-column:auto}.action{align-items:flex-start;flex-direction:column}.spin{width:100%}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.01ms!important;animation-duration:.01ms!important}}
</style></head><body>
<header><div class="nav"><a class="brand" href="#roulette"><span class="brand-mark">◉</span><span class="brand-name">RULETA<small>EVROPSKÉ KOLO</small></span></a><div class="wallet" aria-live="polite"><span class="wallet-icon">◈</span><span><span class="wallet-label">ZŮSTATEK</span><strong class="wallet-value" id="balance">2 500 ž</strong></span></div></div></header>
<main id="roulette"><div class="heading"><div><p class="eyebrow">EVROPSKÁ RULETA · 37 ČÍSEL</p><h1>Roztoč kolo.</h1><p class="heading-copy">Vyber sázku a nech rozhodnout výsledek.</p></div><span class="odds">ČERVENÁ / ČERNÁ · 2× &nbsp; ČÍSLO · 36×</span></div>
<section class="table"><div class="table-head"><div><h2>Evropské kolo</h2><p>Nula je zelená. Sázky jsou pouze virtuální.</p></div><span class="eyebrow">EUROPEAN WHEEL</span></div><div class="wheel-wrap"><div class="roulette-board" id="roulette-board" aria-label="Evropské ruletové kolo"></div></div>
<div class="form"><label class="field">SÁZKA V ŽETONECH<input id="roulette-bet" type="number" min="1" value="100" inputmode="numeric"></label><label class="field">TYP SÁZKY<select id="roulette-type"><option value="red">Červená · 2×</option><option value="black">Černá · 2×</option><option value="green">Zelená 0 · 36×</option><option value="number">Přesné číslo · 36×</option></select></label><label class="field full" id="roulette-number-wrap" hidden>VYBER ČÍSLO 0–36<input id="roulette-number" type="number" min="0" max="36" value="7" inputmode="numeric"></label></div>
<div class="action"><button class="spin" id="spin-roulette">Roztočit ruletu <span aria-hidden="true">↗</span></button><span class="feedback" id="roulette-feedback" aria-live="polite">Zadej sázku a roztoč evropské kolo.</span></div></section><p class="note">Demo kasino · virtuální žetony bez vkladů a výběrů</p></main><div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
let state=null,toastTimer;const $=id=>document.getElementById(id),fmt=n=>`${Math.floor(n).toLocaleString("cs-CZ")} ž`;
async function api(path,data){const response=await fetch(path,{method:data?"POST":"GET",headers:data?{"Content-Type":"application/json"}:{},body:data?JSON.stringify(data):undefined});const result=await response.json();if(!response.ok)throw Error(result.error||"Požadavek se nepodařil.");state=result.state;render();if(result.message)toast(result.message);return result}
function render(){if(state)$("balance").textContent=fmt(state.balance)}
function toast(message){const element=$("toast");element.textContent=message;element.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>element.classList.remove("show"),2400)}
function fail(error){toast(error.message)}
const ROULETTE_ORDER=[0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26];
const ROULETTE_REDS=new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
function renderRouletteWheel(winningNumber=null,reds=[...ROULETTE_REDS]){const board=$("roulette-board"),segment=360/ROULETTE_ORDER.length;const colorFor=number=>number===0?"green":reds.includes(number)?"red":"black";const gradients=ROULETTE_ORDER.map((number,index)=>`${number===0?"#198653":reds.includes(number)?"#c8443d":"#252a27"} ${index*segment}deg ${(index+1)*segment}deg`).join(",");board.innerHTML=`<div class="roulette-wheel" style="background:conic-gradient(${gradients})">${ROULETTE_ORDER.map((number,index)=>`<span class="roulette-pocket ${colorFor(number)} ${number===winningNumber?"winner":""}" data-number="${number}" style="--angle:${index*segment}deg">${number}</span>`).join("")}<span class="roulette-center">R</span></div><span class="roulette-pointer" aria-hidden="true"></span>`;return board.querySelector(".roulette-wheel")}
renderRouletteWheel();
function updateNumberBetVisibility(){const visible=$("roulette-type").value==="number";$("roulette-number-wrap").hidden=!visible;$("roulette-number-wrap").style.display=visible?"grid":"none"}
$("roulette-type").onchange=updateNumberBetVisibility;updateNumberBetVisibility();
async function animateRoulette(result){const wheel=renderRouletteWheel(null,result.reds),index=ROULETTE_ORDER.indexOf(result.number),rotation=360*5-index*360/ROULETTE_ORDER.length;const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;wheel.style.transition=reduced?"none":"";wheel.style.transform="rotate(0deg)";void wheel.offsetWidth;if(reduced){wheel.style.transform=`rotate(${rotation}deg)`}else{await new Promise(resolve=>{let timer;const finish=()=>{clearTimeout(timer);resolve()};wheel.addEventListener("transitionend",finish,{once:true});timer=setTimeout(finish,6200);wheel.style.transform=`rotate(${rotation}deg)`})}wheel.querySelector(`[data-number="${result.number}"]`).classList.add("winner")}
$("spin-roulette").onclick=async()=>{const button=$("spin-roulette");button.disabled=true;try{const result=await api("/api/roulette",{bet:Number($("roulette-bet").value),choice:$("roulette-type").value,number:Number($("roulette-number").value)});await animateRoulette(result);$("roulette-feedback").textContent=`Padlo ${result.number} · ${result.color}. ${result.won?`Výhra ${fmt(result.payout)}.`:"Tentokrát bez výhry."}`}catch(error){fail(error)}finally{button.disabled=false}};
api("/api/state").catch(fail);
</script></body></html>'''


def new_state():
	return {
		"balance": STARTING_BALANCE,
		"games": 0,
		"wins": 0,
		"history": [],
	}


def load_state():
	try:
		state = new_state()
		stored = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
		if isinstance(stored, dict):
			state.update(stored)
		if isinstance(state["balance"], bool) or not isinstance(state["balance"], int) or state["balance"] < 0:
			raise ValueError("Neplatný zůstatek")
		if not isinstance(state["history"], list):
			state["history"] = []
		if isinstance(state["games"], bool) or not isinstance(state["games"], int):
			state["games"] = 0
		if isinstance(state["wins"], bool) or not isinstance(state["wins"], int):
			state["wins"] = 0
		return state
	except (OSError, json.JSONDecodeError, ValueError, TypeError):
		return new_state()


def save_state(state):
	temporary = SAVE_FILE.with_suffix(".tmp")
	temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
	temporary.replace(SAVE_FILE)


def validate_bet(state, value):
	if isinstance(value, bool) or not isinstance(value, int) or value < 1:
		raise ValueError("Sázka musí být kladné celé číslo.")
	if value > state["balance"]:
		raise ValueError("Na tak vysokou sázku nemáš dost žetonů.")
	return value


def roulette_wins(number, choice, selection):
	if choice == "number":
		return number == selection
	if choice == "green":
		return number == 0
	if number == 0:
		return False
	if choice == "red":
		return number in RED_NUMBERS
	if choice == "black":
		return number not in RED_NUMBERS
	return False


def process_roulette(state, data):
	bet = validate_bet(state, data.get("bet"))
	choice = data.get("choice")
	if choice not in {"red", "black", "green", "number"}:
		raise ValueError("Vyber platný typ sázky.")
	number_choice = data.get("number")
	if choice == "number" and (isinstance(number_choice, bool) or not isinstance(number_choice, int) or not 0 <= number_choice <= 36):
		raise ValueError("Číslo musí být od 0 do 36.")
	number = RNG.randint(0, 36)
	color = "zelená" if number == 0 else "červená" if number in RED_NUMBERS else "černá"
	won = roulette_wins(number, choice, number_choice)
	payout = bet * (36 if choice in {"green", "number"} else 2) if won else 0
	state["balance"] -= bet
	state["balance"] += payout
	state["games"] += 1
	if payout > bet:
		state["wins"] += 1
	state["history"].insert(0, {"label": f"Ruleta · {number}", "net": payout - bet, "time": datetime.now().strftime("%H:%M")})
	del state["history"][8:]
	return {"number": number, "color": color, "won": won, "payout": payout, "reds": sorted(RED_NUMBERS), "message": f"Ruleta: {number} · {color}."}


class RouletteHandler(BaseHTTPRequestHandler):
	def log_message(self, _format, *_args):
		return

	def send_json(self, payload, status=200):
		body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.send_header("Cache-Control", "no-store")
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self):
		if urlsplit(self.path).path == "/":
			body = PAGE.encode("utf-8")
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=utf-8")
			self.send_header("Content-Length", str(len(body)))
			self.send_header("Cache-Control", "no-store")
			self.end_headers()
			self.wfile.write(body)
		elif urlsplit(self.path).path == "/api/state":
			with STATE_LOCK:
				self.send_json({"state": load_state()})
		else:
			self.send_json({"error": "Stránka nebyla nalezena."}, 404)

	def do_POST(self):
		if urlsplit(self.path).path != "/api/roulette":
			self.send_json({"error": "Akce nebyla nalezena."}, 404)
			return
		try:
			length = int(self.headers.get("Content-Length", "0"))
			if not 0 < length <= 4096:
				raise ValueError("Neplatná velikost požadavku.")
			data = json.loads(self.rfile.read(length))
			if not isinstance(data, dict):
				raise ValueError("Neplatný požadavek.")
			with STATE_LOCK:
				state = load_state()
				result = process_roulette(state, data)
				save_state(state)
			self.send_json({**result, "state": state})
		except (ValueError, json.JSONDecodeError) as error:
			self.send_json({"error": str(error)}, 400)
		except OSError:
			self.send_json({"error": "Zůstatek se nepodařilo uložit."}, 500)


class RouletteTests(unittest.TestCase):
	def test_colors_and_zero(self):
		self.assertTrue(roulette_wins(1, "red", None))
		self.assertTrue(roulette_wins(2, "black", None))
		self.assertTrue(roulette_wins(0, "green", None))
		self.assertFalse(roulette_wins(0, "red", None))

	def test_exact_number_and_payouts(self):
		self.assertTrue(roulette_wins(17, "number", 17))
		self.assertFalse(roulette_wins(17, "number", 18))
		self.assertEqual(36 * 10, 360)
		self.assertEqual(2 * 10, 20)

	def test_bet_validation(self):
		state = new_state()
		with self.assertRaises(ValueError):
			validate_bet(state, state["balance"] + 1)
		with self.assertRaises(ValueError):
			validate_bet(state, True)


def main():
	import argparse
	import webbrowser

	parser = argparse.ArgumentParser(description="Lokální evropská ruleta s virtuálními žetony")
	parser.add_argument("--port", type=int, default=PORT, help="port webového serveru (výchozí 8765)")
	parser.add_argument("--test", action="store_true", help="spustit rychlé testy rulety")
	args = parser.parse_args()
	if args.test:
		unittest.main(argv=["casino.py"], verbosity=2)
		return
	server = ThreadingHTTPServer((HOST, args.port), RouletteHandler)
	url = f"http://{HOST}:{args.port}"
	print(f"Lucky Roulette běží na {url}")
	print("Ukončíš ho stiskem Ctrl+C. Hraje se pouze o virtuální žetony.")
	try:
		webbrowser.open(url)
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nRuleta ukončena.")
	finally:
		server.server_close()


if __name__ == "__main__":
	main()
