/* Jyotish engine: sidereal (Lahiri) chart, Parashari layer, rule matching. Needs global Astronomy. */
const J = (() => {
const SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGN_LORDS=["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"];
const NAKS=["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"];
const DASHA=[["Ketu",7],["Venus",20],["Sun",6],["Moon",10],["Mars",7],["Rahu",18],["Jupiter",16],["Saturn",19],["Mercury",17]];
const YEAR=365.25*86400000;
const EXALT={Sun:0,Moon:1,Mars:9,Mercury:5,Jupiter:3,Venus:11,Saturn:6,Rahu:1,Ketu:7};
const OWN={Sun:[4],Moon:[3],Mars:[0,7],Mercury:[2,5],Jupiter:[8,11],Venus:[1,6],Saturn:[9,10],Rahu:[],Ketu:[]};
const MT={Sun:[4,0,20],Moon:[1,3,30],Mars:[0,0,12],Mercury:[5,15,20],Jupiter:[8,0,10],Venus:[6,0,15],Saturn:[10,0,20]};
const SEVEN=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"];
const D2R=Math.PI/180, norm=x=>((x%360)+360)%360;

function dignity(name,sign,lon){
  if(EXALT[name]===sign)return"exalted";
  if(name in EXALT&&(EXALT[name]+6)%12===sign)return"debilitated";
  const m=MT[name]; if(m&&Math.floor(lon/30)===m[0]&&lon%30>=m[1]&&lon%30<m[2])return"moolatrikona";
  if((OWN[name]||[]).includes(sign))return"own sign";
  return"";
}
// Lahiri ayanamsa (mean), cubic fit to Swiss Ephemeris SIDM_LAHIRI 1700-2200 (error < 0.01").
function ayanamsaMean(T){return 23.857092360735482+1.3968879247565578*T+0.0003070808099396047*T*T+1.586904157710585e-08*T*T*T}
function nutation(T){ // main IAU1980 terms, degrees
  const Om=(125.04452-1934.136261*T)*D2R, L=(280.4665+36000.7698*T)*D2R, Lp=(218.3165+481267.8813*T)*D2R;
  const dpsi=(-17.20*Math.sin(Om)-1.32*Math.sin(2*L)-0.23*Math.sin(2*Lp)+0.21*Math.sin(2*Om))/3600;
  const deps=(9.20*Math.cos(Om)+0.57*Math.cos(2*L)+0.10*Math.cos(2*Lp)-0.09*Math.cos(2*Om))/3600;
  return{dpsi,deps};
}
const BODIES={Sun:"Sun",Mercury:"Mercury",Venus:"Venus",Mars:"Mars",Jupiter:"Jupiter",Saturn:"Saturn"};
function tropical(name,date){
  const t=Astronomy.MakeTime(date);
  if(name==="Moon")return Astronomy.EclipticGeoMoon(t).lon;
  return Astronomy.Ecliptic(Astronomy.GeoVector(Astronomy.Body[BODIES[name]],t,true)).elon;
}
function meanNode(T){return norm(125.04452-1934.136261*T+0.0020708*T*T+T*T*T/450000)}

function placement(name,lon,lagnaSign,retro){
  const sign=Math.floor(lon/30), span=360/27, ni=Math.floor(lon/span);
  return{name,longitude:+lon.toFixed(4),sign:SIGNS[sign],sign_index:sign,degree_in_sign:+(lon%30).toFixed(2),
    house:((sign-lagnaSign+12)%12)+1,nakshatra:NAKS[ni],pada:Math.floor((lon%span)/(span/4))+1,nakshatra_lord:DASHA[ni%9][0],
    retrograde:!!retro,dignity:name==="Lagna"?"":dignity(name,sign,lon),navamsa_sign:SIGNS[Math.floor(lon/(30/9))%12],
    lord_of_houses:SIGN_LORDS.map((l,s)=>l===name?((s-lagnaSign+12)%12)+1:0).filter(Boolean).sort((a,b)=>a-b)};
}
function iso(d){return d.toISOString().slice(0,10)}
function vimshottari(moonLon,birth){
  const span=360/27, idx=Math.floor(moonLon/span), si=idx%9, frac=(moonLon%span)/span;
  let t=new Date(birth.getTime()-frac*DASHA[si][1]*YEAR); const out=[];
  for(let k=0;k<9;k++){const[ml,my]=DASHA[(si+k)%9];const end=new Date(t.getTime()+my*YEAR);const ads=[];let at=t;
    for(let j=0;j<9;j++){const[al,ay]=DASHA[(si+k+j)%9];const ae=new Date(at.getTime()+my*ay/120*YEAR);ads.push({lord:al,start:iso(at),end:iso(ae)});at=ae}
    out.push({lord:ml,start:iso(t),end:iso(end),antardashas:ads});t=end}
  return out;
}
function computeChart({name,date,time,utc_offset,latitude,longitude,place}){
  const [Y,M,D]=date.split("-").map(Number),[h,mi]=time.split(":").map(Number);
  const utc=new Date(Date.UTC(Y,M-1,D,h,mi)-utc_offset*3600000);
  if(Y<100)utc.setUTCFullYear(Y);
  const T=(Astronomy.MakeTime(utc).tt)/36525;
  const nut=nutation(T), ayanT=ayanamsaMean(T)+nut.dpsi;
  // Ascendant
  const gast=Astronomy.SiderealTime(utc)*15, ramc=norm(gast+longitude)*D2R;
  const eps=(23.439291-0.0130042*T+nut.deps)*D2R, phi=latitude*D2R;
  const ascTrop=norm(Math.atan2(Math.cos(ramc),-(Math.sin(ramc)*Math.cos(eps)+Math.tan(phi)*Math.sin(eps)))/D2R);
  const asc=norm(ascTrop-ayanT), ls=Math.floor(asc/30);
  const lagna=placement("Lagna",asc,ls,false);
  const planets=[];
  for(const n of ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]){
    const lon=norm(tropical(n,utc)-ayanT);
    const a=tropical(n,new Date(utc.getTime()-43200000)),b=tropical(n,new Date(utc.getTime()+43200000));
    const speed=((b-a+540)%360)-180;
    planets.push(placement(n,lon,ls,speed<0));
  }
  const rahu=norm(meanNode(T)-ayanamsaMean(T));
  planets.push(placement("Rahu",rahu,ls,true),placement("Ketu",norm(rahu+180),ls,true));
  const moon=planets.find(p=>p.name==="Moon");
  return{name,place:place||"",birth_local:`${date}T${time}`,utc_offset,latitude,longitude,ayanamsa:+ayanT.toFixed(4),lagna,planets,dashas:vimshottari(moon.longitude,utc)};
}
function currentDasha(c,on){on=on||iso(new Date());
  for(const md of c.dashas)if(md.start<=on&&on<md.end){for(const ad of md.antardashas)if(ad.start<=on&&on<ad.end)return[md.lord,ad.lord];return[md.lord,""]}
  return["",""];}

/* ---------- Parashari layer ---------- */
const SPECIAL={Mars:[4,7,8],Jupiter:[5,7,9],Saturn:[3,7,10]}; let NODE_ASPECTS=[7];
const KENDRA=[1,4,7,10],TRIKONA=[1,5,9],DUSTHANA=[6,8,12],NAT_BEN=["Jupiter","Venus","Mercury","Moon"];
const MAHA={Mars:"Ruchaka",Mercury:"Bhadra",Jupiter:"Hamsa",Venus:"Malavya",Saturn:"Sasa"};
const P=c=>Object.fromEntries(c.planets.map(p=>[p.name,p]));
const lordOf=(c,h)=>SIGN_LORDS[(c.lagna.sign_index+h-1)%12];
function aspectHouses(pl,h){return(["Rahu","Ketu"].includes(pl)?NODE_ASPECTS:(SPECIAL[pl]||[7])).map(o=>((h+o-2)%12)+1).sort((a,b)=>a-b)}
function aspects(c){const out=[];for(const p of c.planets)for(const h of aspectHouses(p.name,p.house))out.push({planet:p.name,house:h,planets:c.planets.filter(q=>q.house===h&&q.name!==p.name).map(q=>q.name)});return out}
const aspectsBetween=(c,a,b)=>{const p=P(c);return aspectHouses(a,p[a].house).includes(p[b].house)};
function functionalNature(c){const out={};
  for(const n of SEVEN){const owned=[];for(let h=1;h<=12;h++)if(lordOf(c,h)===n)owned.push(h);
    const has=s=>owned.some(h=>s.includes(h));
    const kendra=has([4,7,10]),tri=has(TRIKONA),bad=has([3,6,11]),eighth=owned.includes(8)&&!owned.includes(1)&&!["Sun","Moon"].includes(n);
    out[n]=kendra&&has([5,9])?"yogakaraka":tri&&!bad&&!eighth?"functional benefic":(bad||eighth)&&!tri?"functional malefic":tri?"mixed":kendra&&NAT_BEN.includes(n)?"neutral (kendradhipati dosha)":"neutral"}
  return out}
function yogas(c){const p=P(c),mh=p.Moon.house,found=[],add=(name,description,planets)=>found.push({name,description,planets});
  const fm=h=>((h-mh+12)%12)+1;
  for(const[pl,y]of Object.entries(MAHA)){const q=p[pl];if(KENDRA.includes(q.house)&&["own sign","exalted","moolatrikona"].includes(q.dignity))add(`${y} yoga`,`${pl} ${q.dignity} in house ${q.house} (a kendra)`,[pl])}
  if(KENDRA.includes(fm(p.Jupiter.house)))add("Gajakesari yoga",`Jupiter in house ${fm(p.Jupiter.house)} from the Moon`,["Jupiter","Moon"]);
  if(p.Sun.sign===p.Mercury.sign)add("Budhaditya yoga",`Sun and Mercury together in ${p.Sun.sign}`,["Sun","Mercury"]);
  if(p.Moon.sign===p.Mars.sign)add("Chandra-Mangala yoga",`Moon and Mars together in ${p.Moon.sign}`,["Moon","Mars"]);
  const seen=new Set();
  for(const a of SEVEN){const b=SIGN_LORDS[p[a].sign_index];if(b!==a&&SEVEN.includes(b)&&SIGN_LORDS[p[b].sign_index]===a&&!seen.has(b+a)){seen.add(a+b);
    add("Parivartana yoga",`${a} and ${b} exchange signs (${p[a].sign} / ${p[b].sign}), linking houses ${p[a].house} and ${p[b].house}`,[a,b])}}
  const L={};for(let h=1;h<=12;h++)L[h]=lordOf(c,h);const pairs=new Set();
  for(const k of KENDRA)for(const t of TRIKONA){const a=L[k],b=L[t];if(a===b||k===t)continue;const key=[a,b].sort().join();if(pairs.has(key))continue;
    let how=null;if(p[a].sign===p[b].sign)how=`together in house ${p[a].house}`;else if(aspectsBetween(c,a,b)&&aspectsBetween(c,b,a))how="in mutual aspect";
    else if(SIGN_LORDS[p[a].sign_index]===b&&SIGN_LORDS[p[b].sign_index]===a)how="exchanging signs";
    if(how){pairs.add(key);add("Raja yoga",`${a} (lord of ${k}) and ${b} (lord of ${t}) ${how}`,[a,b])}}
  for(const[n,v]of Object.entries(functionalNature(c)))if(v==="yogakaraka")add("Yogakaraka",`${n} owns both a kendra and a trikona for ${c.lagna.sign} lagna (placed in house ${p[n].house})`,[n]);
  for(const w of[2,11])for(const t of[5,9]){const a=L[w],b=L[t];if(a!==b&&p[a].sign===p[b].sign)add("Dhana yoga",`${a} (lord of ${w}) with ${b} (lord of ${t}) in house ${p[a].house}`,[a,b])}
  for(const[h,y]of[[6,"Harsha"],[8,"Sarala"],[12,"Vimala"]]){const l=L[h];if(DUSTHANA.includes(p[l].house)&&L[1]!==l)add(`Vipareeta Raja yoga (${y})`,`${l}, lord of ${h}, sits in house ${p[l].house}`,[l])}
  for(const pl of SEVEN){const q=p[pl];if(q.dignity!=="debilitated")continue;const ex=(q.sign_index+6)%12;
    for(const hlp of new Set([SIGN_LORDS[q.sign_index],SIGN_LORDS[ex]])){const hp=p[hlp];if(KENDRA.includes(hp.house)||KENDRA.includes(fm(hp.house))){
      add("Neecha Bhanga",`${pl} debilitated in ${q.sign}, but ${hlp} (lord of ${hlp===SIGN_LORDS[q.sign_index]?SIGNS[q.sign_index]:SIGNS[ex]}) is in a kendra from the lagna or Moon`,[pl,hlp]);break}}}
  if(!SEVEN.filter(q=>!["Sun","Moon"].includes(q)).some(q=>[2,12].includes(fm(p[q].house))))add("Kemadruma yoga","No planet in the 2nd or 12th from the Moon (check cancellations)",["Moon"]);
  return found}

function factors(c){const t=new Set([`lagna:${c.lagna.sign.toLowerCase()}`,`${c.lagna.sign.toLowerCase()} lagna`]);
  for(const p of c.planets){const n=p.name.toLowerCase();[`${n} in house ${p.house}`,`${n} in ${p.sign.toLowerCase()}`,`${n} in ${p.nakshatra.toLowerCase()}`].forEach(x=>t.add(x));
    if(p.dignity)t.add(`${n} ${p.dignity}`);if(p.retrograde&&!["Rahu","Ketu"].includes(p.name))t.add(`${n} retrograde`);
    for(const h of p.lord_of_houses)t.add(`lord of house ${h} in house ${p.house}`)}
  const[md,ad]=currentDasha(c);if(md){t.add(`${md.toLowerCase()} mahadasha`);t.add(`${md.toLowerCase()}-${ad.toLowerCase()} dasha`);t.add(`${ad.toLowerCase()} antardasha`)}
  const p=P(c);
  for(const a of aspects(c)){const n=a.planet.toLowerCase();t.add(`${n} aspects house ${a.house}`);if(a.house===1)t.add(`${n} aspects lagna`);for(const x of a.planets)t.add(`${n} aspects ${x.toLowerCase()}`)}
  const names=c.planets.map(q=>q.name);
  names.forEach((a,i)=>names.slice(i+1).forEach(b=>{if(p[a].sign===p[b].sign){const A=a.toLowerCase(),B=b.toLowerCase();[`${A} conjunct ${B}`,`${B} conjunct ${A}`,`${A} with ${B}`,`${B} with ${A}`].forEach(x=>t.add(x))}}));
  for(const[n,v]of Object.entries(functionalNature(c)))t.add(`${n.toLowerCase()} ${v.split(" (")[0]}`);
  for(const y of yogas(c)){t.add(y.name.toLowerCase());t.add(y.name.toLowerCase().split(" (")[0])}
  return[...t].sort()}

function summary(c){const L=[`Native: ${c.name}${c.place?", born in "+c.place:""}, ${c.birth_local} (UTC${c.utc_offset>=0?"+":""}${c.utc_offset}), lat ${c.latitude}, lon ${c.longitude}. Lahiri ayanamsa ${c.ayanamsa}.`,
  `Lagna: ${c.lagna.sign} ${c.lagna.degree_in_sign}° (${c.lagna.nakshatra} pada ${c.lagna.pada}), Navamsa lagna ${c.lagna.navamsa_sign}.`,"Planets (whole-sign houses):"];
  for(const p of c.planets){const ex=[p.dignity,p.retrograde&&!["Rahu","Ketu"].includes(p.name)?"retrograde":""].filter(Boolean).join(", ");
    L.push(`- ${p.name}: ${p.sign} ${p.degree_in_sign}°, house ${p.house}, ${p.nakshatra} pada ${p.pada} (star lord ${p.nakshatra_lord}), D9 ${p.navamsa_sign}${p.lord_of_houses.length?"; lord of "+p.lord_of_houses.join(", "):""}${ex?"; "+ex:""}`)}
  L.push("Graha drishti (houses aspected):");const by={};for(const a of aspects(c))(by[a.planet]=by[a.planet]||[]).push(a.house+(a.planets.length?` (${a.planets.join(", ")})`:""));
  for(const[k,v]of Object.entries(by))L.push(`- ${k} aspects ${v.join(", ")}`);
  L.push(`Functional nature for ${c.lagna.sign} lagna: `+Object.entries(functionalNature(c)).map(([k,v])=>`${k} ${v}`).join("; "));
  const ys=yogas(c);L.push(ys.length?"Yogas detected (verify strength and cancellations):":"Yogas detected: none of the core yogas checked.");ys.forEach(y=>L.push(`- ${y.name}: ${y.description}`));
  const[md,ad]=currentDasha(c);L.push(md?`Current Vimshottari dasha: ${md} mahadasha / ${ad} antardasha.`:"Current date is outside the 120-year Vimshottari cycle.");
  L.push("Mahadasha sequence: "+c.dashas.map(d=>`${d.lord} ${d.start.slice(0,4)}-${d.end.slice(0,4)}`).join("; "));
  return L.join("\n")}

/* ---------- rule matching ---------- */
const STOP=new Set("a an the of in on and or is are to for with by at as be it its this that from will gives give can may when if".split(" "));
const words=s=>new Set((String(s||"").toLowerCase().match(/[a-z0-9]+/g)||[]).filter(w=>!STOP.has(w)));
function relevantRules(rules,fs,question,limit=40){
  const fw=new Set();fs.forEach(f=>words(f).forEach(w=>fw.add(w)));const qw=words(question);const out=[];
  for(const r of rules){let cond=" "+String(r.condition).toLowerCase().replace(/\s+/g," ")+" ";
    cond=cond.replace(/\b(the|a)\s+/g,"").replace(/(\d+)(st|nd|rd|th)\s+house/g,"house $1").replace(/house\s+(\d+)\s*(st|nd|rd|th)\b/g,"house $1");
    let s=fs.reduce((n,f)=>n+(cond.includes(` ${f} `)||cond.includes(` ${f},`)?10:0),0);
    s+=[...words(r.condition)].filter(w=>fw.has(w)).length*0.5;
    const iw=new Set([...words(r.interpretation),...words(r.topic)]);const q=[...qw].filter(w=>iw.has(w)).length;s+=q;
    if(s>=10||q>=1)out.push({...r,score:s})}
  return out.sort((a,b)=>b.score-a.score).slice(0,limit)}

const SYSTEM=`You are a student of Parashari Jyotish (the system of Brihat Parashara Hora Shastra), learning from your teacher. Use the sidereal (Lahiri) chart data given; never recompute positions.
Reason the Parashari way: lagna and lagna lord first, then house lords and their placements, graha drishti, functional benefics/malefics for this lagna, yogas, dignity, then the Vimshottari dasha for timing. Use the Moon chart and D9 to confirm. The yogas listed are detected mechanically: confirm their strength before relying on them.

How to reason:
1. The teacher's rules are your primary source. When a rule's condition is met by the chart, apply it and cite it as [R:<id>]. Check that the condition is truly met before citing.
2. The teacher's past corrections override anything else. Follow them.
3. You may add general classical knowledge where no taught rule covers a point, but mark each such statement as (general knowledge) so the teacher can confirm or correct it.
4. Weigh conflicting indications, mention dignity, house lordship, aspects and the current dasha, and say how confident you are.
5. End with a section "Questions for my teacher": 1-3 things you were unsure about, so the teacher can teach you a new rule.
Be concrete and kind. Do not make fatalistic, medical or legal predictions. Write in plain prose with short headings (lines starting with ##) and no tables.`;

function buildPrompt(chart,rules,corrections,question){
  const rel=relevantRules(rules,factors(chart),question);
  const parts=["## Chart\n"+summary(chart)];
  parts.push("## Teacher's rules that may apply\n"+(rel.length?rel.map(r=>`[R:${r.id}] IF ${r.condition} THEN ${r.interpretation}${r.source?` (source: ${r.source})`:""}`).join("\n"):"(none taught yet for these placements)"));
  if(corrections.length)parts.push("## Teacher's past corrections (follow these)\n"+corrections.slice(0,25).map(c=>`- On "${(c.question||"general analysis").slice(0,80)}": ${c.correction}`).join("\n"));
  parts.push("## Question\n"+(question||"Give an overall analysis of this chart."));
  return{prompt:SYSTEM+"\n\n---\n\n"+parts.join("\n\n"),rules:rel}}

return{SIGNS,computeChart,currentDasha,aspects,functionalNature,yogas,factors,summary,relevantRules,buildPrompt};
})();
if(typeof module!=="undefined")module.exports=J;
