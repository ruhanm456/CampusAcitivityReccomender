from pathlib import Path

# Allow importing the existing root-level "app" package via
# CampusActivityReccomender.app.api.main
__path__.append(str(Path(__file__).resolve().parents[2] / "app"))
