from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()

FILE_PATH = {
    'CONFIG': BASE_DIR / "conf" / "config.ini",
    'LOG' : BASE_DIR / "logs",
    'EXTRACT': BASE_DIR / "extract.yaml",
    'REPORT_TEMP': BASE_DIR / "report" / "temp"
}

API_TIMEOUT = 30

if __name__ == "__main__":
    print(BASE_DIR)