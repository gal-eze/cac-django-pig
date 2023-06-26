import base64
import csv
import random
import subprocess as sp

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import truncatechars
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView

from .forms import TransactionForm, UploadFileForm
from .models import Portfolio, Security, Transaction


def page_user(request):
    return render(request, "home/page-user.html")


@login_required
def dashboard(request):
    try:
        portfolio = Portfolio.objects.get(customer=request.user)
    except Exception as e:
        portfolio = Portfolio.objects.create(customer=request.user)

    portfolio.update_investment()

    result = (
        Transaction.objects.filter(portfolio=portfolio)
        .values("security__symbol", "security__description", "security__sector")
        .annotate(
            avg_price=Avg("price"),
            sum_quantity=Sum("quantity"),
            sum_investment_amount=Sum("investment_amount"),
        )
    )

    holdings = []

    sectors = [[], []]

    sector_wise_investment = {}

    stocks = [[], []]

    for row in result:
        symbol = row["security__symbol"]
        sector = row["security__sector"]
        investment_amount = row["sum_investment_amount"]
        holdings.append(
            {
                "CompanySymbol": symbol,
                "CompanyName": row["security__description"],
                "NumberShares": row["sum_quantity"],
                "InvestmentAmount": investment_amount,
                "AverageCost": row["avg_price"],
            }
        )

        stocks[0].append(
            round((investment_amount / portfolio.total_investment) * 100, 2)
        )

        stocks[1].append(symbol)

        if sector in sector_wise_investment:
            sector_wise_investment[sector] += investment_amount
        else:
            sector_wise_investment[sector] = investment_amount

    for sec in sector_wise_investment.keys():
        sectors[0].append(
            round((sector_wise_investment[sec] / portfolio.total_investment) * 100, 2)
        )

        sectors[1].append(sec)

    context = {
        "holdings": holdings,
        "totalInvestment": portfolio.total_investment,
        "stocks": stocks,
        "sectors": sectors,
    }

    return render(request, "portfolio/dashboard.html", context)


def calculate_random_price_variation(price):
    # Obtener la variación con dos decimales ente 3 y -3
    percent_variation = round(random.uniform(-300, 300) * 0.01, 2)
    # Calcular la variación del precio
    price_variation = float(price) * percent_variation / 100
    # Calcular el nuevo precio sumando la variación al precio original
    new_price = float(price) + price_variation
    # Redondear el nuevo precio a 2 decimales
    return round(new_price, 2)


def update_values(request):
    try:
        portfolio = Portfolio.objects.get(customer=request.user)
        current_value = 0
        unrealized_pnl = 0
        growth = 0
        transactions = Transaction.objects.filter(portfolio=portfolio)
        stockdata = {}
        for t in transactions:
            last_trading_price = calculate_random_price_variation(t.security.last_price)

            pnl = (last_trading_price * t.quantity) - t.investment_amount
            net_change = pnl / t.investment_amount
            stockdata[t.security.symbol] = {
                "LastTradingPrice": last_trading_price,
                "PNL": pnl,
                "NetChange": net_change * 100,
            }
            current_value += last_trading_price * t.quantity
            unrealized_pnl += pnl
        growth = unrealized_pnl / portfolio.total_investment
        return JsonResponse(
            {
                "StockData": stockdata,
                "CurrentValue": current_value,
                "UnrealizedPNL": unrealized_pnl,
                "Growth": growth * 100,
            }
        )
    except Exception as e:
        return JsonResponse({"Error": str(e)})


"""
    CRUD Transaction
"""


@login_required
def transaction_list(request):
    portfolio = Portfolio.objects.get(customer=request.user)
    transactions = portfolio.get_transactions()
    return render(
        request,
        "portfolio/transactions/transaction_list.html",
        {"transactions": transactions},
    )

@login_required
def transaction_filter(request):
    symbol = request.GET.get("symbol")
    transactions = Transaction.objects.filter(
        security__symbol__icontains=symbol
    ).order_by("-date")

    context = {"transactions": transactions, "filter_value": symbol}
    return render(request, "portfolio/transactions/transaction_list.html", context)


@login_required
def transaction_create(request):
    if request.method == "POST":
        formulario = TransactionForm(request.POST)
        if formulario.is_valid():
            transaction = formulario.save(commit=False)
            transaction.portfolio = Portfolio.objects.get(customer=request.user)
            transaction.save()

            # Actualizar last_price de Security
            security = transaction.security
            security.last_price = transaction.price
            security.save(update_fields=['last_price'])

            return redirect("transaction-list")
    else:
        formulario = TransactionForm()
    return render(
        request, "portfolio/transactions/transaction_create.html", {"form": formulario}
    )


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "portfolio/transactions/transaction_update.html"
    success_url = reverse_lazy("transaction-list")

    def get_initial(self):
        initial = super().get_initial()
        initial["symbol"] = self.object.security.symbol
        initial["date"] = self.object.date.strftime("%Y-%m-%d")
        return initial

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(Transaction, pk=pk)
        return obj


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "portfolio/transactions/transaction_delete.html"
    success_url = reverse_lazy("transaction-list")


"""
    Upload securities file
"""


@login_required
@staff_member_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            return render(
                request,
                "portfolio/securities/securities_upload_detail.html",
                {"file": file},
            )
    else:
        form = UploadFileForm()
    return render(
        request, "portfolio/securities/securities_upload.html", {"form": form}
    )


@login_required
@staff_member_required
def preview_data(request):
    if request.method == "POST":
        file = request.FILES["securities_csv_file"]
        file_content = file.read()
        file_base64 = base64.b64encode(file_content).decode("utf-8")
        decoded_file = file_content.decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)
        data = list(reader)
        headers = data[0]
        securities = data[1:]

        return render(
            request,
            "portfolio/securities/securities_upload_detail.html",
            {"headers": headers, "securities": securities, "file_base64": file_base64},
        )

    return render(request, "portfolio/upload/upload_file.html")


@login_required
@staff_member_required
def save_data(request):
    if request.method == "POST":
        file_base64 = request.POST.get("file")
        file_content = base64.b64decode(file_base64)
        file_content = file_content.decode("utf-8")

        csv_data = csv.reader(file_content.splitlines(), delimiter=",")
        next(csv_data)  # Omitir la primera línea si es un encabezado
        for row in csv_data:
            symbol = row[0]
            description = row[1]
            sector = row[2].split("-")
            if len(sector) > 1:
                sector = truncatechars(sector[1].strip(), 100)
            else:
                sector = "undefined"
            Security.objects.create(
                symbol=symbol, description=description, sector=sector
            )

        return render(request, "portfolio/securities/securities_upload_success.html")

    return render(request, "portfolio/securities/securities_upload.html")


@login_required
@staff_member_required
def securities_list(request):
    securities = Security.objects.all().order_by("symbol")
    context = {"securities": securities}
    print("Cantidad de Securities: " + str(len(securities)))
    return render(request, "portfolio/securities/securities_list.html", context)


@login_required
@staff_member_required
def security_filter(request):
    symbol = request.GET.get("symbol")
    securities = Security.objects.filter(symbol__icontains=symbol).order_by("symbol")

    context = {"securities": securities, "security_filter_value": symbol}
    return render(request, "portfolio/securities/securities_list.html", context)

### end securities file
