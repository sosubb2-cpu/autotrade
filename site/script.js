var $=function(i){return document.getElementById(i)};
var G="Газпром",R="Роснефть";
var V=[
{t:"Машинист автокрана 25 т",co:G,cat:"Спецтехника",b:209000,s:21000,f:"Южно-Приобское, Жагрина",l:["Удостоверение машиниста 7 разряда и выше","Краны 25 тонн (Клинцы, Челябинцы)","Проживание: общежитие и вагон-городок на Жагрине, питание в столовой"]},
{t:"Водитель D — Газель Бизнес, 12 мест",co:G,cat:"Водители",b:125000,s:21000,f:"Южно-Приобское, Жагрина",l:["Категория D, карта тахографа (оформляют сами)","Рабочий день 08:00–20:00","Проживание: общежитие и вагон-городок, питание в столовой"]},
{t:"Машинист КМУ",co:G,cat:"Спецтехника",b:135000,s:21000,f:"Южно-Приобское",l:["Удостоверение машиниста КМУ","Работает в паре со стропальщиком, день 08:00–20:00","Проживание: общежитие, питание в столовой"]},
{t:"Водитель СЕ",co:G,cat:"Водители",b:189000,s:21000,f:"Южно-Приобское, Жагрина",l:["Категория СЕ, карта тахографа","Смена 08:00–20:00 или 20:00–08:00","Проживание: общежитие или вагон-городок на Жагрине"]},
{t:"Механик",co:G,cat:"Механики",b:165000,s:21000,f:"Южно-Приобское",l:["Водительское удостоверение (передвижение на машине по м/р)","Удостоверение контролёра по выпуску ТС, промбезопасность А1 и Б9.3","Обязанности: выпуск транспорта на линию, сбор путевок, контроль техники","Проживание: общежитие, питание в столовой"]},
{t:"Стропальщик",co:G,cat:"Спецтехника",b:100000,s:21000,f:"Южно-Приобское, Жагрина",l:["Удостоверение стропальщика 4 разряда и выше","Экипаж: 1 крановой и 2 стропальщика","Смена 08:00–20:00 или 20:00–08:00"]},
{t:"Вакуумка Урал Next (техническая вода)",co:R,cat:"Водители",b:135000,s:15000,f:"Кондинское, Нефтеюганск",l:["Рабочий день 08:00–20:00","Вахта 30/30, 60/30 или 90/30","Проживание: вагон-городок по 4 человека, питание в столовой"]},
{t:"Самосвал Урал Next",co:R,cat:"Водители",b:120000,s:15000,f:"Каменное, Кондинское",l:["Карта тахографа, плюс переработки","Возит запчасти и песок с куста на куст","Рабочий день 08:00–20:00, проживание в вагон-городке"]},
{t:"Водитель D — вахтовка Урал Next",co:R,cat:"Водители",b:135000,s:15000,f:"Каменное, Ем-Ёга, Кондинское",l:["Категория D, карта тахографа (оформляют сами)","Перевозка персонала по месторождению, день 08:00–20:00","Проживание: вагон-городок по 4 человека"]},
{t:"Водитель B — пикап JAC T6 / T8",co:R,cat:"Водители",b:95000,s:15000,f:"Северная Приобка",l:["Перевозка сотрудников по месторождению","Переработки: в среднем водители выходят на 115–120 тыс. ₽","Проживание: вагон-городок по 4 человека"]}
];
var C=[["📅","График вахты согласовывается"],["📄","Официальное трудоустройство, белая зарплата, северный стаж"],["💳","Выплаты 2 раза в месяц: суточные после заезда, зарплата с 10 по 20 число"],["🧥","Новая спецодежда по сезону"],["✈️","Билеты в обе стороны за наш счёт"],["🩺","Медкомиссия за счёт компании: в Тюмени либо по месту жительства (только если в вашем городе есть больница, зарегистрированная Газпромом)"],["🎓","ЗЗВ оплачиваем (для Газпрома): 3–4 дня в Тюмени, на это время предоставляется хостел, питание за свой счёт"],["🏦","Зарплата на любую карту или на третье лицо"]];
var P=['<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>','<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>','<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>','<path d="M8 3L3 7l3 3 2-1v12h8V9l2 1 3-3-5-4a4 4 0 0 1-8 0z"/>','<path d="M3 13L21 4l-7 17-3-7z"/>','<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 8v8M8 12h8"/>','<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>','<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 15-5 16 0"/>'];
function ic(i){return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+P[i]+'</svg>'}
$("conds").innerHTML=C.map(function(c,i){return '<div class="cond reveal"><i>'+ic(i)+'</i><p>'+c[1]+'</p></div>'}).join("");
var st={co:"Все",cat:"Все",q:"",so:"0"};
function chips(id,arr,k){$(id).innerHTML=arr.map(function(a){return '<button class="chip'+(st[k]==a?' on':'')+'" data-k="'+k+'">'+a+'</button>'}).join("")}
function fmt(n){return n.toLocaleString("ru-RU")}
function draw(){
chips("f1",["Все",G,R],"co");chips("f2",["Все","Водители","Спецтехника","Механики"],"cat");
var a=V.filter(function(v){return(st.co=="Все"||v.co==st.co)&&(st.cat=="Все"||v.cat==st.cat)&&(v.t+v.f).toLowerCase().indexOf(st.q)>-1});
if(st.so=="1")a.sort(function(x,y){return y.b-x.b});
$("jobs").innerHTML=a.length?a.map(function(v){var i=V.indexOf(v);return '<article class="v reveal"><div class="top"><div><span class="tg '+(v.co==G?'g':'r')+'">'+v.co+'</span><span class="tg">'+v.cat+'</span><h3>'+v.t+'</h3><div class="mu">📍 '+v.f+'</div></div><div class="sal"><b>'+fmt(v.b)+' ₽</b><div>+ '+fmt(v.s)+' ₽ суточные</div></div></div><div class="more"><div><ul>'+v.l.map(function(x){return '<li>'+x+'</li>'}).join("")+'</ul></div></div><div class="acts"><button class="btn" data-t="'+i+'">Подробнее</button><button class="btn p" data-apply="'+i+'">Откликнуться</button></div></article>'}).join(""):'<div class="card mu">Ничего не найдено. Измените фильтры.</div>';
watch()}
document.body.onclick=function(e){var t=e.target,d=t.dataset;
if(d.k){st[d.k]=t.textContent;draw()}
if(d.t!==undefined){var c=t.closest(".v");c.classList.toggle("open");t.textContent=c.classList.contains("open")?"Свернуть":"Подробнее"}
if(d.apply!==undefined){$("av").value=d.apply===""?"-1":d.apply;$("dlg").showModal()}};
$("q").oninput=function(){st.q=this.value.trim().toLowerCase();draw()};$("so").onchange=function(){st.so=this.value;draw()};
$("av").innerHTML='<option value="-1">Любая подходящая</option>'+V.map(function(v,i){return '<option value="'+i+'">'+v.t+' ('+v.co+')</option>'}).join("");
$("ax").onclick=function(){$("dlg").close()};
function toast(m){var t=$("ts");t.textContent=m;t.classList.add("s");setTimeout(function(){t.classList.remove("s")},3800)}
function post(url,data){return fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}).then(function(r){if(!r.ok)throw 0})}
function esc(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML}
$("as").onclick=function(){var btn=this,n=$("an").value.trim(),p=$("ap").value.trim(),c=$("ac").value.trim();
if(!n||p.replace(/\D/g,"").length<10||!c){toast("Заполните имя, телефон и город");return}
var v=$("av").value,vt=v=="-1"?"Любая подходящая":V[v].t+" ("+V[v].co+")";
btn.disabled=true;
post("/api/apply",{vacancy:vt,name:n,phone:p,city:c,schedule:"согласовывается",website:$("hp").value})
.then(function(){$("dlg").close();$("an").value=$("ap").value=$("ac").value="";toast("Отклик отправлен! Менеджер свяжется с вами.")})
.catch(function(){toast("Не удалось отправить, попробуйте позже")})
.then(function(){btn.disabled=false})};
var rv=[];
function drawR(){$("revs").innerHTML=rv.length?rv.map(function(r){return '<div class="card"><b>'+esc(r.n)+'</b> <span style="color:var(--ac)">'+"★".repeat(r.r)+'</span><div>'+esc(r.t)+'</div></div>'}).join(""):'<div class="card mu">Отзывов пока нет. Будьте первым!</div>'}
function loadR(){fetch("/api/reviews").then(function(r){return r.json()}).then(function(l){rv=l.map(function(x){return{n:x.name,t:x.text,r:x.rating}});drawR()}).catch(drawR)}
$("rs").onclick=function(){var n=$("rn").value.trim()||"Аноним",t=$("rt").value.trim(),r=+$("rr").value;if(t.length<5){toast("Напишите пару слов");return}
post("/api/reviews",{name:n,rating:r,text:t}).then(function(){$("rt").value="";toast("Спасибо! Отзыв появится после проверки.")}).catch(function(){toast("Не удалось отправить отзыв")})};
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{threshold:.12});
function watch(){document.querySelectorAll(".reveal:not(.in)").forEach(function(x){io.observe(x)})}
var co=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;co.unobserve(e.target);var el=e.target,n=+el.dataset.n,s=el.dataset.s||"",t0=performance.now();
(function f(t){var k=Math.min((t-t0)/1400,1);el.textContent=fmt(Math.round(n*(1-Math.pow(1-k,3))))+s;if(k<1)requestAnimationFrame(f)})(t0)})});
document.querySelectorAll("[data-n]").forEach(function(x){co.observe(x)});
window.onscroll=function(){var h=document.documentElement;$("pr").style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+"%"};
draw();loadR();
