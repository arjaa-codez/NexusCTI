import sys
import uvicorn

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from nexuscti.config import SERVER_HOST, SERVER_PORT


def main():
    print("=" * 70)
    print(f"[*] Starting NexusCTI Server at http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"[*] API Documentation at http://{SERVER_HOST}:{SERVER_PORT}/docs")
    print("=" * 70)

    uvicorn.run(
        "nexuscti.api.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
