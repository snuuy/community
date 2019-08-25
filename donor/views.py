from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from django.contrib.auth import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import json
import math
import stripe
stripe.api_key = "sk_test_CtioXHD6KZI5skEKRchf9oQb00aNQF97IE"

# Create your views here.

class DonorRegistration(APIView):
    @csrf_exempt
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
    @csrf_exempt
    def post(self, request, format=None):
        data = request.data
        uid = data.get('uid')
        donor = Donor.objects.filter(uid=uid).first()
        if donor is None:
            user = User.objects.create_user(username=uid,password="na",email="na")
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
    @csrf_exempt
    def post(self, request, format=None):
        data = request.data
        uid = data.get('uid')
        recipient = Recipient.objects.filter(uid=uid).first()
        if recipient is None:
            user = User.objects.create_user(username=uid,password="na",email="na")
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
    @csrf_exempt
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
    @csrf_exempt
    def post(self, request):
        store = Store.objects.get(id=request.data['storeId'])
        purchase = Purchase(purchase_value=request.data['amount'],store=store)
        purchase.save()
        return Response({"uuid":purchase.uuid},200)

class ScanPurchase(APIView):
    @csrf_exempt
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
    @csrf_exempt
<<<<<<< HEAD
    def post(self, request):
        user = User.objects.filter(id=request.user.id).first()
=======
    def post(self, request, format=None):
        user = User.objects.get(id=request.user)
        print (user)
>>>>>>> b8864d4e8b1f30ce8f7f0f24c81542189b965fb0
        purchaseId = request.data.get('purchaseId', None)
        Pur = Purchase.objects.get(id=purchaseId)
        if user.Donor.customerId == None:
            customerId = stripe.Customer.create(description=request.user.id,source=request.data['token']).id
        else:
            customerId = request.user.Donor.customerId
        stripe.Charge.create(
            amount = int(Pur.purchase_value*100),
            currency = "cad",
            customer = customerId
        )
        Don = Donor.objects.get(user=request.user)
        print (Don)
        Don.total_reimbursements_made += 1
        Don.total_reimbursements_value += Pur.purchase_value
        Don.customerId = customerId
        Don.save()
<<<<<<< HEAD
        Rec = Pur.recipient
=======
        print (Pur.recipient)
        Rec = Recipient.objects.get(user=User.objects.get(username = Pur.recipient))
>>>>>>> b8864d4e8b1f30ce8f7f0f24c81542189b965fb0
        Rec.total_reimbursements_value += Pur.purchase_value
        Rec.total_reimbursements_accepted += 1
        Rec.save()
        Pur.doner = Don
        print (request.user)
        # Pur.donor = request.user
        Pur.save()
        return Response({"result":"success"},200)

class Profile(APIView):
    @csrf_exempt
    def get(self,request,format=None):
        user = User.objects.get(id=1)
        if Recipient.objects.filter(user=user).exists() == True:
            user_type = "Recipient"
            type_object = Recipient.objects.get(user=user)
            purchases = list(Purchase.objects.filter(recipient=Recipient.objects.get(user=user)))
            purchases_JSON = map(lambda x: {
                "id":x.id,
                "amount":x.purchase_value,
                "pending":x.donor == None
            },purchases)
            return Response({"result":"success","type":user_type,"total_reimbursements_accepted":type_object.total_reimbursements_accepted, "total_reimbursements_value":type_object.total_reimbursements_value, "purchases_list":purchases_list},200)
        elif Donor.objects.filter(user=user).exists() == True:
            user_type = "Donor"
            type_object = Donor.objects.get(user=user)
            reimbursements = list(Purchase.objects.filter(donor=Donor.objects.get(user=user)))
            reimbursements_JSON = map(lambda x: {
                "id":x.id,
                "amount":x.purchase_value,
            },reimbursements)
            return Response({"result":"success","type":user_type,"total_reimbursements_made":type_object.total_reimbursements_made, "total_reimbursements_value":type_object.total_reimbursements_value, "reimbursements_list":reimbursements_JSON},200)
        else:
            return Response({"result":"failure, User is not Donor or Recipient"},500)
        


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
