from collections import defaultdict
import os

def set_color(color):
    os.system('color {}'.format(color))

TRADER_FILENAME = "trader.txt"
ERRORS_FILENAME = "errors.txt"

editted_file = dict()
items = defaultdict(int)
buy_costs = defaultdict(list)
sell_costs = defaultdict(list)
trader_category = dict()
line_num = 0
price_errors = []
def all_same(l):
    if len(l) == 0:
        return True
    s = l[0][0]
    for c in l:
        if c[0] != s:
            return False
    return True
    
def yes(string):
    if string.lower() in ("", "y","yes","yeah","yea"):
        return True
    return False
    
def parse(filename):
    global editted_file
    global items
    global buy_costs
    global sell_costs
    global trader_category
    global line_num
    global price_errors
    
    del editted_file
    del items
    del buy_costs
    del sell_costs
    del trader_category
    del line_num
    del price_errors
    
    editted_file = dict()
    items = defaultdict(int)
    buy_costs = defaultdict(list)
    sell_costs = defaultdict(list)
    trader_category = dict()
    line_num = 0
    price_errors = []
    
    with open(filename, "r") as file:
        #Parse and locally store data.
        for line in file.readlines():
            line_num += 1
            orig_line = line
            line = line.strip('\t ')
            if line.startswith("<"):
                if "Trader" in line:
                    trader = " ".join(line.split()[1:])
                if "Category" in line:
                    category = " ".join(line.split()[1:])
            
            if line.startswith("-") or line.startswith("/") or line.startswith('\t'):
                editted_file[line_num] = orig_line
                continue
            line = [item.strip('\t') for item in line.split(',')]
            if len(line) == 4:
                item_name = line[0].strip()
                capacity = line[1].strip()
                buy_price = line[2].strip()
                sell_price = line[3].strip().split()[0].strip()
                if int(sell_price) > int(buy_price) and buy_price != '-1':
                    price_errors.append(line_num)
                
                if item_name != '#x9':
                    items[item_name] += 1
                trader_category[line_num] = (trader,category)
                buy_costs[item_name].append((buy_price,line_num))
                sell_costs[item_name].append((sell_price,line_num))
                editted_file[line_num] = (item_name,capacity, buy_price, sell_price)
                continue
            editted_file[line_num] = orig_line
            
def write_errors(filename):
    global editted_file
    global items
    global buy_costs
    global sell_costs
    global trader_category
    global price_errors
    
    with open(filename, "w") as output:
        if len(price_errors) > 0:
            for line_n in price_errors:
                item_name,capacity,buy_price,sell_price = editted_file[line_n]
                print("[!] Price Error: {} | Buy Value = {} | Sell Value = {} | Line = {}".format(item_name, buy_price,sell_price, line_n))
              

        for item_name, count in items.items():
            if count > 1:
                buy_prices = buy_costs[item_name]
                sell_prices = sell_costs[item_name]
                if not (all_same(buy_prices) and all_same(sell_prices)):          
                    print("-----------------------------------------------------------------------------------------------------------\n", file = output)
                    print("[!] Inconsistent Price Error: {} \n".format(item_name), file = output)
                    for buys, sells in zip(buy_prices, sell_prices):
                        assert(buys[1] == sells[1])
                        line_n = buys[1]
                        buy_price = buys[0]
                        sell_price = sells[0]
                        c_trader, c_category = trader_category[line_n]
                        print("{0:^30} | {1:^30} | Buy Price = {2:^6} | Sell Price = {3:^6}".format(c_trader, c_category, buy_price, sell_price), file = output)
                        
def write_output():
    #output new trader to output.txt
    global editted_file
    
    with open(TRADER_FILENAME, "w") as new_file:
        for line in editted_file.values():
            if type(line) is str:
                new_file.write(line)
            elif type(line) is tuple:
                new_file.write("\t\t{0:<40},{1:<3},{2:<10},{3:<10}\n".format(*line))
            
