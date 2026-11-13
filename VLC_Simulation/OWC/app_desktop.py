"""Native desktop host for the same Python simulation service used by the browser."""
from app_server import start_server


def launch_desktop_app():
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError("Desktop mode requires pywebview: pip install -r requirements.txt") from exc
    server, url = start_server()
    try:
        webview.create_window("VLC friendly jamming - Python CNN/DND",url=url,
                              width=1400,height=880,min_size=(1024,700),resizable=True)
        webview.start()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    launch_desktop_app()
