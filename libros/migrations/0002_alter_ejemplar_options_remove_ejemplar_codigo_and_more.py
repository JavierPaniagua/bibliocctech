import re

from django.db import migrations, models


def convertir_codigos_y_ubicaciones(apps, schema_editor):
    Ejemplar = apps.get_model('libros', 'Ejemplar')

    numeros_usados = set()

    for ejemplar in Ejemplar.objects.select_related('libro').all():
        codigo_viejo = (ejemplar.codigo or '').strip()
        numero = None

        numeros_encontrados = re.findall(
            r'\d+',
            codigo_viejo,
        )

        if numeros_encontrados:
            numero = int(numeros_encontrados[-1])

        if not numero or numero in numeros_usados:
            numero = max(numeros_usados, default=0) + 1

            while numero in numeros_usados:
                numero += 1

        numeros_usados.add(numero)

        ubicacion_anterior = (
            ejemplar.libro.ubicacion or ''
        ).strip()

        estanteria = ''
        balda = ''

        if ubicacion_anterior:
            texto = ubicacion_anterior.upper()
            texto = texto.replace('ESTANTERÍA', '')
            texto = texto.replace('ESTANTERIA', '')
            texto = texto.replace('ESTANTE', '')
            texto = texto.strip(' :-')

            partes = [
                parte.strip()
                for parte in texto.split('-')
                if parte.strip()
            ]

            if len(partes) >= 2:
                estanteria = partes[0]
                balda = partes[1]
            else:
                estanteria = texto

        ejemplar.numero_inventario = numero
        ejemplar.codigo_anterior = codigo_viejo
        ejemplar.estanteria = estanteria
        ejemplar.balda = balda

        ejemplar.save(
            update_fields=[
                'numero_inventario',
                'codigo_anterior',
                'estanteria',
                'balda',
            ]
        )


def restaurar_codigo_anterior(apps, schema_editor):
    Ejemplar = apps.get_model('libros', 'Ejemplar')

    for ejemplar in Ejemplar.objects.all():
        if ejemplar.codigo_anterior:
            codigo = ejemplar.codigo_anterior
        else:
            codigo = (
                f'CCTL-LIB-'
                f'{ejemplar.numero_inventario:06d}'
            )

        ejemplar.codigo = codigo

        ejemplar.save(
            update_fields=['codigo']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejemplar',
            name='balda',
            field=models.CharField(
                blank=True,
                max_length=20,
                verbose_name='Balda',
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='codigo_anterior',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=30,
                verbose_name='Código anterior',
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='estanteria',
            field=models.CharField(
                blank=True,
                max_length=20,
                verbose_name='Estantería',
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='etiqueta_impresa',
            field=models.BooleanField(
                default=False,
                verbose_name='Etiqueta impresa',
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='fecha_impresion_etiqueta',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name=(
                    'Fecha de impresión de etiqueta'
                ),
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='numero_inventario',
            field=models.PositiveIntegerField(
                blank=True,
                db_index=True,
                null=True,
                unique=True,
                verbose_name='Número de inventario',
            ),
        ),

        migrations.AddField(
            model_name='ejemplar',
            name='proveedor',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='Proveedor',
            ),
        ),

        migrations.AlterField(
            model_name='libro',
            name='categoria',
            field=models.CharField(
                blank=True,
                max_length=100,
                verbose_name='Categoría',
            ),
        ),

        migrations.RunPython(
            convertir_codigos_y_ubicaciones,
            restaurar_codigo_anterior,
        ),

        migrations.RemoveField(
            model_name='ejemplar',
            name='codigo',
        ),

        migrations.RemoveField(
            model_name='libro',
            name='ubicacion',
        ),

        migrations.AlterModelOptions(
            name='ejemplar',
            options={
                'ordering': ['numero_inventario'],
                'verbose_name': 'Ejemplar',
                'verbose_name_plural': 'Ejemplares',
            },
        ),
    ]