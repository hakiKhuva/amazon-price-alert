import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText

class PriceTracker:
    def __init__(self, config:dict) -> None:
        assert config.get("url"), "url is missing!"
        assert config.get("budget_price") != None, "budget_price is missing!"
        assert config.get("budget_price") > 0.00, "budget_price is missing!"

        self.url = config.get("url")
        # budget of user
        self.budget = config.get("budget_price")
        # user agent for headers
        self.user_agent = config.get(
            "user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        )
        # script timeout
        self.timeout = config.get("timeout",60)
        # for printing details only first time
        self._is_printed = False
        # sender email
        send_email = config.get("sender_email")
        send_password = config.get("sender_password")
        client_email = config.get("receiver_email")

        # checking if None
        assert send_email != None and type(send_email) == str
        assert send_password != None and type(send_password) == str
        assert client_email != None and type(client_email) == str

        self.__email_sender = send_email
        # sender email's passwod
        self.__email_password = send_password
        # receiver email
        self._client_email = client_email

    
    def _get_data(self) -> bytes:
        """
        returns URL page content
        """
        req = requests.get(self.url, headers={
            "user-agent" : self.user_agent
        })
        
        return req.content

    
    def _scrape_data(self) -> dict:
        """
        returns dictionary if all data exists else None
        """
        # getting data and passing it to the soup
        soup = BeautifulSoup(self._get_data(), "html.parser")

        # getting product title
        productTitle = soup.find("span",attrs={ "id" : "productTitle" })

        # getting product price block
        productPriceDisplay = soup.find("div", attrs={ "id" : "corePriceDisplay_desktop_feature_div" })

        # if title not found
        if not productTitle:
            print("Product title not found!")
            return
        
        # if product price block not found
        if not productPriceDisplay:
            print("Product price not found!")
            return 

        #  getting data
        # :------------:
        # title of product
        product_title = productTitle.getText().strip()
        # currency symbol
        price_symbol = productPriceDisplay.find("span", { "class" : "a-price-symbol" }).getText().strip()
        # price of product
        price_whole = "".join(productPriceDisplay.find("span", { "class" : "a-price-whole" }).getText().strip().split(","))
        # stripping to get whole number
        price_whole = price_whole.rstrip(".")
        # getting fraction part
        price_fraction = productPriceDisplay.find("span", { "class" : "a-price-fraction" }).getText().strip()
        
        # typecasting to float
        product_price = "{}.{}".format(price_whole, price_fraction)
        product_price = float(product_price)

        return {
            "title" : product_title,
            "price" : product_price,
            "symbol" : price_symbol
        }


    def _print_details(self, name:str, price:float, symbol:str ) -> None:
        """
        Print details by passed parameters only for first time
        """
        if not self._is_printed:
            print("Product name  : {}".format(name))
            print("Product price : {}{}".format(symbol,price))
            print("Your budget   : {}{}".format(symbol, self.budget))

            self._is_printed = True


    def run(self) -> None:
        """
        Run script
        """
        content = self._scrape_data()   # getting title, price, symbol

        if not content: return # if data is None
        
        title,price,symbol = content["title"], content["price"], content["symbol"]

        self._print_details(title, price, symbol)   # print details to the console

        if price <= self.budget:
            # if price is less than or equal to budget
            self._send_mail(title, price, symbol)
        else:
            print("Current price({}{}) is more than your budget.".format(symbol, price))
            print("waiting for {} second(s).".format(self.timeout), end="\r")

            time_passed = 0
            while time_passed < self.timeout:
                print("waiting for {} second(s).".format(self.timeout-time_passed), end="\r")
                time.sleep(1)
                time_passed += 1
            
            print("\n\nrunning script again"+" "*len(str(self.timeout)))
            self.run()

    
    def _send_mail(self, title, price, symbol):
        """
        Sending email to client that product price is now in his/her budget
        """
        message = f"""
        <h1>Product price changed</h1>
        <hr/>
        <div>
        <div>Product Title : {title}</div>
        <br/>
        <div>Product Price(current) : {symbol}{price}</div>
        <br/>
        <div>Your Budget : {symbol}{self.budget}</div>
        </div>
        <hr/>
        <div>
        <a href="{self.url}">Click to open product page</a>
        </div>
        """

        message = MIMEText(message, "html", "utf-8")
        message["From"] = self.__email_sender
        message["To"] = self._client_email
        message["Subject"] = "Price changed!!!"
        message = message.as_string()
        
        try:
            smtp_obj = smtplib.SMTP("smtp.gmail.com",587)
            smtp_obj.ehlo()
            smtp_obj.starttls()
            smtp_obj.login(self.__email_sender, self.__email_password)
            smtp_obj.sendmail(
                self.__email_sender,
                self._client_email,
                message
            )
        except Exception as e:
            print("An error occured[sending email] :", e)
        else:
            print("Email sent successfully.")
            smtp_obj.quit()


tracker = PriceTracker({
    "url" : "https://www.amazon.in/Boat-Bassheads-242-Earphones-Resistance/dp/B07S9S86BF/",
    "budget_price" : 449,
    "sender_email" : "sender_email",
    "sender_password" : "sender_email_password",
    "receiver_email" : "client_email",
    "timeout" : 3600
})

tracker.run()
