import time

from createKeystore import *

test_name = "sendTokenPrivacy"
data = None

with open('../util/test_data.json') as json_file:
    data = json.load(json_file)


class SendTokenPrivacy(CreateKeystore):
    """ Class to test send privacy transaction """

    def __init__(self):
        super(SendTokenPrivacy, self).__init__()
        self.tx_hash = ''
        self.token_ota = ''

    def send_token_privacy_transaction(self):
        """ test send privacy transaction"""

        print sys._getframe().f_code.co_name + ": start"

        print "tokenBuyStamp start"
        child = pexpect.spawn('node tokenBuyStamp --address ' + data['wallet']['address'] +
                              ' --stampBalance 1' +
                              ' --FeeSel ' + data['send']['fee_selection'] +
                              ' --gasLimit ' + data['send']['gas_price'] +
                              ' --gasPrice ' + data['send']['gas_limit'] +
                              ' --submit ' + data['send']['submit'] +
                              ' --password ' + data['wallet']['password'], cwd='../../src/')
        if commonUtil.show_logs:
             child.logfile = sys.stdout
        commonUtil.check_expect_eof(child, test_name)


        # create a wallet with balance
        self.create_wallet()


        # Start privacy transaction
        print "tokenSendPrivacy start"
        child = pexpect.spawn('node tokenSendPrivacy --address ' + data['wallet']['address'] +
                              ' --contractBalance 1' +
                              ' --waddress ' + self.get_wan_address() +
                              ' --amount ' + data['send']['amount']
                              , cwd='../../src/')

        if commonUtil.show_logs:
             child.logfile = sys.stdout

        commonUtil.check_expect_condition("Input stamp OTA you want to us", child, test_name, "Input stamp OTA you want to us")
        result = child.after
        count = str(result.count("status"))

        child = pexpect.spawn('node tokenSendPrivacy --address ' + data['wallet']['address'] +
                              ' --contractBalance 1' +
                              ' --waddress ' + self.get_wan_address() +
                              ' --amount ' + data['send']['amount'] +
                              ' --stampOTA ' + count +
                              ' --submit ' + data['send']['submit'] +
                              ' --password ' + data['wallet']['password'], cwd='../../src/')
        if commonUtil.show_logs:
             child.logfile = sys.stdout
        commonUtil.check_expect_condition(data['send']['txn_message'], child, test_name,
                                          "Transaction hash not found")
        print "tokenSendPrivacy end"



        # Transaction successful, now wait for block to get scanned
        time.sleep(int(data['send privacy']['fetch OTA wait time']))
        print "fetchTokenOTA start"
        child = pexpect.spawn('node fetchTokenOTA --address ' + self.get_address() +
                              ' --password ' + self.get_password(), cwd='../../src/')

        if commonUtil.show_logs:
            child.logfile = sys.stdout

        commonUtil.check_expect_eof(child, test_name)

        result = child.before
        summary = result.find(data['fetchOTA']['ota_message'])
        ota_start = ''
        if (summary != -1):
            ota_start = result.find('0x', summary)

        if (ota_start != -1 & summary != -1):
            self.token_ota = result[ota_start:ota_start + 134]
        else:
            commonUtil.exit_test('OTA not found', test_name, child)
        print "fetchTokenOTA end"




        time.sleep(float(data['general']['balance sync sleep time']))
        print "watchTokenOTA start"
        child = pexpect.spawn('node watchTokenOTA --address ' + self.get_address() +
                              ' --tokenAddress ' + data['wallet']['token address'] +
                              ' --OTAAddress ' + self.token_ota, cwd='../../src/')

        if commonUtil.show_logs:
            child.logfile = sys.stdout

        commonUtil.check_expect_condition(data['wallet']['token address'] + ")[\s\S]*(" + data['send']['amount'],
                                          child,
                                          test_name,
                                          "Balance not found")
        print "watchTokenOTA end"


        print sys._getframe().f_code.co_name + ": end"

def main():
    sendTokenPrivacy = SendTokenPrivacy()
    print (" --------------- " + test_name + " start -------------")
    sendTokenPrivacy.send_token_privacy_transaction()
    commonUtil.test_successful(test_name)
    print (" --------------- " + test_name + " complete -------------")


if __name__ == "__main__":
    main()
    commonUtil.write_results()
