from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def __str__(self):
        parts = []

        if self.first_name:
            parts.append(self.first_name)

        if self.last_name:
            parts.append(self.last_name)

        name = " ".join(parts)

        if name:
            return name

        return self.username

    @property
    def initials(self):
        letters = ""

        if self.first_name:
            letters += self.first_name[0]

        if self.last_name:
            letters += self.last_name[0]

        if letters:
            return letters.upper()

        return self.username[0].upper()
