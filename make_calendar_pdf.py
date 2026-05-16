#!/usr/bin/env python3
"""Generate a Thai fortune calendar PDF from the reading data."""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, glob

W, H = A4
MARGIN = 20 * mm

# ── Try to register a Thai font ──
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
THAI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansThai-Regular.ttf",
    "/usr/share/fonts/noto/NotoSansThai-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/opentype/tlwg/Loma.ttf",
]
THAI_FONTS_BOLD = [
    "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansThai-Bold.ttf",
    "/usr/share/fonts/noto/NotoSansThai-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
    "/usr/share/fonts/opentype/tlwg/Loma-Bold.ttf",
]

for p in THAI_FONTS:
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont("ThaiFont", p))
        FONT = "ThaiFont"
        break
for p in THAI_FONTS_BOLD:
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont("ThaiFontBold", p))
        FONT_BOLD = "ThaiFontBold"
        break

# ── Color palette ──
BG_DARK = HexColor("#0f0f1a")
CARD_BG = HexColor("#1a1a2e")
ACCENT_GOLD = HexColor("#f6d365")
ACCENT_GREEN = HexColor("#43e97b")
ACCENT_RED = HexColor("#f5576c")
ACCENT_PINK = HexColor("#f093fb")
ACCENT_BLUE = HexColor("#667eea")
TEXT_MAIN = HexColor("#e0d8d0")
TEXT_MUTED = HexColor("#888888")
CARD_BORDER = HexColor("#ffffff1a")

