import uuid

from rest_framework import serializers
from .models import Order, Passenger, Offer, Document

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Offer
        exclude = ('id',)

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Document
        exclude = ('id',)

class PassengerSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()
    document = DocumentSerializer()

    class Meta:
        model  = Passenger
        exclude = ('id', )

    def create(self, validated_data):
        document_data = validated_data.pop('document')
        offer_data = validated_data.pop('offer')

        document = Document.objects.create(**document_data)
        offer = Offer.objects.create(**offer_data)

        passenger = Passenger.objects.create(document=document, offer=offer, **validated_data)

        return passenger
    
    def update(self, instance, validated_data):
        document_data = validated_data.pop('document')

        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname  = validated_data.get('lastname',  instance.lastname)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)

        document_serializer = DocumentSerializer(instance=instance.document, data=document_data)
        if document_serializer.is_valid():
            document_serializer.update(instance=instance.document, validated_data=document_data)

        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model  = Order
        fields = '__all__'

    def create(self, validated_data):
        passengers_data = validated_data.pop('passengers')
        order = Order.objects.create(**validated_data)

        for passenger_data in passengers_data:
            offer_data = passenger_data.pop('offer')
            document_data = passenger_data.pop('document')

            offer = Offer.objects.create(**offer_data)
            document = Document.objects.create(**document_data)

            passenger = Passenger.objects.create(
                order=order,
                offer=offer,
                document=document,
                **passenger_data
            )
            order.passengers.add(passenger)

        return order
    
    def update(self, instance, validated_data):
        passengers_data = validated_data.pop('passengers')

        instance.status = validated_data.get('status', instance.status)

        existing_passengers = list(instance.passengers.all())
        for passenger_data in passengers_data:
            passenger_id = uuid.UUID(str(passenger_data.get('passenger_id')))

            if passenger_id:
                existing_passenger = next((passenger for passenger in existing_passengers if passenger.passenger_id == passenger_id), None)
                if existing_passenger:
                    passenger_data['passenger_id'] = uuid.UUID(str(passenger_id))
                    passenger_serializer = PassengerSerializer(existing_passenger, data=passenger_data, partial=True)
                    if passenger_serializer.is_valid():
                        passenger_serializer.update(existing_passenger, passenger_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['order_number'] = representation.pop('primary_key')
        return representation






