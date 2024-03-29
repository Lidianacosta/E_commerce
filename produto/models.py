import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from PIL import Image
from utils.utils import formata_preco
# Create your models here.


class Produto(models.Model):
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    nome = models.CharField(max_length=100)
    descricao_curta = models.TextField(max_length=150)
    descricao_longa = models.TextField(max_length=255)
    imagem = models.ImageField(
        upload_to="produto_imagens/%Y/%m", blank=True, null=True
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name="Preço Promocional"
    )
    tipo = models.CharField(
        max_length=1,
        default='V',
        choices=(
            ('V', 'Variavel'),
            ('S', "Simples")
        )
    )

    def get_preco_formatado(self):
        return formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self):
        return formata_preco(self.preco_marketing_promocional)
    get_preco_promocional_formatado.short_description = 'Preço promocional'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_heigth = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return

        new_heigth = round((new_width * original_heigth) / original_width)

        new_img = img_pil.resize((new_width, new_heigth), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            quality=50
        )
        img_pil.close()
        new_img.close()

    def save(self, *args, **kwargs) -> None:

        if not self.slug:
            self.slug = slugify(self.nome)

        super().save(*args, **kwargs)

        max_image_size = 600

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return f"{self.nome}"


class Variacao(models.Model):
    class Meta:
        verbose_name = "Variação"
        verbose_name_plural = "Variações"

    nome = models.CharField(max_length=100, blank=True, null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome
