from django.db import models

class Document(models.Model):
    passport_number = models.CharField(max_length=255)
    passport_expiry = models.DateField()
    nationality     = models.CharField(max_length=255)
    document_type   = models.CharField(max_length=300)

class Offer(models.Model):
    price_info   = models.JSONField()
    fares_info   = models.JSONField()
    baggage_info = models.JSONField() 

class Passenger(models.Model):

    PASSENGER_TYPES = (
        ('ADT', 'ADULT'),
        ('CHD', 'CHILD'),
        ('INF', 'INFANT'),
        ('INS', 'INFANT_WITH_SEAT'),
    )

    GENDER_TYPES = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    passenger_id       = models.UUIDField()
    firstname          = models.CharField(max_length=255)
    lastname           = models.CharField(max_length=255)
    middlename         = models.CharField(max_length=255)
    gender             = models.CharField(choices=GENDER_TYPES)
    birth_date         = models.DateField()
    passenger_category = models.CharField(max_length=255)
    passenger_type     = models.CharField(choices=PASSENGER_TYPES)
    phone_number       = models.CharField(max_length=255)
    email_address      = models.CharField(max_length=255)
    offer              = models.OneToOneField(Offer, on_delete=models.SET_DEFAULT, default=None)
    document           = models.OneToOneField(Document, on_delete=models.SET_DEFAULT, default=None)

    def __str__(self) -> str:
        return self.firstname

class Order(models.Model):

    ORDER_STATUS = (
        ('B', 'STATUS_BOOK'),
        ('T', 'STATUS_TICKET'),
        ('V', 'STATUS_VOID'),
        ('R', 'STATUS_REFUND'),
        ('E', 'STATUS_BOOK_ERROR'),
        ('C', 'STATUS_TICKET_ERROR'),
        ('O', 'STATUS_PAID_WAIT'),
        ('G', 'STATUS_IN_PROGRESS'),
        ('W', 'STATUS_VOID_ERROR'),
        ('F', 'STATUS_REFUND_ERROR'),
    )

    primary_key       = models.BigIntegerField(primary_key=True)
    gds_pnr           = models.CharField(max_length=255)
    supplier_pnr      = models.CharField(max_length=255)
    status            = models.CharField(max_length=255, choices=ORDER_STATUS, default='B')
    created_at        = models.DateTimeField(auto_now_add=False)
    ticket_time_limit = models.DateTimeField()
    void_time_limit   = models.IntegerField()
    price             = models.FloatField()
    currency          = models.CharField(max_length=255)
    offer             = models.JSONField()
    provider          = models.JSONField()
    airline_code      = models.CharField(max_length=300)
    passengers        = models.ManyToManyField(Passenger)

    def __str__(self) -> str:
        return self.gds_pnr
    
    class Meta:
        ordering = ['-primary_key']
    








