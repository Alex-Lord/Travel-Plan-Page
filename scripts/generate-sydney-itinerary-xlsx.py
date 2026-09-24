#!/usr/bin/env python3
"""Generate a print-ready Sydney itinerary workbook from the local trip source."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "private" / "trip-data.json"
DESTINATION = ROOT / "Sydney-行程-A4打印版.xlsx"

NAVY = "17365D"
BLUE = "2C7DA0"
PALE_BLUE = "DCECF5"
PALE_SAND = "F8F1E7"
MUTED = "5E6B76"
WHITE = "FFFFFF"
THIN = Side(style="thin", color="B7C7D2")

TYPE_LABELS = {
    "arrival": "抵达", "departure": "出发", "flight": "航班",
    "transfer": "交通", "rail": "火车", "ferry": "轮渡",
    "attraction": "景点", "walk": "步行", "hike": "徒步",
    "shopping": "城市漫步", "rest": "休息/用餐", "return": "返程",
    "note": "提示",
}


def add_header(ws, title: str, subtitle: str, end_column: int) -> None:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_column)
    cell = ws.cell(1, 1, title)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.font = Font(name="Microsoft YaHei", size=18, bold=True, color=WHITE)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 31

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_column)
    cell = ws.cell(2, 1, subtitle)
    cell.fill = PatternFill("solid", fgColor=PALE_BLUE)
    cell.font = Font(name="Microsoft YaHei", size=9, color=MUTED)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 23


def style_table_header(ws, row: int, values: list[str]) -> None:
    for column, value in enumerate(values, 1):
        cell = ws.cell(row, column, value)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.font = Font(name="Microsoft YaHei", size=9, bold=True, color=WHITE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    ws.row_dimensions[row].height = 22


def style_body_row(ws, row: int, columns: int, fill: str | None = None) -> None:
    for column in range(1, columns + 1):
        cell = ws.cell(row, column)
        if fill:
            cell.fill = PatternFill("solid", fgColor=fill)
        cell.font = Font(name="Microsoft YaHei", size=8.5, color="17212B")
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def place_names(item: dict, places: dict[str, dict]) -> str:
    ids = item.get("placeIds") or ([item["placeId"]] if item.get("placeId") else [])
    names = []
    for place_id in ids:
        place = places.get(place_id, {})
        name = place.get("nameZh") or place.get("name")
        if name and name not in names:
            names.append(name)
    return " → ".join(names) or "—"


def short_text(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else f"{text[:limit - 1]}…"


def configure_page(ws, orientation: str, fit_height: int | None = None) -> None:
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = orientation
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    if fit_height is not None:
        ws.page_setup.fitToHeight = fit_height
    ws.page_margins = PageMargins(left=0.25, right=0.25, top=0.35, bottom=0.35, header=0.15, footer=0.15)
    ws.oddFooter.center.text = "第 &P / &N 页"
    ws.oddFooter.center.size = 8
    ws.oddFooter.center.font = "Microsoft YaHei"
    ws.sheet_view.showGridLines = False


def build_overview(workbook: Workbook, data: dict, places: dict[str, dict]) -> None:
    ws = workbook.active
    ws.title = "A4行程总览"
    add_header(ws, "悉尼 · A4 行程总览", "2026.09.26 — 2026.10.01  |  2 人  |  打印前请复核实时天气、交通与预约状态", 5)
    style_table_header(ws, 4, ["日期", "主题", "关键时间", "路线 / 地点", "当日重点与提醒"])
    widths = [12, 25, 21, 36, 54]
    for index, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(index)].width = width

    row = 5
    for day in data["days"]:
        times = "\n".join(item["time"] for item in day["schedule"])
        route = []
        for item in day["schedule"]:
            name = place_names(item, places)
            if name != "—" and name not in route:
                route.append(name)
        focus = "\n".join(
            f"• {short_text(item['text'], 115)}" for item in day["schedule"]
        )
        date_label = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%m/%d")
        weekday = "一二三四五六日"[datetime.strptime(day["date"], "%Y-%m-%d").weekday()]
        ws.cell(row, 1, f"D{day['day']}  {date_label}\n周{weekday}")
        ws.cell(row, 2, day["title"])
        ws.cell(row, 3, times)
        ws.cell(row, 4, "\n".join(route))
        ws.cell(row, 5, focus)
        style_body_row(ws, row, 5, PALE_SAND if day["day"] % 2 else None)
        ws.cell(row, 1).font = Font(name="Microsoft YaHei", size=9, bold=True, color=NAVY)
        ws.cell(row, 2).font = Font(name="Microsoft YaHei", size=9, bold=True, color=NAVY)
        ws.row_dimensions[row].height = max(72, 22 * len(day["schedule"]))
        row += 1

    ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=5)
    note = ws.cell(row + 1, 1, "总提醒：两人各自固定使用交通支付介质；蓝山、海岸线和 Manly 行程前复核天气与班次；返程日 06:30 出发，优先保障国际航班。")
    note.font = Font(name="Microsoft YaHei", size=8.5, italic=True, color=MUTED)
    note.alignment = Alignment(wrap_text=True, vertical="center")
    note.fill = PatternFill("solid", fgColor=PALE_BLUE)
    ws.row_dimensions[row + 1].height = 30
    ws.print_title_rows = "$1:$4"
    configure_page(ws, ws.ORIENTATION_LANDSCAPE, 1)


def build_daily_details(workbook: Workbook, data: dict, places: dict[str, dict]) -> None:
    ws = workbook.create_sheet("每日详表")
    add_header(ws, "悉尼 · 每日详细行程", "2026.09.26 — 2026.10.01  |  每日自动分页（A4 纵向）", 4)
    style_table_header(ws, 4, ["时间", "类型", "地点", "安排与注意事项"])
    for index, width in enumerate([17, 14, 31, 71], 1):
        ws.column_dimensions[get_column_letter(index)].width = width

    row = 5
    for day_index, day in enumerate(data["days"]):
        if day_index:
            ws.row_breaks.append(row - 1)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        date_label = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%Y 年 %m 月 %d 日")
        heading = ws.cell(row, 1, f"D{day['day']} · {date_label} · {day['title']}")
        heading.fill = PatternFill("solid", fgColor=NAVY)
        heading.font = Font(name="Microsoft YaHei", size=11, bold=True, color=WHITE)
        heading.alignment = Alignment(vertical="center")
        ws.row_dimensions[row].height = 25
        row += 1
        for item in day["schedule"]:
            ws.cell(row, 1, item["time"])
            ws.cell(row, 2, TYPE_LABELS.get(item.get("type"), item.get("type", "安排")))
            ws.cell(row, 3, place_names(item, places))
            ws.cell(row, 4, item["text"])
            style_body_row(ws, row, 4, PALE_SAND if row % 2 else None)
            ws.cell(row, 1).font = Font(name="Microsoft YaHei", size=8.5, bold=True, color=NAVY)
            ws.cell(row, 2).alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
            ws.row_dimensions[row].height = max(38, min(78, 14 + len(item["text"]) // 2))
            row += 1
        if day.get("notes"):
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
            note = ws.cell(row, 1, "当日备忘：" + "；".join(day["notes"]))
            note.fill = PatternFill("solid", fgColor=PALE_BLUE)
            note.font = Font(name="Microsoft YaHei", size=8, color=MUTED, italic=True)
            note.alignment = Alignment(wrap_text=True, vertical="center")
            note.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
            ws.row_dimensions[row].height = 28
            row += 1
        row += 1

    ws.print_title_rows = "$1:$4"
    configure_page(ws, ws.ORIENTATION_PORTRAIT)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    places = {place["id"]: place for place in data.get("places", [])}
    workbook = Workbook()
    workbook.properties.creator = "Travel Plan Page"
    workbook.properties.title = "悉尼行程 A4 打印版"
    build_overview(workbook, data, places)
    build_daily_details(workbook, data, places)
    workbook.save(DESTINATION)
    print(DESTINATION)


if __name__ == "__main__":
    main()
