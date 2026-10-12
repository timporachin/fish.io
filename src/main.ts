import './style.css';
import {createState, stepState, FixedClock, SIMULATION_TICK_SECONDS} from './simulation';
import {createUnderwater} from './rendering/underwater';
document.querySelector<HTMLDivElement>('#app')!.innerHTML=`<canvas aria-label="Underwater habitat"></canvas><header><div><h1>FISH.IO</h1><small>UNDERWATER WORLDS</small></div><div class="habitat"><strong>Coral bay</strong><small>HABITAT 01</small></div></header><section class="caption"><small>THE BEGINNING</small><h2>A world below.</h2><p>Your first habitat is taking shape.<br>Species arrive with the next milestone.</p></section><nav aria-label="Habitat controls"><button id="pause" aria-pressed="false">Pause</button><button id="showroom">Species showroom</button><span id="status" role="status">Preparing habitat</span></nav><dialog><small>SPECIES SHOWROOM</small><h2>A living collection.</h2><p>No species are available yet. Realistic fish assets will be introduced after the C1 modeling milestone is approved.</p><button id="close">Return to habitat</button></dialog><div id="rotate"><div><h2>Explore in landscape</h2><p>Rotate your phone for the underwater view.</p></div></div><p id="error" role="alert" hidden></p>`;
const canvas=document.querySelector('canvas')!;
const status=document.querySelector<HTMLElement>('#status')!;
let paused=false;
let state=createState(42); const clock=new FixedClock();
const pause=document.querySelector<HTMLButtonElement>('#pause')!;
pause.onclick=()=>{paused=!paused;if(paused)clock.pause();else clock.resume();pause.textContent=paused?'Resume':'Pause';pause.setAttribute('aria-pressed',String(paused));};
const dialog=document.querySelector('dialog')!;
document.querySelector<HTMLButtonElement>('#showroom')!.onclick=()=>dialog.showModal();
document.querySelector<HTMLButtonElement>('#close')!.onclick=()=>dialog.close();
try{
 const world=createUnderwater(canvas); let previous=performance.now();
 document.addEventListener('visibilitychange',()=>{previous=performance.now();if(document.hidden)clock.pause();else if(!paused)clock.resume();});
 function frame(now:number){const dt=Math.max(0,Math.min((now-previous)/1000,.25));previous=now;clock.advance(dt,()=>{state=stepState(state);});canvas.dataset.tick=String(state.tick);world.render(matchMedia('(prefers-reduced-motion: reduce)').matches?0:state.tick*SIMULATION_TICK_SECONDS);status.textContent=paused?'Habitat paused':'Coral bay · C0';requestAnimationFrame(frame);}requestAnimationFrame(frame);
 window.addEventListener('pagehide',event=>{if(!event.persisted)world.dispose();});
}catch(error){const alert=document.querySelector<HTMLElement>('#error')!;alert.hidden=false;alert.textContent='The underwater view requires WebGL2. Please use a supported browser.';canvas.dataset.status='unavailable';console.error(error);}
