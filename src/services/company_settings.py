import os
import shutil
from pathlib import Path

from config.db import SessionLocal
from src.models.user import CompanySetting


def _get_storage_dir() -> Path:
    base_dir = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "accountManager"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _copy_logo_to_storage(source_path: str) -> str:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError("Logo file not found")

    storage_dir = _get_storage_dir()
    file_name = source.name or "company_logo"
    destination = storage_dir / file_name

    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    return str(destination)


def ensure_default_company_settings():
    with SessionLocal() as db:
        setting = db.query(CompanySetting).first()
        if setting is None:
            db.add(CompanySetting(company_name="Your Company"))
            db.commit()


def get_company_settings():
    with SessionLocal() as db:
        return db.query(CompanySetting).first()


def save_company_settings(
    company_name=None,
    company_address=None,
    company_registration_number=None,
    gst_number=None,
    company_logo_path=None,
    company_phone=None,
    company_email=None,
    website=None,
):
    cleaned_name = (company_name or "").strip() or "Your Company"

    with SessionLocal() as db:
        setting = db.query(CompanySetting).first()
        if setting is None:
            setting = CompanySetting()
            db.add(setting)

        setting.company_name = cleaned_name
        setting.company_address = (company_address or "").strip() or None
        setting.company_registration_number = (
            company_registration_number or ""
        ).strip() or None
        setting.gst_number = (gst_number or "").strip() or None
        setting.company_phone = (company_phone or "").strip() or None
        setting.company_email = (company_email or "").strip() or None
        setting.website = (website or "").strip() or None

        if company_logo_path:
            logo_path = _copy_logo_to_storage(company_logo_path)
            setting.company_logo_path = logo_path

        db.commit()
        db.refresh(setting)
        return setting
