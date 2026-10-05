
/* ================= 状态与桥接 ================= */
const TYPES = { AMOUNT:"金额", ID_CARD:"身份证", PHONE:"电话", BANK_ACCOUNT:"银行账号", CREDIT_CODE:"信用代码", EMAIL:"邮箱", PERSON:"人名", ORG:"机构名" };
const TAGCLS = { AMOUNT:"amount", ID_CARD:"idcard", PHONE:"phone", BANK_ACCOUNT:"bank", CREDIT_CODE:"credit", EMAIL:"email", PERSON:"person", ORG:"org" };

const state = {
  view:"empty", batchName:"本机批次", outdir:null, mappingPaths:[],
  files:[],            // 后端扫描结果
  fileId:"all", filter:"all",
  excluded:new Set(),  // "fileId:occIdx"（occ 与引擎枚举一致）
  checkedFiles:new Set(),
};

let mapFiles = [];   // 完成屏映射表切换：[{label, mp}]
let curMap = 0;
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
function api(){ return window.pywebview ? window.pywebview.api : null; }
async function call(method, ...args){
  const a = api();
  if(!a) throw new Error("未检测到本地后端——请通过 合同脱敏台 程序打开，而不是直接在浏览器中打开本页。");
  return a[method](...args);
}

/* ================= 视图切换 ================= */
const VIEWS = { empty:"#ws-empty", scan:"#ws-scan", review:"#ws-review", done:"#ws-done" };
function setView(v){
  state.view = v;
  for(const k in VIEWS) $(VIEWS[k]).style.display = (k===v)?"flex":"none";
  $("#actionbar").style.display = (v==="review")?"flex":"none";
  $$(".phase").forEach(p=>{ p.removeAttribute("aria-current"); p.removeAttribute("data-done"); });
  if(v==="scan") $("#ph-scan").setAttribute("aria-current","step");
  if(v==="review"){ $("#ph-scan").setAttribute("data-done","1"); $("#ph-review").setAttribute("aria-current","step"); }
  if(v==="done"){ $("#ph-scan").setAttribute("data-done","1"); $("#ph-review").setAttribute("data-done","1"); $("#ph-done").setAttribute("aria-current","step"); }
  if(v==="review"||v==="done") renderTally();
}

/* ================= 扫描 ================= */
$("#btn-pick").onclick = pickAndScan;
async function pickAndScan(){
  try{
    const r = await call("pick_files");
    if(!r.paths || !r.paths.length) return;
    await scanPaths(r.paths);
  }catch(e){ alert(e.message || String(e)); }
}
async function scanPaths(paths){
  setView("scan");
  $("#scan-num").textContent = "";
  try{
    const useNer = $("#ner-switch").getAttribute("aria-checked")==="true";
    const r = await call("scan_batch", paths, useNer);
    state.files = r.files.map(f=>({...f, hits:f.hits||[]}));
    state.excluded = new Set();
    state.fileId = "all";
    state.filter = "all";
    $$("#hitsbar .chip").forEach(x=>x.setAttribute("aria-pressed", x.dataset.f==="all" ? "true":"false"));
    if(paths.length){
      const folder = folderOf(paths[0]);
      $("#batch-name").textContent = folder + " · 本机运行";
    }
    renderAll();
    const good = state.files.filter(f=>!f.err);
    setView("review");
    if(good.length===0){
      $("#noteline").className = "noteline open";
      $("#noteline").textContent = state.files[0] ? state.files[0].err : "没有可处理的文件。";
    }else{
      renderNoteline();
    }
  }catch(e){ alert(e.message || String(e)); setView("empty"); }
}
function folderOf(p){ const i = String(p).lastIndexOf(/[\\/]/.source) === -1 ? String(p).lastIndexOf("\\") : Math.max(String(p).lastIndexOf("\\"), String(p).lastIndexOf("/")); return String(p).slice(0, i).split(/[\\/]/).pop() || "本机批次"; }

/* ================= 渲染 ================= */
function fileHits(f){ return f.hits.map((h,i)=>({...h, key:f.id+":"+i})); }
function allHits(){ return state.files.filter(f=>!f.err).flatMap(fileHits); }
function shownHits(){
  let hs;
  if(state.fileId==="all"){
    hs = allHits();
  }else{
    const f = state.files.find(f=>String(f.id)===String(state.fileId));
    hs = f ? fileHits(f) : [];  // 复位时序兜底：fileId 指向的文件可能已被清空
  }
  if(state.filter!=="all") hs = hs.filter(h=>h.t===state.filter);
  return hs;
}
function fmtType(t){ return TYPES[t]||t; }

