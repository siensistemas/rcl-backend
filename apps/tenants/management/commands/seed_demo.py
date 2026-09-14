from datetime import timedelta
from decimal import Decimal
from django.utils.text import slugify

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.categories.models import Category
from apps.classifieds.models import Classified
from apps.events.models import Event
from apps.jobs.models import Job
from apps.promotions.models import Promotion
from apps.tenants.models import Municipality
from apps.tourism.models import Attraction, TouristRoute
from apps.users.models import User
from apps.businesses.models import Business


class Command(BaseCommand):
    help = "Sembra datos demo (idempotente): municipios, usuarios, categorias, comercios y contenido publicado."

    def handle(self, *args, **options):
        self.stdout.write("== Seed demo (idempotente) ==")

        # ---------------------------------------------------------------
        # Municipios
        # ---------------------------------------------------------------
        munis = self._get_or_create_munis()
        for m in munis:
            self.stdout.write(f"  Municipio: {m.name} (id={m.id})")

        # ---------------------------------------------------------------
        # Usuarios
        # ---------------------------------------------------------------
        admin = self._create_user('admin', 'Admin123!', 'global_admin', is_staff=True, is_superuser=True,
                                  first_name='Administrador', last_name='Global', email='admin@rcl.local')
        self._create_user('app_test01', 'Rcl12345!', 'user',
                          first_name='App', last_name='Test', email='app_test01@rcl.local')
        for m in munis:
            self._create_user(f'muni.{m.slug}', 'Muni123!', 'municipal_admin', municipality=m,
                              is_staff=True, is_superuser=False, first_name='Admin', last_name=m.name)
        self.stdout.write("  Usuarios creados/verificados:")
        self.stdout.write("    admin / Admin123! (global_admin)")
        self.stdout.write("    app_test01 / Rcl12345! (usuario)")
        self.stdout.write("    muni.<slug> / Muni123! (municipal_admin por municipio)")
        self.stdout.write("    comercio1..N / Comercio123! (merchant por municipio)")

        # ---------------------------------------------------------------
        # Categorias + Comercios + contenido por municipio
        # ---------------------------------------------------------------
        merchants_by_muni = {}
        for i, m in enumerate(munis, start=1):
            merchant = self._create_user(
                f'comercio{i}',
                'Comercio123!',
                'merchant',
                municipality=m,
                first_name='Comerciante',
                last_name=m.name,
            )
            merchants_by_muni[m.id] = merchant
            categories = self._seed_categories(m)
            business = self._seed_businesses(m, merchant, categories)
            self._seed_content(m, business, i)

        # Resumen
        self.stdout.write(self.style.SUCCESS(
            "Seed completado. Revisa /tenants/ y /events/ en la API."
        ))

    # ------------------------------------------------------------------
    def _get_or_create_munis(self):
        defaults = {
            'description': 'Municipio activo en la Red Comercial Local',
            'slogan': 'Juntos crecemos',
            'is_active': True,
            'is_public': True,
        }
        munis = []
        for name, color in [('Santa Rosa', '#16a34a'), ('San Juan', '#2563eb')]:
            m, created = Municipality.objects.get_or_create(name=name, defaults={**defaults, 'primary_color': color})
            munis.append(m)
        return munis

    def _create_user(self, username, password, role, municipality=None, is_staff=False, is_superuser=False,
                     first_name='', last_name='', email=''):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'password': password,
                'role': role,
                'municipality': municipality,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'is_active': True,
                'is_verified': True,
                'email_verified': True,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
        else:
            changed = False
            if user.role != role:
                user.role = role
                changed = True
            if user.municipality_id != (municipality.id if municipality else None):
                user.municipality = municipality
                changed = True
            if user.is_active != True:
                user.is_active = True
                changed = True
            if not user.is_verified:
                user.is_verified = True
                changed = True
            if not user.email_verified:
                user.email_verified = True
                changed = True
            if changed:
                user.save()
            if not user.check_password(password):
                user.set_password(password)
                user.save(update_fields=['password'])
        return user

    def _seed_categories(self, m):
        data = [
            ('Restaurantes', 'fa-utensils', '#ef4444'),
            ('Tiendas', 'fa-store', '#3b82f6'),
            ('Servicios', 'fa-briefcase', '#8b5cf6'),
            ('Salud', 'fa-heart-pulse', '#10b981'),
            ('Educacion', 'fa-graduation-cap', '#f59e0b'),
            ('Otros', 'fa-circle', '#64748b'),
        ]
        cats = []
        for name, icon, color in data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                municipality=m,
                defaults={
                    'slug': f'{slugify(name)}-{m.slug}',
                    'icon': icon,
                    'icon_color': color,
                    'description': f'Categoría {name}',
                    'order': len(cats),
                },
            )
            cats.append(cat)
        return cats

    def _seed_businesses(self, m, merchant, categories):
        c_rest, c_store, c_services = categories[0], categories[1], categories[2]
        business_data = [
            {
                'name': 'Cafeteria El Centro',
                'short_name': 'Cafeteria',
                'description': 'Cafeteria y reposteria artesanal, desayunos y especialidades locales.',
                'address': f'Plaza Central, {m.name}',
                'phone': '+50688880001',
                'whatsapp': '+50688880001',
                'category': c_rest,
                'is_featured': True,
                'is_verified': True,
            },
            {
                'name': 'Comercial SiEnSistemas',
                'short_name': 'SiEnSistemas',
                'description': 'Tecnologia, reparacion de equipos y soluciones digitales para el comercio local.',
                'address': f'Avenida Principal, {m.name}',
                'phone': '+50688880002',
                'whatsapp': '+50688880002',
                'category': c_services,
                'is_featured': True,
                'is_verified': True,
            },
            {
                'name': 'Tienda La Esperanza',
                'short_name': 'La Esperanza',
                'description': 'Abarrotes, ferreteria y articulos para el hogar.',
                'address': f'Barrio El Centro, {m.name}',
                'phone': '+50688880003',
                'category': c_store,
                'is_verified': False,
            },
        ]
        businesses = []
        for data in business_data:
            biz, created = Business.objects.get_or_create(
                name=data['name'],
                municipality=m,
                defaults={
                    'owner': merchant,
                    'category': data['category'],
                    'description': data['description'],
                    'short_name': data['short_name'],
                    'address': data['address'],
                    'phone': data['phone'],
                    'whatsapp': data.get('whatsapp', ''),
                    'is_featured': data.get('is_featured', False),
                    'is_verified': data.get('is_verified', False),
                    'is_approved': True,
                    'is_active': True,
                },
            )
            if not created:
                biz.category = data['category']
                biz.owner = merchant
                biz.is_approved = True
                biz.is_active = True
                biz.is_featured = data.get('is_featured', False)
                biz.save()
            businesses.append(biz)
            self.stdout.write(f"  Comercio: {biz.name} (id={biz.id})")
        return businesses

    def _seed_content(self, m, businesses, offset):
        now = timezone.now()
        cafeteria = businesses[0] if businesses else None
        biz2 = businesses[1] if len(businesses) > 1 else None

        if cafeteria:
            Promotion.objects.get_or_create(
                title='Promo Inaugural Desayuno',
                business=cafeteria,
                defaults={
                    'subtitle': '2x1 en desayunos',
                    'description': 'Disfruta 2x1 en todo desayuno hasta las 10am.',
                    'start_date': now - timedelta(days=1),
                    'end_date': now + timedelta(days=20),
                    'discount_type': 'bogo',
                    'discount_value': 0,
                    'status': 'active',
                    'is_featured': True,
                    'is_unlimited': True,
                    'available_quantity': 999,
                },
            )

        if biz2:
            Promotion.objects.get_or_create(
                title='Mantenimiento de PC 10% off',
                business=biz2,
                defaults={
                    'subtitle': 'Oferta tecnica',
                    'description': 'Revisión técnica con 10% de descuento.',
                    'start_date': now - timedelta(days=1),
                    'end_date': now + timedelta(days=30),
                    'discount_type': 'percentage',
                    'discount_value': 10,
                    'min_purchase': 20000,
                    'status': 'active',
                    'is_featured': True,
                    'is_unlimited': True,
                    'available_quantity': 999,
                },
            )

        Event.objects.get_or_create(
            title=f'Festival Cultural de {m.name}',
            municipality=m,
            defaults={
                'description': 'Música, gastronomía y arte local en la plaza central.',
                'event_type': 'cultural',
                'location': f'Plaza Central, {m.name}',
                'start_date': now + timedelta(days=15 + offset),
                'end_date': now + timedelta(days=16 + offset),
                'is_free': True,
                'capacity': 500,
                'status': 'published',
                'is_featured': True,
            },
        )

        Event.objects.get_or_create(
            title=f'Feria de Comercio Local de {m.name}',
            municipality=m,
            defaults={
                'description': 'Oportunidad para impulsar los negocios del municipio.',
                'event_type': 'commercial',
                'location': f'Salon Municipal, {m.name}',
                'start_date': now + timedelta(days=40 + offset),
                'end_date': now + timedelta(days=41 + offset),
                'is_free': True,
                'capacity': 200,
                'status': 'published',
            },
        )

        attr_mountain, _ = Attraction.objects.get_or_create(
            name=f'Mirador El Bosque {m.name}'.strip(),
            municipality=m,
            defaults={
                'description': 'Vista panorámica del municipio y senderos naturales.',
                'attraction_type': 'natural',
                'address': f'Camino al mirador, {m.name}',
                'is_free': True,
                'opening_hours': 'Lunes a Domingo 6am - 6pm',
                'status': 'published',
                'is_featured': True,
                'latitude': 8.252158,
                'longitude': -83.004418,
            },
        )
        Attraction.objects.get_or_create(
            name=f'Iglesia Colonial de {m.name}',
            municipality=m,
            defaults={
                'description': 'Construcción histórica con arquitectura tradicional.',
                'attraction_type': 'historical',
                'address': f'Centro, {m.name}',
                'entry_fee': 0,
                'is_free': True,
                'opening_hours': 'Lunes a Sabado 8am - 5pm',
                'status': 'published',
            },
        )

        route, _ = TouristRoute.objects.get_or_create(
            name=f'Ruta Natural de {m.name}',
            municipality=m,
            defaults={
                'description': 'Recorrido por senderos y miradores del municipio.',
                'duration_text': '3 horas',
                'is_featured': True,
            },
        )
        route.attractions.add(attr_mountain)

        Job.objects.get_or_create(
            title='Cajero(a) con experiencia',
            municipality=m,
            defaults={
                'description': 'Atención al cliente, manejo de caja y arqueos al cierre.',
                'requirements': 'Experiencia minima de 1 año en caja.',
                'salary_min': 300000,
                'salary_max': 400000,
                'job_type': 'full_time',
                'work_mode': 'onsite',
                'business': cafeteria,
                'status': 'published',
                'location': m.name,
                'application_email': 'rrhh@rcl.local',
            },
        )

        Job.objects.get_or_create(
            title='Auxiliar de ventas',
            municipality=m,
            defaults={
                'description': 'Apoyo en piso de venta y organización de productos.',
                'requirements': 'Bachillerato concluido.',
                'salary_min': 250000,
                'salary_max': 300000,
                'job_type': 'part_time',
                'work_mode': 'onsite',
                'business': cafeteria,
                'status': 'published',
                'location': m.name,
                'application_email': 'rrhh@rcl.local',
            },
        )

        Classified.objects.get_or_create(
            title=f'Bicicleta de montaña en {m.name}',
            municipality=m,
            defaults={
                'description': 'Bicicleta en excelente estado, 21 velocidades, llantas recién cambiadas.',
                'price': 95000,
                'category': 'vehicles',
                'condition': 'used',
                'contact_phone': '+50688889999',
                'location': m.name,
                'status': 'published',
            },
        )

        Classified.objects.get_or_create(
            title=f'Refrigeradora 10 pies en {m.name}',
            municipality=m,
            defaults={
                'description': 'Refrigeradora de segunda mano, funciona perfecto, entrega en el municipio.',
                'price': 150000,
                'category': 'electronics',
                'condition': 'used',
                'contact_phone': '+50688889999',
                'location': m.name,
                'status': 'published',
            },
        )

        self.stdout.write(f"  Contenido publicado para {m.name}")