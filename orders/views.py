import uuid
from datetime import datetime, timedelta

from django.utils import timezone

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .models import Order, Passenger, Offer
from .serializers import OrderSerializer
from .pagination import OrderCustomPagination

class OrderViewSet(viewsets.ModelViewSet):
    queryset          = Order.objects.all().prefetch_related('passengers')
    pagination_class  = OrderCustomPagination
    http_method_names = ['patch', 'get', 'post', ]

    def get_queryset(self):
        order_queryset = self.queryset

        order_number = self.request.query_params.get('order_number')
        status       = self.request.query_params.get('status')
        gds_pnr      = self.request.query_params.get('gds_pnr')
        provider     = self.request.query_params.get('provider')
        airline      = self.request.query_params.get('airline')
        lastname     = self.request.query_params.get('lastname')
        date_from    = self.request.query_params.get('from')
        date_to      = self.request.query_params.get('to')

        if order_number is not None:
            order_queryset = order_queryset.filter(primary_key=order_number)
        
        if status is not None:
            order_queryset = order_queryset.filter(status=status)
        
        if gds_pnr is not None:
            order_queryset = order_queryset.filter(gds_pnr__contains=gds_pnr)

        if provider is not None:
            order_queryset = order_queryset.filter(provider__contains={'name': provider})

        if airline is not None:
            order_queryset = order_queryset.filter(airline_code__contains=airline)
        
        if lastname is not None:
            order_queryset = order_queryset.filter(passengers__lastname__contains=lastname)

        if date_from and date_to:

            input_format = '%Y-%m-%d'
            output_format = '%Y-%m-%d %H:%M:%S'

            parsed_date_from = datetime.strptime(date_from, input_format)
            formatted_date_from = parsed_date_from.strftime(output_format)

            parsed_date_to = timezone.make_aware(datetime.strptime(date_to, input_format))
            parsed_date_to += timedelta(days=1)
            formatted_date_to = parsed_date_to.strftime(output_format)

            order_queryset = order_queryset.filter(created_at__range=(formatted_date_from, formatted_date_to))
        
        return order_queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        last_order = self.queryset.last()

        for passenger in data['passengers']:
            passenger['passenger_id'] = uuid.uuid4()
        
        if last_order is not None:
            number = self.queryset.last()
            data['primary_key'] = number.primary_key + 1
        else:
            data['primary_key'] = 1

        serializer = OrderSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            response = {
                'status' : 'success',
                'message': 'booking data has been saved'
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        
        response = {
            'status' : 'error',
            'message': 'booking data has not been saved'
        }
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrderSerializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                'status' : 'success',
                'message': 'booking data has been updated'
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        
        response = {
            'status' : 'error',
            'message': 'booking data has not been updated'
        }
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        return OrderSerializer










