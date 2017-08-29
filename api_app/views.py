import calendar
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from api_app.serializers import *
import datetime


@ensure_csrf_cookie
def validate_data(request):
    numtarj = request.GET.get('numtarj', None)
    pin = request.GET.get('pin', None)
    ccv = request.GET.get('ccv', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    ci = request.GET.get('ci', None)
    profile = request.GET.get('profile', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {'product': Product.objects.filter(numCard=numtarj).exists(),
            'ccv': True,
            'month': True,
            'year': True,
            'pin': True,
            'ci': True}

    if data['product']:

        product = Product.objects.get(numCard=numtarj)

        if ((product.month == month) and (product.year == year) and (product.ccv == ccv)) or not (profile is None):
            data['customer'] = Customer.objects.filter(id=product.customer.id).exists()
            data['account'] = Account.objects.filter(product=product.id).exists()
            if data['customer'] and data['account'] or not (profile is None):
                customer = Customer.objects.get(id=product.customer.id)
                accounts = Account.objects.filter(product=product.id)
                if customer.ident == ci or not (profile is None):
                    for a in accounts:
                        if a.pin == pin or not (profile is None):
                            data['correct'] = True
                            data['customer_name'] = customer.firstName
                            data['customer_last'] = customer.lastName
                            data['customer_ident'] = customer.ident

                            if customer.phone.home is None:
                                data['phone_home'] = "None-None"
                            else:
                                data['phone_home'] = customer.phone.home

                            if customer.phone.cellphone is None:
                                data['cellphone'] = "None-None"
                            else:
                                data['cellphone'] = customer.phone.cellphone

                            if customer.phone.office is None:
                                data['phone_office'] = "None-None"
                            else:
                                data['phone_office'] = customer.phone.office

                            data['birthday'] = customer.birthday
                            break
                        else:
                            data['correct'] = False
                            data['pin'] = False
                else:
                    data['correct'] = False
                    data['ci'] = False
            else:
                data['correct'] = False
        else:
            data['correct'] = False

            if product.month != month:
                data['month'] = False
            if product.year != year:
                data['year'] = False
            if product.ccv != ccv:
                data['ccv'] = False
    else:
        data['correct'] = False

    if not (data['correct']):
        data['error'] = msj_error

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


def conv_int(cadena):
    s = ''
    for c in cadena:
        s = s + str(ord(c))
        if len(s) == 6:
            return s
    return s


def conv_balance(a):
    a = str(a).split('.')
    b = a[0][::-1]
    l = len(b)
    i = 0
    j = 3
    amount = ''
    while i < l:
        if j >= l:
            amount = amount + b[i:l]
        else:
            amount = amount + b[i:j] + '.'
        i = i + 3
        j = j + 3
    amount = amount[::-1]
    if len(a) == 2:
        amount = amount + ',' + a[1][:2]
    else:
        amount = amount + ',00'
    return amount


@ensure_csrf_cookie
def get_product(request):
    numtarj = request.GET.get('num', None)
    msj_error = 'Ha ocurrido un error por favor intente nuevamente.'

    data = {
        'product': [],
        'exist': Product.objects.filter(numCard=numtarj).exists()
    }

    if Product.objects.filter(numCard=numtarj).exists():
        product = Product.objects.get(numCard=numtarj)
        customer = Customer.objects.get(pk=product.customer.id)
        products = Product.objects.filter(customer=customer.id).exclude(numCard=numtarj)
        loans = Loan.objects.filter(customer=customer.id)

        for p in products:
            tdc = Tdc.objects.get(product=p.id)
            details_tdc = ['TDC Propias', tdc.name + " ****" + p.numCard[12:]]

            data['product'].append(details_tdc)

        for l in loans:
            details_loan = ['Pago Préstamo', 'Préstamo-'+ conv_int('PRESTAMO') + str(l.id)]

            data['product'].append(details_loan)

        data['correct'] = True

    else:
        data['correct'] = False

    if not (data['correct']):
        data['error'] = msj_error

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def get_references(request):
    ref = request.GET.get('ref', None)

    data = {
        'amount': '',
        'description': ''
    }

    if Movement.objects.filter(ref=ref).exists():
        print('existe')
        mov = Movement.objects.get(ref=ref)

        data['amount'] = conv_balance(mov.amount)
        data['description'] = mov.details
        data['correct'] = True

    else:
        data['correct'] = False

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def exist_account(request):
    ci = request.GET.get('ci', None)
    account = request.GET.get('acc', None)

    data = {
        'ident': False,
        'acc': False,
        'customer': False,
        'exist': False
    }

    if Customer.objects.filter(ident=ci).exists():
        customer = Customer.objects.get(ident=ci)
        if Account.objects.filter(numAcc=account).exists():
            if Account.objects.filter(product__customer=customer.id,
                                      numAcc=account).exists():
                data['exist'] = True
            else:
                data['customer'] = True
        else:
            data['acc'] = True
    else:
        data['ident'] = True

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def exist_tdc(request):
    ci = request.GET.get('ci', None)
    numtdc = request.GET.get('num', None)

    data = {
        'ident': False,
        'tdc': False,
        'customer': False,
        'exist': False
    }

    if Customer.objects.filter(ident=ci).exists():
        customer = Customer.objects.get(ident=ci)
        if Product.objects.filter(numCard=numtdc).exists():
            if Tdc.objects.filter(product__customer=customer.id, product__numCard=numtdc).exists():
                data['exist'] = True
            else:
                data['customer'] = True
        else:
            data['tdc'] = True
    else:
        data['ident'] = True

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def data_customer(request):
    num = request.GET.get('num', None)
    option = request.GET.get('option', 0)
    select = request.GET.get('select', '0')
    startDate = request.GET.get('start', None)
    endDate = request.GET.get('end', None)

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'account': [],
            'tdc': [],
            'loan': [],
            'mov_acc': [[], []],
            'mov_tdc': [[], [], []],
            'management': [[], []],
            'chart': [['Meses', 'Activos', 'Pasivos']]
            }

    if request.method.lower() != "options":
        if data['product']:
            product = Product.objects.get(numCard=num)
            customer = Customer.objects.get(pk=product.customer.id)
            accounts = Account.objects.filter(product=product.id).order_by('name')
            products = Product.objects.filter(customer=customer.id).exclude(numCard=num)
            loans = Loan.objects.filter(customer=customer.id)
            balance_acc = 0

            for a in accounts:

                details_acc = ['Cuenta ' + a.name,
                               a.numAcc[:10] + "******" + a.numAcc[16:],
                               "Activa",
                               [conv_balance(a.balance.available), conv_balance(a.balance.deferrer),
                                conv_balance(a.balance.lock)],
                               a.branch.name]

                data['account'].append(details_acc)

                balance_acc = (a.balance.available/1000) + balance_acc
                print(type(balance_acc))

                if option == 'consultar-cuenta':
                    if startDate is None and endDate is None:
                        today = datetime.datetime.today()
                        end_day = calendar.monthrange(today.year, today.month)[1]
                        start = str(today.year) + '-' + str(today.month) + '-1'
                        if today.day == end_day:
                            today = today + datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = str(today.year) + '-0' + str(today.month) + '-' + str(today.day + 1)
                    else:
                        today = startDate.split('/')
                        end_date = endDate.split('/')
                        end_day = calendar.monthrange(int(today[2]), int(today[1]))[1]
                        start = today[2] + '-' + today[1] + '-' + today[0]
                        if int(end_date[0]) == end_day:
                            today = datetime.date(int(end_date[2]), int(end_date[1]), int(end_date[0])) + \
                                    datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = end_date[2] + '-' + end_date[1] + '-' + str((int(end_date[0]) + 1))

                    if select != '0':
                        select.replace('ó', 'o')

                        trans_simple = TransactionSimple.objects.filter(account=a.pk,
                                                                        type=select,
                                                                        movement__date__range=[start, end])

                        transf_out = TransferServices.objects.filter(accSource=a.pk,
                                                                     type=select,
                                                                     movement__date__range=[start, end]).order_by('id')

                        transf_in = TransferServices.objects.filter(accDest=a.pk,
                                                                    type=select,
                                                                    movement__date__range=[start, end]).order_by('id')

                        payments = PaymentTlf.objects.filter(account=a.pk,
                                                             type=select,
                                                             movement__date__range=[start, end]).order_by('id')
                    else:
                        trans_simple = TransactionSimple.objects.filter(account=a.pk,
                                                                        movement__date__range=[start, end])

                        transf_out = TransferServices.objects.filter(accSource=a.pk,
                                                                     movement__date__range=[start, end]).order_by('id')

                        transf_in = TransferServices.objects.filter(accDest=a.pk,
                                                                    movement__date__range=[start, end]).order_by('id')

                        payments = PaymentTlf.objects.filter(account=a.pk,
                                                             movement__date__range=[start, end]).order_by('id')

                    transaction = transf_out | transf_in

                    if a.name == 'Ahorro':
                        i = 0
                    else:
                        i = 1

                    for t in trans_simple:
                        mov = Movement.objects.get(pk=t.movement.id)
                        if t.type == 'Deposito':
                            sig = '+'
                        else:
                            sig = '-'
                        details_mov = [mov.date,
                                       mov.ref,
                                       t.get_type_display(),
                                       sig + conv_balance(mov.amount),
                                       conv_balance(t.amountResult)]

                        if t.type == 'Pagos':
                            if t.tdc is None:
                                details = mov.details
                            else:
                                details = mov.details + ' --Pago de TDC ' + t.tdc.name + \
                                          ' perteneciente a ' + t.tdc.product.customer.get_name()
                        else:
                            details = mov.details

                        details_mov.append(details)

                        data['mov_acc'][i].append(details_mov)

                    for tr in transaction:
                        mov = Movement.objects.get(pk=tr.movement.id)
                        if tr.type == 'Pagos':
                            w = 'o'
                        else:
                            w = 'a'
                        details_mov = [mov.date,
                                       mov.ref,
                                       tr.get_type_display()]

                        if tr.accDest is not None:
                            if tr.accDest.id == a.id:
                                details_mov.append('+' + conv_balance(mov.amount))
                                details_mov.append(conv_balance(tr.amountDest))
                                details = mov.details + ' --' + tr.get_type_display() + ' recibid' + w \
                                          + ' de la cuenta de ' + tr.accSource.product.customer.get_name()
                        if tr.accDest is None or tr.accDest.id != a.id:
                            details_mov.append('-' + conv_balance(mov.amount))
                            details_mov.append(conv_balance(tr.amountSource))
                            if tr.accDest is None:
                                details = mov.details
                            else:
                                if tr.get_type_display() == 'Transferencia':
                                    details = mov.details + ' --Transferencia Terceros mismo banco realizad' + \
                                              w + ' a la cuenta de ' + tr.accDest.product.customer.get_name()
                                else:
                                    details = mov.details + ' --' + tr.get_type_display() + ' realizad' + \
                                              w + ' a la cuenta de ' + tr.accDest.product.customer.get_name()

                        details_mov.append(details)

                        data['mov_acc'][i].append(details_mov)

                    for p in payments:
                        mov = Movement.objects.get(pk=p.movement.id)
                        details_mov = [mov.date,
                                       mov.ref,
                                       p.type,
                                       '-' + conv_balance(mov.amount),
                                       conv_balance(p.amountResult),
                                       mov.details + ' --Recarga a operadora ' +
                                       p.get_operator_display()]
                        data['mov_acc'][i].append(details_mov)

                    data['mov_acc'][i].sort(reverse=True)

                if option == 'gestion-productos':

                    if a.name == 'Corriente':
                        check = Checkbook.objects.filter(account=a.id, numCheck__gte=1)

                        for c in check:
                            data['management'][0].append('Chequera ' + str(c.numCheckbook))
                            data['management'][1].append(c.status)

            data['chart'].append(['Agosto', float(balance_acc), float(balance_acc)])
            for p in products:
                tdc = Tdc.objects.get(product=p.id)
                payment = TransactionSimple.objects.filter(tdc=tdc.pk, type='Pagos').order_by('-movement')[0]
                movement = Movement.objects.get(pk=payment.movement.pk)
                details_tdc = [tdc.name,
                               p.numCard[:4] + "********" + p.numCard[12:],
                               movement.date,
                               conv_balance(movement.amount),
                               conv_balance(tdc.balance),
                               conv_balance(tdc.balanceAvailable),
                               conv_balance(tdc.minimumPayment),
                               tdc.date,
                               conv_balance(tdc.limit)]
                if tdc.status:
                    details_tdc.insert(2, 'Activa')
                else:
                    details_tdc.insert(2, 'Inactiva')

                data['tdc'].append(details_tdc)

                if option == 'consultar-tdc':
                    if startDate is None and endDate is None:
                        today = datetime.datetime.today()
                        end_day = calendar.monthrange(today.year, today.month)[1]
                        start = str(today.year) + '-' + str(today.month) + '-1'
                        if today.day == end_day:
                            today = today + datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = str(today.year) + '-0' + str(today.month) + '-' + str(today.day + 1)
                    else:
                        today = startDate.split('/')
                        end_date = endDate.split('/')
                        end_day = calendar.monthrange(int(today[2]), int(today[1]))[1]
                        start = today[2] + '-' + today[1] + '-' + today[0]
                        if int(end_date[0]) == end_day:
                            today = datetime.date(int(end_date[2]), int(end_date[1]), int(end_date[0])) + \
                                    datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = end_date[2] + '-' + end_date[1] + '-' + str((int(end_date[0]) + 1))

                    if select != '0':
                        trans_simple = TransactionSimple.objects.filter(tdc=tdc.pk,
                                                                        type=select,
                                                                        movement__date__range=[start, end])
                    else:
                        trans_simple = TransactionSimple.objects.filter(tdc=tdc.pk,
                                                                        movement__date__range=[start, end])

                    if tdc.name == 'VISA':
                        i = 0
                    elif tdc.name == 'MASTERCARD':
                        i = 1
                    else:
                        i = 2

                    for t in trans_simple:
                        mov = Movement.objects.get(pk=t.movement.id)
                        if t.type == 'Pagos':
                            sig = '+'
                        else:
                            sig = '-'
                        details_mov = [mov.date,
                                       t.get_type_display(),
                                       sig + conv_balance(mov.amount)]

                        data['mov_tdc'][i].append(details_mov)

                    data['mov_tdc'][i].sort(reverse=True)

                if option == 'gestion-productos':
                    data['management'][0].append(tdc.name + ' ****' + p.numCard[12:])
                    data['management'][1].append(tdc.status)

            for l in loans:
                details_loan = [conv_int('PRESTAMO') + str(l.id),
                                'Cuenta ' + l.account.name + ' ****' + l.account.numAcc[16:],
                                conv_balance(l.paidAmount),
                                l.date_payment,
                                l.numInstallments,
                                conv_balance(l.startingAmount),
                                conv_balance(l.overdue_amount),
                                l.date,
                                l.date_expires,
                                l.paidInstallments,
                                l.overdueInstallments]

                data['loan'].append(details_loan)

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def validate_data_forgot(request):
    numtarj = request.GET.get('numtarj', None)
    ccv = request.GET.get('ccv', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    ci = request.GET.get('ci', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {'product': Product.objects.filter(numCard=numtarj).exists(),
            'ccv': True,
            'month': True,
            'year': True,
            'ci': True}

    if data['product']:
        product = Product.objects.get(numCard=numtarj)
        if (product.month == month) and (product.year == year) and (product.ccv == ccv):
            data['customer'] = Customer.objects.filter(id=product.customer.id).exists()
            if data['customer']:
                customer = Customer.objects.get(id=product.customer.id)
                if customer.ident == ci:
                    data['correct'] = True
                    data['customer_name'] = customer.firstName
                    data['customer_last'] = customer.lastName
                    data['customer_ident'] = customer.ident

                    if customer.phone.home is None:
                        data['phone_home'] = "None-None"
                    else:
                        data['phone_home'] = customer.phone.home

                    if customer.phone.cellphone is None:
                        data['cellphone'] = "None-None"
                    else:
                        data['cellphone'] = customer.phone.cellphone

                    if customer.phone.office is None:
                        data['phone_office'] = "None-None"
                    else:
                        data['phone_office'] = customer.phone.office

                    data['birthday'] = customer.birthday
                else:
                    data['correct'] = False
                    data['ci'] = False
            else:
                data['correct'] = False
        else:
            data['correct'] = False
            if product.month != month:
                data['month'] = False
            if product.year != year:
                data['year'] = False
            if product.ccv != ccv:
                data['ccv'] = False
    else:
        data['correct'] = False

    if not (data['correct']):
        data['error'] = msj_error

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def send_transfer(request):
    acc_source = request.GET.get('acc_source', None).split(' ')
    type = request.GET.get('type', None)
    acc_dest = request.GET.get('acc_dest', None).split(' ')
    amount = decimal.Decimal(request.GET.get('amount', None))
    num = request.GET.get('num', None)
    details = request.GET.get('detail', 'Transferencia entre sus cuentas')

    name = 'TRANSFERENCIA'
    d = True

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'success': False,
            'msg': 'Ha ocurrido un error validando sus datos'
            }

    if request.method.lower() != "options":
        if data['product']:
            product = Product.objects.get(numCard=num)
            s = Account.objects.filter(name=acc_source[0],
                                       numAcc__endswith=acc_source[1].replace('*', '')).exists()

            if type == 'transf-mis-cuentas':
                d = Account.objects.filter(name=acc_dest[0],
                                           numAcc__endswith=acc_dest[1].replace('*', '')).exists()
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    dest = Account.objects.filter(name=acc_dest[0],
                                                  numAcc__endswith=acc_dest[1].replace('*', ''))[0]
                    if source.product.customer_id == dest.product.customer_id:
                        if source.product.customer_id == product.customer_id:
                            bs = Balance.objects.get(pk=source.balance_id)
                            bd = Balance.objects.get(pk=dest.balance_id)

                            bs.available = bs.available - amount
                            bd.available = bd.available + amount

                            num = TransferServices.objects.filter(type=name.capitalize()).count()

                            mov = Movement(ref=conv_int(name) + str(num + 1),
                                           amount=amount,
                                           details=details,
                                           date=datetime.datetime.today())
                            mov.save()
                            transf = TransferServices(type=name.capitalize(),
                                                      movement=mov,
                                                      accSource=source,
                                                      accDest=dest,
                                                      amountSource=bs.available,
                                                      amountDest=bd.available)
                            transf.save()
                            bs.save()
                            bd.save()
                            data['success'] = True
                            data['msg'] = 'Transferencia realizada satisfactoriamente.'
            if type == 'transf-mi-banco':
                d = Account.objects.filter(numAcc=acc_dest[0]).exists()
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    dest = Account.objects.get(numAcc=acc_dest[0])
                    if source.product.customer_id == product.customer_id:
                        bs = Balance.objects.get(pk=source.balance_id)
                        bd = Balance.objects.get(pk=dest.balance_id)

                        bs.available = bs.available - amount
                        bd.available = bd.available + amount

                        num = TransferServices.objects.filter(type=name.capitalize()).count()

                        mov = Movement(ref=conv_int(name) + str(num + 1),
                                       amount=amount,
                                       details=details,
                                       date=datetime.datetime.today())
                        mov.save()
                        transf = TransferServices(type=name.capitalize(),
                                                  movement=mov,
                                                  accSource=source,
                                                  accDest=dest,
                                                  amountSource=bs.available,
                                                  amountDest=bd.available)
                        transf.save()
                        bs.save()
                        bd.save()
                        data['success'] = True
                        data['ref'] = mov.ref
                        data['amount'] = conv_balance(mov.amount)
                        data['msg'] = 'Transferencia realizada satisfactoriamente.'
            if type == 'transf-otros-bancos':
                extra = 'COMISION'
                if s:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    if source.product.customer_id == product.customer_id:
                        bs = Balance.objects.get(pk=source.balance_id)
                        bs.available = bs.available - amount

                        num = TransferServices.objects.filter(type=name.capitalize()).count()
                        num_extra = TransactionSimple.objects.filter(type=extra.capitalize()).count()

                        mov = Movement(ref=conv_int(name) + str(num + 1),
                                       amount=amount,
                                       details=details + '--Transferencia a otros bancos realizada a la cuenta de ' +
                                               acc_dest[0].replace('_', ' ') + ' del banco ' + acc_dest[1].replace('_', ' '),
                                       date=datetime.datetime.today())
                        mov_extra = Movement(ref=conv_int(extra) + str(num_extra + 1),
                                             amount=decimal.Decimal(27),
                                             details='Comisión de la transferencia con Ref. ' + mov.ref,
                                             date=datetime.datetime.today())
                        mov.save()
                        mov_extra.save()
                        transf = TransferServices(type=name.capitalize(),
                                                  movement=mov,
                                                  accSource=source,
                                                  amountSource=bs.available)
                        transf.save()
                        bs.available = bs.available - decimal.Decimal(27)
                        transf_extra = TransactionSimple(type=extra.capitalize(),
                                                         movement=mov_extra,
                                                         amountResult=bs.available,
                                                         account=source)
                        transf_extra.save()
                        bs.save()
                        data['success'] = True
                        data['ref'] = mov.ref
                        data['amount'] = conv_balance(mov.amount)
                        data['msg'] = 'Transferencia realizada satisfactoriamente.'

            if not d:
                data['msg'] = 'La cuenta destino no pertenece a Actio Capital.'

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def pay_services(request):
    acc_source = request.GET.get('acc', None).split(' ')
    service = request.GET.get('service', None)
    product_service = request.GET.get('product', None).split(' ')
    amount = decimal.Decimal(request.GET.get('amount', None))
    details = request.GET.get('detail', '')
    num = request.GET.get('num', None)
    name = 'PAGOS'
    d = True

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'success': False,
            'msg': 'Ha ocurrido un error validando sus datos'
            }

    if request.method.lower() != "options":
        if data['product']:
            product = Product.objects.get(numCard=num)
            s = Account.objects.filter(name=acc_source[0],
                                       numAcc__endswith=acc_source[1].replace('*', '')).exists()

            if (service.find('Banavih Aportes FAOV') == 0 or service.find('Electricidad de Caracas') == 0 or
                        service.find('Pago de Impuestos Nacionales Terceros') == 0 or
                        service.find('DirecTV Previo Pago') == 0 or service.find('DirecTV Prepago') == 0 or
                        service.find('Pago de Impuestos Nacionales Propios') == 0):
                if service == 'Pago de Impuestos Nacionales Terceros' or service == 'Pago de Impuestos Nacionales Terceros' :
                    service = 'SENIAT'
                elif service == 'DirecTV Previo Pago' or service == 'DirecTV Prepago':
                    service = 'DirecTV'
                d = Account.objects.filter(product__customer__firstName__icontains=service).exists()
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    dest = Account.objects.filter(product__customer__firstName=service)[0]
                    if source.product.customer_id == product.customer_id:
                        bs = Balance.objects.get(pk=source.balance_id)
                        bd = Balance.objects.get(pk=dest.balance_id)

                        bs.available = bs.available - amount
                        bd.available = bd.available + amount

                        num = Movement.objects.filter(ref__startswith=conv_int(name)).count()
                        print('num************')
                        print(num)

                        mov = Movement(ref=conv_int(name) + str(num + 1),
                                       amount=amount,
                                       details=details,
                                       date=datetime.datetime.today())
                        mov.save()
                        transf = TransferServices(type=name.capitalize(),
                                                  movement=mov,
                                                  accSource=source,
                                                  accDest=dest,
                                                  amountSource=bs.available,
                                                  amountDest=bd.available)
                        transf.save()
                        bs.save()
                        bd.save()
                        data['success'] = True
                        data['msg'] = 'Pago de servicio realizado satisfactoriamente.'
                        data['ref'] = mov.ref
            if service.find('TDC') == 0:
                print('entro tdc')
                if service == 'TDC Propias':
                    d = Tdc.objects.filter(product__numCard__endswith=product_service[1].replace('*', ''),
                                           name=product_service[0]).exists()
                if service == 'TDC de Terceros mismo banco':
                    d = Tdc.objects.filter(product__numCard=product_service[0]).exists()
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    if service == 'TDC Propias':
                        dest = Tdc.objects.filter(product__numCard__endswith=product_service[1].replace('*', ''),
                                                  name=product_service[0],
                                                  product__customer=product.customer.id)[0]
                    if service == 'TDC de Terceros mismo banco':
                        dest = Tdc.objects.get(product__numCard=product_service[0])

                    if service == 'TDC Propias' or service == 'TDC de Terceros mismo banco':
                        if source.product.customer_id == product.customer_id:
                            bs = Balance.objects.get(pk=source.balance_id)

                            bs.available = bs.available - amount
                            dest.balance = dest.balance - amount

                            num = Movement.objects.filter(ref__startswith=conv_int(name)).count()
                            print('num*************')
                            print(num)

                            mov = Movement(ref=conv_int(name) + str(num + 1),
                                           amount=amount,
                                           details=details,
                                           date=datetime.datetime.today())
                            mov.save()
                            transf = TransactionSimple(type=name.capitalize(),
                                                       movement=mov,
                                                       amountResult=bs.available,
                                                       account=source,
                                                       tdc=dest)
                            transf.save()
                            bs.save()
                            dest.save()
                            data['success'] = True
                            data['ref'] = mov.ref
                            data['amount'] = conv_balance(mov.amount)
                            data['msg'] = 'Pago de servicio realizado satisfactoriamente.'

                    if service == 'TDC de Terceros otros bancos':
                        if source.product.customer_id == product.customer_id:
                            bs = Balance.objects.get(pk=source.balance_id)

                            bs.available = bs.available - amount
                            num = Movement.objects.filter(ref__startswith=conv_int(name)).count()
                            print('num*************')
                            print(num)

                            mov = Movement(ref=conv_int(name) + str(num + 1),
                                           amount=amount,
                                           details=details,
                                           date=datetime.datetime.today())
                            mov.save()
                            transf = TransactionSimple(type=name.capitalize(),
                                                       movement=mov,
                                                       amountResult=bs.available,
                                                       account=source)
                            transf.save()
                            bs.save()
                            data['success'] = True
                            data['ref'] = mov.ref
                            data['amount'] = conv_balance(mov.amount)
                            data['msg'] = 'Pago de servicio realizado satisfactoriamente.'
            if (service.find('Digitel') == 0 or service.find('Movistar') == 0 or
                        service.find('CANTV') == 0 or service.find('Movilnet') == 0):
                d = Account.objects.filter(product__customer__firstName__icontains=service.upper()).exists()
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    dest = Account.objects.filter(product__customer__firstName__icontains=service.upper())[0]
                    if source.product.customer_id == product.customer_id:
                        bs = Balance.objects.get(pk=source.balance_id)
                        bd = Balance.objects.get(pk=dest.balance_id)

                        bs.available = bs.available - amount
                        bd.available = bd.available + amount

                        num = Movement.objects.filter(ref__startswith=conv_int(name)).count()

                        mov = Movement(ref=conv_int(name) + str(num + 1),
                                       amount=amount,
                                       details=details,
                                       date=datetime.datetime.today())
                        mov.save()
                        transf = PaymentTlf(operator=service.upper(),
                                            numTlf=product_service[0],
                                            amountResult=bs.available,
                                            movement=mov,
                                            account=source)
                        transf.save()
                        bs.save()
                        bd.save()
                        data['success'] = True
                        data['msg'] = 'Pago de servicio realizado satisfactoriamente.'
                        data['ref'] = mov.ref

    print(data)
    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def status_product(request):
    num = request.GET.get('num', None)
    product = request.GET.get('p', None).split('-')
    action = request.GET.get('action', None)

    data = {
        'product': Product.objects.filter(numCard=num).exists(),
        'correct': False,
        'msg': 'Ha ocurrido un problema validando sus datos. Intente nuevamente.'
    }

    if request.method.lower() != "options" and data['product']:
        prod = Product.objects.get(numCard=num)
        customer = Customer.objects.get(pk=prod.customer_id)

        if product[0] == 'Chequera':
            try:
                account = Account.objects.get(name='Corriente',
                                              checkbook__numCheckbook=product[1],
                                              product__customer=customer.pk)

                checkbook = Checkbook.objects.get(account=account.pk, numCheckbook=product[1])
                if action == 'act':
                    other_act = Checkbook.objects.filter(status='True', account=checkbook.account_id).count()
                    if other_act > 0:
                        data['msg'] = 'No se puede activar su ' + product[0] + ' ' + product[1] + ', porque ' + \
                                      'ya tiene otra chequera de la misma cuenta activada.'
                    else:
                        checkbook.status = True
                        checkbook.save()
                        data['correct'] = True
                        data['msg'] = 'Se ha activado su ' + product[0] + ' ' + product[1] + ' satisfactoriamente.'
                else:
                    if checkbook.numCheck > 0:
                        data['msg'] = 'Se ha desactivado su ' + product[0] + ' ' + product[1] + ' satisfactoriamente.' \
                                      + ' Tenga en cuenta que los cheques restantes de dicha chequera quedan anulados.'
                        checkbook.numCheck = 0
                    else:
                        data['msg'] = 'Se ha desactivado su ' + product[0] + ' ' + product[1] + ' satisfactoriamente.'

                    checkbook.status = False
                    checkbook.save()
                    data['correct'] = True

            except Account.DoesNotExist:
                data['msg'] = 'Intente nuevamente ocurrió un problema en el servidor.'

                response = JsonResponse(data)
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
                response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

                return response

        else:
            try:
                tdc = Tdc.objects.filter(name=product[0],
                                         product__numCard__endswith=product[1].replace('*', ''),
                                         product__customer=customer.pk)[0]
                if action == 'act':
                    tdc.status = True
                    data['msg'] = 'Se ha activado su TDC ' + product[0] + ' ' + product[1] + ' satisfactoriamente.'
                else:
                    tdc.status = False
                    data['msg'] = 'Se ha desactivado su TDC ' + product[0] + ' ' + product[1] + ' satisfactoriamente.'

                tdc.save()
                data['correct'] = True

            except Tdc.DoesNotExist:
                data['msg'] = 'Intente nuevamente ocurrió un problema en el servidor.'

                response = JsonResponse(data)
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
                response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

                return response

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def chart(request):
    num = request.GET.get('num', None)

    data = {
        'product': Product.objects.filter(numCard=num).exists()
    }

    if request.method.lower() != "options" and data['product']:

        today = datetime.date.today()
        trans_simple = TransactionSimple.objects.filter(tdc=tdc.pk,
                                                        type=select,
                                                        movement__date__range=[start, end])



class CustomersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomersSerializer


class BanksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Bank.objects.all()
    serializer_class = BanksSerializer


class BranchesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Branch.objects.all()
    serializer_class = BranchesSerializer


class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class AccountsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TdcViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tdc.objects.all()
    serializer_class = TDCSerializer


class LoansViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    # class UsuarioViewSet(viewsets.ModelViewSet):
    #    """
    #   API endpoint that allows users to be viewed or edited.
    #    """
    #    queryset = Usuarios.objects.all().ord