function renderFiles(){
  const box = $("#filelist"); box.innerHTML = "";
  const mk = (id, name, sub, subcls, count) => {
    const b = document.createElement("button");
    b.className = "filerow";
    b.setAttribute("aria-selected", String(state.fileId)===String(id));
    b.innerHTML = `<span class="sq"></span>
      <span class="meta"><span class="fname">${esc(name)}</span>
      <span class="fsub ${subcls||""}">${esc(sub)}</span></span>
      <span class="fcount num">${count}</span>`;
    b.onclick = ()=>{ state.fileId=id; renderAll(); renderNoteline(); };
    box.appendChild(b);
  };
  mk("all","批次汇总",`${state.files.length} 个文件 · ${state.files.filter(f=>f.err).length} 个跳过`,"", allHits().length);
  for(const f of state.files){
    mk(f.id, f.name, f.err ? "扫描失败" : (f.warnings.length ? "含批注/修订，注意" : `${f.hits.length} 处命中`),
       f.err ? "err" : (f.warnings.length ? "warn" : ""), f.err ? "—" : f.hits.length);
  }
}

function renderHits(){
  const list = $("#hitlist"); list.innerHTML = "";
  const hs = shownHits();
  $("#total-count").textContent = hs.length;
  for(const h of hs){
    const ex = state.excluded.has(h.key);
    const row = document.createElement("div");
    row.className = "hitrow" + (ex?" excluded":"");
    row.innerHTML = `
      <input type="checkbox" class="check" ${ex?"":"checked"} aria-label="抹除该处">
      <div class="body">
        <div class="line1">
          <span class="tag t-${TAGCLS[h.t]}">${fmtType(h.t)}</span>
          <span class="orig">${esc(h.o)}</span>
          <span class="exlabel">已排除，不抹除</span>
          <span class="loc num">${esc(h.l)}</span>
        </div>
        <div class="ctx">${esc(h.c).replace("「"+esc(h.o)+"」", "「<mark>"+esc(h.o)+"</mark>」")}</div>
      </div>`;
    row.querySelector(".check").addEventListener("change", ev=>{
      if(ev.target.checked) state.excluded.delete(h.key); else state.excluded.add(h.key);
      renderTally(); renderHits();
    });
    list.appendChild(row);
  }
}

function renderNoteline(){
  const f = state.files.find(x=>String(x.id)===String(state.fileId));
  const notes = [];
  if(state.fileId==="all"){
    for(const x of state.files){ if(x.err) notes.push(`${x.name}：${x.err}`); }
  }else if(f){
    if(f.err) notes.push(f.err);
    for(const w of (f.warnings||[])) notes.push(w);
  }
  $("#noteline").className = "noteline" + (notes.length?" open":"");
  $("#noteline").textContent = notes.join(" ");
}

function renderTally(){
  const hs = allHits();
  const per = t => hs.filter(h=>h.t===t).length;
  $("#t-amount").textContent = per("AMOUNT");
  $("#t-idcard").textContent = per("ID_CARD");
  $("#t-phone").textContent = per("PHONE");
  $("#t-bank").textContent = per("BANK_ACCOUNT");
  $("#t-credit").textContent = per("CREDIT_CODE");
  $("#t-email").textContent = per("EMAIL");
  $("#t-person").textContent = per("PERSON");
  $("#t-org").textContent = per("ORG");
  const checked = hs.filter(h=>!state.excluded.has(h.key)).length;
  $("#c-scanned").textContent = state.files.filter(f=>!f.err).length;
  $("#c-hits").textContent = hs.length;
  $("#seg-hits").classList.toggle("warn", hs.length>0);
  $("#c-excluded").textContent = state.excluded.size;
  $("#sel-count").textContent = shownHits().filter(h=>!state.excluded.has(h.key)).length;
  $("#pending-count").textContent = checked;
  $("#excl-count").textContent = state.excluded.size;
  $("#btn-apply").textContent = `执行抹除（${checked}）`;
  $("#btn-apply").disabled = checked===0;
}
function renderAll(){ renderFiles(); renderHits(); renderTally(); renderNoteline(); }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }

