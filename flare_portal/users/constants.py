from typing import Literal

ADMIN = Literal["ADMIN"]
RESEARCHER = Literal["RESEARCHER"]
Roles = Literal[ADMIN, RESEARCHER]

ROLE_CHOICES = ((ADMIN, "Admin"), (RESEARCHER, "Researcher"))
