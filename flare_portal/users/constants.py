from typing import Literal

ADMIN = "ADMIN"
RESEARCHER = "RESEARCHER"
Roles = Literal["ADMIN", "RESEARCHER"]

ROLE_CHOICES = ((ADMIN, "Admin"), (RESEARCHER, "Researcher"))
