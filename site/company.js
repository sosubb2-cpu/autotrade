// ДАННЫЕ КОМПАНИИ: заполните один раз, они подставятся на всех страницах
// (верхняя полоска, подвал, контакты, политика, согласие).
// Пустые поля: в верхней полоске они просто скрыты, на страницах «Контакты», политике и согласии виден жёлтый маркер [...].
var CO={
  name:"ООО «АВТОТРЕЙД»",   // полное название юрлица, как в ЕГРЮЛ
  inn:"8601064902",                    // ИНН
  ogrn:"1178617012177",                   // ОГРН
  addr:"628007, ХМАО – Югра, г. Ханты – Мансийск, ул. Доронина, дом 6, помещение 1",                   // юридический адрес
  email:"ooo.avtt@yandex.ru",                  // общая почта компании (она же для обращений по персональным данным)
  resp:"",                   // ответственный за обработку персональных данных (ФИО или должность)
  vk:"https://vk.ru/ooo.avtt",                     // ссылка на группу ВКонтакте, например "https://vk.com/ваша_группа"
  topCity:"Ханты-Мансийск",   // офис, адрес которого показывается в самой верхней полоске (название города как в offices)
  showEmptySlots:true,        // true: пустые телефоны и ссылка VK видны жёлтым [..]; false: скрыты, пока не заполнены
  offices:[
    {city:"Тюмень",         addr:"г. Тюмень, ул. Сакко, 24"},
    {city:"Ханты-Мансийск", addr:"г. Ханты-Мансийск, ул. Доронина, 6, помещение 1"}
  ],
  // Телефоны специалистов по подбору персонала. Публикуйте номер только с согласия сотрудника.
  contacts:[
    {name:"Алина",     phone:"+7 982 189 05 55"},   // например "+7 900 000-00-00"
    {name:"Мирослава", phone:"+7 912 411 55 50"}
  ]
};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function mapUrl(a){return "https://yandex.ru/maps/?text="+encodeURIComponent(a)}
function fillCo(){
  document.querySelectorAll("[data-co]").forEach(function(e){
    var v=CO[e.dataset.co];
    if(v){e.textContent=v;e.classList.remove("ph")}else{e.textContent="["+(e.dataset.ph||e.dataset.co)+"]";e.classList.add("ph")}
  });
  var cp=document.getElementById("co-phones");
  if(cp)cp.innerHTML=CO.contacts.map(function(c){
    var d=(c.phone||"").replace(/[^\d+]/g,"");
    return '<div class="card"><b>'+esc(c.name)+'</b><br><span class="mu">Специалист по подбору персонала</span><br>'+
      (d?'<a class="map" href="tel:'+esc(d)+'">'+esc(c.phone)+'</a>':'<span class="ph">[телефон]</span>')+'</div>'}).join("");
  var co=document.getElementById("co-offices");
  if(co)co.innerHTML=CO.offices.map(function(o){
    return '<div class="card"><span class="tg r">'+esc(o.city)+'</span><br><b>'+esc(o.addr)+'</b><br><a class="map" target="_blank" rel="noopener" href="'+mapUrl(o.addr)+'">Открыть на карте</a></div>'}).join("");
  var vk=document.getElementById("co-vk");
  if(vk){if(CO.vk){vk.href=CO.vk}else{vk.removeAttribute("href");vk.title="Укажите ссылку в company.js";vk.style.opacity=".55"}}
  var ml=document.getElementById("co-mail");
  if(ml){if(CO.email){ml.href="mailto:"+CO.email;ml.textContent=CO.email;ml.classList.remove("ph")}else{ml.textContent="[email]";ml.classList.add("ph")}}
}
fillCo();
