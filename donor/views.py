from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from django.contrib.auth import *
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
import json
import math
import stripe
stripe.api_key = "sk_test_CtioXHD6KZI5skEKRchf9oQb00aNQF97IE"

# Create your views here.

class DonorRegistration(APIView):
    def post(self, request, format=None):
        data = request.DATA
        username = data.get('username', None)
        password = data.get('password', None)
        email = data.get('email', None)
        first_name = data.get('first name', None)
        last_name = data.get('last name', None)
        if (username != None) or (password != None):
            new_user = User(username=username, password=password, email=email, first_name = first_name, last_name = last_name)
            new_user.save()
            new_donor = Donor(user=User.objects.get(username=username))
            new_donor.save()  


class DonorLogin(APIView):
    def post(self, request, format=None):
        data = request.data
        uid = data.get('uid')
        donor = Donor.objects.filter(uid=uid).first()
        if donor is None:
            user = User(username=uid,password="na",email="na")
            user.save()
            donor = Donor(uid=uid,user=user)
            donor.save()
            return Response(
            {
            "success": False,
            "user": { "id":donor.id }
            }
            ,200)
        else:
            user = User.objects.get(id=donor.user.id)
            login(request,user)
            return Response(
            {
            "success": True,
            "user": { "id":donor.id }
            }
            ,200)


class RecipientLogin(APIView):
    def post(self, request, format=None):
        data = request.data
        uid = data.get('uid')
        recipient = Recipient.objects.filter(uid=uid).first()
        if recipient is None:
            user = User(username=uid,password="na",email="na")
            user.save()
            recipient = Recipient(uid=uid,user=user,latitude=request.data['lat'],longitude=request.data['long'])
            recipient.save()
            return Response(
            {
            "success": False,
            "user": { "id":recipient.id }
            }
            ,200)
        else:
            user = User.objects.get(id=recipient.user.id)
            login(request,user)
            return Response(
            {
            "success": True,
            "user": { "id":recipient.id }
            }
            ,200)
        
class DonorView(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer

class RecipientView(viewsets.ModelViewSet):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer

class StoreView(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class PurchaseView(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GetPurchases(APIView):
    def get(self, request):
        
        (latitude,longitude) = (request.query_params['lat'],request.query_params['long'])
        def distance(purchase):
            return math.sqrt((float(purchase.recipient.latitude) - float(latitude))**2 + (float(purchase.recipient.longitude) - float(longitude))**2)

        purchases = list(Purchase.objects.all().exclude(recipient=None))
        purchases.sort(key=distance)
        purchases = map(lambda x: {
            "id":x.id,
            "lat":x.recipient.latitude,
            "long":x.recipient.longitude,
            "amount":x.purchase_value
        },purchases)
        return Response({"purchases":purchases},200)

class NewPurchase(APIView):
    def post(self, request):
        store = Store.objects.get(id=request.data['storeId'])
        purchase = Purchase(purchase_value=request.data['amount'],store=store)
        purchase.save()
        return Response({"uuid":purchase.uuid},200)

class ScanPurchase(APIView):
    def post(self, request):
        try:
            purchase = Purchase.objects.get(uuid=request.data['uuid'])
            if purchase.recipient is None:
                rec = Recipient.objects.get(user=request.user)
                purchase.recipient = rec 
                purchase.save()
                return Response({"success":True},200)
            else:
                return Response({"success":False,"error":"Barcode already scanned"},400)
        except ObjectDoesNotExist:
            return Response({"success":False,"error":'Invalid barcode'},400)

class Reimburse(APIView):
    def post(self, request, format=None):
        user = User.objects.get(username=request.user.username)
        purchaseId = request.data.get('purchaseId', None)
        Pur = Purchase.objects.get(id=purchaseId)
        if not request.user.customerId:
            customerId = stripe.Customer.create(description="Customer "+request.user.id,source=request.data.token).id
        else:
            customerId = request.user.customerId
        stripe.Charge.create(
            amount = Pur.purchase_value,
            currency = "cad",
            customer = customerId
        )
        Don = Donor.objects.get(user=request.user)
        Don.total_reimbursements_made += 1
        Don.total_reimbursements_value += Pur.purchase_value
        Don.save()
        Rec = Recipient.objects.get(user=Pur.recipient)
        Rec.total_reimbursements_value += Pur.purchase_value
        Rec.total_reimbursements_accepted += 1
        Rec.save()
        Pur.doner = Don
        print (request.user)
        # Pur.donor = request.user
        Pur.save()
        return Response({"result":"success"},200)

    # Donor Registration 
    # Donor Login
    # Donor Profile
    # Recipient Search

    # Recipient Registration
    # Recipient Login
    # Recipient Profile
    
    # Store Registration
    # Store Login
    # Store Profile
