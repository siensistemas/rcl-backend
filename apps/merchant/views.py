from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from apps.ads.models import Ad
from apps.ads.serializers import AdSerializer
from apps.businesses.models import Business
from apps.businesses.serializers import BusinessCreateSerializer
from apps.classifieds.models import Classified
from apps.classifieds.serializers import ClassifiedSerializer
from apps.events.models import Event
from apps.events.serializers import EventSerializer
from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer
from apps.promotions.models import Promotion
from apps.promotions.serializers import PromotionSerializer
from apps.reels.models import Reel
from apps.reels.serializers import ReelSerializer
from apps.tenants.models import Municipality
from apps.tourism.models import Attraction
from apps.tourism.serializers import AttractionSerializer, TouristRouteSerializer
from apps.users.models import User
from apps.users.serializers import UserSerializer
from shared.permissions import IsMerchant
from shared.tenant import resolve_tenant_for_user

from .serializers import MerchantBusinessSerializer


class MerchantViewSet(viewsets.ViewSet):
    """Endpoints del panel del comerciante.

    - GET/POST    /merchant/
    - PUT/DELETE  /merchant/{id}/
    - GET         /merchant/stats/
    - POST        /merchant/promotions/
    - POST        /merchant/register/
    """

    permission_classes = [permissions.IsAuthenticated, IsMerchant]
    lookup_value_regex = '[0-9]+'

    def get_permissions(self):
        if self.action == 'register':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsMerchant()]

    # ---- Gestión de comercios ----

    def list(self, request):
        businesses = Business.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
        serializer = MerchantBusinessSerializer(businesses, many=True)
        return Response({'results': serializer.data})

    def create(self, request):
        if Business.objects.filter(owner=request.user, is_active=True).exists():
            raise ValidationError(
                {'business': 'Ya tienes un comercio registrado. Cada comerciante '
                             'solo puede tener un comercio.'}
            )
        data = self._mutable_data(request)
        data.setdefault('municipality', self._default_municipality_id(request.user))
        serializer = BusinessCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save(owner=request.user)
        return Response(
            MerchantBusinessSerializer(business).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        business = get_object_or_404(Business, pk=pk, owner=request.user, is_active=True)
        serializer = BusinessCreateSerializer(business, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        return Response(MerchantBusinessSerializer(business).data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        business = get_object_or_404(Business, pk=pk, owner=request.user)
        business.is_active = False
        business.save(update_fields=['is_active'])
        return Response({'message': 'Comercio eliminado'})

    # ---- Estadísticas ----

    @action(detail=False, methods=['get'])
    def stats(self, request):
        businesses = Business.objects.filter(owner=request.user, is_active=True)
        promotions = Promotion.objects.filter(business__owner=request.user)
        now = timezone.now()

        total_views = sum(b.views_count for b in businesses)
        active_promotions = promotions.filter(
            status='active', start_date__lte=now, end_date__gte=now
        ).count()

        try:
            averages = [b.rating_average for b in businesses if b.rating_average]
            average_rating = round(sum(averages) / len(averages), 2) if averages else 0.0
            total_reviews = sum(b.total_ratings for b in businesses)
        except AttributeError:
            average_rating = 0.0
            total_reviews = 0

        return Response({
            'total_views': total_views,
            'total_claims': promotions.aggregate(total=Sum('redeemed_count'))['total'] or 0,
            'active_promotions': active_promotions,
            'total_promotions': promotions.count(),
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'daily_views': [],
        })

    # ---- Promociones ----

    @action(detail=False, methods=['post'])
    def promotions(self, request):
        data = self._mutable_data(request)
        business_id = data.get('business')
        business = self._resolve_business(request.user, business_id)
        data['business'] = business.id
        data.setdefault('start_date', timezone.now())
        data.setdefault('end_date', timezone.now() + timezone.timedelta(days=30))
        data.setdefault('status', 'active')

        serializer = PromotionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        promotion = serializer.save()
        return Response(
            PromotionSerializer(promotion).data,
            status=status.HTTP_201_CREATED,
        )

    # ---- Reels (panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='reels')
    def reels(self, request):
        if request.method == 'POST':
            return self._create_panel_item(
                request, Reel, ReelSerializer,
                defaults={'status': 'draft'},
            )
        items = Reel.objects.filter(business__owner=request.user)
        serializer = ReelSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Eventos (panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='events')
    def events(self, request):
        if request.method == 'POST':
            return self._create_panel_item(
                request, Event, EventSerializer,
                defaults={
                    'status': 'draft',
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timezone.timedelta(days=1),
                },
            )
        items = Event.objects.filter(business__owner=request.user)
        serializer = EventSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Empleos (panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='jobs')
    def jobs(self, request):
        if request.method == 'POST':
            return self._create_panel_item(
                request, Job, JobSerializer,
                defaults={'status': 'draft'},
            )
        items = Job.objects.filter(business__owner=request.user)
        serializer = JobSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Clasificados (panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='classifieds')
    def classifieds(self, request):
        if request.method == 'POST':
            return self._create_panel_item(
                request, Classified, ClassifiedSerializer,
                defaults={'status': 'draft'},
            )
        items = Classified.objects.filter(business__owner=request.user)
        serializer = ClassifiedSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Turismo (atracciones, panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='tourism')
    def tourism(self, request):
        # Las atracciones turísticas pertenecen al municipio, no a un negocio
        municipality = resolve_tenant_for_user(request.user) or self._default_municipality(request.user)
        if request.method == 'POST':
            data = self._mutable_data(request)
            data.pop('business', None)
            data.setdefault('is_free', True)
            serializer = AttractionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(municipality=municipality)
            return Response(AttractionSerializer(item).data, status=status.HTTP_201_CREATED)
        items = Attraction.objects.filter(municipality=municipality)
        serializer = AttractionSerializer(items, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['get', 'post'], url_path='tourism-routes')
    def tourism_routes(self, request):
        if request.method == 'POST':
            from apps.tourism.models import TouristRoute
            from apps.tourism.serializers import TouristRouteSerializer
            data = self._mutable_data(request)
            municipality = resolve_tenant_for_user(request.user) or self._default_municipality(request.user)
            serializer = TouristRouteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(municipality=municipality)
            return Response(TouristRouteSerializer(item).data, status=status.HTTP_201_CREATED)
        from apps.tourism.models import TouristRoute
        items = TouristRoute.objects.filter(municipality=resolve_tenant_for_user(request.user))
        serializer = TouristRouteSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Publicidad (panel del comerciante) ----

    @action(detail=False, methods=['get', 'post'], url_path='ads')
    def ads(self, request):
        if request.method == 'POST':
            return self._create_panel_item(
                request, Ad, AdSerializer,
                defaults={
                    'status': 'draft',
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timezone.timedelta(days=30),
                },
            )
        items = Ad.objects.filter(business__owner=request.user)
        serializer = AdSerializer(items, many=True)
        return Response({'results': serializer.data})

    # ---- Registro de comerciante ----

    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        business_name = (data.get('business_name') or data.get('businessName') or '').strip()

        if not username or not email or not password:
            return Response(
                {'error': 'username, email y password son requeridos'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'El nombre de usuario ya existe'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'El correo ya está registrado'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except Exception as e:
            return Response(
                {'error': ' '.join(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        municipality_id = data.get('municipality')
        if not municipality_id:
            municipality_id = self._default_municipality_id(request.user)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role='merchant',
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            municipality_id=municipality_id,
        )

        business = None
        if business_name and municipality_id:
            business = Business.objects.create(
                name=business_name,
                description=data.get('description', ''),
                address=data.get('address', ''),
                phone=data.get('phone', ''),
                website=data.get('website', ''),
                owner=user,
                municipality_id=municipality_id,
            )

        result = {
            'access_token': str(RefreshToken.for_user(user).access_token),
            'refresh_token': str(RefreshToken.for_user(user)),
            'token_type': 'Bearer',
            'user': UserSerializer(user).data,
        }
        if business:
            result['business'] = MerchantBusinessSerializer(business).data
        return Response(result, status=status.HTTP_201_CREATED)

    def _default_municipality_id(self, user):
        if user and getattr(user, 'municipality_id', None):
            return user.municipality_id
        municipality = Municipality.objects.filter(is_active=True).first()
        return municipality.id if municipality else None

    def _default_municipality(self, user):
        tenant = resolve_tenant_for_user(user)
        if tenant is not None:
            return tenant
        if user and getattr(user, 'municipality_id', None):
            return Municipality.objects.filter(pk=user.municipality_id).first()
        return Municipality.objects.filter(is_active=True).first()

    def _resolve_business(self, user, business_id=None):
        """Resuelve el negocio del request.

        Usa el id recibido si existe y pertenece al usuario; si el usuario
        tiene exactamente un negocio activo, lo asigna automáticamente.
        """
        if business_id:
            return get_object_or_404(
                Business, pk=business_id, owner=user, is_active=True
            )
        businesses = Business.objects.filter(owner=user, is_active=True)
        if businesses.count() == 1:
            return businesses.first()
        raise ValidationError(
            {'business': 'Indica el negocio (tienes varios) o crea un negocio primero.'}
        )

    def _mutable_data(self, request):
        """Datos del request en una estructura mutable sin deep-copy (los
        archivos de multipart no se pueden copiar en profundidad)."""
        data = request.data
        if not isinstance(data, dict) and hasattr(data, '_mutable'):
            data._mutable = True
        return data

    def _create_panel_item(self, request, model, serializer_class, defaults=None, extra=None):
        data = self._mutable_data(request)
        business_id = data.get('business')
        default_business = self._resolve_business(request.user, business_id)
        data['business'] = default_business.id

        for key, value in (defaults or {}).items():
            data.setdefault(key, value)

        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        save_kwargs = {
            'business': default_business,
            'municipality': resolve_tenant_for_user(request.user) or self._default_municipality(request.user),
        }
        save_kwargs.update(extra or {})
        item = serializer.save(**save_kwargs)
        return Response(
            serializer_class(item).data,
            status=status.HTTP_201_CREATED,
        )