def fix_errors():       
    #Edit buy price > sell price error    
    global editted_file
    global items
    global buy_costs
    global sell_costs
    global trader_category
    global price_errors
    
    for line_n in price_errors:
        item_name,capacity,buy_price,sell_price = editted_file[line_n]
        print("[!] Price Error: {} | Buy Value = {} | Sell Value = {}".format(item_name, buy_price,sell_price))
        print("[INFO] Entering nothing will use the old value.")
        new_buy_val = input("Enter new Buy Value: ")
        if not new_buy_val:
            new_buy_val = buy_price
        new_sell_val = input("Enter new Sell Value: ")
        if not new_sell_val:
            new_sell_val = sell_price
        editted_file[line_n] = (item_name, capacity, new_buy_val, new_sell_val)
        
    #Edit price inconsitencies in multiple locations/traders
    for item_name, count in items.items():
        if count > 1:
            buy_prices = buy_costs[item_name]
            sell_prices = sell_costs[item_name]
            if not (all_same(buy_prices) and all_same(sell_prices)):
                print("-----------------------------------------------------------------------------------------------------------\n")
                print("\n [!] Inconsistent Price Error: {} \n".format(item_name))
                for buys, sells in zip(buy_prices, sell_prices):
                    assert(buys[1] == sells[1])
                    line_n = buys[1]
                    buy_price = buys[0]
                    sell_price = sells[0]
                    c_trader, c_category = trader_category[line_n]
                    print("{0:<30} | {1:<30} | Buy Price = {2:<6} | Sell Price = {3:<6}".format(c_trader, c_category, buy_price, sell_price))
                if(yes(input("\n\nWould you like to modify ALL buy and sell prices AT ONCE (set all buy/sell prices to be the same)? [Y/n]"))):
                    new_buy_val = None
                    new_sell_val = None
                    while not new_buy_val:
                        new_buy_val = input("Enter new Buy Value: ")
                    while not new_sell_val:
                        new_sell_val = input("Enter new Sell Value: ")
                    for buys, sells in zip(buy_prices, sell_prices):
                        if buys[1] != sells[1]:
                            assert(buys[1] == sells[1])
                        line_n = buys[1]
                        editted_file[line_n] = (item_name, editted_file[line_n][1], new_buy_val, new_sell_val)
                elif(yes(input("\n\nWould you like to modify EACH buy and sell price INDIVIDUALLY? [Y/n]"))):
                    for buys, sells in zip(buy_prices, sell_prices):
                        assert(buys[1] == sells[1])
                        line_n = buys[1]
                        buy_price = buys[0]
                        sell_price = sells[0]
                        c_trader, c_category = trader_category[line_n]
                        print("{0:<30} | {1:<30} | Buy Price = {2:<6} | Sell Price = {3:<6}".format(c_trader, c_category, buy_price, sell_price))
                        print("[INFO] Entering nothing will use the old value.")
                        new_buy_val = input("Enter new Buy Value : ")
                        if not new_buy_val:
                            new_buy_val = buy_price
                        new_sell_val = input("Enter new Sell Value: ")
                        if not new_sell_val:
                            new_sell_val = sell_price
                        editted_file[line_n] = (item_name, editted_file[line_n][1], new_buy_val, new_sell_val)
                cont = input("\nSave Progress? [Y/n/quit]")
                if(yes(cont)):
                    write_output()
                elif cont.lower() in ("q","quit", "exit"):
                    break

def get_item_details(item_name) -> bool:
    global buy_costs
    global sell_costs
    global trader_category
    if not buy_costs.get(item_name):
        return False
        
    buy_prices = buy_costs[item_name]
    sell_prices = sell_costs[item_name]    
    
    for buys, sells in zip(buy_prices, sell_prices):
        assert(buys[1] == sells[1])
        
        line_n = buys[1]
        capacity = editted_file[line_n][1]
        buy_price = buys[0]
        sell_price = sells[0]
        c_trader, c_category = trader_category[line_n]
        
        print("{0:^30} | {1:^30} | Capacity = {2:^2} | Buy Price = {3:^6} | Sell Price = {4:^6} | (Line: {5:^6}".format(c_trader, c_category, capacity, buy_price, sell_price, str(line_n) + ')'))
        
    if yes(input("\nWould you like to modify {}'s details? [Y/n]".format(item_name))):
        modify_item(item_name)
        
    return True
    
def modify_item(item_name):
    global buy_costs
    global sell_costs
    global trader_category
    if not buy_costs.get(item_name):
        return False
        
    buy_prices = buy_costs[item_name]
    sell_prices = sell_costs[item_name]       
    
    
    for buys, sells in zip(buy_prices, sell_prices):
        assert(buys[1] == sells[1])
        
        line_n = buys[1]
        buy_price = buys[0]
        sell_price = sells[0]
        capacity = editted_file[line_n][1]
        c_trader, c_category = trader_category[line_n]
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
        editted_file[line_n] = (item_name, new_capacity, new_buy_val, new_sell_val)
        write_output()
        
    return True
                