/* ================= 抹除 ================= */
const veil = $("#veil");
$("#btn-apply").onclick = async ()=>{
  const n = allHits().filter(h=>!state.excluded.has(h.key)).length;
  const fileIds = new Set(allHits().filter(h=>!state.excluded.has(h.key)).map(h=>h.key.split(":")[0]));
  $("#dlg-body").innerHTML =
    `将对 <b>${fileIds.size}</b> 个文件执行 <b class="num">${n}</b> 处抹除：
      <ul>
        <li>生成脱敏文件（保留原格式）<span class="num-r">×${fileIds.size}</span></li>
        <li>生成映射表 JSON<span class="num-r">×1</span></li>
        <li>生成审查报告 MD<span class="num-r">×1</span></li>
      </ul>
      <div class="dwarn">PDF 将从内容流真删除、不可恢复；请确认已勾选的每一处都核对过。此操作不联网，产物保存在本机。</div>`;
  veil.classList.add("open");
};
$("#dlg-cancel").onclick = ()=> veil.classList.remove("open");
$("#dlg-ok").onclick = async ()=>{
  veil.classList.remove("open");
  const byFile = {};
  for(const f of state.files){
    if(f.err) continue;
    const sels = [];
    for(let i=0;i<f.hits.length;i++){
      const h = f.hits[i];
      if(!state.excluded.has(f.id+":"+i)) sels.push([h.t, h.o, h.occ]);
    }
    byFile[String(f.id)] = {path:f.path, selections:sels};
  }
  try{
    let outdir = state.outdir;
    if(!outdir){
      const first = state.files.find(f=>!f.err);
      const r = await call("choose_outdir", first ? folderOfFull(first.path) : null);
      outdir = r.dir;
      if(!outdir) return;
      state.outdir = outdir;
    }
    const payload = { outdir, use_ner: $("#ner-switch").getAttribute("aria-checked")==="true",
                      files: Object.values(byFile) };
    const r = await call("apply_batch", payload);
    renderDone(r);
    const fl = $("#flash"); fl.classList.remove("go"); void fl.offsetWidth; fl.classList.add("go");
    setTimeout(()=> setView("done"), 240);
  }catch(e){ alert(e.message || String(e)); }
};
function folderOfFull(p){ const s = String(p); const i = Math.max(s.lastIndexOf("\\"), s.lastIndexOf("/")); return s.slice(0, i); }

function renderDone(r, title){
  const isRestore = title === "还原完成";
  $("#done-stamp-title").textContent = isRestore ? "还原完成" : "抹除完成";
  $("#done-sub").textContent = isRestore
    ? "占位符已按映射表换回原文。PDF 原位回填，版式可能与原件有细微差异。"
    : "PDF 从内容流真删除，不可复制恢复；Word 以占位符替换，保留格式。占位符全局一致。";
  $("#mapping-row").style.display = isRestore ? "none" : "";
  $("#done-stamp-n").textContent =
    `${r.results.filter(x=>x.ok).reduce((a,x)=>a+x.count,0)} 处 · ${r.results.filter(x=>x.ok).length} 个文件`;
  const box = $("#outlist"); box.innerHTML = "";
  for(const res of r.results){
    const d = document.createElement("div");
    d.className = "outrow";
    if(res.ok){
      d.innerHTML = `<div><div class="oname">${esc(res.out.split(/[\\/]/).pop())}</div>
        <div class="osub num">${res.count} 处${(res.warnings&&res.warnings.length)?" · 含批注/修订请人工检查":""}</div></div>
        <span class="ospacer"></span><button class="btn">打开所在文件夹</button>`;
      d.querySelector("button").onclick = ()=> call("open_path", res.out);
    }else{
      d.innerHTML = `<div><div class="oname">${esc(res.name)}</div>
        <div class="osub bad">${esc(res.error||"处理失败")}</div></div>`;
    }
    box.appendChild(d);
  }
  const oks = r.results.filter(x=>x.ok);
  if(oks.length){
    mapFiles = oks.map(x=>({
      label: x.name.replace(/\.\w+$/, ""),
      mp: x.out.replace(/_脱敏\.\w+$/, "_脱敏_映射表.json"),
    }));
    curMap = 0;
    $("#mapping-name").textContent = mapFiles[0].mp.split(/[\\/]/).pop();
    $("#btn-map").onclick = async ()=>{
      const open = !$("#mapview").classList.contains("open");
      $("#mapview").classList.toggle("open", open);
      $("#maptabs").classList.toggle("open", open && mapFiles.length>1);
      if(open) await loadMapping();
    };
    const tabs = $("#maptabs"); tabs.innerHTML = "";
    mapFiles.forEach((mf, i)=>{
      const b = document.createElement("button");
      b.className = "chip";
      b.textContent = mf.label;
      b.title = mf.mp.split(/[\\/]/).pop();
      b.setAttribute("aria-pressed", String(i===curMap));
      b.onclick = async ()=>{
        curMap = i;
        $$("#maptabs .chip").forEach((x, j)=>x.setAttribute("aria-pressed", String(j===i)));
        $("#mapping-name").textContent = mf.mp.split(/[\\/]/).pop();
        $("#mapview").classList.add("open");
        $("#maptabs").classList.add("open");
        await loadMapping();
      };
      tabs.appendChild(b);
    });
  }
};
async function loadMapping(){
  const mf = mapFiles[curMap];
  if(!mf) return;
  $("#mapview").textContent = "读取中…";
  const m = await call("read_mapping", mf.mp);
  $("#mapview").textContent = m.ok ? m.text : (m.error || "读取失败");
}

