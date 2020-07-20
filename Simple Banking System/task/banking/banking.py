import random
import sqlite3

# ============= create account ===========

is_exit = False


def create_pin():
    return str(int(random.random() * 1e4)).zfill(4)


def create_checksum(string):
    accum = 0
    for i in reversed(range(len(string))):
        val = int(string[i]) * (1 if i % 2 else 2)
        accum += val if val <= 9 else val - 9
    return (10 - accum % 10) if accum % 10 > 0 else 0


def create_account():
    bank_id_st = '400000'
    act_st = str(int(random.random() * 1e6)).zfill(9)
    checksum_st = str(create_checksum(bank_id_st + act_st))
    return bank_id_st + act_st + checksum_st


def enter_acct():
    acct = input('Enter your card number:\n')
    if len(acct) != 16 or not acct.isnumeric():
        print('Invalid card number')
        return False
    lpin = input('Enter your PIN:\n')
    if len(lpin) != 4 or not lpin.isnumeric():
        print('Invalid PIN')
        return False
    query = "SELECT pin FROM card WHERE  number = '{}'".format(acct)
    cursor.execute(query)
    results = cursor.fetchone()
    if results is None:
        print('Wrong card number or PIN')
        return False
    if lpin != results[0]:
        print('Wrong card number or PIN')
        return False
    print('You have successfully logged in!')
    return acct


def get_balance(card_number):
    query = "SELECT balance FROM card WHERE  number = '{}'".format(card_number)
    cursor.execute(query)
    return int(cursor.fetchone()[0])


def add_income(card_number, addition):
    query = "UPDATE card SET balance = balance + {} WHERE number = {}".format(addition, card_number)
    cursor.execute(query)
    connection.commit()


def close_account(card_number):
    query = "DELETE FROM card WHERE number = {}".format(card_number)
    cursor.execute(query)
    connection.commit()


def has_enough_money(card_number, transfer_amount):
    if get_balance(card_number) < transfer_amount:
        return False
    return True


def is_card_exists(card_number):
    query = "SELECT * FROM card WHERE  number = '{}'".format(card_number)
    cursor.execute(query)
    return not cursor.fetchone() is None


def execute_transaction(from_card, to_card, amount):
    add_income(from_card, -1 * amount)
    add_income(to_card, amount)


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0


# ============= MAIN ============
connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
command1 = '''CREATE TABLE IF NOT EXISTS card 
(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)'''
cursor.execute(command1)

while True:
    # ============= User input ============
    choice = int(input('1. Create an account\n'
                       '2. Log into account\n'
                       '0. Exit'))
    if choice == 0:
        print('Bye!')
        connection.commit()
        break

    if choice == 1:
        try:
            card_num = create_account()
            print('Your card has been created')
            print('Your card number:\n{}'.format(card_num))
            pin = create_pin()
            print('Your card PIN:\n{}'.format(pin))
            cmd = "INSERT INTO card (number, pin) VALUES('{}', '{}')".format(card_num, pin)
            cursor.execute(cmd)
            connection.commit()
        except sqlite3.OperationalError:
            print('invalid attempt to append to database ----------')
            print('attempting to add {} with pin {} to\n'.format(card_num, pin))
            cursor.execute('SELECT * FROM card')
            results = cursor.fetchall()
            print(len(results))
            print(results)

    elif choice == 2:
        c_num = enter_acct()
        while True:
            if c_num:
                print('1. Balance\n'
                      '2. Add income\n'
                      '3. Do transfer\n'
                      '4. Close account\n'
                      '5. Log out\n'
                      '0. Exit')
            else:
                break
            choice2 = int(input())

            if choice2 == 1:
                print("Balance:", get_balance(c_num))
            elif choice2 == 2:
                income = int(input("Enter income:\n"))
                add_income(c_num, income)
                print("Income was added!\n")
            elif choice2 == 3:
                print("Transfer")
                t_card_number = input("Enter card number:\n")
                if t_card_number != c_num:
                    if is_luhn_valid(t_card_number):
                        if is_card_exists(t_card_number):
                            t_amount = int(input("Enter how much money you want to transfer:"))
                            if has_enough_money(c_num, t_amount):
                                execute_transaction(c_num, t_card_number, t_amount)
                            else:
                                print("Not enough money!")
                        else:
                            print("Such a card does not exist.")
                    else:
                        print("Probably you made mistake in the card number. Please try again!")
                else:
                    print("You can't transfer money to the same account!")
            elif choice2 == 4:
                close_account(c_num)
                print("\nThe account has been closed!\n")
                break
            elif choice2 == 5:
                print('You have successfully logged out!')
                break
            elif choice2 == 0:
                is_exit = True
                break
    if is_exit:
        break