def get_choice():
    print("\n[1] Generate Error Report ('output.txt')\n[2] Correct All Errors\n[3] View Item Details\n[4] Modify Item Details\n[5] Quit\n")
    choice = input("What would you like to do?")
    if choice.lower() in ('1', '2', '3','4', '5', 'quit', 'exit'):
        return choice
    else:
        os.system("cls")
        print("\nSorry, that choice wasn't recognized. Please try again.")
        return get_choice()


    
os.system("mode con: cols=150 lines=55")
os.system("cls")
set_color('0A')
os.system("TITLE STS Trader Editor")
choice = get_choice()
while choice not in ('5', 'quit', 'exit'):

    os.system("cls")
    set_color('0A')
    parse(TRADER_FILENAME)
    
    if choice == '1':
        write_errors(ERRORS_FILENAME)
        print("\n[INFO] Success.")
    elif choice == '2':
        fix_errors()
        os.system("cls")
        print("\nNo more errors.")
    elif choice == '3':
        if not get_item_details(input("Please enter the item name you are looking for: ")):
            print("\nSorry, that item was not found.")
        else:
            os.system("cls")
            print("\n[INFO] Success.")
    elif choice == '4':
        if not modify_item(input("Please enter the item name you want to modify: ")):
            print("\nSorry, that item was not found.")
        else:
            os.system("cls")
            print("\n[INFO] Success.")
    choice = get_choice()
    
