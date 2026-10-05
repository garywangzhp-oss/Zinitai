"""生成合成合同样本：tests/samples/示例采购合同.docx + 示例服务合同.pdf

样本覆盖全部 5 类敏感信息 + 一个 Luhn 校验应拒识的 13 位订单号。
用法：python tests/make_samples.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def luhn_complete(prefix: str) -> str:
    """给 18 位前缀补一个校验位，使整体通过 Luhn。"""
    for d in "0123456789":
        cand = prefix + d
        total = 0
        for i, ch in enumerate(reversed(cand)):
            v = int(ch)
            if i % 2 == 1:
                v *= 2
                if v > 9:
                    v -= 9
            total += v
        if total % 10 == 0:
            return cand
    raise AssertionError("unreachable")


def make_docx(out: Path, bank_a: str):
    from docx import Document

    doc = Document()
    doc.add_heading("设备采购合同", level=1)
    doc.add_paragraph("合同编号：CG-2026-0818（编号非敏感，不应被抹除）")
    doc.add_paragraph("甲方（买方）：北京华创示例科技有限公司")
    doc.add_paragraph("乙方（卖方）：上海智造设备有限公司")

    info = doc.add_table(rows=6, cols=2)
    rows = [
        ("甲方统一社会信用代码", "91110108MA01B2C4XW"),
        ("法定代表人及身份证号", "张伟民 11010519900307891X"),
        ("联系电话", "13812345678"),
        ("乙方联系电话", "021-65558899"),
        ("开户银行及账号", f"工商银行北京分行 {bank_a}"),
        ("采购订单号", "1234567890123（13 位但未过 Luhn，不应按银行账号抹除）"),
    ]
    for i, (k, v) in enumerate(rows):
        info.rows[i].cells[0].text = k
        info.rows[i].cells[1].text = v

    doc.add_heading("第一条 合同价款", level=2)
    doc.add_paragraph("设备总价款为￥128,500.00，含税。")
    doc.add_paragraph("上述总价大写：人民币壹拾贰万捌仟伍佰元整。")
    doc.add_heading("第二条 付款方式", level=2)
    doc.add_paragraph("合同签订后 7 日内支付预付款 3.5 万元；到货验收合格后支付尾款 93,500 元。")
    doc.add_paragraph("履约保证金 5000 元于质保期满后 10 个工作日内无息退还。")
    doc.add_paragraph("本合同自双方盖章之日起生效，一式肆份。")
    doc.save(out)
    print(f"  生成 {out}")


def make_pdf(out: Path, bank_b: str):
    import pymupdf as fitz

    doc = fitz.open()
    page = doc.new_page()
    lines = [
        ("技术开发服务合同", 18),
        ("合同编号：JS-2026-0330（编号非敏感，不应被抹除）", 11),
        ("甲方：广州云帆网络科技有限公司", 11),
        ("统一社会信用代码：91440101MA9Y2K7Q8R", 11),
        ("项目负责人：李娜，电话 13699998888", 11),
        ("乙方负责人身份证号：44010619881122334X", 11),
        ("乙方联系电话：020-83334455", 11),
        (f"收款账户：招商银行广州分行 {bank_b}", 11),
        ("服务费总额为￥350,000.00（含税）。", 11),
        ("大写金额：人民币叁拾伍万元整。", 11),
        ("首期款 150,000 元于合同生效后 5 个工作日内支付。", 11),
        ("违约金按合同总价的 0.05% 逐日计算。", 11),
        ("本协议一式两份，双方各执一份。", 11),
    ]
    y = 72
    for text, size in lines:
        page.insert_text((72, y), text, fontname="china-s", fontsize=size)
        y += size + 10
    doc.save(out)
    doc.close()
    print(f"  生成 {out}")


def main():
    out_dir = Path(__file__).parent / "samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    bank_a = luhn_complete("62220202001122334")   # 18 位
    bank_b = luhn_complete("622588013770998")     # 16 位
    print(f"样本银行账号（Luhn 有效）：{bank_a} / {bank_b}")
    make_docx(out_dir / "示例采购合同.docx", bank_a)
    make_pdf(out_dir / "示例服务合同.pdf", bank_b)


if __name__ == "__main__":
    main()