# ── Month data ──
MONTHS = [
    {
        "id": 1, "thai": "พฤษภาคม 2569", "eng": "May 2026",
        "tone": "neutral",
        "tags": [("blue", "ย้ายที่อยู่"), ("pink", "รักใหม่")],
        "events": [
            ("🏠", "อาจมีการย้ายที่อยู่ใหม่"),
            ("🚧", "สร้างบ้าน/ต่อเติม อาจล่าช้ากว่าแผน"),
            ("💖", "ช่วงเจอความรักหรือความสัมพันธ์ใหม่"),
        ],
        "warnings": []
    },
    {
        "id": 2, "thai": "มิถุนายน 2569", "eng": "Jun 2026",
        "tone": "good",
        "tags": [("green", "ปัง"), ("pink", "รักใหม่")],
        "events": [
            ("🤝", "สร้างคอนเนคชั่นกับผู้ใหญ่ — อุปถัมภ์ดี"),
            ("✈️", "เดินทางขยายประสบการณ์ — โอกาสใหม่"),
            ("💖", "ความสัมพันธ์มั่นคง > ปริมาณ"),
            ("💞", "ช่วงเจอความรักหรือความสัมพันธ์ใหม่"),
        ],
        "warnings": [
            ("⚠️", "งานกับคนอื่นติดขัด — ห้ามให้ใครยืมเงิน/ค้ำประกัน"),
            ("💰", "ห้ามให้กู้ยืม — เสี่ยงเสียเพื่อน"),
        ]
    },
    {
        "id": 3, "thai": "กรกฎาคม 2569", "eng": "Jul 2026",
        "tone": "good",
        "tags": [("green", "ปัง")],
        "events": [
            ("🤲", "ช่วยเหลือคน — เสริมดวงแรง"),
            ("🙏", "ทำบุญ ทำทาน — ผลชัดเจน"),
            ("💫", "ใช้เสน่ห์สร้างสัมพันธ์ใหม่"),
        ],
        "warnings": [
            ("⚠️", "ทำงานกับคนอื่น — สื่อสารให้ชัด อย่าให้เข้าใจผิด"),
            ("⚠️", "อย่าทำอะไรผิดกฎหมาย"),
            ("🏥", "สุขภาพ: ทำงานหนัก + กดดัน — ดูแลการกิน นอน ออกกำลัง"),
        ]
    },
    {
        "id": 4, "thai": "สิงหาคม 2569", "eng": "Aug 2026",
        "tone": "mixed",
        "tags": [("green", "ปัง"), ("red", "ระวัง"), ("gold", "เสี่ยงโชค")],
        "events": [
            ("🎨", "ความคิดสร้างสรรค์สูง — ศิลปะ/เขียน/ดนตรี"),
            ("🧘", "ออกบวช/หาความสงบ — ทางเลือกที่ดี"),
        ],
        "warnings": [
            ("⚠️", "โฟกัสตัวเองและเป้าหมาย — อย่ากังวลเรื่องคู่ครอง"),
            ("⚠️", "ระวังซุ่มซ่าม — เจ็บตัว/ได้แผล"),
            ("💰", "เดือนเสี่ยงโชค — ซื้อหวยได้"),
        ]
    },
    {
        "id": 5, "thai": "กันยายน 2569", "eng": "Sep 2026",
        "tone": "mixed",
        "tags": [("red", "ระวัง"), ("gold", "เสี่ยงโชค")],
        "events": [
            ("👫", "แฟน/คู่ครองอาจมีปัญหาให้ช่วยแก้"),
            ("🔄", "เปลี่ยนตำแหน่ง หรือย้ายที่ทำงาน"),
        ],
        "warnings": [
            ("⚠️", "เปิดใจแสดงความรู้สึก — อย่าเงียบ"),
            ("⚠️", "การไม่แสดงออก = คนรอบข้างเข้าใจผิด"),
            ("💰", "เดือนเสี่ยงโชค — ซื้อหวยได้"),
        ]
    },
    {
        "id": 6, "thai": "ตุลาคม 2569", "eng": "Oct 2026",
        "tone": "neutral",
        "tags": [("pink", "รัก ❤️")],
        "events": [
            ("💬", "ดูแลคนรัก — พูดคุยบ่อยๆ ปรับความเข้าใจ"),
        ],
        "warnings": []
    },
    {
        "id": 7, "thai": "พฤศจิกายน 2569", "eng": "Nov 2026",
        "tone": "mixed",
        "tags": [("red", "ระวัง"), ("gold", "เสี่ยงโชค"), ("teal", "อิสระ")],
        "events": [
            ("🧘", "ลองทำสิ่งใหม่ — ความสุขในแบบตัวเอง"),
            ("💡", "อย่าให้ความคิดว่าต้องมีคู่ ฉุดรั้งความสุข"),
        ],
        "warnings": [
            ("⚠️", "ปัญหากับผู้ใหญ่ / ทำงานทางไกลระวังเรื่องเดือดร้อน"),
            ("🏥", "เสี่ยงเกิดแผล/ผ่าตัด — มีสติทุกกิจกรรม"),
            ("💰", "เดือนเสี่ยงโชค — ซื้อหวยได้"),
        ]
    },
    {
        "id": 8, "thai": "ธันวาคม 2569", "eng": "Dec 2026",
        "tone": "mixed",
        "tags": [("green", "ปัง"), ("red", "ระวัง"), ("gold", "เสี่ยงโชค"), ("blue", "เดินทาง")],
        "events": [
            ("✈️", "ใช้ความสามารถ + เดินทางต่อยอดงาน โดยเฉพาะต่างประเทศ"),
            ("💞", "ใส่ใจความสัมพันธ์ที่จริงใจ — อย่าเหงา"),
        ],
        "warnings": [
            ("⚠️", "มีสติเตรียมพร้อม — โอกาสดีกำลังมา"),
            ("⚠️", "ห้ามให้ใครยืมเงิน"),
            ("🏥", "เครียดเรื่องงาน+เงิน — จัดระบบชีวิต หาเวลาพัก"),
            ("⚠️", "ระวังอุบัติเหตุ/ของมีคม"),
            ("💰", "เดือนเสี่ยงโชค — ซื้อหวยได้"),
        ]
    },
    {
        "id": 9, "thai": "มกราคม 2570", "eng": "Jan 2027",
        "tone": "good",
        "tags": [("green", "ปัง")],
        "events": [
            ("🚀", "ลงมือทำโปรเจกต์ที่วางแผนไว้ — ดวงหนุนสำเร็จ"),
            ("🤝", "ใช้เสน่ห์สร้างคอนเนคชั่น — โอกาสใหม่"),
        ],
        "warnings": [
            ("⚠️", "ระวังบริหารทีมงาน — อย่าให้เพื่อนยืมเงิน"),
        ]
    },
    {
        "id": 10, "thai": "กุมภาพันธ์ 2570", "eng": "Feb 2027",
        "tone": "mixed",
        "tags": [("green", "ปัง"), ("red", "ระวัง")],
        "events": [
            ("🎨", "ปลดปล่อยความคิดสร้างสรรค์ — ศิลปะ/เรียนรู้"),
            ("🧘", "หาความสงบ — สมาธิ/ธรรมชาติ"),
        ],
        "warnings": [
            ("🏥", "เครียดจากธุรกิจ (ครอบครัว+ต่างชาติ) — ดูแลสุขภาพ"),
            ("👨‍👩‍👧‍👧", "ใช้เวลากับครอบครัว — สื่อสารความห่วงใย"),
            ("⚠️", "อย่าปล่อยให้กลัวจนไม่ไปหาหมอ"),
        ]
    },
    {
        "id": 11, "thai": "มีนาคม 2570", "eng": "Mar 2027",
        "tone": "mixed",
        "tags": [("green", "ปัง"), ("red", "ระวัง")],
        "events": [
            ("👑", "คบคนมีฐานะ — เสริมฐานะการเงิน"),
            ("🤝", "ร่วมงานกับคนมีประสบการณ์ — โตในอนาคต"),
        ],
        "warnings": [
            ("⚠️", "ความรัก: กระทบกระทั่งง่าย — พูดคุยกันดีๆ"),
            ("💰", "วางแผนการเงินจริงจัง — หักค่าใช้จ่ายไม่จำเป็น"),
            ("💬", "สื่อสารความรู้สึก — อย่าเก็บไว้คนเดียว"),
            ("🤗", "เปิดรับมิตรภาพใหม่ — ทำให้ชีวิตสมดุล"),
        ]
    },
    {
        "id": 12, "thai": "เมษายน 2570", "eng": "Apr 2027",
        "tone": "good",
        "tags": [("green", "ปัง"), ("red", "ระวัง"), ("blue", "เปลี่ยนงาน")],
        "events": [
            ("🧠", "วิเคราะห์เก่ง — เรียนรู้ทักษะใหม่ไว"),
            ("📚", "ถ่ายทอดความรู้ — เป็นครู/ที่ปรึกษา"),
            ("🔄", "เปลี่ยนตำแหน่ง/สายอาชีพ/ที่ทำงาน"),
            ("✈️", "เดินทางไกลเพื่อทำงาน"),
        ],
        "warnings": [
            ("⚠️", "เลี่ยงปัญหากับคนรอบข้าง — อย่าใจร้อน"),
            ("⚖️", "ระวังข้อพิพาท/คดีความ"),
        ]
    },
]

