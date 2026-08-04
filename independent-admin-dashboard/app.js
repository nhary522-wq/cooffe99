const seed = {
  products:[
    {id:1,name:"بن خولاني فاخر",sku:"COF-101",category:"محاصيل القهوة",price:78,stock:4,status:"نشط"},
    {id:2,name:"قهوة إثيوبية مختصة",sku:"COF-102",category:"محاصيل القهوة",price:69,stock:18,status:"نشط"},
    {id:3,name:"طاحونة يدوية احترافية",sku:"TLS-204",category:"أدوات القهوة",price:189,stock:2,status:"نشط"},
    {id:4,name:"كيمكس زجاجي 600 مل",sku:"TLS-218",category:"أدوات القهوة",price:115,stock:0,status:"غير متوفر"},
    {id:5,name:"قهوة كولومبية متوازنة",sku:"COF-115",category:"محاصيل القهوة",price:72,stock:27,status:"مسودة"}
  ],
  orders:[
    {id:1,number:"#10482",customer:"عبدالله الشهري",total:264,status:"قيد التجهيز",payment:"مدفوع",date:"27 يوليو، 10:42"},
    {id:2,number:"#10481",customer:"محمد العتيبي",total:145,status:"جديد",payment:"مدفوع",date:"27 يوليو، 09:18"},
    {id:3,number:"#10480",customer:"محمد الغامدي",total:389,status:"تم الشحن",payment:"مدفوع",date:"26 يوليو، 21:05"},
    {id:4,number:"#10479",customer:"حسن القحطاني",total:92,status:"ملغي",payment:"مسترد",date:"26 يوليو، 18:31"},
    {id:5,number:"#10478",customer:"أحمد نهاري",total:218,status:"تم التسليم",payment:"مدفوع",date:"26 يوليو، 15:12"}
  ],
  customers:[
    {id:1,name:"عبدالله الشهري",email:"abdullah@example.sa",phone:"05•• ••• 8421",orders:8,spent:1240,status:"نشط"},
    {id:2,name:"نورة العتيبي",email:"noura@example.sa",phone:"05•• ••• 3812",orders:4,spent:623,status:"نشط"},
    {id:3,name:"محمد الغامدي",email:"mohammed@example.sa",phone:"05•• ••• 1170",orders:12,spent:2480,status:"نشط"},
    {id:4,name:"ريم القحطاني",email:"reem@example.sa",phone:"05•• ••• 9064",orders:2,spent:210,status:"موقوف"}
  ],
  payments:[
    {id:1,number:"PAY-3F9A82",order:"#10482",method:"مدى",amount:264,status:"مكتملة",date:"27 يوليو، 10:43"},
    {id:2,number:"PAY-18C42D",order:"#10481",method:"Apple Pay",amount:145,status:"مكتملة",date:"27 يوليو، 09:19"},
    {id:3,number:"PAY-7B29E1",order:"#10479",method:"مدى",amount:92,status:"مستردة",date:"26 يوليو، 18:36"}
  ],
  content:[
    {id:"banners",name:"الإعلانات الرئيسية",desc:"إدارة الصور والعناوين وأزرار الدعوة",count:"3 إعلانات",updated:"منذ ساعتين",icon:"▧"},
    {id:"pages",name:"الصفحات الثابتة",desc:"سياسة الخصوصية، الشروط، ومن نحن",count:"5 صفحات",updated:"أمس",icon:"▤"},
    {id:"messages",name:"رسائل التواصل",desc:"متابعة استفسارات ورسائل العملاء",count:"6 غير مقروءة",updated:"منذ 18 دقيقة",icon:"✉"},
    {id:"reviews",name:"تقييمات المنتجات",desc:"مراجعة ونشر تقييمات العملاء",count:"14 بانتظار المراجعة",updated:"اليوم",icon:"☆"},
    {id:"coupons",name:"الكوبونات والعروض",desc:"إنشاء الخصومات وتتبع استخدامها",count:"4 نشطة",updated:"منذ 3 أيام",icon:"%"},
    {id:"navigation",name:"قوائم وروابط المتجر",desc:"تنظيم عناصر التنقل والروابط المهمة",count:"12 رابطًا",updated:"منذ أسبوع",icon:"⌘"}
  ],
  activity:[
    ["✓","تم تأكيد الطلب #10482","منذ 4 دقائق"],["□","انخفض مخزون طاحونة يدوية إلى قطعتين","منذ 18 دقيقة"],["↗","تم شحن الطلب #10480","منذ 42 دقيقة"],["★","أضيف تقييم جديد لمنتج البن الخولاني","منذ ساعة"]
  ]
};
const state={page:"dashboard",query:"",filter:"all",data:loadData()};
function loadData(){try{return JSON.parse(localStorage.getItem("madar-data"))||structuredClone(seed)}catch{return structuredClone(seed)}}
function saveData(){localStorage.setItem("madar-data",JSON.stringify(state.data))}
const nav=[
  ["الرئيسية",[["dashboard","⌂","نظرة عامة"],["analytics","⌁","التحليلات"]]],
  ["التجارة",[["orders","▣","الطلبات","5"],["products","◇","المنتجات"],["inventory","▥","المخزون","3"],["payments","◉","المدفوعات"],["customers","♙","العملاء"]]],
  ["المحتوى",[["content","▤","المحتوى","6"],["marketing","✦","التسويق والعروض"]]],
  ["النظام",[["team","♟","الفريق والصلاحيات"],["settings","⚙","الإعدادات"],["activity","◷","سجل النشاط"]]]
];
const pageInfo={
 dashboard:["نظرة عامة","صباح الخير، غانم"],analytics:["التقارير","التحليلات والأداء"],orders:["التجارة","إدارة الطلبات"],products:["الكتالوج","المنتجات"],inventory:["الكتالوج","المخزون"],payments:["المالية","المدفوعات والاسترداد"],customers:["العملاء","إدارة العملاء"],content:["المحتوى","محتوى المتجر"],marketing:["التسويق","التسويق والعروض"],team:["النظام","الفريق والصلاحيات"],settings:["النظام","إعدادات المنصة"],activity:["النظام","سجل النشاط"]
};
const main=document.querySelector("#main");
function init(){
  document.querySelector("#navigation").innerHTML=nav.map(([title,items])=>`<p class="nav-section">${title}</p>${items.map(([id,icon,label,count])=>`<button class="nav-item" data-page="${id}"><span class="ico">${icon}</span><span>${label}</span>${count?`<span class="count">${count}</span>`:""}</button>`).join("")}`).join("");
  document.addEventListener("click",handleClick);
  document.querySelector("#entityForm").addEventListener("submit",handleForm);
  document.querySelector("#globalSearch").addEventListener("input",e=>renderCommand(e.target.value));
  document.addEventListener("keydown",handleKeys);
  window.addEventListener("hashchange",()=>navigate(location.hash.slice(1)||"dashboard",false));
  navigate(location.hash.slice(1)||"dashboard",false);
}
function navigate(page,push=true){
  if(!pageInfo[page])page="dashboard";state.page=page;state.query="";state.filter="all";
  if(push)location.hash=page;
  document.querySelectorAll(".nav-item").forEach(x=>x.classList.toggle("active",x.dataset.page===page));
  document.querySelector("#breadcrumb").textContent=pageInfo[page][0];document.querySelector("#pageTitle").textContent=pageInfo[page][1];
  document.querySelector("#sidebar").classList.remove("open");render();
}
function handleClick(e){
  const page=e.target.closest("[data-page]");if(page){navigate(page.dataset.page);return}
  const target=e.target.closest("[data-action]");if(!target)return;
  const {action,id,type}=target.dataset;
  if(action==="toggle-sidebar")document.querySelector("#sidebar").classList.toggle("open");
  if(action==="command")openCommand();
  if(action==="close-command")close("command");
  if(action==="close-modal")close("modal");
  if(action==="close-drawer")close("drawer");
  if(action==="add")openForm(type);
  if(action==="view")openDetails(type,Number(id));
  if(action==="edit")openForm(type,Number(id));
  if(action==="delete")removeEntity(type,Number(id));
  if(action==="filter"){state.filter=target.value;render()}
  if(action==="export")exportCsv(type);
  if(action==="notifications"){toast("لديك 3 تنبيهات تحتاج إلى مراجعة");navigate("inventory")}
  if(action==="profile")toast("حسابك محمي بدور: مدير المنصة");
  if(action==="toggle"){target.classList.toggle("on");toast("تم حفظ الإعداد")}
  if(action==="content")toast(`تم فتح وحدة ${target.dataset.name}`);
  if(action==="reset"){if(confirm("هل تريد استعادة البيانات التجريبية؟")){state.data=structuredClone(seed);saveData();render();toast("تمت استعادة البيانات")}}
 }
