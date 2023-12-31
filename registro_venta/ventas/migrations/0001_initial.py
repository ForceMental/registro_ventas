# Generated by Django 4.2.6 on 2023-10-09 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_venta', models.CharField(choices=[('A', 'Aprobada'), ('P', 'Pendiente'), ('C', 'Cancelada')], default='P', max_length=1)),
                ('producto_vendido', models.CharField(max_length=50)),
                ('stock_entregado', models.IntegerField()),
                ('fecha_venta', models.DateField(auto_now_add=True)),
                ('visita_id', models.IntegerField()),
                ('compra_confirmada', models.BooleanField(default=False)),
            ],
        ),
    ]
