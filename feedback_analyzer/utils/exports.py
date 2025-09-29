from __future__ import annotations

import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_csv(df: pd.DataFrame) -> bytes:
	buf = io.StringIO()
	df.to_csv(buf, index=False)
	return buf.getvalue().encode("utf-8")


def export_pdf_summary(df: pd.DataFrame) -> bytes:
	buffer = io.BytesIO()
	c = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4

	margin = 40
	y = height - margin
	c.setFont("Helvetica-Bold", 16)
	c.drawString(margin, y, "Customer Feedback Summary Report")
	y -= 24
	c.setFont("Helvetica", 11)

	def line(text: str):
		nonlocal y
		c.drawString(margin, y, text[:110])
		y -= 16

	line(f"Total feedback: {len(df)}")
	if "sentiment_score" in df.columns:
		line(f"Avg sentiment: {df['sentiment_score'].mean():.2f}")
	if "priority" in df.columns:
		line(f"Urgent share: {(df['priority']>=0.85).mean()*100:.1f}%")
	if "topic" in df.columns:
		by_topic = df.groupby('topic').size().sort_values(ascending=False).head(5)
		line("Top topics:")
		for k, v in by_topic.items():
			line(f" - {k}: {v}")

	c.showPage()
	c.save()
	buffer.seek(0)
	return buffer.read()


