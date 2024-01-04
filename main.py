from collections import UserDict
from datetime import date, datetime
import pickle


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError
        self.__value = new_value

    def is_valid(self, value):
        return True

    def __str__(self):
        return str(self.__value)


class Name(Field):
    def __init__(self, value):
        if not self.is_valid_name(value):
            raise ValueError
        super().__init__(value)

    def is_valid(self, value):
        return self.is_valid_name(value)

    def is_valid_name(self, value):
        return value.isalpha()


class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone_number(value):
            raise ValueError
        super().__init__(value)

    def is_valid(self, value):
        return self.is_valid_phone_number(value)

    def is_valid_phone_number(self, value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid_birthday(value):
            raise ValueError
        super().__init__(value)

    def is_valid(self, value):
        return self.is_valid_birthday(value)

    def is_valid_birthday(self, new_birthday):
        if new_birthday is not None:
            try:
                datetime.strptime(new_birthday, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        return True


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, value):
        try:
            self.phones.append(Phone(value))
            return True
        except ValueError:
            print(f"Phone can not be added {value}")
            return False

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)

    def edit_phone(self, phone, new_phone):
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                try:
                    self.phones[i] = Phone(new_phone)
                    return True
                except ValueError:
                    print(f"Phone {phone} can not be replaced by {new_phone}")
                    return False
        raise ValueError(f"Phone {phone} not found in the record.")

    def find_phone(self, phone):
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                return True
        return False

    def days_to_birthday(self):
        if self.birthday.value is not None:
            birthday = datetime.strptime(self.birthday.value, "%Y-%m-%d")
            today = date.today()
            next_birthday = datetime(today.year, birthday.month, birthday.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birthday.month, birthday.day).date()
            days_left = (next_birthday - today).days
            return days_left
        return None


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            print(f"{name} does not exist in dictionary")

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            print(f"{name} does not exist in dictionary")

    def __iter__(self):
        return AddressBookIterable(self)


class AddressBookIterable:
    def __init__(self, address_book):
        self.record = list(address_book.data.values())
        self.index = 0

    def __next__(self):
        if self.index < len(self.record):
            contact = self.record[self.index]
            self.index += 1
            return contact
        else:
            raise StopIteration


def input_error(func):
    def wrapper(*args, **argv):
        try:
            result = func(*args, **argv)
        except KeyError as err:
            return f"Error: Contact not found"
        except ValueError as err:
            return f"Error: Invalid input"
        except IndexError as err:
            return f"Error: Invalid command format"
        except TypeError as err:
            return f"Error {err}"

        return result

    return wrapper


class AddressBookManager():
    def __init__(self):
        self.address_book = self.read_book_from_file()

    @input_error
    def hello_user(self):
        return "How can I help you"

    @input_error
    def goodbye_user(self):
        self.save_book_to_file()
        return "Good bye!"

    @input_error
    def add_contact(self, name, birthday=None):
        new_record = Record(name, birthday)
        self.address_book.add_record(new_record)
        return f"Contact {name} with birthday {birthday} added successfully"

    @input_error
    def add_contact_phone(self, name, phone):
        record = self.address_book.find(name)
        if record:
            if record.find_phone(phone):
                return f"Contact {name} has already phone {phone}"
            elif record.add_phone(phone):
                return f"Contact {name} add phone {phone}"
            else:
                raise KeyError
        else:
            raise ValueError

    @input_error
    def change_contact_phone(self, name, phone, new_phone):
        record = self.address_book.find(name)
        if record:
            if record.find_phone(phone):
                record.edit_phone(phone, new_phone)
                return f"Contact {name} has changed old phone number {phone} to new one {new_phone}"
            else:
                return f"Contact {name} has no phone as {phone}"
        else:
            raise ValueError

    @input_error
    def remove_contact_phone(self, name, phone):
        record = self.address_book.find(name)
        if record:
            if record.find_phone(phone):
                record.remove_phone(phone)
                return f"Contact {name} has removed phone number {phone}"
            else:
                return f"Contact {name} has no phone number as {phone}"
        else:
            raise ValueError

    @input_error
    def phones_of_contact(self, name):
        record = self.address_book.find(name)
        if record:
            return f"Name: {record.name}; Phones: {', '.join(p.value for p in record.phones)}"
        else:
            raise ValueError

    @input_error
    def show_all_contacts(self):
        result = ''
        result += "Address Book"
        for index, record in enumerate(self.address_book):
            result += f"\n{index + 1} contact: \n\tName: {record.name}; \n\tPhones: {', '.join(p.value for p in record.phones)}; \n\tBirthday: {record.birthday}."
        return result

    @input_error
    def birthday_of_contact(self, name):
        record = self.address_book.find(name)
        if record and record.birthday.value is not None:
            return f"Left {record.days_to_birthday()} days to {name}'s birthday"
        elif record and record.birthday.value is None:
            return f"Date of birth is unknown"
        else:
            raise ValueError

    def save_book_to_file(self):
        with open("book.bin", 'wb') as fd:
            pickle.dump(self.address_book, fd)
            return f"Address Book has been saved to book.bin"

    def read_book_from_file(self):
        with open("book.bin", 'rb') as fd:
            unpacked = pickle.load(fd)
            return unpacked

    def search_contact(self, string):
        result = 'Matching with'
        for record in self.address_book:
            if string.lower() in record.name.value:
                result += f"\n\tname {record.name.value}"
            else:
                for phone in record.phones:
                    if string in phone.value:
                        result += f"\n\t{record.name.value}'s phone number {phone.value}"
        return result


manager = AddressBookManager()

OPERATIONS = {
    'hello': manager.hello_user,
    'add contact': manager.add_contact,
    'add': manager.add_contact_phone,
    'change': manager.change_contact_phone,
    'remove': manager.remove_contact_phone,
    'phones': manager.phones_of_contact,
    'birthday': manager.birthday_of_contact,
    'show all': manager.show_all_contacts,
    'search': manager.search_contact,
    'good bye': manager.goodbye_user,
    'close': manager.goodbye_user,
    'exit': manager.goodbye_user,
}


def get_handler(operator):
    return OPERATIONS[operator]


def parse_command(input_string):
    input_list = input_string.lower().split()
    if input_list[0] == 'show' and input_list[1] == 'all' and len(input_list) == 2:
        return input_string.lower().strip(), []
    elif input_list[0] == 'good' and input_list[1] == 'bye' and len(input_list) == 2:
        return input_string.lower().strip(), []
    elif input_list[0] == 'add' and input_list[1] == 'contact':
        return 'add contact', input_list[2:]
    else:
        return input_list[0], input_list[1:]


def main():
    print('Commands:'
          '\n\thello - greet the contact'
          '\n\tadd contact {name} {birthday} - add a new contact (birthday is optional)'
          '\n\tadd {name} {phone} - add a phone number to an existing contact'
          '\n\tchange {name} {phone} {new_phone} - change a phone number for a contact'
          '\n\tremove {name} {phone} - remove a phone number from a contact'
          '\n\tphones {name} - show all phone numbers belonging to a contact'
          "\n\tbirthday {name} - show how many days are left until the contact's birthday"
          '\n\tshow all - display all contacts'
          '\n\tsearch {string} - search for contacts by name or phone number'
          '\n\tgood bye, close, exit - exit the program')
    while True:
        command = input("Enter a command: ").lower().strip()
        operator, args = parse_command(command)
        handler = get_handler(operator)
        print(handler(*args))

        if operator in {'good bye', 'close', 'exit'}:
            break


if __name__ == '__main__':
    main()