function handleKeys(e){
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();openCommand()}
  if(e.key==="Escape"){["command","modal","drawer"].forEach(close)}
}
function openCommand(){const el=document.querySelector("#command");el.classList.add("open");el.setAttribute("aria-hidden","false");const input=document.querySelector("#globalSearch");input.value="";renderCommand("");setTimeout(()=>input.focus(),20)}
function close(id){const el=document.querySelector("#"+id);el.classList.remove("open");el.setAttribute("aria-hidden","true")}
function render(){const renderers={dashboard:dashboard,analytics:analytics,products:()=>tablePage("products"),orders:()=>tablePage("orders"),customers:()=>tablePage("customers"),payments:()=>tablePage("payments"),inventory:inventory,content:content,marketing:marketing,team:team,settings:settings,activity:activity};main.innerHTML=renderers[state.page]();main.focus()}
function head(title,desc,action="",type=""){return `<div class="page-head"><div><h2>${title}</h2><p>${desc}</p></div>${type||action?`<div class="actions">${type?`<button class="btn secondary" data-action="export" data-type="${type}">تصدير CSV</button>`:""}${action?`<button class="btn primary" data-action="add" data-type="${type}">＋ ${action}</button>`:""}</div>`:""}</div>`}
function dashboard(){
 const revenue=state.data.orders.reduce((s,x)=>s+x.total,0);
 return `${head("ملخص اليوم","صورة واضحة لأداء متجرك وما يحتاج إلى انتباه")}
 <section class="stats">
 ${stat("إجمالي المبيعات",revenue.toLocaleString("ar-SA")+" ر.س","↑ 12.4% عن الأسبوع الماضي","◒")}
 ${stat("الطلبات الجديدة",state.data.orders.length,"↑ 8.2% عن الأمس","▣")}
 ${stat("متوسط قيمة الطلب","221 ر.س","↑ 3.1% هذا الشهر","⌁")}
 ${stat("العملاء النشطون",state.data.customers.filter(x=>x.status==="نشط").length,"عميلان جديدان اليوم","♙")}
 </section>
 <div class="dashboard-grid">
 <section class="panel"><div class="panel-head"><div><h3>المبيعات خلال الأسبوع</h3><p>إجمالي المبيعات اليومية بالريال</p></div><button class="text-btn" data-page="analytics">عرض التقرير ←</button></div>${chart()}</section>
 <section class="panel"><div class="panel-head"><div><h3>حالة الطلبات</h3><p>توزيع الطلبات الحالية</p></div></div><div class="progress-list">${progress("جديد",28,12)}${progress("قيد التجهيز",42,18)}${progress("تم الشحن",19,8)}${progress("مكتمل",11,5)}</div></section>
 <section class="panel"><div class="panel-head"><div><h3>أحدث النشاطات</h3><p>آخر التحديثات على المنصة</p></div><button class="text-btn" data-page="activity">عرض الكل</button></div><div class="activity-list">${state.data.activity.map(a=>`<div class="activity"><span class="activity-icon">${a[0]}</span><div><p>${a[1]}</p><span>${a[2]}</span></div><b>‹</b></div>`).join("")}</div></section>
 <section class="panel"><div class="panel-head"><div><h3>تنبيهات المخزون</h3><p>منتجات وصلت إلى حد إعادة الطلب</p></div><button class="text-btn" data-page="inventory">إدارة المخزون</button></div>${state.data.products.filter(x=>x.stock<=4).map(x=>`<div class="low-stock"><span class="product-thumb">☕</span><div><strong>${x.name}</strong><small>${x.sku}</small></div><span class="stock-count">${x.stock} قطع</span></div>`).join("")}</section>
 </div>`;
}
function stat(label,value,trend,icon){return `<article class="stat-card"><div class="stat-top"><span>${label}</span><span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><span class="trend">${trend}</span></article>`}
function chart(){let v=[42,66,53,82,64,91,76];return `<div class="chart">${v.map((x,i)=>`<div class="bar-wrap"><div class="bar" style="--h:${x}%"></div><span>${["الأحد","الإثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت"][i]}</span></div>`).join("")}</div><div class="chart-legend"><span>هذا الأسبوع</span><strong>8,740 ر.س</strong></div>`}
function progress(label,pct,count){return `<div class="progress-row"><header><span>${label}</span><span>${count} طلبًا · ${pct}%</span></header><div class="progress-track"><div class="progress-fill" style="--w:${pct}%"></div></div></div>`}
const schemas={
 products:{title:"المنتجات",desc:"إدارة بيانات المنتجات وأسعارها وحالة نشرها",add:"إضافة منتج",cols:["المنتج","التصنيف","السعر","المخزون","الحالة"],fields:[["name","اسم المنتج","text"],["sku","رمز SKU","text"],["category","التصنيف","select",["محاصيل القهوة","أدوات القهوة"]],["price","السعر","number"],["stock","المخزون","number"],["status","الحالة","select",["نشط","مسودة","غير متوفر"]]]},
 orders:{title:"الطلبات",desc:"متابعة دورة الطلب من الإنشاء حتى التسليم",add:"إنشاء طلب",cols:["الطلب","العميل","الإجمالي","الدفع","الحالة"],fields:[["number","رقم الطلب","text"],["customer","العميل","text"],["total","الإجمالي","number"],["payment","الدفع","select",["مدفوع","بانتظار الدفع","مسترد"]],["status","الحالة","select",["جديد","قيد التجهيز","تم الشحن","تم التسليم","ملغي"]]]},
 customers:{title:"العملاء",desc:"عرض ملفات العملاء وسجل مشترياتهم دون كشف بيانات حساسة",add:"إضافة عميل",cols:["العميل","الهاتف","الطلبات","إجمالي الإنفاق","الحالة"],fields:[["name","الاسم","text"],["email","البريد الإلكتروني","email"],["phone","الهاتف","text"],["orders","عدد الطلبات","number"],["spent","إجمالي الإنفاق","number"],["status","الحالة","select",["نشط","موقوف"]]]},
 payments:{title:"المدفوعات",desc:"مراجعة العمليات والاستردادات والتسويات المالية",add:"تسجيل عملية",cols:["العملية","الطلب","الوسيلة","المبلغ","الحالة"],fields:[["number","رقم العملية","text"],["order","رقم الطلب","text"],["method","الوسيلة","select",["مدى","Apple Pay","تحويل بنكي","الدفع عند الاستلام"]],["amount","المبلغ","number"],["status","الحالة","select",["مكتملة","قيد المعالجة","فاشلة","مستردة"]]]}
};
function tablePage(type){
 const s=schemas[type], rows=filtered(type);
 return `${head(s.title,s.desc,s.add,type)}<div class="toolbar"><div class="field-search"><input value="${state.query}" data-search="${type}" placeholder="ابحث في ${s.title}..." aria-label="بحث"></div><select class="select" data-action="filter"><option value="all">كل الحالات</option><option value="active">النشطة فقط</option><option value="attention">تحتاج انتباهًا</option></select><button class="btn secondary" onclick="toast('تم تحديث البيانات')">↻ تحديث</button></div>
 <div class="table-wrap">${rows.length?`<table><thead><tr>${s.cols.map(x=>`<th>${x}</th>`).join("")}<th>الإجراءات</th></tr></thead><tbody>${rows.map(x=>row(type,x)).join("")}</tbody></table>`:`<div class="empty-state">⌕<b>لا توجد نتائج مطابقة</b><span>جرّب تغيير عبارة البحث أو عامل التصفية.</span></div>`}</div>
 <div class="pagination"><span>عرض ${rows.length} من ${state.data[type].length}</span><div><button>‹</button><button class="active">1</button><button>›</button></div></div>`;
}
function filtered(type){return state.data[type].filter(x=>{const q=state.query.trim().toLowerCase();const match=!q||Object.values(x).join(" ").toLowerCase().includes(q);const filter=state.filter==="all"||state.filter==="active"&&["نشط","مكتملة","مدفوع"].includes(x.status)||state.filter==="attention"&&["موقوف","ملغي","فاشلة","غير متوفر"].includes(x.status);return match&&filter})}
document.addEventListener("input",e=>{if(e.target.dataset.search){state.query=e.target.value;render();const input=document.querySelector(`[data-search="${e.target.dataset.search}"]`);input.focus();input.setSelectionRange(state.query.length,state.query.length)}});
function row(type,x){
 const cls=v=>/ملغي|موقوف|فاشلة|غير متوفر/.test(v)?"danger":/جديد|قيد|مسودة/.test(v)?"warning":/تم الشحن|مسترد/.test(v)?"info":"";
 const actions=`<td><div class="row-actions"><button class="row-btn" data-action="view" data-type="${type}" data-id="${x.id}" title="عرض">◉</button><button class="row-btn" data-action="edit" data-type="${type}" data-id="${x.id}" title="تعديل">✎</button><button class="row-btn" data-action="delete" data-type="${type}" data-id="${x.id}" title="حذف">×</button></div></td>`;
 if(type==="products")return `<tr><td><div class="entity"><span class="product-thumb">☕</span><div><strong>${x.name}</strong><small>${x.sku}</small></div></div></td><td>${x.category}</td><td>${x.price} ر.س</td><td>${x.stock}</td><td><span class="status ${cls(x.status)}">${x.status}</span></td>${actions}</tr>`;
 if(type==="orders")return `<tr><td><strong>${x.number}</strong><small>${x.date}</small></td><td>${x.customer}</td><td>${x.total} ر.س</td><td><span class="status ${cls(x.payment)}">${x.payment}</span></td><td><span class="status ${cls(x.status)}">${x.status}</span></td>${actions}</tr>`;
 if(type==="customers")return `<tr><td><div class="entity"><span class="avatar">${x.name.slice(0,2)}</span><div><strong>${x.name}</strong><small>${x.email}</small></div></div></td><td>${x.phone}</td><td>${x.orders}</td><td>${x.spent} ر.س</td><td><span class="status ${cls(x.status)}">${x.status}</span></td>${actions}</tr>`;
 return `<tr><td><strong>${x.number}</strong><small>${x.date}</small></td><td>${x.order}</td><td>${x.method}</td><td>${x.amount} ر.س</td><td><span class="status ${cls(x.status)}">${x.status}</span></td>${actions}</tr>`;
}
function inventory(){const products=state.data.products;return `${head("المخزون","راقب الكميات وحدود إعادة الطلب وحركة المخزون","تسوية مخزون","products")}<section class="stats">${stat("إجمالي الوحدات",products.reduce((s,x)=>s+x.stock,0),"عبر "+products.length+" منتجات","▥")}${stat("مخزون منخفض",products.filter(x=>x.stock>0&&x.stock<=4).length,"يحتاج إعادة طلب","!")}${stat("نفد من المخزون",products.filter(x=>x.stock===0).length,"أوقف البيع تلقائيًا","×")}${stat("قيمة المخزون","8,420 ر.س","بسعر التكلفة","◉")}</section>${tablePage("products").replace(head(schemas.products.title,schemas.products.desc,schemas.products.add,"products"),"")}`}
function content(){return `${head("محتوى المتجر","تحكم بكل ما يظهر لعملائك من مكان واحد")}<div class="content-grid">${state.data.content.map(x=>`<article class="module-card" data-action="content" data-name="${x.name}"><span class="module-icon">${x.icon}</span><h3>${x.name}</h3><p>${x.desc}</p><div class="module-meta"><strong>${x.count}</strong><span>آخر تحديث: ${x.updated}</span></div></article>`).join("")}</div>`}
function analytics(){return `${head("التحليلات والأداء","قرارات أوضح مبنية على مؤشرات المبيعات والعملاء")}<section class="stats">${stat("صافي الإيرادات","8,740 ر.س","↑ 12.4%","◒")}${stat("معدل التحويل","3.8%","↑ 0.6 نقطة","⌁")}${stat("العملاء العائدون","41%","↑ 4.2%","♙")}${stat("الطلبات الملغاة","2.1%","↓ 0.8%","×")}</section><div class="dashboard-grid"><section class="panel"><div class="panel-head"><div><h3>اتجاه الإيرادات</h3><p>آخر سبعة أيام</p></div></div>${chart()}</section><section class="panel"><div class="panel-head"><div><h3>أفضل قنوات الوصول</h3><p>نسبة الطلبات حسب المصدر</p></div></div><div class="progress-list">${progress("بحث مباشر",42,196)}${progress("انستغرام",31,143)}${progress("إحالات",17,79)}${progress("أخرى",10,46)}</div></section></div>`}
function marketing(){return `${head("التسويق والعروض","أنشئ الحملات والكوبونات وتابع نتائجها","حملة جديدة","products")}<div class="content-grid">${["خصم الصيف|خصم 15% على المحاصيل المختصة|نشطة|142 استخدامًا","شحن مجاني|للطلبات فوق 150 ر.س|نشطة|89 استخدامًا","عميل جديد|خصم أول طلب|مجدولة|—"].map((x,i)=>{let a=x.split("|");return `<article class="module-card"><span class="module-icon">${i?"%":"✦"}</span><h3>${a[0]}</h3><p>${a[1]}</p><div class="module-meta"><span class="status ${a[2]==="مجدولة"?"warning":""}">${a[2]}</span><strong>${a[3]}</strong></div></article>`}).join("")}</div>`}
function team(){return `${head("الفريق والصلاحيات","تحكم بمن يصل إلى كل جزء من لوحة الإدارة","دعوة عضو","customers")}<div class="table-wrap"><table><thead><tr><th>عضو الفريق</th><th>الدور</th><th>نطاق الوصول</th><th>آخر نشاط</th><th>الحالة</th></tr></thead><tbody>${[["غانم نهاري","مدير المنصة","صلاحية كاملة على المنصة","الآن"],["عبدالرحمن نهاري","مدير الطلبات","الطلبات والعملاء والشحن","منذ 12 دقيقة"],["حسن نهاري","مدير المحتوى","المحتوى والتسويق","أمس"],["علي نهاري","المحاسب","المدفوعات والاستردادات والتقارير المالية","أمس"]].map(x=>`<tr><td><div class="entity"><span class="avatar">${x[0].slice(0,2)}</span><strong>${x[0]}</strong></div></td><td>${x[1]}</td><td>${x[2]}</td><td>${x[3]}</td><td><span class="status">نشط</span></td></tr>`).join("")}</tbody></table></div>`}
function settings(){return `${head("إعدادات المنصة","إدارة الهوية والتجارة والإشعارات والأمان")}<div class="settings-grid"><nav class="settings-nav"><button class="active">عام</button><button>التجارة</button><button>الدفع</button><button>الشحن</button><button>الإشعارات</button><button>الأمان</button></nav><section class="settings-form"><h3>الإعدادات العامة</h3><div class="form-grid"><label class="form-group"><span>اسم المتجر</span><input value="A23"></label><label class="form-group"><span>البريد</span><input value="hello@mathaq.sa"></label><label class="form-group"><span>العملة</span><select><option>ريال سعودي (SAR)</option></select></label><label class="form-group"><span>ضريبة القيمة المضافة</span><input value="15%"></label></div><div class="toggle-row"><div><strong>وضع الصيانة</strong><p class="eyebrow">إيقاف واجهة المتجر مؤقتًا</p></div><button class="toggle" data-action="toggle" aria-label="وضع الصيانة"></button></div><div class="toggle-row"><div><strong>تنبيهات المخزون</strong><p class="eyebrow">إرسال تنبيه عند الوصول إلى الحد الأدنى</p></div><button class="toggle on" data-action="toggle" aria-label="تنبيهات المخزون"></button></div><div class="form-actions"><button class="btn secondary" data-action="reset">استعادة البيانات التجريبية</button><button class="btn primary" onclick="event.preventDefault();toast('تم حفظ الإعدادات')">حفظ الإعدادات</button></div></section></div>`}
function activity(){return `${head("سجل النشاط","أثر تدقيقي واضح لكل الإجراءات الإدارية")}<section class="panel"><div class="activity-list">${[...state.data.activity,["⚙","عدّل غانم نهاري إعدادات الشحن","أمس، 14:20"],["♙","سجّل عبدالرحمن نهاري الدخول إلى لوحة الإدارة","أمس، 09:03"]].map(a=>`<div class="activity"><span class="activity-icon">${a[0]}</span><div><p>${a[1]}</p><span>${a[2]}</span></div><span>عنوان IP مخفي</span></div>`).join("")}</div></section>`}
function openForm(type,id){
 const s=schemas[type]||schemas.products;let item=id?state.data[type].find(x=>x.id===id):{};
 document.querySelector("#modalTitle").textContent=id?`تعديل ${s.title.slice(0,-1)}`:s.add;document.querySelector("#modalEyebrow").textContent=id?"تحديث البيانات":"إضافة جديدة";
 document.querySelector("#entityForm").dataset.type=type;document.querySelector("#entityForm").dataset.id=id||"";
 document.querySelector("#modalFields").innerHTML=`<div class="form-grid">${s.fields.map(([key,label,input,options])=>`<label class="form-group"><span>${label}</span>${input==="select"?`<select name="${key}" required>${options.map(o=>`<option ${item[key]===o?"selected":""}>${o}</option>`).join("")}</select>`:`<input name="${key}" type="${input}" value="${item[key]??""}" required>`}</label>`).join("")}</div>`;
 const el=document.querySelector("#modal");el.classList.add("open");el.setAttribute("aria-hidden","false");setTimeout(()=>el.querySelector("input,select").focus(),20)
}
function handleForm(e){e.preventDefault();const type=e.currentTarget.dataset.type,id=Number(e.currentTarget.dataset.id),data=Object.fromEntries(new FormData(e.currentTarget));["price","stock","total","orders","spent","amount"].forEach(k=>{if(k in data)data[k]=Number(data[k])});if(id){Object.assign(state.data[type].find(x=>x.id===id),data)}else{data.id=Math.max(0,...state.data[type].map(x=>x.id))+1;data.date="الآن";state.data[type].unshift(data)}saveData();close("modal");render();toast(id?"تم حفظ التعديلات بنجاح":"تمت الإضافة بنجاح")}
function openDetails(type,id){const item=state.data[type].find(x=>x.id===id);document.querySelector("#drawerTitle").textContent=item.name||item.number;document.querySelector("#drawerContent").innerHTML=`<div class="detail-hero"><h3>${item.name||item.customer||item.number}</h3><p>${type==="orders"?"ملخص الطلب ومراحل تنفيذه":"عرض شامل للبيانات المسجلة"}</p></div><div class="detail-grid">${Object.entries(item).filter(([k])=>k!=="id").map(([k,v])=>`<div class="detail-item"><span>${fieldName(k)}</span><strong>${v}${["price","total","spent","amount"].includes(k)?" ر.س":""}</strong></div>`).join("")}</div><div class="timeline"><h3>سجل التغييرات</h3><div class="timeline-item"><strong>آخر تحديث للبيانات</strong><span>اليوم، بواسطة غانم نهاري</span></div><div class="timeline-item"><strong>تم إنشاء السجل</strong><span>مسجل في سجل النشاط</span></div></div>`;const el=document.querySelector("#drawer");el.classList.add("open");el.setAttribute("aria-hidden","false")}
function fieldName(k){return {name:"الاسم",sku:"رمز المنتج",category:"التصنيف",price:"السعر",stock:"المخزون",status:"الحالة",number:"الرقم",customer:"العميل",total:"الإجمالي",payment:"الدفع",date:"التاريخ",email:"البريد",phone:"الهاتف",orders:"الطلبات",spent:"الإنفاق",order:"الطلب",method:"الوسيلة",amount:"المبلغ"}[k]||k}
function removeEntity(type,id){if(!confirm("هل أنت متأكد من حذف هذا السجل؟ لا يمكن التراجع من داخل اللوحة."))return;state.data[type]=state.data[type].filter(x=>x.id!==id);saveData();render();toast("تم حذف السجل")}
function renderCommand(q){const entries=[...state.data.products.map(x=>["◇",x.name,"منتج",`products:${x.id}`]),...state.data.orders.map(x=>["▣",`${x.number} — ${x.customer}`,"طلب",`orders:${x.id}`]),...state.data.customers.map(x=>["♙",x.name,"عميل",`customers:${x.id}`])].filter(x=>!q||x[1].includes(q)).slice(0,8);document.querySelector("#commandResults").innerHTML=`<div class="command-results">${entries.length?entries.map(x=>`<div class="command-item" onclick="commandOpen('${x[3]}')"><span>${x[0]}</span><div><strong>${x[1]}</strong><small>${x[2]}</small></div></div>`).join(""):`<div class="empty-state"><b>لا توجد نتائج</b></div>`}</div>`}
function commandOpen(ref){const [type,id]=ref.split(":");close("command");navigate(type);setTimeout(()=>openDetails(type,Number(id)),50)}
function exportCsv(type){if(!state.data[type]){toast("لا توجد بيانات قابلة للتصدير في هذا القسم","error");return}const rows=state.data[type],keys=Object.keys(rows[0]);const csv="\ufeff"+[keys.join(","),...rows.map(r=>keys.map(k=>`"${String(r[k]).replaceAll('"','""')}"`).join(","))].join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download=`madar-${type}.csv`;a.click();URL.revokeObjectURL(a.href);toast("تم تجهيز ملف التصدير")}
function toast(message,type=""){const el=document.createElement("div");el.className=`toast ${type}`;el.textContent="✓  "+message;document.querySelector("#toastRegion").append(el);setTimeout(()=>el.remove(),3000)}
init();
