from collections import defaultdict
import os

TRADER_FILENAME = "trader.txt"
ERRORS_FILENAME = "errors.txt"
LOGO_FILE = "ascii_logo.txt"

os.system("mode con: cols=150 lines=55")
os.system("cls")
os.system("TITLE STS Trader Editor")

class trader_editor:
    def __init__(self):
        self._set_color('0A')
        self.editted_file = dict()
        self.items = defaultdict(int)
        self.buy_costs = defaultdict(list)
        self.sell_costs = defaultdict(list)
        self.trader_category = dict()
        self.line_num = 0
        self.price_errors = []
    
        
    def _set_color(self, color):
        os.system('color {}'.format(color))
        
    def _all_same(self, l):
        if len(l) == 0:
            return True
        s = l[0][0]
        for c in l:
            if c[0] != s:
                return False
        return True
    
    def _yes(self, string):
        if string.lower() in ("", "y","yes","yeah","yea"):
            return True
        return False
        
    def parse(self, filename):
        self.editted_file = dict()
        self.items = defaultdict(int)
        self.buy_costs = defaultdict(list)
        self.sell_costs = defaultdict(list)
        self.trader_category = dict()
        self.line_num = 0
        self.price_errors = []
        
        with open(filename, "r") as file:
            #self.parse and locally store data.
            for line in file.readlines():
                self.line_num += 1
                orig_line = line
                line = line.strip('\t ')
                if line.startswith("<"):
                    if "Trader" in line:
                        trader = " ".join(line.split()[1:])
                    if "Category" in line:
                        category = " ".join(line.split()[1:])
                
                if line.startswith("-") or line.startswith("/") or line.startswith('\t'):
                    self.editted_file[self.line_num] = orig_line
                    continue
                    
                line = [item.strip('\t') for item in line.split(',')]
                if len(line) == 4:
                    item_name = line[0].strip()
                    capacity = line[1].strip()
                    buy_price = line[2].strip()
                    sell_price = line[3].strip().split()[0].strip()
                
                    if int(sell_price) > int(buy_price) and buy_price != '-1':
                        self.price_errors.append(self.line_num)
                    
                    if item_name != '#x9':
                        self.items[item_name] += 1
                    self.trader_category[self.line_num] = (trader,category)
                    self.buy_costs[item_name].append((buy_price,self.line_num))
                    self.sell_costs[item_name].append((sell_price,self.line_num))
                    self.editted_file[self.line_num] = (item_name,capacity, buy_price, sell_price)
                    continue
                self.editted_file[self.line_num] = orig_line
                
    def write_errors(self, filename):
        with open(filename, "w") as output:
            if len(self.price_errors) > 0:
                for line_n in self.price_errors:
                    item_name,capacity,buy_price,sell_price = self.editted_file[line_n]
                    print("[!] Price Error: {} | Buy Value = {} | Sell Value = {} | Line = {}".format(item_name, buy_price,sell_price, line_n))
                  
            for item_name, count in self.items.items():
                if count > 1:
                    buy_prices = self.buy_costs[item_name]
                    sell_prices = self.sell_costs[item_name]
                    if not (self._all_same(buy_prices) and self._all_same(sell_prices)):          
                        print("-----------------------------------------------------------------------------------------------------------\n", file = output)
                        print("[!] Inconsistent Price Error: {} \n".format(item_name), file = output)
                        for buys, sells in zip(buy_prices, sell_prices):
                            assert(buys[1] == sells[1])
                            line_n = buys[1]
                            buy_price = buys[0]
                            sell_price = sells[0]
                            c_trader, c_category = self.trader_category[line_n]
                            print("{0:^30} | {1:^30} | Buy Price = {2:^6} | Sell Price = {3:^6}".format(c_trader, c_category, buy_price, sell_price), file = output)
                            
    def write_output(self):
        #output new trader to ERRORS_FILENAME
        with open(TRADER_FILENAME, "w") as new_file:
            for line in self.editted_file.values():
                if type(line) is str:
                    new_file.write(line)
                elif type(line) is tuple:
                    new_file.write("\t\t{0:<40},{1:<3},{2:<10},{3:<10}\n".format(*line))
                
    def fix_errors(self):       
        #Edit buy price > sell price error    
        for line_n in self.price_errors:
            item_name,capacity,buy_price,sell_price = self.editted_file[line_n]
            print("[!] Price Error: {} | Buy Value = {} | Sell Value = {}".format(item_name, buy_price,sell_price))
            print("[INFO] Entering nothing will use the old value.")
            new_buy_val = input("Enter new Buy Value: ")
            if not new_buy_val:
                new_buy_val = buy_price
            new_sell_val = input("Enter new Sell Value: ")
            if not new_sell_val:
                new_sell_val = sell_price
            self.editted_file[line_n] = (item_name, capacity, new_buy_val, new_sell_val)
            
        #Edit price inconsitencies in multiple locations/traders
        for item_name, count in self.items.items():
            if count > 1:
                buy_prices = self.buy_costs[item_name]
                sell_prices = self.sell_costs[item_name]
                if not (self._all_same(buy_prices) and self._all_same(sell_prices)):
                    print("-----------------------------------------------------------------------------------------------------------\n")
                    print("\n [!] Inconsistent Price Error: {} \n".format(item_name))
                    for buys, sells in zip(buy_prices, sell_prices):
                        assert(buys[1] == sells[1])
                        line_n = buys[1]
                        buy_price = buys[0]
                        sell_price = sells[0]
                        c_trader, c_category = self.trader_category[line_n]
                        print("{0:<30} | {1:<30} | Buy Price = {2:<6} | Sell Price = {3:<6}".format(c_trader, c_category, buy_price, sell_price))
                    if(self._yes(input("\n\nWould you like to modify ALL buy and sell prices AT ONCE (set all item ocurrences buy/sell prices to be the same)? [Y/n]"))):
                        new_buy_val = None
                        new_sell_val = None
                        while not new_buy_val:
                            new_buy_val = input("Enter new Buy Value: ").strip()
                        while not new_sell_val:
                            new_sell_val = input("Enter new Sell Value: ").strip()
                        for buys, sells in zip(buy_prices, sell_prices):
                            if buys[1] != sells[1]:
                                assert(buys[1] == sells[1])
                            line_n = buys[1]
                            self.editted_file[line_n] = (item_name, self.editted_file[line_n][1], new_buy_val, new_sell_val)
                    elif(self._yes(input("\n\nWould you like to modify EACH buy and sell price INDIVIDUALLY? [Y/n]"))):
                        for buys, sells in zip(buy_prices, sell_prices):
                            assert(buys[1] == sells[1])
                            line_n = buys[1]
                            buy_price = buys[0]
                            sell_price = sells[0]
                            c_trader, c_category = self.trader_category[line_n]
                            print("{0:<30} | {1:<30} | Buy Price = {2:<6} | Sell Price = {3:<6}".format(c_trader, c_category, buy_price, sell_price))
                            print("[INFO] Entering nothing will use the old value.")
                            new_buy_val = input("Enter new Buy Value : ")
                            if not new_buy_val:
                                new_buy_val = buy_price
                            new_sell_val = input("Enter new Sell Value: ")
                            if not new_sell_val:
                                new_sell_val = sell_price
                            self.editted_file[line_n] = (item_name, self.editted_file[line_n][1], new_buy_val, new_sell_val)
                    cont = input("\nSave Progress? [Y/n/quit]")
                    if(self._yes(cont)):
                        self.write_output()
                    elif cont.lower() in ("q","quit", "exit"):
                        break

    def get_item_details(self, item_name) -> bool:
        if not self.buy_costs.get(item_name):
            return False
            
        buy_prices = self.buy_costs[item_name]
        sell_prices = self.sell_costs[item_name]    
        
        for buys, sells in zip(buy_prices, sell_prices):
            assert(buys[1] == sells[1])
            
            line_n = buys[1]
            capacity = self.editted_file[line_n][1]
            buy_price = buys[0]
            sell_price = sells[0]
            c_trader, c_category = self.trader_category[line_n]
            
            print("{0:^30} | {1:^30} | Capacity = {2:^2} | Buy Price = {3:^6} | Sell Price = {4:^6} | (Line: {5:^6}".format(c_trader, c_category, capacity, buy_price, sell_price, str(line_n) + ')'))
            
        if self._yes(input("\nWould you like to modify {}'s details? [Y/n]".format(item_name))):
            self.modify_item(item_name)
            
        return True
        
    def modify_item(self, item_name):
        if not self.buy_costs.get(item_name):
            return False
            
        buy_prices = self.buy_costs[item_name]
        sell_prices = self.sell_costs[item_name]       
        
        
        for buys, sells in zip(buy_prices, sell_prices):
            assert(buys[1] == sells[1])
            
            line_n = buys[1]
            buy_price = buys[0]
            sell_price = sells[0]
            capacity = self.editted_file[line_n][1]
            c_trader, c_category = self.trader_category[line_n]
            print("\n \n ENTRY BEING MODIFIED:\n")
            print("{0:^30} | {1:^30} | Capacity = {2:^2} | Buy Price = {3:^6} | Sell Price = {4:^6} | (Line: {5:^5}".format(c_trader, c_category, capacity, buy_price, sell_price, str(line_n)+')'))
            
            
            print("\n[INFO] Entering nothing will use the old value.\n")
            
            new_capacity = input("Enter new CAPACITY Value : ")
            if not new_capacity:
                new_capacity = capacity
            new_buy_val = input("Enter new BUY PRICE Value : ")
            if not new_buy_val:
                new_buy_val = buy_price
            new_sell_val = input("Enter new SELL PRICE Value: ")
            if not new_sell_val:
                new_sell_val = sell_price
            self.editted_file[line_n] = (item_name, new_capacity, new_buy_val, new_sell_val)
            self.write_output()
            
        return True
                    

    def _get_choice(self):
        print(f"\n[1] Generate Error Report ('{ERRORS_FILENAME}')\n[2] Correct All Errors\n[3] View Item Details\n[4] Modify Item Details\n[5] Quit\n")
        choice = input("What would you like to do?")
        if choice.lower() in ('1', '2', '3','4', '5', 'quit', 'exit', 'q'):
            return choice
        else:
            os.system("cls")
            print("\nSorry, that choice wasn't recognized. Please try again.")
            return self._get_choice()


    def run(self):
    
        self._set_color('0A')
        choice = self._get_choice()
        while choice not in ('5', 'quit', 'exit', 'q'):
            os.system("cls")
            self.parse(TRADER_FILENAME)
            
            if choice == '1':
                self.write_errors(ERRORS_FILENAME)
                print("\n[INFO] Success.")
            elif choice == '2':
                self.fix_errors()
                os.system("cls")
                print("\nSuccessfully adjusted items.")
            elif choice == '3':
                if not self.get_item_details(input("Please enter the item name you are looking for (Has to be exact item classname): ")):
                    print("\nSorry, that item was not found.")
                else:
                    os.system("cls")
                    print("\n[INFO] Success.")
            elif choice == '4':
                if not self.modify_item(input("Please enter the item name you want to modify: (Has to be exact item classname)")):
                    print("\nSorry, that item was not found.")
                else:
                    os.system("cls")
                    print("\n[INFO] Success.")
            choice = self._get_choice()
        os.system("cls")
        self._set_color('09')
        with open(LOGO_FILE) as logo:
            print(logo.read())
        print("{0:^100}".format("Thanks for using Eden's Trader Editor."))
        print("{0:^100}".format("If you can any questions, feel free to join our Discord:"))
        print("{0:^100}".format("https://discord.gg/a2SZD3D"))
        os.system("pause")

if __name__ == "__main__":
    trader_editor().run()
        