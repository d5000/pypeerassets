
'''miscellaneous utilities.'''

import binascii
from pypeerassets.constants import *
from pypeerassets import paproto

def localnode_testnet_or_mainnet(node):
    '''check if local node is configured to testnet or mainnet'''

    if node.getinfo()["testnet"] is True:
        return "testnet"
    else:
        return "mainnet"

def load_p2th_privkeys_into_node(node):
    '''load production p2th privkey into local node'''

    if localnode_testnet_or_mainnet(node) is "testnet":
        try:
            node.importprivkey(testnet_PAPROD, "PAPROD")
            assert testnet_PAPROD_addr in node.getaddressesbyaccount("PAPROD")
        except Exception:
            return {"error": "Loading P2TH privkey failed."}
    else:
        try:
            node.importprivkey(mainnet_PAPROD, "PAPROD")
            assert mainnet_PAPROD_addr in node.getaddressesbyaccount("PAPROD")
        except Exception:
            return {"error": "Loading P2TH privkey failed."}

def load_test_p2th_privkeys_into_node(node):
    '''load test p2th privkeys into local node'''

    if localnode_testnet_or_mainnet(node) is "testnet":
        try:
            node.importprivkey(testnet_PATEST, "PATEST")
            assert mainnet_PATEST_addr in node.getaddressesbyaccount("PATEST")
        except Exception:
            return {"error": "Loading P2TH privkey failed."}

    else:
        try:
            node.importprivkey(mainnet_PATEST, "PATEST")
            assert mainnet_PAPROD_addr in node.getaddressesbyaccount("PATEST")
        except Exception:
            return {"error": "Loading P2TH privkey failed."}

def find_deck_spawns(node, prod_or_test="prod"):
    '''find deck spawn transactions via local node, it requiers that Deck spawn P2TH were imported in local node.'''

    if prod_or_test == "prod":
        decks = [i["txid"] for i in node.listtransactions("PAPROD")]
    else:
        decks = [i["txid"] for i in node.listtransactions("PATEST")]

    return decks

def read_tx_opreturn(node, txid):
    '''Decode OP_RETURN message from <txid>'''

    vout = node.getrawtransaction(txid, 1)['vout'][1] # protocol requires that OP_RETURN is vout[1]

    asm = vout['scriptPubKey']['asm']
    n = asm.find('OP_RETURN')
    if n == -1:
        return False #{'error': 'OP_RETURN not found'}
    else:
        # add 10 because 'OP_RETURN ' is 10 characters
        n += 10
        data = asm[n:]
        n = data.find(' ')
        #make sure that we don't include trailing opcodes
        if n == -1:
            return binascii.unhexlify(data)
        else:
            return binascii.unhexlify(data[:n])

def validate_deckspawn_metainfo(deck):
    '''validate deck_spawn'''

    assert deck.version > 0, {"error": "Deck metainfo incomplete, version can't be 0."}
    assert deck.name is not "", {"error": "Deck metainfo incomplete, Deck must have a name."}
    assert deck.issue_mode in (0, 1, 2, 4), {"error": "Deck metainfo incomplete, unknown issue mode."}

def parse_deckspawn_metainfo(protobuf):
    '''decode deck_spawn tx op_return protobuf message and validate it.'''

    deck = paproto.DeckSpawn()
    deck.ParseFromString(protobuf)

    validate_deckspawn_metainfo(deck)

    return {
        "version": deck.version,
        "name": deck.name,
        "issue_mode": deck.MODE.Name(deck.issue_mode),
        "number_of_decimals": deck.number_of_decimals,
        "asset_specific_data": deck.asset_specific_data
    }

def validate_deckspawn_p2th(node, deck_id, testnet=False, prod_or_test="prod"):
    '''validate if deck spawn pays to p2th in vout[0] and if it correct P2TH address'''

    raw = node.getrawtransaction(deck_id, 1)
    vout = raw["vout"][0]["scriptPubKey"].get("addresses")[0]
    error = {"error": "This deck is not properly tagged."}

    if testnet:

        if prod_or_test == "prod":
            assert vout == constants.testnet_PAPROD_addr, error
            return True
        if prod_or_test == "test":
            assert vout == constants.testnet_PATEST_addr, error
            return True

    if not testnet:

        if prod_or_test == "prod":
            assert vout == constants.mainnet_PAPROD_addr, error
            return True
        if prod_or_test == "test":
            assert vout == constants.mainnet_PATEST_addr, error
            return True

def load_deck_p2th_into_local_node(node, deck, prod=True):
    '''
    load deck p2th into local node,
    this allows building of proof-of-timeline for this deck
    '''

    error = {"error": "Deck P2TH import went wrong."}

    if localnode_testnet_or_mainnet(node) == "testnet":

        if prod:

            node.importprivkey(testnet_PAPROD, deck["name"])
            assert testnet_PAPROD_addr in node.getaddressesbyaccount(deck["name"]), error

        else:

            node.importprivkey(testnet_PATEST, deck["name"])
            assert testnet_PATEST_addr in node.getaddressesbyaccount(deck["name"]), error

    else:

        if prod:

            node.importprivkey(mainnet_PAPROD, deck["name"])
            assert testnet_PAPROD_addr in node.getaddressesbyaccount(deck["name"]), error

        else:

            node.importprivkey(mainnet_PATEST, deck["name"])
            assert testnet_PATEST_addr in node.getaddressesbyaccount(deck["name"]), error

