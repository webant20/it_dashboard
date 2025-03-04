from django.db import models
from AssetApp.models import Asset, PO  # Assuming Asset model exists in AssetApp

class CartridgeStock(models.Model):
    material_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.material_code} - {self.description} ({self.qty} in stock)"

class CartridgeAddition(models.Model):
    cartridge = models.ForeignKey(CartridgeStock, on_delete=models.CASCADE, related_name="additions")
    added_qty = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    po_number = models.ForeignKey(PO, on_delete=models.SET_NULL, null=True, blank=True, related_name="cartridge_additions")


    def save(self, *args, **kwargs):
        # Update stock quantity
        self.cartridge.qty += self.added_qty
        self.cartridge.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Added {self.added_qty} to {self.cartridge.material_code} on {self.date_added}"

class CartridgeIssue(models.Model):
    cartridge = models.ForeignKey(CartridgeStock, on_delete=models.CASCADE, related_name="issues")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="cartridge_issues")
    issued_qty = models.PositiveIntegerField()
    date_issued = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure the asset type is "Printer" or "Plotter"
        allowed_types = ["Printer", "Plotter"]
        if self.asset.asset_type.name not in allowed_types:
            raise ValueError("Cartridges can only be issued to assets of type Printer or Plotter.")

        # Check if stock is sufficient before issuing
        if self.cartridge.qty >= self.issued_qty:
            self.cartridge.qty -= self.issued_qty
            self.cartridge.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Not enough stock available!")

    def __str__(self):
        return f"Issued {self.issued_qty} of {self.cartridge.material_code} to {self.asset} on {self.date_issued}"
