import flet as ft
import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import connect
from backend.services.auth_service import AuthService
from backend.exceptions import PMSError

def main(page: ft.Page):
    page.title = "Pharmacy Management System"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 700

    def login_click(e):
        conn = connect()
        auth_service = AuthService(conn)
        try:
            print(f"Attempting login for user: {username_field.value}")
            # Attempt to login
            session = auth_service.login(username_field.value, password_field.value)
            print(f"Login successful! Role: {session.role}")
            
            # If successful, change the view to the Dashboard
            page.clean()
            page.add(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=60),
                        ft.Text(f"Welcome, {session.full_name}!", size=30, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Role: {session.role}", size=20, color=ft.Colors.BLUE_700),
                        ft.Container(height=30),
                        ft.FilledButton("Enter Pharmacy Dashboard", icon=ft.Icons.LOCAL_PHARMACY, scale=1.2)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )
            )
        except PMSError as err:
            print(f"Login failed: {err}")
            # Show error snackbar (Flet 1.0 syntax)
            snack = ft.SnackBar(ft.Text(str(err)), bgcolor=ft.Colors.RED_700)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception as e:
            print(f"Crash: {e}")
            snack = ft.SnackBar(ft.Text(f"Crash: {e}"), bgcolor=ft.Colors.RED_700)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            conn.close()

    # Build the Login UI
    title = ft.Text("Pharmacy Login", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    subtitle = ft.Text("Please sign in to continue", size=16, color=ft.Colors.GREY_700)
    
    username_field = ft.TextField(label="Username", icon=ft.Icons.PERSON, width=300)
    password_field = ft.TextField(label="Password", icon=ft.Icons.LOCK, password=True, can_reveal_password=True, width=300)
    
    login_btn = ft.FilledButton("Login", on_click=login_click, width=300, height=50, style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8),
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE
    ))

    # Center the login card
    login_card = ft.Card(
        elevation=10,
        content=ft.Container(
            padding=50,
            content=ft.Column(
                [title, subtitle, ft.Container(height=20), username_field, password_field, ft.Container(height=20), login_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
    )

    page.add(login_card)

if __name__ == "__main__":
    ft.app(target=main) if hasattr(ft, 'app') else ft.app(main) if hasattr(ft, 'app') else ft.run(main)