/* 未捕获错误一律可见：红色 toast，杜绝"点了没反应"的静默失败 */
function toastErr(msg){
  const t = document.createElement("div");
  t.style.cssText = "position:fixed;left:14px;bottom:64px;z-index:99;background:var(--cinnabar-deep);color:#fff;padding:9px 14px;font-size:12px;max-width:60%;box-shadow:0 10px 24px rgba(0,0,0,.28)";
  t.textContent = "出错了：" + msg;
  document.body.appendChild(t);
  setTimeout(()=> t.remove(), 8000);
}
window.addEventListener("error", e=> toastErr(e.message || "脚本异常"));
window.addEventListener("unhandledrejection", e=> toastErr(String((e.reason && e.reason.message) || e.reason || "异步调用失败")));

$("#btn-open-folder").onclick = async ()=>{
  if(!state.outdir){ toastErr("还没有输出目录——请先执行一次抹除或还原"); return; }
  try{ await call("open_path", state.outdir); }
  catch(e){ toastErr("打开文件夹失败：" + (e.message || e)); }
};
$("#btn-restore").onclick = async ()=>{
  try{
    const r = await call("pick_files");
    if(!r.paths || !r.paths.length) return;
    const res = await call("restore_batch", r.paths);
    renderDone(res, "还原完成");
    state.outdir = res.outdir || state.outdir;
    setView("done");
  }catch(e){ alert(e.message || String(e)); }
};
$("#btn-report").onclick = ()=> call("open_path", state.outdir || (state.files[0]&&state.files[0].path) || ".");
$("#btn-again").onclick = ()=>{ try{
  state.files=[]; state.outdir=null; state.excluded=new Set();
  state.fileId="all"; state.filter="all";   // 复位选中文件与筛选，否则渲染会按旧 id 找已清空的文件
  $$("#hitsbar .chip").forEach(x=>x.setAttribute("aria-pressed", x.dataset.f==="all" ? "true" : "false"));
  renderAll(); setView("empty");
}catch(e){ toastErr(e.message || String(e)); } };
$("#btn-restart").onclick = ()=> $("#btn-again").onclick();

/* ================= 词库与 NER ================= */
const drawer = $("#drawer");
$("#open-lexicon").onclick = ()=> drawer.classList.add("open");
$("#open-lexicon2").onclick = async ()=>{ drawer.classList.remove("open"); await call("open_lexicon"); };
$("#drawer-close").onclick = ()=> drawer.classList.remove("open");
$("#ner-switch").onclick = e=>{
  const on = e.currentTarget.getAttribute("aria-checked")==="true";
  e.currentTarget.setAttribute("aria-checked", String(!on));
  if(state.files.length){
    scanPaths(state.files.map(f=>f.path));  // NER 变更后重扫当前批次
  }
};

/* ================= 筛选 ================= */
$$("#hitsbar .chip").forEach(c=> c.onclick = ()=>{
  $$("#hitsbar .chip").forEach(x=>x.setAttribute("aria-pressed","false"));
  c.setAttribute("aria-pressed","true");
  state.filter = c.dataset.f; renderHits(); renderTally();
});

setView("empty");
