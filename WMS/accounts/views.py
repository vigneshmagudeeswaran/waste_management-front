from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import *
from .filters import *
from .decorators import *


# Create your views here.
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(user = user,name=user.username,)
            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "username OR password is incorrect")
    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    querys = Query.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_querys = querys.count()
    delivered = querys.filter(status='Delivered').count()
    pending = querys.filter(status='Pending').count()

    context = {'querys': querys, 'customers': customers, 'total_orders': total_querys, 'delivered': delivered,
               'pending': pending,'total_customers': total_customers}
    return render(request, "accounts/dashboard.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customers'])
def userPage(request):
    #customer = Customer.objects.get(id=pk_test)
    querys = request.user.customer.query_set.all()

    total_querys = querys.count()
    delivered = querys.filter(status='Delivered').count()
    pending = querys.filter(status='Pending').count()

    print('Querys:', querys)

    context = {'querys': querys, 'total_orders': total_querys,
               'delivered': delivered, 'pending': pending,'customer':customer}
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customers'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customers'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    querys = customer.query_set.all()
    querys_count = querys.count()
    myFilter = QueryFilter(request.GET, queryset=querys)
    querys = myFilter.qs
    context = {'customer': customer, 'querys': querys, 'total_orders': querys_count, 'myFilter': myFilter}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    QueryFormSet = inlineformset_factory(Customer, Query, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    formset = QueryFormSet(queryset=Query.objects.none(), instance=customer)
    # form = QueryForm(initial={'customer': customer})
    if request.method == 'POST':
        formset = QueryFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'form': formset}
    return render(request, 'accounts/query_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    query = Query.objects.get(id=pk)
    form = QueryForm(instance=query)
    if request.method == 'POST':
        form = QueryForm(request.POST, instance=query)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/query_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    query = Query.objects.get(id=pk)
    if request.method == "POST":
        query.delete()
        return redirect('/')
    context = {'item': query}
    return render(request, 'accounts/delete.html', context)


def user(request):
    return render(request, 'accounts/customer.html')



