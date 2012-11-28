#!C:\Python33\python.exe
import time
import configparser
import sys

modes = ["no_extra",
         "default",
         "cascade",
         "parallel"]

def get_config():
    conf = {}
    config = configparser.ConfigParser()
    config.read('foo.ini')
    foo = config.sections()

    return (config)

class loan(object):
    def __init__(self, interest_rate, principal, min_payment, loan_num, extra=0):
        self.apr = interest_rate
        self.principal = principal
        self.min_payment = min_payment
        self.loan_num = loan_num
        self.default_extra = extra

        self.balance = principal
        self.total_money =0
        self.months=0

    def calculate_loan(self, extra=0, num_months=-1):
        if extra == -1:
            local_extra = 0
        else:
            local_extra = self.default_extra + extra

        months = 0
        monthly_rate = (self.apr/12)/100
        balance = self.balance
        total_money = 0
        while balance > 0:
            interest = balance * monthly_rate
            principal_payment = self.min_payment - interest + local_extra
            balance=balance - principal_payment
            total_money += self.min_payment + local_extra
            months+=1
            if months == num_months:
                break

        if balance < 0:
            remainder = 0-balance
            total_money -= remainder

        self.balance = balance
        self.total_money += total_money
        self.months+=months

        return (months,total_money)

    def reset(self):
        self.balance = self.principal
        self.total_money = 0
        self.months = 0

    def get_resources_spent(self):
        return (self.months, self.total_money)

    def print_config(self):
        string = "Loan Number: %s, Interest Rate: %s," %(self.loan_num, self.apr)
        string+= " Payment: %s, Principal: %s" %(self.min_payment, self.principal)
#        print (string)


class option(object):
    def __init__(self, option_num, loans, mode, order, order2, extra_cash, loans_paid=0):
        self.errmsg = "Option%s: " %(option_num)
        self.option_num = option_num

        self.loans_paid = loans_paid

        self.mode = None
        self.order = None
        self.order2 = None
        self.extra_cash = extra_cash

        self.loans = loans

        if mode.lower() not in modes:
            print(self.errmsg + "Unsupported Mode: %s" %(mode))
            sys.exit(1)

        if mode != None:
            self.mode = mode.lower()
        if order != None:
            self.order = order
        if order2 != None:
            self.order2 = order2

        if self.mode.lower() == "cascade" or self.mode.lower() == "parallel":
            if self.order == None:
                print(self.errmsg + "%s Mode requires an order section" %(mode))
                sys.exit(1)

        if self.mode.lower() == "parallel":
            if self.order2 == None:
                print(self.errmsg + "%s Mode requires an order2 arguments" %(mode))
                sys.exit(1)

    def run_option(self):
#        print (self.option_num, self.mode, self.order, self.order2)

        if self.mode == "cascade":
            self.cascade()
        elif self.mode == "no_extra":
            self.no_extra()
        elif self.mode == "parallel":
            self.parallel()
        else:
            self.default()

    def cascade(self):
        # first we need to determine when each loan would normally end
        normal_months = []
        for x in self.loans:
            x.reset()
            month, money = x.calculate_loan()
            normal_months.append(month)
            x.reset()

        # Now we have when each loan would normally end, start cascading
        calc_month = []
        calc_money = []

        for x in range(len(self.loans)):
            calc_month.append(5)
            calc_money.append(55.5)

        more_extra = 0

        # Still need to check to see when the other loans finish
        for x in self.order:
            index = 0
            loan=None
            for loan in self.loans:
                if int(loan.loan_num) == int(x):
                    break
                index +=1

            month, money = loan.calculate_loan(self.extra_cash + more_extra)
            more_extra = loan.min_payment + loan.default_extra
            print (more_extra)

            calc_month[index] = month
            calc_money[index] = money


    def no_extra(self):
         # Nothing really to do, just run the defaults
        total_money = 0
        months = []
        money = []

        for x in self.loans:
            x.reset()
            (month, l_money) = x.calculate_loan(-1)
            months.append(month)
            money.append(l_money)
            total_money += l_money

       # print (months, money, total_money)

    def parallel(self):
        print("")

    def default(self):
        # Nothing really to do, just run the defaults
        total_money = 0
        months = []
        money = []

        for x in self.loans:
            x.reset()
            (month, l_money) = x.calculate_loan()
            months.append(month)
            money.append(l_money)
            total_money += l_money

        #print (months, money, total_money)


################## Main ##############################
config = get_config()

loans = []
options = []

loan_dict = []
options_dict= []
#paid_off = []

num_loans = int(config["common"]["num_loans"])
paid_off = (config["common"]["paid_off"])
num_options = int(config["common"]["num_options"])
extra_cash = float(config["common"]["extra_cash"])

num_paid = len(paid_off.strip().split())



# append the config sections to a variable for the loans
for x in range(num_loans + num_paid):
    if str(x+1) in paid_off:
        continue
    loan_dict.append(config["loan%s"%(x+1)])

loan_ctr = 1
# Create the loan objects
for x in loan_dict:
    foo = loan(float(x["apr"]),
               float(x["balance"]),
               float(x["payment"]),
               loan_ctr,
               float(x["extra_principal"]))
    loan_ctr+=1
    while str(loan_ctr) in paid_off:
        loan_ctr+=1
    loans.append(foo)

option_ctr =0
# append the config sections to a variable for the loans
for x in range(num_options):
#    options_dict.append(config["option%s"%(x)])
    option_num = x
    mode = config["option%s"%x]["mode"]
    order = None
    order2 = None
    try:
        temp = config["option%s"%x]["order"]
        order = temp.strip().split('"')[1].split()

        order2 = config["option%s"%x]["order2"]
        order2 = temp.strip().split('"')[1].split()
    except KeyError:
        pass

    bar = option(option_num, loans, mode, order, order2, extra_cash, num_paid)
    options.append(bar)

months_list = []
total_cost = 0

# go through the loans and calculate the loans with defaults
#for x in loans:
#    months, cost = x.calculate_loan()
#    months_list.append(months)
#    total_cost += cost

#print(total_cost)
#print(months_list)


# go through and run the different options
for x in options:
    x.run_option()
