

import sqlite3
import os
import flet as ft
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# =============================================================================
# نماذج البيانات والمصنع
# =============================================================================
@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    barcode: str = ""
    quantity: int = 0

@dataclass
class Sale:
    id: Optional[int] = None
    date: str = ""
    total: float = 0.0
    type: str = "cash"
    customer: str = ""

class Database:
    def __init__(self):
        # تحديد مسار قاعدة البيانات بشكل آمن لأندرويد
        db_path = "grocery_store.db"
        try:
            # في أندرويد، نحاول الوصول لبيانات التطبيق
            storage = os.environ.get('FLET_APP_STORAGE_DATA', '')
            if storage:
                db_path = os.path.join(storage, "grocery_store.db")
        except:
            pass
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, barcode TEXT UNIQUE, quantity INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, total REAL, type TEXT, customer TEXT, paid INTEGER DEFAULT 0)")
        self.conn.commit()

    def get_all_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        return [Product(id=r[0], name=r[1], price=r[2], barcode=r[3], quantity=r[4]) for r in cursor.fetchall()]

    def add_sale(self, s: Sale):
        cursor = self.conn.cursor()
        paid = 1 if s.type == "cash" else 0
        cursor.execute("INSERT INTO sales (date, total, type, customer, paid) VALUES (?, ?, ?, ?, ?)", (s.date, s.total, s.type, s.customer, paid))
        self.conn.commit()

    def update_stock(self, barcode, qty_sold):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE barcode = ?", (qty_sold, barcode))
        self.conn.commit()

# =============================================================================
# الواجهة الرئيسية
# =============================================================================
def main(page: ft.Page):
    try:
        page.title = "Smart Grocery POS"
        page.rtl = True
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # لضمان عدم ظهور شاشة بيضاء، سنستخدم خطوط النظام الافتراضية
        page.theme = ft.Theme(font_family=None)
        
        db = Database()
        cart = {}

        def show_message(text, color="green"):
            snack = ft.SnackBar(content=ft.Text(text, color="white"), bgcolor=color)
            page.overlay.append(snack)
            snack.open = True
            page.update()

        def go_home(e=None):
            page.clean()
            page.add(
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(colors=["#1565C0", "#0D47A1"]),
                    content=ft.Column([
                        ft.Container(height=50),
                        ft.Icon(ft.Icons.STOREFRONT, size=80, color="white"),
                        ft.Text("نظام البقالة الذكي", size=30, color="white", weight="bold"),
                        ft.Container(height=30),
                        ft.ElevatedButton("بدء عملية بيع", icon=ft.Icons.SHOPPING_CART, on_click=lambda _: show_message("قيد التطوير", "blue")),
                        ft.ElevatedButton("إدارة المخزون", icon=ft.Icons.INVENTORY, on_click=lambda _: show_message("قيد التطوير", "orange")),
                        ft.Text("V 1.5 | يعمل على أندرويد", color="#BBDEFB", size=12),
                    ], horizontal_alignment="center")
                )
            )

        go_home()
        
    except Exception as ex:
        # في حال وجود أي خطأ، سنظهره على الشاشة بدلاً من البياض
        page.add(ft.Text(f"حدث خطأ في التشغيل: {str(ex)}", color="red", size=20))

if __name__ == "__main__":
    ft.app(target=main)
