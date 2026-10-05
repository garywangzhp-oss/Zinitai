// 复现：选中具体文件 → 开始新批次 → 崩溃 "reading 'hits'"
const fs = require("fs");
const path = require("path");
const { JSDOM } = require(path.join(__dirname, "jsdom_env", "node_modules", "jsdom"));

const html = fs.readFileSync(path.join(__dirname, "..", "gui", "index.html"), "utf-8");
const errors = [];

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  url: "http://127.0.0.1:1/index.html",
  pretendToBeVisual: true,
  beforeParse(window) {
    window.alert = (m) => errors.push("ALERT: " + m);
    window.pywebview = {
      api: {
        pick_files: async () => ({ paths: ["D:/x/劳动合同.pdf"] }),
        scan_batch: async () => ({
          ok: true,
          files: [{ id: 0, path: "D:/x/劳动合同.pdf", name: "劳动合同.pdf",
                    err: null, warnings: [], hits: [
                      { t: "AMOUNT", o: "10000 元", c: "…「10000 元」…", l: "第7页", occ: 0 },
                    ] }],
        }),
        apply_batch: async () => ({ ok: true, outdir: "D:/out",
          results: [{ name: "劳动合同.pdf", out: "D:/out/劳动合同_脱敏.pdf", count: 1, warnings: [], ok: true }] }),
        choose_outdir: async () => ({ dir: "D:/out" }),
        open_path: async () => ({ ok: true }),
        read_mapping: async () => ({ ok: true, text: "[]" }),
        restore_batch: async () => ({ ok: true, outdir: "D:/out", results: [] }),
        open_lexicon: async () => ({ ok: true }),
      },
    };
    window.addEventListener("error", (e) => errors.push("PAGE ERROR: " + e.message));
    window.addEventListener("unhandledrejection", (e) =>
      errors.push("UNHANDLED REJECTION: " + String(e.reason && e.reason.message || e.reason)));
  },
});

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const { window } = dom;
  const doc = window.document;
  await sleep(100);

  // 走真实扫描流程
  await window.scanPaths(["D:/x/劳动合同.pdf"]);
  await sleep(30);
  console.log("扫描后视图:", doc.querySelector("#ws-review").style.display,
    "| 命中:", doc.querySelectorAll(".hitrow").length);

  // 点选具体文件（复现用户操作：fileId 记住具体文件）
  const fileRows = doc.querySelectorAll("#filelist .filerow");
  fileRows[1].click(); // 第 1 个具体文件（非批次汇总）
  await sleep(20);
  console.log("已点选具体文件");

  // 抹除 → 完成屏
  await window.pywebview.api.apply_batch; // noop 保序
  window.renderDone({
    ok: true, outdir: "D:/out",
    results: [{ name: "劳动合同.pdf", out: "D:/out/劳动合同_脱敏.pdf", count: 1, warnings: [], ok: true }],
  }, "抹除完成");
  window.setView("done");
  console.log("完成屏显示:", doc.querySelector("#ws-done").style.display);

  // ★ 关键操作：开始新批次
  doc.querySelector("#btn-again").click();
  await sleep(50);

  // toastErr 的提示条（若有）
  const toasts = [...doc.querySelectorAll("body > div")]
    .map(d => d.textContent).filter(t => t && t.startsWith("出错了"));
  console.log("点击后 ws-empty:", doc.querySelector("#ws-empty").style.display,
    "| ws-done:", doc.querySelector("#ws-done").style.display);
  console.log("toast:", toasts.length ? toasts : "无");
  console.log("errors:", errors.length ? errors : "无");
  if (errors.length) process.exit(1);
}

main().then(
  () => { console.log("RESULT: PASS"); process.exit(0); },
  () => { console.log("RESULT: FAIL"); process.exit(1); }
);
