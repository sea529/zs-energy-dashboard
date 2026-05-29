"""
EMS 数据自动采集脚本
每周由 GitHub Actions 调用，更新 data/latest.json

依赖：pip install playwright
运行：python fetch_data.py
"""
import json, os, re, asyncio
from datetime import datetime, timedelta
from pathlib import Path

# ─── 配置 ──────────────────────────────────────────────
EMS_URL    = "https://www.titanenergy.cn"
STATIONS   = ["ZS7", "ZS8"]
OUTPUT     = Path(__file__).parent / "data" / "latest.json"

# EMS 账号（从 GitHub Secrets 读取）
EMS_PHONE  = os.environ.get("EMS_PHONE", "")
EMS_PASS   = os.environ.get("EMS_PASSWORD", "")


async def fetch_station(page, station_id: str) -> dict:
    """抓取单个电站数据"""
    print(f"  → 抓取 {station_id}...")

    # 首页概览
    await page.goto(f"{EMS_URL}/#/ems/station/home/{station_id}", wait_until="networkidle")
    await page.wait_for_timeout(2500)
    text = await page.inner_text("body")

    # 解析概览数据（正则从页面文本提取）
    def val(pattern, default=0):
        m = re.search(pattern, text)
        return float(m.group(1)) if m else default

    capacity  = val(r"储能装机容量.*?([\d.]+)\s*\(kWh\)")
    pr        = val(r"PR\s*([\d.]+)%")
    cycles    = val(r"储能循环次数.*?([\d.]+)\s*\(cycle\)")
    safe_days = int(val(r"安全运行.*?(\d+)\s*\(天\)"))

    # 跳转收益分析页面
    await page.goto(f"{EMS_URL}/#/ems/station/profit/{station_id}/ess-profit", wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # 等待表格加载
    await page.wait_for_selector("table tbody tr", timeout=10000)

    rows = await page.query_selector_all("table tbody tr")
    dates, charge, discharge, revenue = [], [], [], []

    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 4:
            continue
        texts = [await c.inner_text() for c in cells]
        date_str = texts[0].strip()
        if not re.match(r"^\d{8}$", date_str):
            continue  # 跳过合计行
        d = f"{date_str[4:6]}-{date_str[6:8]}"
        dates.append(d)
        revenue.append(float(texts[1].replace(",", "")))
        charge.append(float(texts[2].replace(",", "")))
        discharge.append(float(texts[3].replace(",", "")))

    monthly_revenue = sum(revenue)
    total_charge    = sum(charge)
    total_discharge = sum(discharge)

    return {
        "capacity": capacity,
        "pr": pr,
        "cycles": cycles,
        "safe_days": safe_days,
        "monthly_revenue": round(monthly_revenue, 2),
        "total_charge": round(total_charge, 2),
        "total_discharge": round(total_discharge, 2),
        "daily": {
            "dates":     dates,
            "charge":    charge,
            "discharge": discharge,
            "revenue":   revenue,
        }
    }


async def main():
    from playwright.async_api import async_playwright

    print("启动浏览器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page    = await context.new_page()

        # 登录
        print("登录 EMS...")
        await page.goto(f"{EMS_URL}/#/login", wait_until="networkidle")
        await page.fill("input[placeholder*='手机']", EMS_PHONE)
        await page.fill("input[type='password']",    EMS_PASS)
        await page.click("button[type='submit']")
        await page.wait_for_url("**/#/ems**", timeout=15000)
        print("  登录成功")

        # 采集各站数据
        result = {
            "updated":  datetime.today().strftime("%Y-%m-%d"),
            "stations": {}
        }

        station_names = {
            "ZS7": "中山顶盛物业管理A站",
            "ZS8": "中山顶盛物业管理B站",
        }

        for sid in STATIONS:
            data = await fetch_station(page, sid)
            data["name"] = station_names[sid]
            result["stations"][sid] = data
            print(f"  {sid} 完成：收益 {data['monthly_revenue']} 元，{len(data['daily']['dates'])} 天数据")

        await browser.close()

    # 写入 JSON
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 数据已写入 {OUTPUT}")
    print(f"   ZS7: {result['stations']['ZS7']['monthly_revenue']} 元")
    print(f"   ZS8: {result['stations']['ZS8']['monthly_revenue']} 元")


if __name__ == "__main__":
    asyncio.run(main())