os.system("cls")
set_color('09')
print("""MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMNOxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxONMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMk'.'''''''''''''''''''''''''''''''''''''''..xWMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMWx'',,,,,,,,,'''''',,,,,,,,,'''''',,,,,,,,,'.oWMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMWo.,,,,,'..,:ccccc'.,,,,,,,.'clccc:,'.',,,;'.lNMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMNl.,,,,.'lOXWWMMMNl.,,,,,,'.lNMMMWWXOo'.,,,,.cNMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMNc.,,,.,kWMMMMMMMNl.,,,,,,'.lNMMMMMMMWO,.,,,.:XMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMX:.,,..xWMMMMMMMMNl.,,,,,,'.lNMMMMMMMMWk'.,,.;KMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMWNK0OkxxxxkO0Kk,.,'.:XMMMMMMMMMNl.,,,,,,'.lNMMMMMMMMMXc.,,.,kK0Okxxxxxk0KXWMMMMMMMMMMMMM
MMMMMMMMWKxoc:;,'''''''',,,.....:KWMMMMMMMMNl.,,,,,,'.lNMMMMMMMMMXc.....',,''''''.'',;:ldONMMMMMMMMM
MMMMMWXxc,'',;,,,'''',,,,,;;,,'..cNMMMWKOkkkl;;,''','.lNMMMMMMMMWx..',,,,,;,,,'''',,,,,'.';o0WMMMMMM
MMMMNx;',,;,'.',;:ccc:;'.',,,,,,.:XMXOxxk0KXXXKOxool,.cNMMMMMMMMWo.',,,,,'.',;:ccc:,'.',,,'.'oXMMMMM
MMMNo'';,,,.'lOXNWWWWWNKx:.',,,,.;OkdkXWWWWWWWWWWWWWKd:lONMMMMMMWo.',,,'.,o0XNWWWWWX0d,.',,,'.:KMMMM
MMWd'',,,,..xWMMMMMMMMMMMNd'.,,,..;:lkKWWWWWWWWWWWWMW0dollOWMMMMNl.,,,'.cKMMMMMMMMMMMMO,.,,,,'.cNMMM
MMX:.,,,,,.'kMMMMMMMMMMMMMNo.',,.'xK0O0XWWWWWNKKXWWWWWWWNocKMMMMNc.,,'.:KMMMMMMMMMMMMMK;.,,,,,.'OMMM
MMK;.,,,,,'.;kXWMMMMMMMMMMM0,.,,'oNWWWWWWWWNK00XNWWWWWWWWk:kMMMMNc.,,..xWMMMWNWWMMMMN0c'',,,,,..kMMM
MMX:.,,,,,,,'';ldOKNWMMMMMMNl....lKNNNNXK000KNWWWNNNNWNNNKcoNMMMNl....;0MWKxlccldkxl:,',,,,,,,.'OMMM
MMWx..,,,,,,,,,''',:coxOXNMMXOkkdc;,;:ldkOKKKKKOkkxk0XXXNNx;xWMMMXOkkkKN0o:;;,''...',,,,,,,,,'.lNMMM
MMMNd'.,,,,,,,,,,,,,,''';:lxOXWXo;,,:cclodddddoolllloxkOOOd;;oONMMMMMN0o;,,;,,',..,,,,,,,,,,..cKMMMM
MMMMWO:'.',,,,,,,,,,,,,;,,''';lo;,;;:ldkoclcccoddoollllllllc;',oKMNOoc;,,,;;,'''',,,,,,,,,..;xNMMMMM
MMMMMMNOo;'..',,,,,,,,,,,,,,,,'...,,;:clccll::okOdl::ccolccccc;,xkc,',;;,,,''',,,,,,,,'..,ckXMMMMMMM
MMMWNNNWWN0xl:,'..',,,,,,,,,,,,,..';cccclolcllcccccccccl:clllc;c:..,,',,'..',,,,''..';cdOXWWNNNWMMMM
MMKl::::xWMMMWXOxlc;'..',,,,,,,,,'';clllolcclccloodolclc,,''',;'.:xxc,,'..''...,:ldkKNWMMWOc;:;cOMMM
MMk'.,,.;KMMMMMMMMWN0koc,.',,,,,,'.,,;:ccc;lxocloollllc:cll:;;''cO0Xk,....':lxOXWMMMMMMMMNl.',..dWMM
MMO'.,,.'kMMMMMMMMMMMMMWXd'.,,,,,.''..;lcc;;lolclccccclllolllolcllc:'.'..c0WMMMMMMMMMMMMMK;.,,..xMMM
MM0,.,,'.cNMMMMMMMMMMMMMMWo.,,,,,'...........',;,,;;:llllc:cllcclll'.',.:XMMMMMMMMMMMMMMWd.',,..xMMM
MMK;.,,,'.oNMMMMMMMMMMMMMXc.,,,,,'. ...........'..;:lloolc:loocclllc'.'.,0MMMMMMMMMMMMMWk,.,,,..kMMM
MMK;.,,,,'.:xKWWMMMMMMWXkc'',,,,'....,c'..........;clllol:cooc:cllll;.''.;xKNWMMMMMMWXOl'',,,,.'OMMM
MMK:.,,,,,,'';clloooolc;'',,,,'.'okc.,;..........;ccccclccc:;,;lllll:.',,'.,:clloollc;'',,,,,,.'OMMM
MMXc..'',,,,,,,,,''',,,,,,'..';dKN0l,''..''''',;:clllllcc:::::clllll;...',,,,,''''',,,,,,,,''..;0MMM
MMWXkdl:;,'''..........'',:lx0NMNd;;::cl;...;:;coooooooc:::;;:clllll,:do:;,'...........'',;:coxKWMMM
MMMMMMMWNXK0OkdddddddxkOKXWMMMMKo;:llc:,..':'..dX0kxoolc::::ccllccll:;xNWNK0kxdddodddxk0KXNWMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMNOc;clllc;....:lod0WWWNKOd:clccloooodxOO:oNMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMWO;;:cllccc;;lkKNWXKNWWMNOllld0KKKKXXNWWO;lNMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMKl;:cl;,;cld0WWWWNkkXWWOllcl0WWXKNWWWWNd,,kWMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0c;cc:::xNNNXkdkxxdxkdc:lccxNN00WWWWXdc;,xWMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMWXkl,.';:;dNWWOcxNWWWOl;,cll::oodxkOXXl':dONMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMNxcokOx:;coxKNWKokMMWk:',cllc,;;;xKKKKo.;KMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMk:kWWWWKxoONXXNNxlkXO;,cccll:;,,,ckXNNO;,kWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMWxc0WWWWWN00NWWWWN0coOo;;;:ccccclocoKWN0l.:KMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMKddKWWWWWWWWWWWWWXllNW0ko;:dxxk0NNXKKNNO:oNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMNOxxkkkkkkkxxkkkxdKWMMM0:oNWNWWWWWNKXNx:kMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWX0OkkkO0KXXXNNWMMMMMXldNWWWWWWWWWXxcxNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMKxdOKNNNNKOxoo0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKOkkkkxddkKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM""")
print("{0:^100}".format("Thanks for using Eden's Trader Editor."))
print("{0:^100}".format("If you can any questions, feel free to join our Discord:"))
print("{0:^100}".format("https://discord.gg/a2SZD3D"))
set_color('')
os.system("pause")
    