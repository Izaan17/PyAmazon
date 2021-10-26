import threading
import pyfiglet
import smtplib
import datetime
from selenium import webdriver
import time
from termcolor import cprint

REFRESH_TIME = 0
VERSION = 1.0


# Whenever we need to save data to a file we call this function.
def save_file(contents, directory, mode='w', lines=False):
    try:
        with open(directory, mode) as file:
            if lines:
                file.writelines(contents)
            else:
                file.write(contents)
    except Exception as e:
        print(e)


# Whenever we need to read data from a file we call this function.
def read_file(directory, lines=False, mode='r'):
    try:
        with open(directory, mode) as file:
            if lines:
                return file.readlines()
            return file.read()
    except Exception as e:
        print(e)


# This makes the text have a border around it.
def border(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)


# We can send emails using this function.
def send_email(subject='', body=''):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('pythonlogstest@gmail.com', 'eypgbhcnqezxjrhb')

    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail(
        'pythonlogstest@gmail.com',
        'izaan.nyc@gmail.com',
        msg
    )

    server.quit()


# This is the function that compares the prices of the previous items price.
def compare_price(link):
    while True:
        initial_price, initial_price_formatted, prod_name = get_prod_info(link)
        new_price, new_price_formatted, prod_name = get_prod_info(link)
        msg = f"""
    PRODUCT: {prod_name}
    NEW PRICE: {new_price}
    OLD PRICE: {initial_price}
    URL: {link}"""
        # if the  new price is lower than the original we will send a email.
        if float(initial_price_formatted) > float(new_price_formatted):
            send_email(subject='Price Decreased!', body=msg)
            print(f"[+] Price Changed: {msg}")
            break
        elif float(new_price_formatted) > float(initial_price_formatted):
            send_email(subject='Price Increased!', body=msg)
            print(f"[+] Price Changed: {msg}")
            break
        else:
            print(f'[NO CHANGES]:{prod_name}')
        time.sleep(REFRESH_TIME)
    # Save prod info in log file
    save_file(f'{border(datetime.datetime.now() + prod_name + initial_price)}\n', 'pylog.txt', mode='a')


# This function returns us product information such as the price, formatted price (price into float) and the product name.
def get_prod_info(link):
    # prepare the option for the chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    # start chrome browser
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(link)
    # get price of item
    try:
        price = driver.find_element_by_id('priceblock_ourprice').text
    except:
        price = driver.find_element_by_class_name('a-size-medium a-color-price priceBlockBuyingPriceString').text
    price_formatted = str(price).replace('$', '')
    price_formatted = float(price_formatted)
    prod_name = driver.find_element_by_id('productTitle').text
    driver.close()
    driver.quit()
    return price, price_formatted, prod_name


# This function returns a True or False value depending if the url fits all the flags.
def check_link(url):
    link_file = read_file('websites.md')
    if 'https://www.amazon.' in url:
        return True, '[+] Valid amazon link.'
    elif url in link_file and url != '':
        return False, '[*] Link already in list.'
    else:
        return False, '[ERROR]: This is not an amazon link.'


# We kill the program with this function.
def killall():
    exit()
    quit()


# This function allows us to add new urls to the file which stores the urls.
def add_url(url):
    valid, reason = check_link(url)
    if valid:
        save_file(url + "\n", 'websites.md', mode='a')
    print(reason)


# This function removes urls from the websites.md file.
def remove_url():
    while True:
        # get urls
        urls = read_file('websites.md', lines=True)
        if len(urls) > 0:
            link_to_remove, output = user_selection(urls, prompt='[REMOVE]: ')
            if link_to_remove:
                # remove the link from the file
                links = read_file('websites.md', lines=True)
                del links[link_to_remove - 1]
                save_file(links, 'websites.md', lines=True)
            if link_to_remove == 0 or len(urls) <= 0:
                break
            else:
                print(output)
        else:
            print('[LINKS] No links to remove.')
            break


# This function is used multiple times in the script to get user input based on user choices.
def user_selection(choices, header='', header_color=None, color=None, prompt='>>> ', bordered=False):
    current_index = 1
    formatted_choices = []
    if isinstance(choices, list):
        cprint(pyfiglet.figlet_format(header, font="standard"), header_color)
        for choice in choices:
            choice_formatted = f"[{current_index}]: {choice}"
            formatted_choices.append(choice_formatted)
            current_index += 1
            if not bordered:
                cprint(choice_formatted, color)
        if bordered:
            cprint(border('\n'.join(formatted_choices)), color)

        try:
            selected = input(prompt)
            if len(choices) >= int(selected) > 0:
                return int(selected), ''
            else:
                return False, "[Error]: Selected choice not available."
        except ValueError:
            return False, "[Error]: Please only use numbers."


# This function runs in the beginning of the script.
def start():
    cprint(pyfiglet.figlet_format('PyAmazon', font="standard"), color='yellow')
    cprint(border(f"""[VERSION] {VERSION}\n[REFRESH] {REFRESH_TIME}\n[INFO] Made By Izaan Noman            """),
           color="white")


# This is the main function we run with all other functions inside.
def main():
    global REFRESH_TIME
    start()
    while 1:
        choice, output = user_selection(bordered=True, prompt='[SELECT]: ', color='white',
                                        choices=['Add Link', 'Remove Link', 'Change Refresh Time', 'Start Track',
                                                 'Quit'])
        if choice is False:
            print(output)
        if choice == 1:
            while 1:
                url = input('[URL]: ')
                if url == '0':
                    break
                else:
                    add_url(url=url)
        elif choice == 2:
            remove_url()
        elif choice == 3:
            REFRESH_TIME = int(input('[REFRESH]: '))
        elif choice == 4:
            for link in read_file('websites.md', lines=True):
                t = threading.Thread(target=compare_price, args=[link], daemon=True)
                t.start()
        elif choice == 5:
            killall()


if __name__ == '__main__':
    main()
