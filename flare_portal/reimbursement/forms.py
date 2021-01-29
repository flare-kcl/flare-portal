import csv
import io
from typing import Any, Dict, List

from django import forms
from django.core.validators import FileExtensionValidator

from .models import Voucher, VoucherPool


class VoucherUploadForm(forms.Form):
    import_file = forms.FileField(
        validators=[FileExtensionValidator(["csv"])],
    )

    def clean(self) -> Dict[str, Any]:
        # Don't continue if no upload
        file = self.cleaned_data.get("import_file")
        if file is None:
            return self.cleaned_data

        # Open uploaded file
        data = io.StringIO(file.read().decode("utf-8"))
        upload = csv.DictReader(data)

        # Build a list of ID's
        codes = []
        for row in upload:
            if code := row.get("code"):
                if len(code) <= 255 and code not in codes:
                    codes.append(code)
                else:
                    self.add_error(
                        "import_file",
                        "Codes must be 255 characters or less.",
                    )

        # Count of all vouchers in the CSV
        row_count = len(codes)

        # Filter out existing vouchers
        existing_codes = Voucher.objects.filter(code__in=codes).values_list(
            "code", flat=True
        )
        codes = [c for c in codes if c not in existing_codes]

        # Update data object
        self.cleaned_data["codes"] = codes
        self.cleaned_data["row_count"] = row_count
        return self.cleaned_data

    def save(self, *, voucher_pool: VoucherPool) -> List[Voucher]:
        """
        Accepts an upload .csv file and creates the corresponding voucher codes.
        """

        if not self.is_valid():
            raise ValueError("Form should be valid before calling .save()")

        vouchers = Voucher.objects.bulk_create(
            [
                Voucher(code=code, pool=voucher_pool)
                for code in self.cleaned_data["codes"]
            ]
        )

        return vouchers
