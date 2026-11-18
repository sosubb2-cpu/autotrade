// Общий каркас всех страниц: верхняя полоска с контактами, меню, подвал, окно отклика.
(function(){
var page = location.pathname.replace(/\/$/, "") || "/";
var NAV=[["/index","Главная"],["/vacancies","Вакансии"],["/about","О компании"],["/contacts","Контакты"],["/fleet","Наша техника"]]
function svg(p){return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+p+'</svg>'}
var PIN='<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>';
var PH='<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>';
var ARR='<path d="M3 11l18-8-8 18-2-8z"/>';
var slots=CO.showEmptySlots!==false;
var L=[],Rt=[];
// все офисы из company.js: сначала тот, что указан в topCity, потом остальные
var ordered=(CO.offices||[]).slice().sort(function(x,y){return (y.city==CO.topCity)-(x.city==CO.topCity)});
ordered.forEach(function(o){
  L.push('<a class="ti-i addr" href="'+mapUrl(o.addr)+'" target="_blank" rel="noopener" title="Открыть на карте" aria-label="Открыть на карте: '+esc(o.addr)+'"><i class="ti">'+svg(PIN)+'</i><span>'+esc(o.addr)+'</span><i class="ti arr">'+svg(ARR)+'</i></a>');
});
(CO.contacts||[]).forEach(function(c){
  var d=(c.phone||"").replace(/[^\d+]/g,"");
  if(d)Rt.push('<a class="ti-i" href="tel:'+esc(d)+'" title="'+esc(c.name)+'"><i class="ti">'+svg(PH)+'</i><span>'+esc(c.phone)+'</span></a>');
  else if(slots)Rt.push('<span class="ti-i"><i class="ti">'+svg(PH)+'</i><span class="ph">[телефон, '+esc(c.name)+']</span></span>');
});
if(CO.vk)Rt.push('<a class="ti-i" href="'+esc(CO.vk)+'" target="_blank" rel="noopener"><i class="ti">VK</i><span>Группа ВКонтакте</span></a>');
else if(slots)Rt.push('<span class="ti-i"><i class="ti">VK</i><span class="ph">[ссылка на группу ВК]</span></span>');
if(CO.email)Rt.push('<a class="ti-i hm" href="mailto:'+esc(CO.email)+'"><i class="ti">'+svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>')+'</i><span>'+esc(CO.email)+'</span></a>');
var top=(L.length||Rt.length)?'<div class="topbar"><div class="w"><div class="tb-l">'+L.join("")+'</div><div class="tb-r">'+Rt.join("")+'</div></div></div>':"";
var links=NAV.map(function(n){return '<a href="'+n[0]+'"'+(n[0]==page?' class="on"':'')+'>'+n[1]+'</a>'}).join("");
var nav='<nav id="nv"><div class="w"><a class="logo" href="/"><b>АВТО<i>ТРЕЙД</i></b></a><div class="links">'+links+'<button class="btn p sm" data-apply="">Откликнуться</button></div><button class="burger" id="bg" aria-label="Меню">☰</button></div></nav>';
var offs=(CO.offices||[]).map(function(o){return esc(o.addr)}).join(" · ");
var foot='<footer><b data-co="name"></b> · Транспортные услуги в ХМАО и ЯНАО<br>'+
'<span class="fs">ИНН <span data-co="inn" data-ph="ИНН"></span> · ОГРН <span data-co="ogrn" data-ph="ОГРН"></span> · <span data-co="addr" data-ph="юридический адрес"></span></span><br>'+
'<span class="fs">'+offs+'</span><br>'+
'<span class="fs">'+NAV.map(function(n){return '<a href="'+n[0]+'">'+n[1]+'</a>'}).join(" · ")+'</span><br>'+
'<span class="fs"><a href="/privacy">Политика обработки персональных данных</a> · <a href="/consent">Согласие на обработку</a></span><br>'+
'<span class="fs">Названия «Газпром-нефть», «Роснефть» и «РН-Бурение» принадлежат их правообладателям и используются только для указания места выполнения работ.</span></footer>';
var dlg='<dialog id="dlg"><h3 style="margin-top:0">Отклик на вакансию</h3>'+
'<label>Вакансия</label><select id="av"></select>'+
'<label>Имя</label><input id="an" maxlength="60">'+
'<label>Телефон</label><input id="ap" type="tel" placeholder="+7 ___ ___ __ __">'+
'<label>Город проживания</label><input id="ac" maxlength="60">'+
'<input id="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">'+
'<label style="display:flex;gap:10px;align-items:flex-start;color:var(--tx);font-size:13px;margin-bottom:14px"><input type="checkbox" id="cn" style="width:auto;margin:3px 0 0"><span>Я даю <a href="consent.html" target="_blank" style="color:var(--ac)">согласие на обработку персональных данных</a> и ознакомился с <a href="privacy.html" target="_blank" style="color:var(--ac)">Политикой</a></span></label>'+
'<div style="display:flex;gap:8px"><button class="btn p" id="as">Отправить отклик</button><button class="btn" id="ax">Закрыть</button></div></dialog><div class="toast" id="ts"></div>';
document.body.insertAdjacentHTML("afterbegin",'<div id="pr"></div>'+top+nav);
document.body.insertAdjacentHTML("beforeend",foot+dlg);
var n=document.getElementById("nv");
document.getElementById("bg").onclick=function(){n.classList.toggle("open")};
n.addEventListener("click",function(e){if(e.target.tagName=="A")n.classList.remove("open")});
fillCo();
})();