TAG_COLORS = {
    "green": (HexColor("#43e97b"), HexColor("#43e97b27")),
    "red": (HexColor("#f5576c"), HexColor("#f5576c27")),
    "blue": (HexColor("#667eea"), HexColor("#667eea27")),
    "pink": (HexColor("#f093fb"), HexColor("#f093fb27")),
    "gold": (HexColor("#f6d365"), HexColor("#f6d36527")),
    "teal": (HexColor("#38f9d7"), HexColor("#38f9d727")),
}

TONE_COLORS = {
    "good": ACCENT_GREEN,
    "warn": ACCENT_RED,
    "mixed": ACCENT_GOLD,
    "neutral": ACCENT_BLUE,
}


def draw_card_bg(c, x, y, w, h, tone):
    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BORDER)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    bar_color = TONE_COLORS.get(tone, ACCENT_BLUE)
    c.setFillColor(bar_color)
    c.roundRect(x, y + h - 4, w, 4, [0, 0, 2, 2], fill=1, stroke=0)


def draw_tag(c, x, y, text, color_key):
    fg, bg = TAG_COLORS.get(color_key, (TEXT_MUTED, HexColor("#ffffff0d")))
    c.setFillColor(bg)
    tw = pdfmetrics.stringWidth(text, FONT, 8) + 12
    c.roundRect(x, y - 10, tw, 16, 99, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont(FONT_BOLD if FONT_BOLD else FONT, 8)
    c.drawString(x + 6, y - 7, text)


def draw_circle_emoji(c, x, y, emoji):
    c.setFont(FONT, 11)
    c.drawString(x, y - 4, emoji)


def build_pdf(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("ปฏิทินดวงชะตา 2569–2570")
    c.setAuthor("ซินแส")

    # ── Cover page ──
    c.setFillColor(BG_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Decorative top bar
    c.setFillColor(ACCENT_GOLD)
    c.rect(0, H - 6*mm, W, 6*mm, fill=1, stroke=0)
    c.rect(0, 0, W, 3*mm, fill=1, stroke=0)

    c.setFillColor(ACCENT_GOLD)
    c.setFont(FONT_BOLD if FONT_BOLD else FONT, 36)
    c.drawCentredString(W / 2, H - 70*mm, "✦ ปฏิทินดวงชะตา ✦")

    c.setFillColor(TEXT_MAIN)
    c.setFont(FONT, 18)
    c.drawCentredString(W / 2, H - 85*mm, "พ.ศ. 2569 — 2570")

    c.setFont(FONT, 13)
    c.drawCentredString(W / 2, H - 95*mm, "พยากรณ์รายเดือนตามตำราซินแส")

    c.setFillColor(TEXT_MUTED)
    c.setFont(FONT, 10)
    c.drawCentredString(W / 2, H - 105*mm, "พฤษภาคม 2569 – เมษายน 2570")

    # Legend
    legend_y = H - 125*mm
    legend_items = [
        (ACCENT_GREEN, "เดือนปัง"),
        (ACCENT_RED, "เดือนระวัง"),
        (ACCENT_GOLD, "ผสม/กลาง"),
        (ACCENT_BLUE, "ปกติ"),
    ]
    for i, (color, text) in enumerate(legend_items):
        lx = W/2 - 60*mm + i * 30*mm
        c.setFillColor(color)
        c.circle(lx, legend_y + 2, 3, fill=1, stroke=0)
        c.setFillColor(TEXT_MAIN)
        c.setFont(FONT, 9)
        c.drawString(lx + 5, legend_y - 2, text)

    c.showPage()

    # ── Calendar pages ──
    for month in MONTHS:
        x0 = MARGIN
        y0 = MARGIN
        pw = W - 2 * MARGIN
        ph = H - 2 * MARGIN

        # Background
        c.setFillColor(BG_DARK)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        card_h = ph
        draw_card_bg(c, x0, y0, pw, card_h, month["tone"])

        # Month title
        c.setFillColor(TEXT_MAIN)
        c.setFont(FONT_BOLD if FONT_BOLD else FONT, 22)
        c.drawString(x0 + 12*mm, y0 + card_h - 28*mm, month["thai"])
        c.setFillColor(TEXT_MUTED)
        c.setFont(FONT, 12)
        c.drawString(x0 + 12*mm, y0 + card_h - 36*mm, month["eng"])

        # Tags
        tag_x = x0 + 12*mm
        tag_y = y0 + card_h - 46*mm
        for tag_color, tag_text in month["tags"]:
            draw_tag(c, tag_x, tag_y, tag_text, tag_color)
            tag_x += pdfmetrics.stringWidth(tag_text, FONT, 8) + 22

        # Events
        ey = y0 + card_h - 62*mm
        c.setFont(FONT, 11)
        for icon, text in month["events"]:
            c.setFillColor(ACCENT_GREEN)
            c.setFont(FONT, 14)
            c.drawString(x0 + 16*mm, ey, icon)
            c.setFillColor(TEXT_MAIN)
            c.setFont(FONT, 10)
            c.drawString(x0 + 30*mm, ey + 1, text)
            ey -= 11*mm

        # Warnings section
        if month["warnings"]:
            ey -= 3*mm
            # Divider line
            c.setStrokeColor(HexColor("#ffffff14"))
            c.setLineWidth(0.5)
            c.line(x0 + 16*mm, ey + 4*mm, x0 + pw - 16*mm, ey + 4*mm)
            ey -= 2*mm

            for icon, text in month["warnings"]:
                c.setFillColor(ACCENT_RED)
                c.setFont(FONT, 13)
                c.drawString(x0 + 16*mm, ey, icon)
                c.setFillColor(TEXT_MAIN)
                c.setFont(FONT, 10)
                c.drawString(x0 + 30*mm, ey + 1, text)
                ey -= 10*mm

        c.showPage()

    # ── Summary page ──
    c.setFillColor(BG_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_card_bg(c, x0, y0, pw, ph, "good")

    c.setFillColor(ACCENT_GOLD)
    c.setFont(FONT_BOLD if FONT_BOLD else FONT, 20)
    c.drawString(x0 + 12*mm, y0 + ph - 28*mm, "✦ สรุปประจำปี")

    summaries = [
        ("🙏", "ทำบุญช่วยเหลือผู้อื่น = เสริมดวงแรงที่สุดในปีนี้"),
        ("🧠", "เรียนรู้ไว — ถ่ายทอดความรู้ให้คนอื่น"),
        ("✈️", "เดินทางต่างประเทศ/ไกลบ้าน — เปิดโลกใหม่"),
        ("💫", "เสน่ห์แรง — คนอยากเข้าใกล้"),
        ("🎨", "ความคิดสร้างสรรค์นอกกรอบ"),
        ("💼", "โฟกัสอาชีพธาตุทอง (IT, law, finance, management)"),
        ("🌏", "ค้าข้ามประเทศ/ต่างชาติ — ดวงหนุน"),
        ("👴", "สร้างสัมพันธ์กับผู้ใหญ่"),
        ("💰", "กันเงินสำรอง 6 เดือน — ห้ามลงทุนเสี่ยง"),
        ("💬", "สื่อสารกับคนรักให้มากขึ้น"),
    ]

    sy = y0 + ph - 50*mm
    for icon, text in summaries:
        c.setFillColor(ACCENT_GREEN)
        c.setFont(FONT, 14)
        c.drawString(x0 + 16*mm, sy, icon)
        c.setFillColor(TEXT_MAIN)
        c.setFont(FONT, 10)
        c.drawString(x0 + 30*mm, sy + 1, text)
        sy -= 10*mm

    # Color guide
    color_guide_y = y0 + 12*mm
    c.setFillColor(ACCENT_GOLD)
    c.setFont(FONT_BOLD if FONT_BOLD else FONT, 12)
    c.drawString(x0 + 12*mm, color_guide_y, "สีมงคล:")
    c.setFillColor(ACCENT_GREEN)
    c.setFont(FONT, 10)
    c.drawString(x0 + 12*mm + 35*mm, color_guide_y, "เขียว (ไม้)")
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x0 + 12*mm + 65*mm, color_guide_y, "ฟ้า/น้ำเงิน/ดำ (น้ำ)")
    c.setFillColor(ACCENT_RED)
    c.setFont(FONT_BOLD if FONT_BOLD else FONT, 10)
    c.drawString(x0 + 12*mm, color_guide_y - 8*mm, "สีควรเลี่ยง: น้ำตาล/เหลือง (ดิน), ขาว/เงิน (ทอง), แดง/ชมพู (ไฟ)")

    c.showPage()
    c.save()
    print(f"✅ PDF saved: {path}")


if __name__ == "__main__":
    build_pdf("/home/opencode/horo/fortune-calendar.pdf")
