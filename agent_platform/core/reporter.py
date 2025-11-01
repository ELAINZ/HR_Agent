import json
from jinja2 import Template

def save_json(results, path="report.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def generate_html_report(results, path="report.html"):
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    pass_rate = round(passed / total * 100, 1)

    template = Template("""
    <html><body style="font-family:Arial;">
    <h2>HR Agent 测试报告</h2>
    <p>总测试数：{{ total }}，通过数：{{ passed }}，通过率：<b>{{ pass_rate }}%</b></p>
    <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse;">
    <tr style="background:#f0f0f0;">
      <th>ID</th><th>Query</th><th>Expected</th><th>Predicted</th><th>Pass</th><th>Reason</th>
    </tr>
    {% for r in results %}
    <tr style="background-color:{% if r.pass %}#d4edda{% else %}#f8d7da{% endif %};">
      <td>{{r.id}}</td>
      <td>{{r.query}}</td>
      <td>{{r.expected}}</td>
      <td>{{r.predicted}}</td>
      <td>{{r.pass}}</td>
      <td>{{r.error}}</td>
    </tr>
    {% endfor %}
    </table></body></html>
    """)

    html = template.render(results=results, total=total, passed=passed, pass_rate=pass_rate)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"报告生成完成 ({pass_rate}% 通过率)，输出文件: {path}")
